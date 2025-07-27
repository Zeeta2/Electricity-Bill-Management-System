from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Initialize Database
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS customers
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, meter_no TEXT UNIQUE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS bills
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_id INTEGER, units INTEGER, amount REAL, date TEXT,
                  FOREIGN KEY(customer_id) REFERENCES customers(id))''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        name = request.form['name']
        meter_no = request.form['meter_no']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO customers (name, meter_no) VALUES (?, ?)", (name, meter_no))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    return render_template('add_customer.html')

@app.route('/calculate_bill', methods=['GET', 'POST'])
def calculate_bill():
    if request.method == 'POST':
        meter_no = request.form['meter_no']
        units = int(request.form['units'])
        rate_per_unit = 5  # Fixed rate
        amount = units * rate_per_unit

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT id FROM customers WHERE meter_no = ?", (meter_no,))
        customer = c.fetchone()
        if customer:
            customer_id = customer[0]
            c.execute("INSERT INTO bills (customer_id, units, amount, date) VALUES (?, ?, ?, DATE('now'))",
                      (customer_id, units, amount))
            conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    return render_template('calculate_bill.html')

@app.route('/view_bills')
def view_bills():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''SELECT customers.name, customers.meter_no, bills.units, bills.amount, bills.date
                 FROM bills JOIN customers ON bills.customer_id = customers.id''')
    data = c.fetchall()
    conn.close()
    return render_template('view_bills.html', data=data)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
