from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    if DATABASE_URL:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        return conn, cursor
    else:
        basedir = os.path.abspath(os.path.dirname(__file__))
        DATABASE = os.path.join(basedir, 'expenses.db')
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn, None

@app.route('/')
def home():
    conn, cursor = get_db_connection()
    try:
        if cursor:
            cursor.execute('SELECT * FROM expenses ORDER BY date DESC')
            expenses = cursor.fetchall()
        else:
            expenses = conn.execute('SELECT * FROM expenses ORDER BY date DESC').fetchall()
        return render_template('index.html', expenses=expenses)
    finally:
        if cursor:
            cursor.close()
            conn.close()
        else:
            conn.close()

@app.route('/add', methods=['POST'])
def add_expense():
    date = request.form['date']
    description = request.form['description']
    amount = request.form['amount']
    
    conn, cursor = get_db_connection()
    try:
        if cursor:
            cursor.execute('INSERT INTO expenses (date, description, amount) VALUES (%s, %s, %s)',
                          (date, description, amount))
            conn.commit()
        else:
            conn.execute('INSERT INTO expenses (date, description, amount) VALUES (?, ?, ?)',
                        (date, description, amount))
            conn.commit()
    finally:
        if cursor:
            cursor.close()
            conn.close()
        else:
            conn.close()
    return redirect(url_for('home'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete_expense(id):
    conn, cursor = get_db_connection()
    try:
        if cursor:
            cursor.execute('DELETE FROM expenses WHERE id = %s', (id,))
            conn.commit()
        else:
            conn.execute('DELETE FROM expenses WHERE id = ?', (id,))
            conn.commit()
    finally:
        if cursor:
            cursor.close()
            conn.close()
        else:
            conn.close()
    return redirect(url_for('home'))

@app.route('/edit/<int:id>', methods=['GET'])
def edit_expense_form(id):
    conn, cursor = get_db_connection()
    try:
        if cursor:
            cursor.execute('SELECT * FROM expenses WHERE id = %s', (id,))
            expense = cursor.fetchone()
        else:
            expense = conn.execute('SELECT * FROM expenses WHERE id = ?', (id,)).fetchone()
        
        if expense is None:
            return "Expense not found", 404
        return render_template('edit.html', expense=expense)
    finally:
        if cursor:
            cursor.close()
            conn.close()
        else:
            conn.close()

@app.route('/edit/<int:id>', methods=['POST'])
def edit_expense(id):
    date = request.form['date']
    description = request.form['description']
    amount = request.form['amount']
    
    conn, cursor = get_db_connection()
    try:
        if cursor:
            cursor.execute('UPDATE expenses SET date = %s, description = %s, amount = %s WHERE id = %s',
                          (date, description, amount, id))
            conn.commit()
        else:
            conn.execute('UPDATE expenses SET date = ?, description = ?, amount = ? WHERE id = ?',
                        (date, description, amount, id))
            conn.commit()
    finally:
        if cursor:
            cursor.close()
            conn.close()
        else:
            conn.close()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=False)