from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import matplotlib.pyplot as plt
import datetime
import matplotlib
import csv
import pandas as pd
import os
from flask import send_file
matplotlib.use('Agg')

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Connect to SQLite database
conn = sqlite3.connect('D:\Downloads\expense_tracker\expense_tracker.db', check_same_thread=False)
cursor = conn.cursor()

# Create expenses table if not exists
def create_expenses_table(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            category TEXT,
            description TEXT,
            date TEXT,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES user_profiles (id)
        )
    ''')
conn.commit()
conn.close()

def create_user_profile(username, password):
    cursor.execute('INSERT INTO user_profiles (username, password) VALUES (?, ?)', (username, password))
    conn.commit()

def add_expense(amount, category, description, user_id):
    date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('INSERT INTO expenses (amount, category, description, date, user_id) VALUES (?, ?, ?, ?, ?)',
                   (amount, category, description, date, user_id))
    conn.commit()


def authenticate_user(username, password):
    cursor.execute('SELECT id FROM user_profiles WHERE username=? AND password=?', (username, password))
    user_id = cursor.fetchone()
    return user_id[0] if user_id else None

def get_total_expense():
    if 'user_id' not in session:
        return 0

    user_id = session['user_id']
    cursor.execute('SELECT SUM(amount) FROM expenses WHERE user_id=?', (user_id,))
    total_expense = cursor.fetchone()[0]
    return total_expense if total_expense else 0


def get_expenses_by_category():
    if 'user_id' not in session:
        return []

    user_id = session['user_id']
    cursor.execute('SELECT category, SUM(amount) FROM expenses WHERE user_id=? GROUP BY category', (user_id,))
    return cursor.fetchall()


def export_to_csv(filename='expense_data.csv'):
    expenses = get_all_expenses()
    if expenses:
        header = ['ID', 'Amount', 'Category', 'Description', 'Date']
        data = [header] + expenses
        with open(filename, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerows(data)
        return filename
    else:
        return None

def get_expense_by_id(expense_id):
    cursor.execute('SELECT * FROM expenses WHERE id=?', (expense_id,))
    return cursor.fetchone()

@app.route('/edit_expense/<int:expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    if request.method == 'GET':
        expense = get_expense_by_id(expense_id)
        return render_template('edit_expense.html', expense=expense)
    elif request.method == 'POST':
        amount = float(request.form['amount'])
        category = request.form['category']
        description = request.form['description']
        cursor.execute('UPDATE expenses SET amount=?, category=?, description=? WHERE id=?',
                       (amount, category, description, expense_id))
        conn.commit()
        return redirect(url_for('view_total_expense'))

@app.route('/delete_expense/<int:expense_id>')
def delete_expense(expense_id):
    cursor.execute('DELETE FROM expenses WHERE id=?', (expense_id,))
    conn.commit()
    return redirect(url_for('view_total_expense'))


@app.route('/export_csv')
def export_csv():
    filename = export_to_csv()
    if filename:
        return send_file(filename, as_attachment=True)
    else:
        return "No expenses to export."
    
@app.route('/')
def index():
    username = None 
    if 'user_id' in session:
        user_id = session['user_id']
        cursor.execute('SELECT username FROM user_profiles WHERE id=?', (user_id,))
        username = cursor.fetchone()[0]
    
    return render_template('index.html', username=username)

@app.route('/log_expense', methods=['POST'])
def log_expense():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    amount = float(request.form['amount'])
    category = request.form['category']
    description = request.form['description']
    add_expense(amount, category, description, session['user_id'])
    return redirect(url_for('index'))

def get_all_expenses():
    if 'user_id' not in session:
        return []

    user_id = session['user_id']
    cursor.execute('SELECT id, amount, category, description, date FROM expenses WHERE user_id=?', (user_id,))
    return cursor.fetchall()


@app.route('/view_total_expense')
def view_total_expense():
    expenses = get_all_expenses()

    # Filter and sort parameters from the request
    filter_amount = request.args.get('filter_amount', type=float)
    sort_order = request.args.get('sort_order', 'asc')

    # Filter expenses based on amount
    if filter_amount is not None:
        expenses = [expense for expense in expenses if expense[1] == filter_amount]

    # Sort expenses based on amount
    expenses.sort(key=lambda x: x[1], reverse=(sort_order == 'desc'))

    total_expense = get_total_expense()
    return render_template('total_expense.html', total_expense=total_expense, expenses=expenses)

@app.route('/view_expense_distribution')
def view_expense_distribution():
    expenses_by_category = get_expenses_by_category()
    if expenses_by_category:
        categories, amounts = zip(*expenses_by_category)
        plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140)
        plt.axis('equal')
        plt.title('Expense Distribution by Category')
        plt.savefig('static/expense_distribution.png')
        plt.close()
        return render_template('expense_distribution.html', chart=True)
    else:
        return "No expenses logged yet."


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        create_user_profile(username, password)
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_id = authenticate_user(username, password)
        if user_id:
            session['user_id'] = user_id
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/change_password')
def change_password():
    return render_template('change_password.html')

if __name__ == '__main__':
    with app.app_context():

        conn = sqlite3.connect('expense_tracker.db', check_same_thread=False)
        cursor = conn.cursor()

        create_expenses_table(cursor)

        conn.commit()

        app.run(debug=True)

# Close the database connection when the program exits
conn.close()