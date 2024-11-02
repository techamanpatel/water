import json
from enum import Enum
import sqlite3
from datetime import datetime

class LedgerType(Enum):
    DAYWISE = 1
    MONTHWISE = 2
    FROMDAYTO = 3
    FROMMONTHTO = 4

def ledger(customerId, ledgerType, startDay=None, endDay=None, startMonth=None, endMonth=None):
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()

    # Fetch customer information
    cursor.execute('''
        SELECT id, customer_name, address, contact, security_deposit_amount
        FROM customers
        WHERE id = ?
    ''', (customerId,))
    customer_data = cursor.fetchone()
    if not customer_data:
        return json.dumps({"error": "Customer not found"})

    id, name, address, contact, security_deposit__amount = customer_data

    # Initialize response structure
    response = {
        "id": id,
        "name": name,
        "address": address,
        "contact": contact,
        "security_deposit__amount": security_deposit__amount,
        "outstanding_bottles": 0,
        "ledger": []
    }

    # Calculate outstanding bottles
    cursor.execute('''
        SELECT SUM(s_quantity) AS total_sold, SUM(r_quantity) AS total_returned
        FROM customer_sales
        WHERE customer_id = ?
    ''', (customerId,))
    outstanding_data = cursor.fetchone()
    total_sold = outstanding_data[0] if outstanding_data[0] else 0
    total_returned = outstanding_data[1] if outstanding_data[1] else 0
    response["outstanding_bottles"] = total_sold - total_returned

    # Ledger based on type
    if ledgerType == LedgerType.DAYWISE:
        cursor.execute('''
            SELECT cs.order_date, cs.invoice, p.product_name, cs.price, cs.s_quantity, cs.r_quantity, cs.amount
            FROM customer_sales AS cs
            JOIN products AS p ON cs.product_id = p.p_id
            WHERE cs.customer_id = ?
            ORDER BY cs.order_date
        ''', (customerId,))
        ledger_entries = cursor.fetchall()

        for idx, entry in enumerate(ledger_entries, start=1):
            order_date, invoice, product_name, price, s_quantity, r_quantity, amount = entry
            response["ledger"].append({
                "sr_no": idx,
                "order_date": order_date,
                "invoice": invoice,
                "product": product_name,
                "price": price,
                "sale_quantity": s_quantity,
                "return_quantity": r_quantity,
                "amount": amount
            })

    elif ledgerType == LedgerType.MONTHWISE:
        cursor.execute('''
            SELECT strftime('%m', cs.order_date) AS month, strftime('%Y', cs.order_date) AS year,
                   SUM(cs.s_quantity) AS total_sale_qty, SUM(cs.r_quantity) AS total_return_qty, SUM(cs.amount) AS total_amount
            FROM customer_sales AS cs
            JOIN products AS p ON cs.product_id = p.p_id
            WHERE cs.customer_id = ?
            GROUP BY month, year
            ORDER BY year, month
        ''', (customerId,))
        ledger_entries = cursor.fetchall()

        for idx, entry in enumerate(ledger_entries, start=1):
            month, year, total_sale_qty, total_return_qty, total_amount = entry
            response["ledger"].append({
                "sr_no": idx,
                "month": month,
                "year": year,
                "sale_quantity": total_sale_qty,
                "return_quantity": total_return_qty,
                "amount": total_amount
            })

    elif ledgerType == LedgerType.FROMDAYTO and startDay and endDay:
        cursor.execute('''
            SELECT cs.order_date, cs.invoice, p.product_name, cs.price, cs.s_quantity, cs.r_quantity, cs.amount
            FROM customer_sales AS cs
            JOIN products AS p ON cs.product_id = p.p_id
            WHERE cs.customer_id = ? AND cs.order_date BETWEEN ? AND ?
            ORDER BY cs.order_date
        ''', (customerId, startDay, endDay))
        ledger_entries = cursor.fetchall()

        for idx, entry in enumerate(ledger_entries, start=1):
            order_date, invoice, product_name, price, s_quantity, r_quantity, amount = entry
            response["ledger"].append({
                "sr_no": idx,
                "order_date": order_date,
                "invoice": invoice,
                "product": product_name,
                "price": price,
                "sale_quantity": s_quantity,
                "return_quantity": r_quantity,
                "amount": amount
            })

    elif ledgerType == LedgerType.FROMMONTHTO and startMonth and endMonth:
        cursor.execute('''
            SELECT strftime('%m', cs.order_date) AS month, strftime('%Y', cs.order_date) AS year,
                   SUM(cs.s_quantity) AS total_sale_qty, SUM(cs.r_quantity) AS total_return_qty, SUM(cs.amount) AS total_amount
            FROM customer_sales AS cs
            JOIN products AS p ON cs.product_id = p.p_id
            WHERE cs.customer_id = ? AND strftime('%Y-%m', cs.order_date) BETWEEN ? AND ?
            GROUP BY month, year
            ORDER BY year, month
        ''', (customerId, startMonth, endMonth))
        ledger_entries = cursor.fetchall()

        for idx, entry in enumerate(ledger_entries, start=1):
            month, year, total_sale_qty, total_return_qty, total_amount = entry
            response["ledger"].append({
                "sr_no": idx,
                "month": month,
                "year": year,
                "sale_quantity": total_sale_qty,
                "return_quantity": total_return_qty,
                "amount": total_amount
            })

    # Close database connection
    conn.close()

    # Convert response to JSON format
    return json.dumps(response, indent=4)


# Example usage
if __name__ == "__main__":
    print(ledger(2, LedgerType.DAYWISE))
    print(ledger(2, LedgerType.MONTHWISE))
    print(ledger(2, LedgerType.FROMDAYTO, startDay="2024-10-01", endDay="2024-10-31"))
    print(ledger(2, LedgerType.FROMMONTHTO, startMonth="2024-01", endMonth="2024-12"))

