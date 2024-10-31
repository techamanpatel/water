from flask import redirect, url_for
import sqlite3

def handle_signup(request):
    # Fetch form data
    username = request.form['username']
    password = request.form['password']
    key = request.form['key']

    SECRET_KEY="KEY786KEY512"
    # Check if the key matches the predefined secret key
    if key != SECRET_KEY:
        # If the key doesn't match, return an error message
        return redirect(url_for('signup'))  # Assuming 'signup' is the signup page route

    # If the key is valid, proceed to store the username and password
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()

    # Insert the new admin user into the database (storing plaintext password for now)
    cursor.execute('''
        INSERT INTO admin (username, password)
        VALUES (?, ?)
    ''', (username, password))

    conn.commit()
    conn.close()

    return redirect(url_for('login'))



def handle_login(request):
    username = request.form['username']
    password = request.form['password']
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()

    # Fetch the user with the provided username
    cursor.execute('''
        SELECT password FROM admin WHERE username = ?
    ''', (username,))
    
    result = cursor.fetchone()
    conn.close()

    # If the username doesn't exist or the password doesn't match, return False
    if result is None or result[0] != password:
        return False

    
    return True