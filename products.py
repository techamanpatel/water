import sqlite3
from flask import redirect, url_for, flash

def add_product(request):
    try:
        product_name = request.form['product_name']
        price = request.form['price']
        product_type = request.form['product_type']
        remarks = request.form['remarks']

        # Insert form data into SQLite3 database
        with sqlite3.connect('db.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO products (product_name, product_price, product_type, remarks)
                VALUES (?, ?, ?, ?)
            ''', (product_name, price, product_type, remarks))
            product_id = cursor.lastrowid
            
            cursor.execute('''
                INSERT INTO stocks (product_id, filled_stock, empty_stock, damaged_stock, customer_stock)
                VALUES (?, 0, 0, 0, 0)
            ''', (product_id,))

        # Flash a success message
        flash("Product added successfully.", "success")
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")

def getProducts():
    try:
        with sqlite3.connect('db.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM products')
            products = cursor.fetchall()
        return products if products else []
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return []

def delete_product(id):
    try:
        with sqlite3.connect('db.db') as conn:
            cursor = conn.cursor()
            # Execute the delete query
            cursor.execute('DELETE FROM stocks WHERE product_id = ?', (id,))
            cursor.execute('DELETE FROM products WHERE p_id = ?', (id,))

        flash("Product deleted successfully.", "success")
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")

def update_product(request):
    product_id = request.form['select_product']
    product_name = request.form['product_name']
    price = int(request.form['price'])
    product_type = request.form['product_type']
    remarks = request.form['remarks']

    # Connect to the database
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()

    # Update the product in the database
    cursor.execute('''
        UPDATE products
        SET product_name = ?, product_price = ?, product_type = ?, remarks = ?
        WHERE p_id = ?
    ''', (product_name, price, product_type, remarks, product_id))

    # Commit changes and close the connection
    conn.commit()
    conn.close()

def product_add_new_filling_stock(request):
# Get form data
    product_name = request.form['product_name']
    filling_quantity = int(request.form['filling_quantity'])
    date = request.form['date']
    
    # Connect to the database
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()

    # Fetch the current stock details for the selected product
    cursor.execute('''
        SELECT id, filling_stock_warehouse, empty_stock_warehouse 
        FROM products 
        WHERE product_name = ?
    ''', (product_name,))
    products = cursor.fetchone()

    if products is None:
        flash('Product not found.', 'error')
        return redirect(url_for('add_new_filling_stock'))

    product_id = products[0]
    current_filling_stock = products[1]
    current_empty_stock = products[2]

    # Ensure that the filling stock quantity doesn't exceed the empty stock
    if filling_quantity > current_empty_stock:
        flash('Filling quantity exceeds available empty stock!', 'error')
        return redirect(url_for('add_new_filling_stock'))

    # Update the stocks (increase filling stock, decrease empty stock)
    new_filling_stock = current_filling_stock + filling_quantity
    new_empty_stock = current_empty_stock - filling_quantity

    # Update the product stock in the database
    cursor.execute('''
        UPDATE products 
        SET filling_stock_warehouse = ?, empty_stock_warehouse = ?, total_stock_warehouse = ?
        WHERE id = ?
    ''', (new_filling_stock, new_empty_stock, new_filling_stock + new_empty_stock, product_id))

    # Commit changes to the database and close the connection
    conn.commit()
    conn.close()
    
    