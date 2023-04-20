import socket
import time
import pickle
import mysql.connector
from datetime import date

# database name
db_name = "sms_database"

# assign the current date to order date
today = date.today()
order_date = today.strftime("%Y-%m-%d")

# create connection to the database
# try will test if database schema exists
try:
    my_db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Dragon4698",
        database=db_name
    )

# except will handle the error and create a database schema
except mysql.connector.errors.ProgrammingError:
    my_db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Dragon4698"
    )

    # create a cursor and initialize it
    my_cursor = my_db.cursor()
    # create database
    my_cursor.execute(f"CREATE DATABASE {db_name}")
    print(f"[MySQL DATABASE] {db_name} has been created. Re-run program")
    exit()

# check to see if connection to MySQL was created
print(f"[{my_db}] connection created")
print(f"[MySQL DATABASE] {db_name} exists")

# create a cursor and initialize it
my_cursor = my_db.cursor()

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname("localhost")
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

# create a server socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bin server and a port with a specific socket
server.bind(ADDR)


# serialize an object and send data stream to client
def send_data(conn, msg):
    pickle_object = pickle.dumps(msg)
    conn.send(pickle_object)


# receive data-stream from client and deserialize it to an object
def rec_data(conn):
    received_data = conn.recv(2018)
    return pickle.loads(received_data)


def user_authentication(conn):
    username_list = []
    password_list = []
    userid_list = []

    client_username = rec_data(conn)
    client_password = rec_data(conn)

    my_cursor.execute("SELECT username, password, userId FROM shopkeepers")
    username_password_list = my_cursor.fetchall()

    # loop username_password_list to retrieve all username, password and user_id and append them to respective list
    for x in username_password_list:
        username_list.append(x[0])
        password_list.append(x[1])
        userid_list.append(x[2])

    count = 0
    password_check = ""
    user_id = ""
    # loop through username_list to check if it matches the inputted username
    for user in username_list:
        # if true assign its corresponding password and user_id to two variables
        if user == client_username:
            password_check = password_list[count]
            user_id = userid_list[count]
            break
        else:
            count += 1

    # if inputted password matches password variable
    if client_password == password_check:
        print(f"[LOGIN SUCCESSFUL] user {client_username} logged in.")
        # send user_id to client
        msg = f"{user_id}"
        send_data(conn, msg)
        time.sleep(0.1)
    else:
        print(f"[LOGIN FAILED] user failed to log in.")
        msg = "failed"
        send_data(conn, msg)
        time.sleep(0.1)


def save_new_client(conn):
    # receive a list of new client details
    new_client = rec_data(conn)
    # insert a new records to customers table with data received from client
    sql = "INSERT INTO customers (lastName, firstName, geographicalLocation, email, status, shopkeeperUsername) \
            VALUES (%s, %s, %s, %s, %s, %s)"
    values = (new_client[0], new_client[1], new_client[2], new_client[3], "start", "NULL")
    my_cursor.execute(sql, values)
    my_db.commit()

    msg = f"[NEW CLIENT CREATED] {new_client[0]} {new_client[1]}"
    print(msg)
    send_data(conn, msg)
    time.sleep(0.1)


def unserved_customers_database(conn):
    sql = "SELECT customerId, lastName, firstName, geographicalLocation, email FROM customers WHERE status = %s"
    status = ("start",)
    my_cursor.execute(sql, status)
    # assign selected data to customers_lists
    customers_lists = my_cursor.fetchall()

    msg = f"[MySQL DATABASE] customers database has been extracted"
    print(msg)
    # send customers_lists to client
    send_data(conn, customers_lists)
    time.sleep(0.1)
    send_data(conn, msg)
    time.sleep(0.1)


def update_client(conn):
    # receive client details to be updated in the customers table
    client_details = rec_data(conn)
    my_cursor.execute(f"UPDATE customers SET lastName = \"{client_details[1]}\", \
                        firstName = \"{client_details[2]}\", \
                        geographicalLocation = \"{client_details[2]}\", \
                        email = \"{client_details[3]}\" \
                        WHERE customerId = {(client_details[0])}")
    my_db.commit()

    msg = f"[CLIENT UPDATED SUCCESSFULLY]"
    print(msg)
    send_data(conn, msg)
    time.sleep(0.1)


def delete_one_client(conn):
    # receive client_id of client to be deleted
    client_id = rec_data(conn)
    my_cursor.execute(f"DELETE FROM customers WHERE customerId = {client_id}")
    my_db.commit()

    msg = "[CLIENT DELETED SUCCESSFULLY]"
    print(msg)
    send_data(conn, msg)
    time.sleep(0.1)


# extract the records of stock table and sent them to client for view table option
def product_database(conn):
    sql = "SELECT productId, productName, price, quantity, geographicalLocation FROM stock"
    my_cursor.execute(sql)
    product_list = my_cursor.fetchall()

    msg = f"[MySQL DATABASE] customers database has been extracted"
    print(msg)
    send_data(conn, product_list)
    time.sleep(0.1)
    send_data(conn, msg)
    time.sleep(0.1)


def order_confirm(conn):
    # receive a list of product ordered by client
    order_id_list = rec_data(conn)
    # loop through the list and decrease qty by 1 in stock table
    for x in order_id_list:
        sql = f"UPDATE stock SET quantity = quantity - 1 WHERE productId = {x}"
        my_cursor.execute(sql)
        my_db.commit()

    # loop through the list and retrieve and sum each product's price to obtain total order price
    total_order_price = 0
    for x in order_id_list:
        sql = f"SELECT price FROM stock WHERE productId = {x}"
        my_cursor.execute(sql)
        product_price_tuple = my_cursor.fetchall()
        product_price_list = product_price_tuple[0]
        product_price = int(product_price_list[0])
        total_order_price += product_price

    msg = f"[MySQL DATABASE] stock has been updated"
    print(msg)
    send_data(conn, msg)
    time.sleep(0.1)
    send_data(conn, total_order_price)
    time.sleep(0.1)


def update_client_state(conn):
    # receive client and shopkeeper id to change the status of the client
    client_shopkeeper_id = rec_data(conn)
    sql = f"UPDATE customers SET status = 'finish', shopkeeperUsername = \"{client_shopkeeper_id[1]}\" \
                WHERE customerId = {client_shopkeeper_id[0]}"
    my_cursor.execute(sql)
    my_db.commit()

    # retrieve the lastname and firstname of customer and send same to client
    sql = f"SELECT lastname, firstname FROM customers WHERE customerId = {client_shopkeeper_id[0]}"
    my_cursor.execute(sql)
    name = my_cursor.fetchall()

    msg = f"[CLIENT UPDATED SUCCESSFULLY]"
    print(msg)
    send_data(conn, msg)
    time.sleep(0.1)
    send_data(conn, name)
    time.sleep(0.1)


def sent_order(conn):
    # receive details of order and create a new record in order table following confirmation of order
    order_details = rec_data(conn)
    sql = "INSERT INTO orderTable (orderDescription, \
                                    totalPrice, taxAmount, \
                                    commissionAmount, \
                                    buyerLastName, \
                                    buyerFirstName, \
                                    orderDate, \
                                    paymentMethod, \
                                    shopkeeperUsername) \
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    values = (
        order_details[0], order_details[1], order_details[2], order_details[3], order_details[4], order_details[5],
        order_date, order_details[6], order_details[7])
    my_cursor.execute(sql, values)
    my_db.commit()

    # increase current shopkeeper total commission by the total commission amount
    sql = f"UPDATE shopkeepers SET totalCommission = totalCommission + {order_details[3]} \
                WHERE userId = {order_details[8]}"
    my_cursor.execute(sql)
    my_db.commit()

    msg = f"[MySQL DATABASE] order registered"
    print(msg)
    send_data(conn, msg)
    time.sleep(0.1)


def extract_daily_commission_and_sales(conn):
    total_daily_sales = 0
    total_daily_commission = 0
    username = rec_data(conn)

    # extract a tuple of order'sales and commission from order table
    sql = f"SELECT totalPrice, commissionAmount FROM orderTable \
                    WHERE orderDate = \"{order_date}\" AND shopkeeperUsername = \"{username}\""
    my_cursor.execute(sql)
    sales_and_commission = my_cursor.fetchall()

    # loop through the tuple to obtain total daily sales anc commission
    for order in sales_and_commission:
        total_daily_sales += order[0]
        total_daily_commission += order[1]

    msg = "[MySQL DATABASE] daily sales and commission extracted"
    send_data(conn, (total_daily_sales, total_daily_commission))
    time.sleep(0.1)
    send_data(conn, msg)
    time.sleep(0.1)


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True
    while connected:
        # receive the length of the msg
        msg_length = conn.recv(HEADER).decode(FORMAT)

        if msg_length:
            # count the lenght of the msg
            msg_length = int(msg_length)
            # receive a msg functions with buffer length of the msg
            msg = conn.recv(msg_length).decode(FORMAT)
            print(f"{addr} {msg}")

            # msg functions
            if msg == DISCONNECT_MESSAGE:
                connected = False
            elif msg == "user authentication":
                user_authentication(conn)
            elif msg == "save_new_client":
                save_new_client(conn)
            elif msg == "unserved_customers_database":
                unserved_customers_database(conn)
            elif msg == "update_client":
                update_client(conn)
            elif msg == "delete_one_client":
                delete_one_client(conn)
            elif msg == "product_database":
                product_database(conn)
            elif msg == "order_confirm":
                order_confirm(conn)
            elif msg == "update_client_state":
                update_client_state(conn)
            elif msg == "sent_order":
                sent_order(conn)
            elif msg == "extract_daily_commission_and_sales":
                extract_daily_commission_and_sales(conn)
            else:
                pass
            conn.send(f"[COMMAND EXECUTED] {msg}".encode(FORMAT))

    # close the connection if disconnect msg receive from client
    conn.close()
    print(f"[CONNECTION] {addr} disconnected")


def start():
    # listen for a connection from the client
    server.listen()

    print(f"[LISTENING] Server is listening on {SERVER}")

    # accept requests from a client socket
    conn, addr = server.accept()

    # function to keep waiting for incoming msg
    handle_client(conn, addr)


print("[STARTING] server is starting...")
start()
