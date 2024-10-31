import sqlite3

def add_employee(request):
    # Fetch form data from request
    join_date = request.form['join_date']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    nic = request.form['nic']
    contact = request.form['contact']
    address = request.form['address']
    designation = request.form['designation']
    account_status = request.form['account_status']
    username = request.form['username']
    password = request.form['password']  # Store as plain text or hashed (as per your requirement)
    
    # You might want to get location_id and product_id from your form as well
    location_id = request.form.get('location_id', None)  # Assuming location_id might be optional
    product_id = request.form.get('product_id', None)    # Assuming product_id might be optional

    # Connect to SQLite database
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()

    # Insert employee details into the employees table
    try:
        cursor.execute('''
            INSERT INTO employees (
                join_date, first_name, last_name, nic, contact, address, designation,
                account_status, username, password, location_id, product_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (join_date, first_name, last_name, nic, contact, address, designation,
            account_status, username, password, location_id, product_id))

        # Commit changes and close the connection
        conn.commit()
        conn.close()
    except:
        pass

    


def get_employees():
    # Connect to SQLite database
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()
    try:
        # Query to fetch all employees data
        cursor.execute('''
            SELECT emp_id, join_date, first_name, last_name, nic, contact, address, 
                designation, account_status, username, location_id, product_id
            FROM employees
        ''')

    # Fetch all rows from the result of the query
        employees = cursor.fetchall()
        conn.close()
        return employees
    except:
        
    # Close the connection
        
        pass
    # Return the list of employees
    
def get_employee_location_info():
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()

    # Fetch the areas along with the employee information
    cursor.execute('''
        SELECT locations.city, locations.location,
               COALESCE(employees.first_name || ' ' || employees.last_name, 'Not Yet') AS employee_name,
               locations.id  -- Make sure to include the location_id
        FROM locations
        LEFT JOIN employee_locations ON locations.id = employee_locations.location_id
        LEFT JOIN employees ON employees.emp_id = employee_locations.emp_id
    ''')
    employee_areas = cursor.fetchall()  # This will now include the location_id
    conn.close()
    return employee_areas


def get_areas():
    # Connect to the database
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT id, city, location FROM locations')
        areas = cursor.fetchall()
        conn.close()
        return areas
    except:
        pass
    
def assign_customer_location(request):
    # Get the employee ID and location ID from the form (single assignment)
    employee_id = request.form['employee']
    location_id = request.form['area']

    # Connect to the database
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()

    # Insert a new record into the employee_locations table
    # Ensure that the same location is not assigned to the same employee more than once
    cursor.execute('''
        INSERT OR IGNORE INTO employee_locations (emp_id, location_id)
        VALUES (?, ?)
    ''', (employee_id, location_id))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def add_location(request):
    # Fetch form data
    city = request.form['city']
    location = request.form['location']

    # Connect to the database
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()

    # Insert the new location into the locations table
    cursor.execute('''
        INSERT INTO locations (city, location)
        VALUES (?, ?)
    ''', (city, location))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    # Optionally, add flash message and redirect (if using Flask)
  
def delete_location_by_id(id):
    try:
        # Connect to the database
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()

        # Delete entries from the employee_locations table first
        cursor.execute('''
            DELETE FROM employee_locations
            WHERE location_id = ?
        ''', (id,))

        # Delete the location from the locations table
        cursor.execute('''
            DELETE FROM locations
            WHERE id = ?
        ''', (id,))

        # Commit the changes and close the connection
        conn.commit()
        conn.close()
    except:
        pass

def edit_employees(request,conn):
    cursor = conn.cursor()
    emp_id = request.form['emp_id']
    join_date = request.form['join_date']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    nic = request.form['nic']
    contact = request.form['contact']
    address = request.form['address']
    designation = request.form['designation']
    account_status = request.form['account_status']
    username = request.form['username']
    password = request.form['password']
    
    # Update employee record in the database
    cursor.execute('''
        UPDATE employees
        SET join_date = ?, first_name = ?, last_name = ?, nic = ?, contact = ?, 
            address = ?, designation = ?, account_status = ?, username = ?, password = ?
        WHERE emp_id = ?
    ''', (join_date, first_name, last_name, nic, contact, address, designation, account_status, username, password, emp_id))
    
    conn.commit()
    conn.close()
    
 