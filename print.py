from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import sqlite3 

def create_and_insert_customer_sales():
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()

    cursor.execute(''' 
        DROP TABLE customer_sales
    ''')

    # Create the customer_sales table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customer_sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            customer_name TEXT NOT NULL,
            address TEXT NOT NULL,
            employee_id INTEGER,
            product_id INTEGER NOT NULL,
            s_quantity INTEGER NOT NULL,
            r_quantity INTEGER NOT NULL,
            price INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            payment_status TEXT NOT NULL,
            payment TEXT NOT NULL,
            order_date DATE NOT NULL,
            invoice VARCHAR(30) NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(p_id),
            FOREIGN KEY (employee_id) REFERENCES employees(emp_id)
        )
    ''')

    # Dummy data to insert
    dummy_entries = [
        (1, "John Doe", "123 Elm St", 1, 3, 5, 0, 100, 500, "complete", "CASH", "2024-10-31", "INV-001"),
        (2, "Jane Smith", "456 Oak St", 1, 4, 3, 0, 150, 450, "complete", "CASH", "2024-10-31", "INV-002"),
        (3, "Alice Johnson", "789 Pine St", 1, 3, 2, 0, 200, 400, "complete", "CASH", "2024-10-31", "INV-003"),
        (1, "John Doe", "123 Elm St", 1, 4, 1, 0, 150, 150, "complete", "CASH", "2024-10-31", "INV-001"),
        (2, "Jane Smith", "456 Oak St", 1, 3, 2, 0, 100, 200, "complete", "CASH", "2024-10-31", "INV-002"),
    ]

    # Insert dummy data into the customer_sales table
    for entry in dummy_entries:
        cursor.execute('''
            INSERT INTO customer_sales (customer_id, customer_name, address, employee_id, product_id,
                                        s_quantity, r_quantity, price, amount, payment_status, 
                                        payment, order_date, invoice)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', entry)

    # Commit the transaction
    conn.commit()
    cursor.close()

def generate_invoice(invoice_id):
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()

    # Fetch data for all rows with the same invoice ID
    cursor.execute('''
        SELECT customer_id, customer_name, address, 
               r_quantity, product_id, amount, price, 
               (amount / price) AS quantity
        FROM customer_sales
        WHERE invoice = ?
    ''', (invoice_id,))

    # Fetch all results
    rows = cursor.fetchall()

    # Initialize invoice details
    invoice_details = {
        'customer_id': None,
        'customer_name': None,
        'address': None,
        'products': [],
        'total_amount': 0
    }

    # Process each row to build the invoice details
    for row in rows:
        customer_id, customer_name, address, r_quantity, product_id, amount, price, quantity = row

        # Set customer information (only once, as it’s the same for each row)
        if invoice_details['customer_id'] is None:
            invoice_details['customer_id'] = customer_id
            invoice_details['customer_name'] = customer_name
            invoice_details['address'] = address

        # Add product information to the invoice details
        invoice_details['products'].append({
            'product_id': product_id,
            'returned_quantity': r_quantity,
            'price': price,
            'quantity': quantity,
            'amount': amount
        })

        # Add to the total amount
        invoice_details['total_amount'] += amount

    # Close the connection
    conn.close()

    
    generate_invoice_pdf(invoice_details, invoice_id)

def generate_invoice_pdf(invoice, filename):
    filename = f"{filename}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 50, f"Invoice ID: {filename[:-4]}")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Customer ID: {invoice['customer_id']}")
    c.drawString(50, height - 100, f"Customer Name: {invoice['customer_name']}")
    c.drawString(50, height - 120, f"Address: {invoice['address']}")

    # Prepare table data
    data = [["Product ID", "Returned Quantity", "Quantity", "Price", "Amount"]]
    for product in invoice['products']:
        data.append([
            product['product_id'],
            product['returned_quantity'],
            f"{product['quantity']:.2f}",
            f"{product['price']:.2f}",
            f"{product['amount']:.2f}"
        ])
    data.append(["", "", "", "Total Amount", f"{invoice['total_amount']:.2f}"])

    # Draw the table
    table = Table(data, colWidths=[80, 100, 100, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke)
    ]))

    table.wrapOn(c, width, height)
    table.drawOn(c, 50, height - 220)

    # Save PDF
    c.save()
    print(f"Invoice PDF generated: {filename}")

# Example usage:
if __name__ == "__main__":

    create_and_insert_customer_sales()


    # invoice_id = "INV-001"
    # generate_invoice(invoice_id)

    # Print the invoice
    # print(f"Invoice: {invoice_id}")
    # print(f"Customer ID: {invoice['customer_id']}")
    # print(f"Customer Name: {invoice['customer_name']}")
    # print(f"Address: {invoice['address']}")
    # print("\nProducts:")
    # for product in invoice['products']:
    #     print(f" - Product ID: {product['product_id']}, Returned Quantity: {product['returned_quantity']}, "
    #           f"Quantity: {product['quantity']}, Amount: {product['amount']}")
    # print(f"\nTotal Amount: {invoice['total_amount']}")

