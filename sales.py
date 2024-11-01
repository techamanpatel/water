import sqlite3
from flask import redirect, url_for, flash

def sales_order(request):
    try:
        # Extract data from form
        customer_id = request.form['customer_id']
        customer_name = request.form['customer_name']
        address = request.form['address']
        employee_name = request.form['employee_name']
        order_date = request.form['order_date']
        invoice = request.form['invoice']
        product_id = request.form['product_id']
        price = request.form['price']
        s_quantity = request.form['s_quantity']
        r_quantity = request.form['r_quantity']
        amount = request.form['amount']
        payment_status = request.form['payment_status']
        payment = request.form['payment']

        with sqlite3.connect('db.db') as conn:
            cursor = conn.cursor()
            # Insert data into customer_sales table
            cursor.execute('''
                INSERT INTO customer_sales (customer_id, customer_name, address, employee_name, order_date, invoice, product_name, price, s_quantity, r_quantity, amount, payment_status, payment)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (customer_id, customer_name, address, employee_name, order_date, invoice, product_id, price, s_quantity, r_quantity, amount, payment_status, payment))
            conn.commit()  # Commit the transaction
        flash("Sales order successfully created!", "success")

    except Exception as e:
        # Rollback if there is an error
        conn.rollback()
        flash(f"An error occurred: {str(e)}", "error")

def get_sales_order():
    try:
        with sqlite3.connect('db.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM customer_sales')
            sales = cursor.fetchall()
        return sales if sales else []
    
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return []
    
def get_customer_products(customer_id):
    try:
        with sqlite3.connect('db.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT product_id, price 
                FROM customer_product_price 
                WHERE customer_id = ?
            ''', (customer_id,))
            customer_products = cursor.fetchall()
        return customer_products if customer_products else []
    except Exception as e:
        flash(f"An error occurred while fetching products for customer {customer_id}: {str(e)}", "error")
        return []

