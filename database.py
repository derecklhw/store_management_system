# run only 2 times for creation of database schema and creation/insertion of records in tables
import mysql.connector

db_name = "sms_database"

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
    print(f"{db_name} has been created. Re-run the script to create and insert records in tables")
    exit()

# check to see if connection to MySQL was created
print(f"[{my_db}] connection created")
print(f"{db_name} exists")

# create a cursor and initialize it
my_cursor = my_db.cursor()

# to create tables
# shopkeepers table
my_cursor.execute("CREATE TABLE shopkeepers (userId INT AUTO_INCREMENT PRIMARY KEY, \
                    username VARCHAR(255), \
                    lastName VARCHAR(255), \
                    firstName VARCHAR(255), \
                    password VARCHAR(255), \
                    totalCommission INT(255))")

# customers table
my_cursor.execute("CREATE TABLE customers (customerId INT AUTO_INCREMENT PRIMARY KEY, \
                  lastName VARCHAR(255), \
                  firstName VARCHAR(255), \
                  geographicalLocation VARCHAR(255), \
                  email VARCHAR(255), \
                  status VARCHAR(255), \
                  shopkeeperUsername VARCHAR(255))")

# stock table
my_cursor.execute("CREATE TABLE stock (productId INT AUTO_INCREMENT PRIMARY KEY, \
                    productName VARCHAR(255), \
                    price INT(255), \
                    quantity INT(255), \
                    geographicalLocation VARCHAR(255))")

# order table
my_cursor.execute("CREATE TABLE orderTable (orderId INT AUTO_INCREMENT PRIMARY KEY, \
                    orderDescription VARCHAR(255), \
                    totalPrice INT(255), \
                    taxAmount INT(255), \
                    commissionAmount INT(255), \
                    buyerLastName VARCHAR(255), \
                    buyerFirstName VARCHAR(255), \
                    orderDate DATE, \
                    paymentMethod VARCHAR(255), \
                    shopkeeperUsername VARCHAR(255))")

# to insert records in tables
# shopkeepers records
sql = "INSERT INTO shopkeepers (username, lastName, firstName, password, totalCommission) VALUES (%s, %s, %s, %s, %s)"
values = [
    ("DL661", "Lam Hon Wah", "Dereck", "12345", 25000),
    ("MJ806", "Muddathir", "Joomun", "password", 10000),
    ("AH1963", "Hobass", "Ashfaaq", "hello", 30000)
]

my_cursor.executemany(sql, values)
my_db.commit()

# customers records
sql = "INSERT INTO customers (lastName, firstName, geographicalLocation, email, status, shopkeeperUsername) \
        VALUES (%s, %s, %s, %s, %s, %s)"
values = [
    ("Corinne", "Hilton", "PHONE", "CH@gmail.com", "start", "NULL"),
    ("Sonny", "Trejo", "LAPTOP", "ST@gmail.com", "start", "NULL"),
    ("Kelsea", "Bean", "ACCESSORIES", "KB@hotmail.com", "start", "NULL"),
    ("Safwan", "Andrade", "PHONE", "SA@icloud.com", "start", "NULL"),
    ("Laurie", "Lim", "LAPTOP", "LL@gmail.com", "start", "NULL"),
    ("Jovan", "Meza", "ACCESSORIES", "JM@hotmail.com", "start", "NULL"),
    ("Ocean", "Ibaara", "LAPTOP", "OI@hotmail.com", "start", "NULL"),
    ("Bobbie", "Guy", "TV", "BG@hotmail.com", "start", "NULL"),
    ("Courtney", "Ware", "LAPTOP", "CW@hotmail.com", "start", "NULL"),
    ("Sofia", "Rollins", "PHONE", "SR@hotmail.com", "start", "NULL"),
    ("Anabel", "Ryder", "ACCESSORIES", "AR@hotmail.com", "start", "NULL"),
    ("Kasey", "Senior", "LAPTOP", "KS@hotmail.com", "start", "NULL"),
    ("Arooj", "Fuller", "TV", "AF@hotmail.com", "start", "NULL"),
    ("Emeli", "Conner", "LAPTOP", "EC@hotmail.com", "start", "NULL"),
    ("Jess", "Steadman", "ACCESSORIES", "JS@hotmail.com", "start", "NULL"),
    ("Octavia", "Caldwell", "PHONE", "PC@hotmail.com", "start", "NULL"),
    ("Mica", "Shepard", "TV", "MS@hotmail.com", "start", "NULL"),
    ("Daniel", "Walter", "ACCESSORIES", "SW@hotmail.com", "start", "NULL"),

]

my_cursor.executemany(sql, values)
my_db.commit()

# stock records
sql = "INSERT INTO stock (productName, price, quantity, geographicalLocation) VALUES (%s, %s, %s, %s)"
values = [
    ("Samsung Galaxy A03", 8100, 20, "PHONE"),
    ("Xiaomi 11T", 28150, 20, "PHONE"),
    ("Apple Iphone SE", 26900, 20, "PHONE"),
    ("Oppo A54", 9690, 20, "PHONE"),
    ("ASUS Zen Book", 53975, 20, "LAPTOP"),
    ("HP Victus", 52275, 20, "LAPTOP"),
    ("Lenovo Chromebook", 19000, 20, "LAPTOP"),
    ("Huawei Matebook", 53000, 20, "LAPTOP"),
    ("Mi LED Smart TV", 32500, 20, "TV"),
    ("Samsung Smart TV", 18990, 20, "TV"),
    ("Westpoint Smart TV", 23590, 20, "TV"),
    ("TCL Television", 11890, 20, "TV"),
    ("Razer Rogue Backpack", 3950, 20, "ACCESSORIES"),
    ("Moshi Pluma", 2150, 20, "ACCESSORIES"),
    ("Belkin True Privacy", 2100, 20, "ACCESSORIES"),
    ("Microsoft surface dial", 5950, 20, "ACCESSORIES")
]

my_cursor.executemany(sql, values)
my_db.commit()
