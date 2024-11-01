import sqlite3

def create_database():

    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()


    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS products (
            p_id INTEGER PRIMARY KEY AUTOINCREMENT ,
                   product_name TEXT NOT NULL,
                   product_price INTEGER NOT NULL,
                   product_type TEXT NOT NULL,
                   remarks TEXT           
    )
 ''')
    
    cursor.execute(''' 
         CREATE TABLE IF NOT EXISTS stocks (
            p_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            filled_stock INTEGER DEFAULT 0,
            empty_stock INTEGER DEFAULT 0,
            damaged_stock INTEGER DEFAULT 0,
            customer_stock INTEGER DEFAULT 0,
            FOREIGN KEY (product_id) REFERENCES products(p_id)
        )
''')
    
   
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            salesman TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            stock_status TEXT NOT NULL,
            remarks TEXT,
            FOREIGN KEY(product_id) REFERENCES products(p_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
   
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            location TEXT NOT NULL
        )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        emp_id INTEGER PRIMARY KEY AUTOINCREMENT,     
        join_date TEXT NOT NULL,                      
        first_name TEXT NOT NULL,                    
        last_name TEXT NOT NULL,                 
        nic TEXT NOT NULL,                           
        contact TEXT NOT NULL,                       
        address TEXT NOT NULL,                 
        designation TEXT NOT NULL,                    
        account_status TEXT NOT NULL,             
        username TEXT NOT NULL UNIQUE,               
        password TEXT NOT NULL,                      
        location_id INTEGER,                          
        product_id INTEGER,                          

        FOREIGN KEY (location_id) REFERENCES locations(id), 
        FOREIGN KEY (product_id) REFERENCES products(p_id)        
    )
''')
    
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employee_locations (
            emp_id INTEGER,
            location_id INTEGER,
            PRIMARY KEY (emp_id, location_id),
            FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE,
            FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE CASCADE
        )
    ''')


    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,       -- Customer ID
            account_open_date TEXT NOT NULL,            -- Date when the account was opened
            customer_name TEXT NOT NULL,                -- Customer's full name
            contact TEXT NOT NULL,                      -- Customer contact number
            address TEXT NOT NULL,                      -- Customer's address
            account_status TEXT NOT NULL,               -- Account status (Active/Inactive)
            security_deposit_amount REAL NOT NULL,      -- Security deposit amount
            security_remarks TEXT,                      -- Remarks for security deposit
            opening_balance REAL NOT NULL,              -- Opening balance for customer
            bottle_balance INTEGER NOT NULL,            -- Bottle balance
            username TEXT NOT NULL UNIQUE,              -- Unique username for login
            password TEXT NOT NULL,                     -- Password (stored in plaintext or hashed)
            employee_id INTEGER,                        -- Foreign key for employee who manages the customer
            location_id INTEGER,                        -- Foreign key for customer's location
            schedules TEXT NOT NULL,                    -- String to track delivery days (1-7 for Mon-Sun)

            -- Foreign key constraints
            FOREIGN KEY (employee_id) REFERENCES employees(emp_id), -- Linking to employees table
            FOREIGN KEY (location_id) REFERENCES locations(id)      -- Linking to locations table
        )
    ''')
        
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customer_product_price (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        price REAL NOT NULL, -- Custom price for this customer-product relation
        
        FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(p_id) ON DELETE CASCADE
    )
''')

    cursor.execute(''' 
     
      CREATE TABLE IF NOT EXISTS sales(
        bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
                  customer_name TEXT,
                   address TEXT,
                   employee_name TEXT ,
                   order_date TEXT,
                   invoice TEXT,
                   product_id INTEGER,
                   price INTEGER,
                   s_quantity INTEGER,
                   r_quantity INTEGER,
                   amount INTEGER,
                   payment_status TEXT,
                   payment INTEGER

        )
      
 ''')
  

    # Create bill_items table
    cursor.execute('''CREATE TABLE IF NOT EXISTS sale_items (
        sale_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        bill_id INTEGER,
        product_id INTEGER,
        price INTEGER,
        quantity INTEGER NOT NULL,
        amount INTEGER,
                   
        FOREIGN KEY (bill_id) REFERENCES sales(bill_id),
        FOREIGN KEY (product_id) REFERENCES customer_product_price(product_id)
        FOREIGN KEY (price) REFERENCES customer_product_price(price)

    )''')

    conn.commit()
    conn.close()
    print("Database and tables created successfully.")

    



    # Commit changes and close the connection
    conn.commit()
    conn.close()

# Call the function to create the database and table
