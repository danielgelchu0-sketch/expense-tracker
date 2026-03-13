from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
# WARNING: Replace with environment variable in production
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

basedir = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(basedir, 'expenses.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    conn = get_db_connection()
    expenses = conn.execute('SELECT * FROM expenses ORDER BY date DESC').fetchall()
    conn.close()
    return render_template('index.html', expenses=expenses)

@app.route('/add', methods=['POST'])
def add_expense():
    date = request.form['date']
    description = request.form['description']
    amount = request.form['amount']
    
    conn = get_db_connection()
    conn.execute('INSERT INTO expenses (date, description, amount) VALUES (?, ?, ?)',
                 (date, description, amount))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete_expense(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM expenses WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/edit/<int:id>', methods=['GET'])
def edit_expense_form(id):
    conn = get_db_connection()
    expense = conn.execute('SELECT * FROM expenses WHERE id = ?', (id,)).fetchone()
    conn.close()
    if expense is None:
        return "Expense not found", 404
    return render_template('edit.html', expense=expense)

@app.route('/edit/<int:id>', methods=['POST'])
def edit_expense(id):
    date = request.form['date']
    description = request.form['description']
    amount = request.form['amount']
    
    conn = get_db_connection()
    conn.execute('UPDATE expenses SET date = ?, description = ?, amount = ? WHERE id = ?',
                 (date, description, amount, id))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=False)