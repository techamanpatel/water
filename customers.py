import sqlite3

def add_new_customer(request):
    # Fetch data from the form (assuming request is passed with these fields)
    account_open_date = request.form['account_open_date']
    customer_name = request.form['customer_name']
    contact = request.form['contact_number']
    address = request.form['address']
    account_status = request.form['account_status']
    security_deposit_amount = float(request.form['security_deposit'])  # Convert to float
    security_remarks = request.form.get('security_remarks', '')  # Optional field, default to empty
    opening_balance = float(request.form['opening_balance'])  # Convert to float
    bottle_balance = int(request.form['opening_bottle'])  # Convert to int for bottle balance
    username = request.form['username']
    password = request.form['password']  # Store plaintext password (consider hashing in production)
    location_id = request.form.get('area')  # Get location ID from form
    location_id = int(location_id) if location_id else None  # Ensure it's an integer

    # For delivery days (this will be a list, convert to string)
    day_mapping = {
        'monday': '1',
        'tuesday': '2',
        'wednesday': '3',
        'thursday': '4',
        'friday': '5',
        'saturday': '6',
        'sunday': '7'
    }
    days = request.form.getlist('days[]')  # Checkbox values for delivery schedule
    schedules = ','.join([day_mapping[day] for day in days])  # Convert days to numbers

    # Assuming employee_id is None for now
    employee_id = None

    # Insert customer data into the customers table
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO customers (account_open_date, customer_name, contact, address, account_status, 
                                security_deposit_amount, security_remarks, opening_balance, bottle_balance, 
                                username, password, employee_id, location_id, schedules)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (account_open_date, customer_name, contact, address, account_status, security_deposit_amount, 
              security_remarks, opening_balance, bottle_balance, username, password, employee_id, location_id, schedules))

        customer_id = cursor.lastrowid  # Get the ID of the newly created customer

        # Fetch selected products and their custom prices
        selected_products = request.form.getlist('products[]')  # List of selected product IDs
        for product_id in selected_products:
            custom_price = request.form.get(f'custom_price_{product_id}')  # Custom price field

            # If custom price is not provided, fetch the default price from the products table
            if not custom_price:
                cursor.execute('SELECT default_price FROM products WHERE p_id = ?', (product_id,))
                products = cursor.fetchone()
                custom_price = products[0] if products else 0.0  # Use default price if available

            # Insert into customer_product_price with customer_id, product_id, and price
            cursor.execute('''
                INSERT INTO customer_product_price (customer_id, product_id, price)
                VALUES (?, ?, ?)
            ''', (customer_id, product_id, float(custom_price)))

        # Commit the changes
        conn.commit()
    except Exception as e:
        print(f"Error adding customer: {e}")
        conn.rollback()
    finally:
        conn.close()


def get_customers():
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()

    # Fetch all customers
    try:
        cursor.execute('''
            SELECT id, customer_name, contact, address, location_id, username
            FROM customers
        ''')
        customers = cursor.fetchall()
        
        conn.close()
        return customers
    except Exception as e:
        print(f"Error fetching customers: {e}")
        return False
