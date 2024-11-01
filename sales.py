import sqlite3
from flask import redirect, url_for, flash

def sales_order(request):
    try:
        customer_id = request.form['customer_id']
        customer_name = request.form['customer_name']
        address = request.form['address']
        employee_name = request.form['employee_name']
        order_date = request.form['order_date']
        invoice = request.form['invoice']
        product_name = request.form['product_name']
        price = request.form['price']
        s_quantity = request.form['s_quantity']
        r_quantity = request.form['r_quantity']
        amount = request.form['amount']
        payment_status = request.form['payment_status']
        payment = request.form['payment']

        with sqlite3.connect('db.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO customer_sales (customer_id, customer_name, address, employee_name, order_date, invoice, product_name, price, s_quantity, r_quantity, amount, payment_status, payment)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, )
            ''', (customer_id, customer_name, address, employee_name, order_date, invoice, product_name, price, s_quantity, r_quantity, amount, payment_status, payment))

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")