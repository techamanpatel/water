from flask import Flask, render_template, session, request, flash, redirect, url_for
import sqlite3
from auth import *
from products import *
from stocks import *
from employees import *
from customers import *
from sales import *

import databases
databases.create_database()

app = Flask(__name__)
app.secret_key = "LJHSLKF*#U#U"

def isauth():
    if "name" not in session:
        return redirect(url_for('login'))
    return None  # Return None if the user is authenticated

@app.route('/signup', methods=['POST'])
def signup():
    handle_signup(request)
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        if handle_login(request):
            session["name"] = request.form['username']
            return redirect(url_for("index"))
    return render_template('login.html')

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/")
def index():
    auth_redirect = isauth()
    if auth_redirect:  # Check if redirection is needed
        return auth_redirect
    return render_template('dashboard.html', session=session)

@app.route("/addproduct", methods=["GET", "POST"])
def addproduct():
    auth_redirect = isauth()
    if auth_redirect:  # Check if redirection is needed
        return auth_redirect

    if request.method == "GET":
        products = getProducts()
        return render_template('addproduct.html', products=products, session=session)

    if request.method == "POST":
        add_product(request)
        return redirect(url_for('addproduct'))

@app.route("/updateproduct", methods=["POST"])
def updateproduct():
    if isauth():
        return isauth()
    if request.method=="POST":
        update_product(request)
    return redirect(url_for('addproduct'))

@app.route("/deleteproduct", methods=["GET"])
def deleteproduct():
    if isauth():
        return isauth()
    id=request.args.get('id')
    delete_product(id)
    return redirect(url_for('addproduct'))

@app.route("/add_new_filling_stock", methods=["GET","POST"])
def add_new_filling_stock():
    if isauth():
        return isauth()
    if request.method=="GET":
        products = get_product_stock_summary()
        return render_template('add_new_bottle_stock.html', products=products)    
    
    if request.method=="POST":
        new_bottle_stock_add(request)
        return redirect(url_for('add_new_filling_stock'))

@app.route('/view_transactions')
def view_transactions():
    if isauth():
        return isauth()
    transactions=get_stock_transactions()
    return render_template('view_transactions.html', transactions=transactions)

@app.route('/stockinout', methods=['GET', 'POST'])
def stock_in_out():
    if isauth():
        return isauth()
    if request.method == 'POST':
        add_stock_transaction(request)
        return redirect('/stockinout')
    
    
    transactions = get_stock_transactions()
    products=getProducts()
    return render_template('stockinout.html', transactions=transactions,session=session, products=products)

@app.route("/check_stock_balance")
def check_stock_balance():
    if isauth():
        return isauth()
    stock_list=check_stock_balance_()
    return render_template("check_stock_balance.html", session=session, stock_list=stock_list)

@app.route('/employee', methods=["GET","POST"])
def employee():
    if request.method=="POST":
        add_employee(request)
    employees=get_employees()
    return render_template('createEmployee.html', employees=employees)

@app.route("/area", methods=["GET","POST"])
def area():
    if request.method=="POST":
        pass
    else:
        employees=get_employees()
        areas=get_areas()
        employee_areas=get_employee_location_info()
        print(employee_areas)
        return render_template('area.html', employees=employees, areas=areas, employee_areas=employee_areas)

@app.route("/assign_area", methods=["POST"])
def assign_area():
    if request.method=="POST":
        assign_customer_location(request)
    return redirect(url_for("area"))

@app.route("/add_area", methods=["POST"])
def add_area():
    if request.method=="POST":
        add_location(request)
        return redirect(url_for("area"))

@app.route('/delete_location/<int:location_id>', methods=['GET'])
def delete_location(location_id):
    delete_location_by_id(location_id)
    return redirect(url_for('area'))
 
@app.route('/showallemployees')
def showallemployees():
    # Connect to the database
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT emp_id, join_date, first_name, last_name, nic, contact, 
               address, designation, account_status, username, password
        FROM employees
    ''')
    employees = cursor.fetchall()
    conn.close()
    return render_template('emp/showallemployee.html', employees=employees)

@app.route('/edit_employee', methods=['GET', 'POST'])
def edit_employee():
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()
    if request.method == 'POST':
        edit_employees(request, conn)
        return redirect(url_for('showallemployees'))

    # If method is GET, we are serving the edit page with employee data
    id=request.args.get('id')
    cursor.execute('SELECT emp_id, join_date, first_name, last_name, nic, contact, address, designation, account_status, username, password FROM employees WHERE emp_id = ?', (id,))
    employee = cursor.fetchone()
    conn.close()

    # Render the page with employee details for editing
    return render_template('emp/edit.html', employee=employee)


@app.route("/show_all_customers", methods=["GET"])
def show_all_customers():
    if isauth():
        return isauth()

    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT c.id, c.customer_name, c.contact, c.address, c.username,
                   l.city || ', ' || l.location AS location, c.schedules,
                   e.first_name || ' ' || e.last_name AS employee_name
            FROM customers c
            LEFT JOIN locations l ON c.location_id = l.id
            LEFT JOIN employees e ON e.location_id = c.location_id
        ''')

        customers = cursor.fetchall()
        print("Fetched customers:", customers)  # Debug print

        # Reverse day mapping for converting numbers to day names
        day_mapping_reverse = {
            '1': 'Monday',
            '2': 'Tuesday',
            '3': 'Wednesday',
            '4': 'Thursday',
            '5': 'Friday',
            '6': 'Saturday',
            '7': 'Sunday'
        }

        customer_data = []
        for customer in customers:
            schedules = customer[6].split(',') if customer[6] else []
            delivery_days = ', '.join([day_mapping_reverse.get(day, day) for day in schedules])
            customer_data.append(list(customer)[:6] + [delivery_days] + list(customer)[7:])
        
        print("Processed customer data:", customer_data)  # Debug print

        conn.close()
        return render_template("customer/allcustomers.html", customers=customer_data)

    except Exception as e:
        print(f"Error fetching customers: {e}")
        conn.close()
        return render_template("customer/allcustomers.html", customers=[])





@app.route("/customer_add", methods=["GET"])
def customer_add():
    # Get area data
    area = get_employee_location_info()
    
    # Get available products for selection in the customer creation form
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()
    cursor.execute('SELECT p_id, product_name, product_price FROM products')
    products = cursor.fetchall()
    conn.close()

    # Pass areas and products to the customer creation form
    return render_template("customer/create.html", area=area, products=products)
@app.route("/add_customer", methods=["POST"])
def add_customer():
    add_new_customer(request)
    return redirect(url_for("show_all_customers"))

@app.route("/new_sales_order",methods=["GET", "POST"])

def new_sales_order():
    auth_redirect = isauth()
    if auth_redirect:  # Check if redirection is needed
        return auth_redirect

    if request.method == "GET":
        sales = get_sales_order()
        return render_template('customer/new_sales_order.html', sales=sales, session=session)

    if request.method == "POST":
        sales_order(request)
        return redirect(url_for('new_sales_order'))

if __name__ == '__main__':
    app.run(host="0.0.0.0")
