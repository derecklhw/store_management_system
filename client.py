import socket
import pickle
import time
from datetime import datetime, date
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageTk, Image
from matplotlib import pyplot as plt
import tomli

with open("config.toml", "rb") as toml:
    toml_dict = tomli.load(toml)

HEADER = toml_dict["server"]["header"]
PORT = toml_dict["server"]["port"]
SERVER = socket.gethostbyname('localhost')
ADDR = (SERVER, PORT)
FORMAT = toml_dict["server"]["format"]
DISCONNECT_MESSAGE = "!DISCONNECT"

# create a client socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connects the client to the server IP address
client.connect(ADDR)
print(f"[CONNECTION ESTABLISHED] connecting to {SERVER}")

USER_ID = ""
USERNAME = ""


# send msg function to server
def send_msg(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)


# receive and print msg function executed from server
def rec_msg():
    print(client.recv(2018).decode(FORMAT))


# serialize an object and send data stream to client
def send_data(msg):
    pickle_object = pickle.dumps(msg)
    client.send(pickle_object)


# receive data-stream from client and deserialize it to an object
def rec_data():
    received_data = client.recv(2018)
    return pickle.loads(received_data)


def center_window(window, width, height):
    # get the screen dimension
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # find the center point
    center_x = int(screen_width / 2 - width / 2)
    center_y = int(screen_height / 2 - height / 2)

    # set the position of the window to center of the screen

    window.geometry(f"{width}x{height}+{center_x}+{center_y}")


class Log_In_Window(tk.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.root = root

        # configure the window
        center_window(self, 500, 250)
        self.title("USER AUTHENTICATION")
        self.resizable(False, False)

        # open and identifies the give image file
        self.background_image = (Image.open("asset/images/login_background.png"))
        # create a background image object
        self.new_background_image = ImageTk.PhotoImage(self.background_image)

        background_image_label = tk.Label(self, image=self.new_background_image)
        background_image_label.place(x=-160, y=-3)

        log_in_frame = tk.Frame(self)
        log_in_frame.place(relx=0.5, rely=0.5, anchor='center')

        # configure log_in_frame widgets
        username_label = tk.Label(log_in_frame, text="Username")
        password_label = tk.Label(log_in_frame, text="Password")
        self.username_entry = tk.Entry(log_in_frame, borderwidth=2)
        self.password_entry = tk.Entry(log_in_frame, show="*", borderwidth=2)
        log_in_button = tk.Button(log_in_frame, text="Login", command=self.login)
        cancel_button = tk.Button(log_in_frame, text="Exit", command=self.exit)

        # grid log_in_frame_widgets
        username_label.grid(row=0, column=0)
        password_label.grid(row=1, column=0)
        self.username_entry.grid(row=0, column=1)
        self.password_entry.grid(row=1, column=1)
        log_in_button.grid(row=2, column=0, pady=5)
        cancel_button.grid(row=2, column=1, pady=5)

    def exit(self):
        cancel_confirmation = tk.messagebox.askyesno("Exit", "Are you sure?")
        # if yes, destroy root window and login window
        if cancel_confirmation:
            self.destroy()
            self.master.destroy()
            send_msg(DISCONNECT_MESSAGE)
            rec_msg()

    def login(self):
        # if username or password entry box values are empty, pop a message box
        if len(self.password_entry.get()) == 0 or len(self.username_entry.get()) == 0:
            messagebox.showwarning("USER AUTHENTICATION", "Username/Password Missing")
            # clear username and password entry boxes
            self.username_entry.delete(0, "end")
            self.password_entry.delete(0, "end")

        else:
            print("[USER AUTHENTICATION] initialised")
            # send user_authentication msg function to server
            send_msg("user authentication")
            username = self.username_entry.get()
            password = self.password_entry.get()

            # send username to server
            send_data(username)
            time.sleep(0.1)
            send_data(password)

            response = rec_data()
            # if username and password doesn't match database
            if response == "failed":
                print(f"[LOGIN FAILED] user failed to log in")
                messagebox.showwarning("USER AUTHENTICATION", "Username/Password incorrect")
                self.username_entry.delete(0, "end")
                self.password_entry.delete(0, "end")
                rec_msg()

            else:
                print(f"[LOGIN SUCCESSFUL] {username} logged in")
                global USER_ID, USERNAME
                USER_ID = response
                USERNAME = username
                rec_msg()

                tk.messagebox.showinfo("USER AUTHENTICATION", f"{USERNAME} login successfully.")
                self.destroy()
                # unhidden the root window
                self.master.deiconify()


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # configure the root window
        center_window(self, 1200, 700)
        self.title("SMS STORE MANAGEMENT SYSTEM")
        self.resizable(False, False)

        # status bar configuration displaying current date and time
        now = datetime.now()
        status_bar = tk.Label(self, text=f' Login Time: {now}', bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # on initialisation hide root window
        self.withdraw()
        # create top level window for log in
        Log_In_Window(self)


class MainFrame(tk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.container = container
        self.pack(fill="both", expand=1)

        # configure main frame column and rows
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=4)
        self.rowconfigure(0, weight=1)

        # configure button and background frame and grid them
        button_frame = tk.Frame(self, bg="medium purple")
        background_frame = tk.Frame(self)

        button_frame.grid(column=0, row=0, sticky="NSEW")
        background_frame.grid(column=1, row=0, sticky="NSEW")

        # configure button frame widgets and pack them in the frame
        self.user_label = tk.Label(button_frame, text=f"Welcome User", bg="medium purple", font=('lucida', 30))
        create_client_button = tk.Button(button_frame, text="Create client", command=self.create_new_client)
        order_button = tk.Button(button_frame, text="Create order", command=self.create_order)
        view_stock_button = tk.Button(button_frame, text="View stock", command=self.view_stock)
        dashboard_button = tk.Button(button_frame, text="Dashboard", command=self.dashboard)
        log_off_button = tk.Button(button_frame, text="Log off", command=self.log_off)

        self.user_label.pack(pady=20)
        create_client_button.pack(pady=20)
        order_button.pack(pady=20)
        view_stock_button.pack(pady=20)
        dashboard_button.pack(pady=20)
        log_off_button.pack(pady=20)

        # open and identifies the give image file
        self.background_image = (Image.open("asset/images/main_background.png"))
        # create a background image object
        self.new_background_image = ImageTk.PhotoImage(self.background_image)
        # configure the background image and place in background frame
        background_image_label = tk.Label(background_frame, image=self.new_background_image)
        background_image_label.place(x=-950, y=-3)

    def create_new_client(self):
        window = CreateNewCustomer(self.container)
        # grab_set allow top level window to receive events and prevent users to interact with root window
        window.grab_set()

    def create_order(self):
        window = CreateOrder(self.container)
        window.grab_set()

    def view_stock(self):
        window = ViewStock(self.container)
        window.grab_set()

    # view daily summary of current shopkeeper in a bar plot
    def dashboard(self):
        plt.title("DASHBOARD")

        # send extract_daily_commission_and_sales msg function to server
        send_msg("extract_daily_commission_and_sales")
        time.sleep(0.1)
        send_data(USERNAME)
        # retrieve total daily commission and sales for current log in user
        daily_commission_and_sales = rec_data()
        print(rec_data())
        rec_msg()

        # create data for x and y axis
        x = ["Daily Sales", "Daily Commission"]
        y = [daily_commission_and_sales[0], daily_commission_and_sales[1]]

        # plot data on bar plot
        plt.bar(x, y, label=USERNAME, color="#ED855A")
        # add label on y-axis
        plt.ylabel('Amount in Mauritian Rupees')
        plt.legend()
        plt.show()

    def log_off(self):
        cancel_confirmation = tk.messagebox.askyesno("Log off", "Are you sure?")
        if cancel_confirmation:
            self.container.destroy()
            send_msg(DISCONNECT_MESSAGE)
            rec_msg()


class CreateNewCustomer(tk.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.root = root

        # configure the window
        center_window(self, 400, 300)
        self.title("CREATE CLIENT")
        self.resizable(False, False)
        self.configure(bg="#857CC5")

        # configure customer details frame and pack it
        customer_details_frame = tk.LabelFrame(self, text="Customer Detail", bg="#ececed")
        customer_details_frame.pack(padx=10, pady=10, fill="both", expand=1)

        # configure customer details frame widget and grid them
        last_name_label = tk.Label(customer_details_frame, text="Last Name")
        first_name_label = tk.Label(customer_details_frame, text="First Name")
        geographical_position_label = tk.Label(customer_details_frame, text="Geographical Location")
        email_label = tk.Label(customer_details_frame, text="Email")

        self.last_name_entry = tk.Entry(customer_details_frame)
        self.first_name_entry = tk.Entry(customer_details_frame)
        self.email_entry = tk.Entry(customer_details_frame)

        location_options = ["PHONE", "LAPTOP", "ACCESSORIES", "TV"]
        self.geographical_position_combo = ttk.Combobox(customer_details_frame, value=location_options)
        self.geographical_position_combo.current(0)

        save_button = tk.Button(customer_details_frame, text="Save", command=self.save)
        clear_button = tk.Button(customer_details_frame, text="Clear", command=self.clear)
        close_button = tk.Button(customer_details_frame, text="Close", command=self.close)

        last_name_label.grid(row=0, column=0, sticky='w', padx=10, pady=5)
        first_name_label.grid(row=1, column=0, sticky='w', padx=10, pady=5)
        geographical_position_label.grid(row=2, column=0, sticky='w', padx=10, pady=5)
        email_label.grid(row=3, column=0, sticky='w', padx=10, pady=5)

        self.last_name_entry.grid(row=0, column=1, columnspan=2, padx=(0, 10), pady=5)
        self.first_name_entry.grid(row=1, column=1, columnspan=2, padx=(0, 10), pady=5)
        self.geographical_position_combo.grid(row=2, column=1, columnspan=2, padx=(0, 10), pady=5)
        self.email_entry.grid(row=3, column=1, columnspan=2, padx=(0, 10), pady=5)

        save_button.grid(row=4, column=0, pady=5)
        clear_button.grid(row=4, column=1, pady=5)
        close_button.grid(row=4, column=2, pady=5)

    def save(self):
        send_msg("save_new_client")
        # retrieve details of new client from entry widgets and combo box
        last_name = self.last_name_entry.get()
        first_name = self.first_name_entry.get()
        geographical_position = self.geographical_position_combo.get()
        email = self.email_entry.get()

        # send details to server to insert a new record
        send_data((last_name, first_name, geographical_position, email))
        print(rec_data())
        rec_msg()
        tk.messagebox.showinfo("SAVE NEW CLIENT", "New client has been created successfully.")
        self.destroy()

    def clear(self):
        # clear all entry widgets
        self.last_name_entry.delete(0, "end")
        self.first_name_entry.delete(0, "end")
        self.geographical_position_combo.current(0)
        self.email_entry.delete(0, "end")

    def close(self):
        self.destroy()


class CreateOrder(tk.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.root = root

        # configure the window
        center_window(self, 1000, 500)
        self.title("CUSTOMERS DATABASE")
        self.resizable(False, False)
        self.configure(bg="#DDABA2")

        # add some style
        style = ttk.Style()

        # pick a theme
        style.theme_use("default")

        # configure our treeview colours
        style.configure("Treeview",
                        background="silver",
                        foreground="black",
                        rowheight=25,
                        fieldbackground="silver"
                        )

        # change selected colour
        style.map('Treeview', background=[('selected', '#CEA3A5')])

        # create Treeview frame
        tree_frame = tk.Frame(self)
        tree_frame.pack(pady=10)

        # Treeview scrollbar
        tree_scroll = tk.Scrollbar(tree_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # create Treeview
        self.stock_tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set, selectmode="extended")
        self.stock_tree.pack()

        # configure scrollbar
        tree_scroll.config(command=self.stock_tree.yview)

        # define the columns
        self.stock_tree['columns'] = ("ID", "Last Name", "First Name", "Geographical Location", "Email")

        # format the column
        self.stock_tree.column("#0", width=0, stretch=tk.NO)
        self.stock_tree.column("ID", width=80, anchor=tk.CENTER)
        self.stock_tree.column("Last Name", width=120, anchor=tk.W)
        self.stock_tree.column("First Name", width=120, anchor=tk.W)
        self.stock_tree.column("Geographical Location", width=120, anchor=tk.W)
        self.stock_tree.column("Email", width=150, anchor=tk.W)

        # create headings
        self.stock_tree.heading("#0", text="", anchor=tk.W)
        self.stock_tree.heading("ID", text="Customer ID", anchor=tk.CENTER)
        self.stock_tree.heading("Last Name", text="Last Name", anchor=tk.W)
        self.stock_tree.heading("First Name", text="First Name", anchor=tk.W)
        self.stock_tree.heading("Geographical Location", text="Location", anchor=tk.W)
        self.stock_tree.heading("Email", text="Email", anchor=tk.W)

        # create striped row tags
        self.stock_tree.tag_configure('oddrow', background="white")
        self.stock_tree.tag_configure('evenrow', background="#F4EAE5")

        # add record entry boxes
        data_frame = tk.LabelFrame(self, text="Client")
        data_frame.pack(fill="x", expand=1, padx=20)

        id_label = tk.Label(data_frame, text="Customer ID")
        ln_label = tk.Label(data_frame, text="Last Name")
        fn_label = tk.Label(data_frame, text="First Name")
        gl_label = tk.Label(data_frame, text="Location")
        email_label = tk.Label(data_frame, text="Email")

        self.id_entry = tk.Entry(data_frame)
        self.ln_entry = tk.Entry(data_frame)
        self.fn_entry = tk.Entry(data_frame)
        self.gl_entry = tk.Entry(data_frame)
        self.email_entry = tk.Entry(data_frame)

        id_label.grid(row=0, column=0, padx=10, pady=10)
        self.id_entry.grid(row=0, column=1, padx=10, pady=10)
        ln_label.grid(row=0, column=2, padx=10, pady=10)
        self.ln_entry.grid(row=0, column=3, padx=10, pady=10)
        fn_label.grid(row=0, column=4, padx=10, pady=10)
        self.fn_entry.grid(row=0, column=5, padx=10, pady=10)
        gl_label.grid(row=1, column=0, padx=10, pady=10)
        self.gl_entry.grid(row=1, column=1, padx=10, pady=10)
        email_label.grid(row=1, column=2, padx=10, pady=10)
        self.email_entry.grid(row=1, column=3, padx=10, pady=10)

        # Buttons
        button_frame = tk.LabelFrame(self, text="Functions")
        button_frame.pack(fill="x", expand=1, padx=30)

        order_button = tk.Button(button_frame, text="Order Client", command=self.order_client)
        update_button = tk.Button(button_frame, text="Update Client", command=self.update_client)
        remove_all_button = tk.Button(button_frame, text="Remove All Clients", command=self.remove_all,
                                      state="disabled")
        remove_one_button = tk.Button(button_frame, text="Remove One Client", command=self.remove_one)
        remove_selected_button = tk.Button(button_frame, text="Remove Selected Clients", command=self.remove_selected,
                                           state="disabled")
        clear_button = tk.Button(button_frame, text="Clear Details", command=self.clear_entries)
        close_button = tk.Button(button_frame, text="Close", command=self.close)

        order_button.grid(row=0, column=0, padx=10, pady=10)
        update_button.grid(row=0, column=1, padx=10, pady=10)
        remove_all_button.grid(row=0, column=2, padx=10, pady=10)
        remove_one_button.grid(row=0, column=3, padx=10, pady=10)
        remove_selected_button.grid(row=0, column=4, padx=10, pady=10)
        clear_button.grid(row=0, column=5, padx=10, pady=10)
        close_button.grid(row=0, column=6, padx=10, pady=10)

        # bind the treeview select function
        self.stock_tree.bind("<ButtonRelease-1>", self.select_client)

        # run to pull data from database on start
        self.query_database()

    def query_database(self):
        # send unserved_customers_database msg function to server
        send_msg("unserved_customers_database")
        # retrieve from database all new clients where status are 'start'
        customer_database = rec_data()
        print(rec_data())
        rec_msg()

        # insert the retrieved information in the treeview
        count = 0
        for customer in customer_database:
            if count % 2 == 0:
                self.stock_tree.insert(parent="", index="end", iid=count, text="",
                                       values=(customer[0], customer[1], customer[2], customer[3], customer[4]),
                                       tags=('evenrow',))
            else:
                self.stock_tree.insert(parent="", index="end", iid=count, text="",
                                       values=(customer[0], customer[1], customer[2], customer[3], customer[4]),
                                       tags=('oddrow',))

            count += 1

    def select_client(self, e):
        # clear entry boxes
        self.id_entry.delete(0, "end")
        self.ln_entry.delete(0, "end")
        self.fn_entry.delete(0, "end")
        self.gl_entry.delete(0, "end")
        self.email_entry.delete(0, "end")

        # grab record number
        selected = self.stock_tree.focus()
        values = self.stock_tree.item(selected, "values")

        # output entry boxes
        self.id_entry.insert(0, values[0])
        self.ln_entry.insert(0, values[1])
        self.fn_entry.insert(0, values[2])
        self.gl_entry.insert(0, values[3])
        self.email_entry.insert(0, values[4])

    def order_client(self):
        # retrieve selected client id
        client_id = self.id_entry.get()
        client_confirmation = tk.messagebox.askyesno("CLIENT DATABASE", "Client confirmation")

        if client_confirmation:
            window = OrderClient(self.root, client_id)
            window.grab_set()
            self.destroy()

    def update_client(self):
        selected = self.stock_tree.focus()
        # retrieve all customer's details from .get function and amend same on treeview dynamically
        self.stock_tree.item(selected, text="",
                             values=(self.id_entry.get(), self.ln_entry.get(), self.fn_entry.get(), self.gl_entry.get(),
                                     self.email_entry.get(),))

        # send update_client msg function to server
        send_msg("update_client")
        # retrieve all customer's details from .get function and server to server for databse update
        client_id = self.id_entry.get()
        ln = self.ln_entry.get()
        fn = self.fn_entry.get()
        gl = self.gl_entry.get()
        email = self.email_entry.get()
        send_data((client_id, ln, fn, gl, email))

        print(rec_data())
        time.sleep(0.1)
        rec_msg()
        # clear all entry boxes
        self.clear_entries()

    def remove_all(self):
        for customer in self.stock_tree.get_children():
            self.stock_tree.delete(customer)

    def remove_one(self):
        # to select the client index 0 among selected and delete in treeview
        selected = self.stock_tree.selection()[0]
        self.stock_tree.delete(selected)

        # send delete_one_client msg function to server
        send_msg("delete_one_client")
        # retrieve client id from entry box and send to server to delete in database
        client_id = self.id_entry.get()
        send_data(client_id)

        print(rec_data())
        time.sleep(0.1)
        rec_msg()

    def remove_selected(self):
        selected = self.stock_tree.selection()
        for customer in selected:
            self.stock_tree.delete(customer)

    def clear_entries(self):
        self.id_entry.delete(0, "end")
        self.ln_entry.delete(0, "end")
        self.fn_entry.delete(0, "end")
        self.gl_entry.delete(0, "end")
        self.email_entry.delete(0, "end")

    def close(self):
        self.destroy()


class OrderClient(tk.Toplevel):
    def __init__(self, root, selected):
        super().__init__(root)
        self.root = root
        self.client = selected

        # configure the window
        center_window(self, 1000, 600)
        self.title("CREATE ORDER")
        self.resizable(False, False)

        # open and identifies the give image file
        self.background_image = (Image.open("asset/images/main_background.png"))
        # create a background image object
        self.new_background_image = ImageTk.PhotoImage(self.background_image)
        # configure the background image and place in background frame
        background_image_label = tk.Label(self, image=self.new_background_image)
        background_image_label.place(x=-50, y=-3)

        # create order_id and order_description lists
        self.order_id_list = []
        self.order_description_list = []

        # configure left main frame
        left_frame = tk.Frame(self, width=500, height=550, bd=3, bg="#DDABA2")
        left_frame.pack(side=tk.LEFT, padx=30)

        # configure right main frame
        right_frame = tk.Frame(self, width=500, height=550, bd=3, bg="#F3A783")
        right_frame.pack(side=tk.RIGHT, padx=30)

        # configure right frame top
        right_frame_top = tk.Frame(right_frame, bg="#F3A783")
        right_frame_top.pack(side=tk.TOP)

        # configure right frame bottom
        right_frame_bottom = tk.Frame(right_frame, bg="#F3A783")
        right_frame_bottom.pack(side=tk.BOTTOM)

        # configure left main frame item label widgets
        samsung_galaxy_a03_label = tk.Label(left_frame, text="Samsung Galaxy A03", bg="#DDABA2")
        xiaomi_11t_label = tk.Label(left_frame, text="Xiaomi 11T", bg="#DDABA2")
        apple_iphone_se_label = tk.Label(left_frame, text="Apple Iphone SE", bg="#DDABA2")
        oppo_a54_label = tk.Label(left_frame, text="Oppo A54", bg="#DDABA2")
        asus_zen_book_label = tk.Label(left_frame, text="ASUS Zen Book", bg="#DDABA2")
        hp_victus_label = tk.Label(left_frame, text="HP Victus", bg="#DDABA2")
        lenovo_chromebook_label = tk.Label(left_frame, text="Lenovo Chromebook", bg="#DDABA2")
        huawei_matebook_label = tk.Label(left_frame, text="Huawei Matebook", bg="#DDABA2")
        mi_led_smart_tv_label = tk.Label(left_frame, text="Mi LED Smart TV", bg="#DDABA2")
        samsung_smart_tv_label = tk.Label(left_frame, text="Samsung Smart TV", bg="#DDABA2")
        westpoint_smart_tv_label = tk.Label(left_frame, text="Westpoint Smart TV", bg="#DDABA2")
        tcl_television_label = tk.Label(left_frame, text="TCL Television", bg="#DDABA2")
        razer_rogue_backpack_label = tk.Label(left_frame, text="Razer Rogue Backpack", bg="#DDABA2")
        moshi_pluma_label = tk.Label(left_frame, text="Moshi Pluma", bg="#DDABA2")
        belin_true_privacy_label = tk.Label(left_frame, text="Belkin True Privacy", bg="#DDABA2")
        microsoft_surface_dial_label = tk.Label(left_frame, text="Microsoft surface dial", bg="#DDABA2")

        # configure left main frame item add to cart button widgets
        samsung_galaxy_a03_button = tk.Button(left_frame, text="Add to cart",
                                              command=lambda: self.add_to_cart("Samsung Galaxy A03", 1))
        xiaomi_11t_button = tk.Button(left_frame, text="Add to cart", command=lambda: self.add_to_cart("Xiaomi 11T", 2))
        apple_iphone_se_button = tk.Button(left_frame, text="Add to cart",
                                           command=lambda: self.add_to_cart("Apple Iphone SE", 3))
        oppo_a54_button = tk.Button(left_frame, text="Add to cart", command=lambda: self.add_to_cart("Oppo A54", 4))
        asus_zen_book_button = tk.Button(left_frame, text="Add to cart",
                                         command=lambda: self.add_to_cart("ASUS Zen Book", 5))
        hp_victus_button = tk.Button(left_frame, text="Add to cart", command=lambda: self.add_to_cart("HP Victus", 6))
        lenovo_chromebook_button = tk.Button(left_frame, text="Add to cart",
                                             command=lambda: self.add_to_cart("Lenovo Chromebook", 7))
        huawei_matebook_button = tk.Button(left_frame, text="Add to cart",
                                           command=lambda: self.add_to_cart("Huawei Matebook", 8))
        mi_led_smart_tv_button = tk.Button(left_frame, text="Add to cart",
                                           command=lambda: self.add_to_cart("Mi LED Smart TV", 9))
        samsung_smart_tv_button = tk.Button(left_frame, text="Add to cart",
                                            command=lambda: self.add_to_cart("Samsung Smart TV", 10))
        westpoint_smart_tv_button = tk.Button(left_frame, text="Add to cart",
                                              command=lambda: self.add_to_cart("Westpoint Smart TV", 11))
        tcl_television_button = tk.Button(left_frame, text="Add to cart",
                                          command=lambda: self.add_to_cart("TCL Television", 12))
        razer_rogue_backpack_button = tk.Button(left_frame, text="Add to cart",
                                                command=lambda: self.add_to_cart("Razer Rogue Backpack", 13))
        moshi_pluma_button = tk.Button(left_frame, text="Add to cart",
                                       command=lambda: self.add_to_cart("Moshi Pluma", 14))
        belin_true_privacy_button = tk.Button(left_frame, text="Add to cart",
                                              command=lambda: self.add_to_cart("Belkin True Privacy", 15))
        microsoft_surface_dial_button = tk.Button(left_frame, text="Add to cart",
                                                  command=lambda: self.add_to_cart("Microsoft surface dial", 16))

        # grid left main frame label widgets
        samsung_galaxy_a03_label.grid(row=0, column=0, pady=5, padx=5)
        xiaomi_11t_label.grid(row=1, column=0, pady=5, padx=5)
        apple_iphone_se_label.grid(row=2, column=0, pady=5, padx=5)
        oppo_a54_label.grid(row=3, column=0, pady=5, padx=5)
        asus_zen_book_label.grid(row=4, column=0, pady=5, padx=5)
        hp_victus_label.grid(row=5, column=0, pady=5, padx=5)
        lenovo_chromebook_label.grid(row=6, column=0, pady=5, padx=5)
        huawei_matebook_label.grid(row=7, column=0, pady=5, padx=5)
        mi_led_smart_tv_label.grid(row=8, column=0, pady=5, padx=5)
        samsung_smart_tv_label.grid(row=9, column=0, pady=5, padx=5)
        westpoint_smart_tv_label.grid(row=10, column=0, pady=5, padx=5)
        tcl_television_label.grid(row=11, column=0, pady=5, padx=5)
        razer_rogue_backpack_label.grid(row=12, column=0, pady=5, padx=5)
        moshi_pluma_label.grid(row=13, column=0, pady=5, padx=5)
        belin_true_privacy_label.grid(row=14, column=0, pady=5, padx=5)
        microsoft_surface_dial_label.grid(row=15, column=0, pady=5, padx=5)

        # grid left main frame add to cart buttons
        samsung_galaxy_a03_button.grid(row=0, column=1, pady=5, padx=5)
        xiaomi_11t_button.grid(row=1, column=1, pady=5, padx=5)
        apple_iphone_se_button.grid(row=2, column=1, pady=5, padx=5)
        oppo_a54_button.grid(row=3, column=1, pady=5, padx=5)
        asus_zen_book_button.grid(row=4, column=1, pady=5, padx=5)
        hp_victus_button.grid(row=5, column=1, pady=5, padx=5)
        lenovo_chromebook_button.grid(row=6, column=1, pady=5, padx=5)
        huawei_matebook_button.grid(row=7, column=1, pady=5, padx=5)
        mi_led_smart_tv_button.grid(row=8, column=1, pady=5, padx=5)
        samsung_smart_tv_button.grid(row=9, column=1, pady=5, padx=5)
        westpoint_smart_tv_button.grid(row=10, column=1, pady=5, padx=5)
        tcl_television_button.grid(row=11, column=1, pady=5, padx=5)
        razer_rogue_backpack_button.grid(row=12, column=1, pady=5, padx=5)
        moshi_pluma_button.grid(row=13, column=1)
        belin_true_privacy_button.grid(row=14, column=1, pady=5, padx=5)
        microsoft_surface_dial_button.grid(row=15, column=1, pady=5, padx=5)

        # configure listbox for basket
        self.basket_list = tk.Listbox(right_frame_top, width=50, height=25)
        self.basket_list.pack(side=tk.TOP, padx=10, pady=10)

        # configure a combobox for mode of payment
        payment_method = ["Cash", "Debit/Credit Card"]
        self.payment_combo = ttk.Combobox(right_frame_bottom, value=payment_method)
        # set the combo box initial value to "Cash"
        self.payment_combo.current(0)

        # configure buttons in right bottom frame and grid them
        proceed_button = tk.Button(right_frame_bottom, text="Proceed", command=self.proceed)
        delete_button = tk.Button(right_frame_bottom, text="Delete item", command=self.delete_item)
        clear_basket_button = tk.Button(right_frame_bottom, text="Clear cart", command=self.clear_basket)
        close_button = tk.Button(right_frame_bottom, text="Close", command=self.close)

        self.payment_combo.grid(row=0, column=0, columnspan=4)
        proceed_button.grid(row=1, column=0, pady=10, padx=5)
        delete_button.grid(row=1, column=1, pady=10, padx=5)
        clear_basket_button.grid(row=1, column=2, pady=10, padx=5)
        close_button.grid(row=1, column=3, pady=10, padx=5)

    def add_to_cart(self, list_msg, productId):
        # insert item in the listbox to the end
        self.basket_list.insert(tk.END, list_msg)

        # append order_id_list and order_description_list
        self.order_id_list.append(productId)
        self.order_description_list.append(list_msg)

    def proceed(self):
        # if length of order_id_list is zero; the cart is empty
        if len(self.order_id_list) == 0:
            # if true, pop an error msg
            tk.messagebox.showerror("Proceed Order", "Error: No item in cart")
        else:
            # else proceed with order confirmation
            order_confirmation = tk.messagebox.askyesno("Order Confirmation", "Confirm order.")
            if order_confirmation:
                # send order_confirm msg function to server
                send_msg("order_confirm")
                time.sleep(0.1)

                # send order_id_list to update qty in server
                send_data(self.order_id_list)
                print(rec_data())
                # retrieve total_order_price from database
                total_order_price = rec_data()
                rec_msg()

                # send update_client_state msg function to server
                send_msg("update_client_state")
                time.sleep(0.1)
                # send client_id and shopkeeper current username to update state of client in database
                send_data((self.client, USERNAME))
                print(rec_data())

                # retrieve lastname and first name of client
                name_tuple = rec_data()
                rec_msg()
                name = name_tuple[0]
                client_lastname = name[0]
                client_firstname = name[1]

                # retrieve payment method from combobox
                payment_method = self.payment_combo.get()

                # create an order receipt top level window with order details as arguments
                window = OrderReceipt(self.root, client_lastname, client_firstname,
                                      total_order_price, self.order_description_list, payment_method)
                window.grab_set()
                self.destroy()

    def delete_item(self):
        # return item selected as a tuple
        item_tuple = self.basket_list.curselection()
        # extract from tuple the deleted item index
        deleted_item = item_tuple[0]
        # pop order_id_list and order_description_list with deleted item index
        self.order_id_list.pop(deleted_item)
        self.order_description_list.pop(deleted_item)
        # remove from listbox
        self.basket_list.delete(tk.ANCHOR)

    def clear_basket(self):
        self.basket_list.delete(0, tk.END)
        self.order_id_list.clear()

    def close(self):
        self.destroy()


class OrderReceipt(tk.Toplevel):
    def __init__(self, root, client_lastname, client_firstname, total_order_price, order_description_list,
                 payment_method):
        super().__init__(root)
        self.root = root
        self.client_lastname = client_lastname
        self.client_firstname = client_firstname
        self.total_order_price = total_order_price
        self.order_description_list = order_description_list
        self.payment_method = payment_method

        # configure the window
        center_window(self, 550, 400)
        self.title("ORDER DIGITAL RECEIPT")
        self.resizable(False, False)

        # open and identifies the give image file
        self.background_image = (Image.open("asset/images/main_background.png"))
        # create a background image object
        self.new_background_image = ImageTk.PhotoImage(self.background_image)
        # configure the background image and place in background frame
        background_image_label = tk.Label(self, image=self.new_background_image)
        background_image_label.place(x=-550, y=-3)

        # calculate commission, tax and total amounts
        self.commission_amount = int(self.total_order_price * 0.10)
        self.tax_amount = int(self.total_order_price * 0.15)
        self.total_order_revenue = self.total_order_price + self.tax_amount

        self.order_id = ""
        self.order_description_string = ""

        # configure text box frame on top
        self.text_box_frame = tk.Frame(self)
        self.text_box_frame.pack()

        # configure button frame in bottom
        self.button_frame = tk.Frame(self, bg="#DDABA2")
        self.button_frame.pack()

        # configure text box for digital receipt display
        self.receipt_text = tk.Text(self.text_box_frame, bd=1, width=60, relief="sunken")
        self.receipt_text.pack()

        close_button = tk.Button(self.button_frame, text="Close", command=self.close)
        close_button.pack(pady=10)

        self.sent_order_server()
        self.display_receipt()

    def sent_order_server(self):
        # send sent_order msg function to server
        send_msg("sent_order")

        # create a string of all ordered items
        self.order_description_string += self.order_description_list[0]
        for item in self.order_description_list[1:]:
            self.order_description_string += ", " + item

        # send order details to server to insert new records in order table
        send_data((self.order_description_string, self.total_order_price, self.tax_amount, self.commission_amount,
                   self.client_lastname, self.client_firstname, self.payment_method, USERNAME, USER_ID))
        print(rec_data())
        rec_msg()

    def display_receipt(self):
        # return today date
        today = date.today()
        order_date = today.strftime("%Y-%m-%d")

        # receipts layout
        self.receipt_text.insert(tk.END, f"{order_date}\n\n")
        self.receipt_text.insert(tk.END, f"Client Name: {self.client_lastname} {self.client_firstname}\n")
        self.receipt_text.insert(tk.END, f"Shopkeeper Username: {USERNAME}\n\n")
        self.receipt_text.insert(tk.END, f"Items:\n")
        for item in self.order_description_list:
            self.receipt_text.insert(tk.END, f"- {item}\n")
        self.receipt_text.insert(tk.END, "\n")
        self.receipt_text.insert(tk.END, f"Cost of Order excluding Tax amount: \t{self.total_order_price}\n")
        self.receipt_text.insert(tk.END, f"Tax Amount: \t\t\t\t{self.tax_amount}\n")
        self.receipt_text.insert(tk.END, f"Total Cost including Tax amount: \t\t{self.total_order_revenue}\n\n")
        self.receipt_text.insert(tk.END, f"Payment Method = {self.payment_method}")

    def close(self):
        self.destroy()


class ViewStock(tk.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.root = root

        # configure the window
        center_window(self, 700, 350)
        self.title("VIEW STOCK")
        self.resizable(False, False)
        self.configure(bg="#857CC5")

        # add some style
        style = ttk.Style()

        # pick a theme
        style.theme_use("default")

        # configure our treeview colours
        style.configure("Treeview",
                        background="silver",
                        foreground="black",
                        rowheight=25,
                        fieldbackground="silver"
                        )

        # change selected colour
        style.map('Treeview', background=[('selected', '#857CC5')])

        # create Treeview frame
        tree_frame = tk.Frame(self)
        tree_frame.pack(pady=10)

        # Treeview scrollbar
        tree_scroll = tk.Scrollbar(tree_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # create Treeview
        self.stock_tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set, selectmode="extended")
        self.stock_tree.pack()

        # configure scrollbar
        tree_scroll.config(command=self.stock_tree.yview)

        # define the columns
        self.stock_tree['columns'] = ("ID", "Name", "Price", "Quantity", "Geographical Location")

        # format the column
        self.stock_tree.column("#0", width=0, stretch=tk.NO)
        self.stock_tree.column("ID", width=80, anchor=tk.CENTER)
        self.stock_tree.column("Name", width=120, anchor=tk.W)
        self.stock_tree.column("Price", width=120, anchor=tk.W)
        self.stock_tree.column("Quantity", width=120, anchor=tk.W)
        self.stock_tree.column("Geographical Location", width=150, anchor=tk.W)

        # create headings
        self.stock_tree.heading("#0", text="", anchor=tk.W)
        self.stock_tree.heading("ID", text="Product ID", anchor=tk.CENTER)
        self.stock_tree.heading("Name", text="Product Name", anchor=tk.W)
        self.stock_tree.heading("Price", text="Price", anchor=tk.W)
        self.stock_tree.heading("Quantity", text="Quantity", anchor=tk.W)
        self.stock_tree.heading("Geographical Location", text="Geographical Location", anchor=tk.W)

        # create striped row tags
        self.stock_tree.tag_configure('oddrow', background="white")
        self.stock_tree.tag_configure('evenrow', background="#A18BB9")

        # Buttons
        button_frame = tk.Frame(self, bg="#857CC5")
        button_frame.pack(fill="x", expand=1, padx=30)

        close_button = tk.Button(button_frame, text="Close", command=self.close)

        close_button.pack(pady=10)

        self.query_database()

    def query_database(self):
        # send product_database msg function to server
        send_msg("product_database")
        # retrieve product details from database
        product_database = rec_data()
        print(rec_data())
        rec_msg()

        # insert the retrieved information in the treeview
        count = 0
        for product in product_database:
            if count % 2 == 0:
                self.stock_tree.insert(parent="", index="end", iid=count, text="",
                                       values=(product[0], product[1], product[2], product[3], product[4]),
                                       tags=('evenrow',))
            else:
                self.stock_tree.insert(parent="", index="end", iid=count, text="",
                                       values=(product[0], product[1], product[2], product[3], product[4]),
                                       tags=('oddrow',))

            count += 1

    def close(self):
        self.destroy()


if __name__ == "__main__":
    app = App()
    MainFrame(app)
    app.mainloop()
