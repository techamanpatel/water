import sqlite3






def get_product_stock_summary():
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()

    # Join stocks with products to get the necessary data
    cursor.execute('''
        SELECT 
            products.p_id AS id, 
            products.product_name, 
            stocks.filled_stock + stocks.empty_stock AS total_bottles_in_stock, 
            stocks.customer_stock AS total_bottles_at_customer, 
            (stocks.filled_stock + stocks.empty_stock - stocks.customer_stock) AS total_stock
        FROM products
        JOIN stocks ON products.p_id = stocks.product_id
    ''')

    # Fetch all records
    product_stock_summary = cursor.fetchall()

    conn.close()

    return product_stock_summary



def new_bottle_stock_add(request):
    product_id = request.form['product_id']  # From dropdown
    quantity = int(request.form['quantity'])  # New stock quantity
    date = request.form['date']  # Date of the transaction
    stock_type = request.form['stock_type']  # filled_stock or empty_stock
    salesman = request.form['salesman']  # Admin or Salesman
    remarks = request.form.get('remarks', '')  # Optional remarks, default to empty string

    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO stock_transactions (product_id, date, salesman, quantity, stock_status, remarks)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (product_id, date, salesman, quantity, stock_type, remarks))

    # Check if stock entry for this product exists
    cursor.execute('SELECT * FROM stocks WHERE product_id = ?', (product_id,))
    stock_entry = cursor.fetchone()

    if stock_entry:
        # Update the relevant stock type (filled_stock or empty_stock)
        if stock_type == 'filled_stock':
            cursor.execute('''
                UPDATE stocks 
                SET filled_stock = filled_stock + ? - damaged_stock 
                WHERE product_id = ?
            ''', (quantity, product_id))
        elif stock_type == 'empty_stock':
            cursor.execute('''
                UPDATE stocks 
                SET empty_stock = empty_stock + ? 
                WHERE product_id = ?
            ''', (quantity, product_id))
    

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    
def get_stock_transactions():
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()

    # Join stock_transactions with products to get the product name
    cursor.execute('''
        SELECT 
            stock_transactions.id,
            stock_transactions.date,
            products.product_name,
            stock_transactions.quantity,
            stock_transactions.stock_status,
            stock_transactions.salesman,
            stock_transactions.remarks
        FROM stock_transactions
        JOIN products ON stock_transactions.product_id = products.p_id
    ''')

    # Fetch all transactions
    transactions = cursor.fetchall()
    
    conn.close()
    
    # Return the transaction list
    return transactions


def add_stock_transaction(request):
    # Fetch form data from the request
    date = request.form['date']
    salesman = request.form['salesman']
    product_id = request.form['product']
    quantity = int(request.form['quantity'])
    stock_status = request.form['status']
    remarks = request.form.get('remarks', '')  # Optional field, default to empty string

    # Connect to the database
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()

    # Insert the transaction into stock_transactions table
    cursor.execute('''
        INSERT INTO stock_transactions (product_id, date, salesman, quantity, stock_status, remarks)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (product_id, date, salesman, quantity, stock_status, remarks))
    #####################################
    # Stock status logic
    if stock_status == 'STOCK IN (fill)':
        # Logic for Stock In (filled bottles)
         # Logic for Stock In (filled bottles)
        cursor.execute('SELECT filled_stock FROM stocks WHERE product_id = ?', (product_id,))
        current_filled_stock = cursor.fetchone()

        if current_filled_stock:
            # Update the filled stock by adding the received quantity
            updated_filled_stock = current_filled_stock[0] + quantity

            cursor.execute('''
                UPDATE stocks
                SET filled_stock = ?
                WHERE product_id = ?
            ''', (updated_filled_stock, product_id))
        else:
            # If no stock entry exists, insert a new entry with the received quantity
            cursor.execute('''
                INSERT INTO stocks (product_id, filled_stock, empty_stock, damaged_stock, customer_stock)
                VALUES (?, ?, 0, 0, 0)
            ''', (product_id, quantity))
            ###############################################################################################

    elif stock_status == 'STOCK OUT (fill)':
        # Logic for Stock Out (filled bottles)
        # Fetch current filled stock and customer stock
        cursor.execute('SELECT filled_stock, customer_stock FROM stocks WHERE product_id = ?', (product_id,))
        stock = cursor.fetchone()

        if stock:
            current_filled_stock = stock[0]
            current_customer_stock = stock[1]

            # Check if the requested quantity is more than the available filled stock
            if quantity > current_filled_stock:
                # Return an error if there are not enough filled bottles
                return "Error: Requested stock out quantity exceeds available filled bottles.", 400
            
            # Update the filled stock and customer stock
            updated_filled_stock = current_filled_stock - quantity
            updated_customer_stock = current_customer_stock + quantity

            cursor.execute('''
                UPDATE stocks
                SET filled_stock = ?, customer_stock = ?
                WHERE product_id = ?
            ''', (updated_filled_stock, updated_customer_stock, product_id))
        else:
            # If no stock entry exists, return an error
            return "Error: No stock entry found for this product.", 400
        
        
            ############################################################################################
            
            
    elif stock_status == 'STOCK IN (empty)':
        # Fetch the current empty stock and customer stock for the product
        cursor.execute('SELECT empty_stock, customer_stock FROM stocks WHERE product_id = ?', (product_id,))
        stock = cursor.fetchone()

        if stock:
            current_empty_stock = stock[0]
            current_customer_stock = stock[1]

            # Check if the quantity is more than the available customer stock
            if quantity > current_customer_stock:
                return "Error: Received quantity exceeds available customer stock.", 400

            # Update the empty stock by adding the received quantity
            updated_empty_stock = current_empty_stock + quantity
            # Update the customer stock by subtracting the received quantity
            updated_customer_stock = current_customer_stock - quantity

            # Update the stocks table with the new values
            cursor.execute('''
                UPDATE stocks
                SET empty_stock = ?, customer_stock = ?
                WHERE product_id = ?
            ''', (updated_empty_stock, updated_customer_stock, product_id))
        else:
            # If no stock entry exists, return an error
            return "Error: No stock entry found for this product.", 400

        ############################################################################################

    elif stock_status == 'STOCK OUT (empty)':
        # Logic for Stock Out (empty bottles)
         # Fetch the current empty stock for the product
        cursor.execute('SELECT empty_stock FROM stocks WHERE product_id = ?', (product_id,))
        current_empty_stock = cursor.fetchone()

        if current_empty_stock:
            # Check if the requested quantity is more than the available empty stock
            if quantity > current_empty_stock[0]:
                return "Error: Requested stock out quantity exceeds available empty bottles.", 400

            # Update the empty stock by subtracting the requested quantity
            updated_empty_stock = current_empty_stock[0] - quantity

            # Update the stocks table with the new value
            cursor.execute('''
                UPDATE stocks
                SET empty_stock = ?
                WHERE product_id = ?
            ''', (updated_empty_stock, product_id))
        else:
            # If no stock entry exists, return an error
            return "Error: No stock entry found for this product.", 400
        ############################################################################################
    elif stock_status == 'damaged':
        # Logic for damaged stock
        # Logic for damaged stock

    
        # Fetch the current filled stock, empty stock, and damaged stock for the product
        cursor.execute('SELECT filled_stock, empty_stock, damaged_stock FROM stocks WHERE product_id = ?', (product_id,))
        stock = cursor.fetchone()

        if stock:
            current_filled_stock = stock[0]
            current_empty_stock = stock[1]
            current_damaged_stock = stock[2]

            # Initialize variables to hold the updated values
            updated_filled_stock = current_filled_stock
            updated_empty_stock = current_empty_stock

            # If the damaged quantity is more than the filled stock
            if quantity > current_filled_stock:
                # Subtract all filled stock and calculate remaining damage for empty stock
                remaining_damage = quantity - current_filled_stock
                updated_filled_stock = 0

                # Now subtract the remaining damage from empty stock
                if remaining_damage > current_empty_stock:
                    return "Error: Not enough bottles to cover the damage.", 400

                updated_empty_stock = current_empty_stock - remaining_damage
            else:
                # If the filled stock can cover the entire damage
                updated_filled_stock = current_filled_stock - quantity

            # Update the damaged stock by adding the damaged quantity
            updated_damaged_stock = current_damaged_stock + quantity

            # Update the stocks table with the new values
            cursor.execute('''
                UPDATE stocks
                SET filled_stock = ?, empty_stock = ?, damaged_stock = ?
                WHERE product_id = ?
            ''', (updated_filled_stock, updated_empty_stock, updated_damaged_stock, product_id))
        else:
            # If no stock entry exists, return an error
            return "Error: No stock entry found for this product.", 400
        

    # Commit and close the connection
    conn.commit()
    conn.close()
    
def check_stock_balance_():
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()

    # Join stocks with products to get product_name
    cursor.execute('''
        SELECT 
            stocks.p_id AS stockid, 
            products.product_name, 
            stocks.filled_stock, 
            stocks.empty_stock, 
            stocks.damaged_stock, 
            stocks.customer_stock 
        FROM stocks
        JOIN products ON stocks.product_id = products.p_id
    ''')

    # Fetch all records
    stock_data = cursor.fetchall()

    # Prepare list to return
    stock_list = []

    # Loop through the fetched data and calculate required values
    for stock in stock_data:
        stockid = stock[0]
        product_name = stock[1]
        filled_stock = stock[2]
        empty_stock = stock[3]
        total_damaged = stock[4]
        customer_stock = stock[5]
        
        present_stock = filled_stock + empty_stock
        total_stock = present_stock + customer_stock

        # Append the calculated data to the stock_list
        stock_list.append({
            'stockid': stockid,
            'product_name': product_name,
            'filled_stock': filled_stock,
            'empty_stock': empty_stock,
            'total_damaged': total_damaged,
            'present_stock': present_stock,
            'customer_stock': customer_stock,
            'total_stock': total_stock
        })

    
    conn.close()

    # Return the stock list
    return stock_list