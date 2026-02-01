from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import random
import string
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'domcredsys-secret-key-2026')

# Configuration
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '4757')
DEFAULT_STORE = os.environ.get('DEFAULT_STORE', '98175')

# Database initialization
def init_db():
    conn = sqlite3.connect('credits.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS credits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            amount REAL NOT NULL,
            store_id TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            claimed_at TIMESTAMP,
            claimed_by TEXT,
            notes TEXT
        )
    ''')
    conn.commit()
    conn.close()

def generate_code():
    """Generate a random 3-character alphanumeric code"""
    conn = sqlite3.connect('credits.db')
    try:
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
            # Check if code already exists
            c = conn.cursor()
            c.execute('SELECT code FROM credits WHERE code = ?', (code,))
            if not c.fetchone():
                return code
    finally:
        conn.close()

@app.route('/')
def index():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            session['username'] = username
            session['store_id'] = request.form.get('store_id', DEFAULT_STORE)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html', default_store=DEFAULT_STORE)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    store_id = session.get('store_id', DEFAULT_STORE)
    
    # Get credits for current store
    conn = sqlite3.connect('credits.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT * FROM credits 
        WHERE store_id = ? 
        ORDER BY created_at DESC
    ''', (store_id,))
    credits = c.fetchall()
    conn.close()
    
    return render_template('dashboard.html', 
                         credits=credits, 
                         store_id=store_id,
                         username=session.get('username'))

@app.route('/create_credit', methods=['POST'])
def create_credit():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    amount = request.form.get('amount')
    notes = request.form.get('notes', '')
    store_id = session.get('store_id', DEFAULT_STORE)
    
    try:
        amount = float(amount)
        if amount <= 0:
            flash('Amount must be greater than 0', 'error')
            return redirect(url_for('dashboard'))
        
        code = generate_code()
        
        conn = sqlite3.connect('credits.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO credits (code, amount, store_id, notes)
            VALUES (?, ?, ?, ?)
        ''', (code, amount, store_id, notes))
        conn.commit()
        conn.close()
        
        flash(f'Credit created successfully! Code: {code}', 'success')
    except ValueError:
        flash('Invalid amount', 'error')
    except Exception as e:
        flash(f'Error creating credit: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/claim_credit', methods=['POST'])
def claim_credit():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    code = request.form.get('code', '').upper().strip()
    customer_name = request.form.get('customer_name', '')
    store_id = session.get('store_id', DEFAULT_STORE)
    
    if len(code) != 3:
        flash('Code must be exactly 3 characters', 'error')
        return redirect(url_for('dashboard'))
    
    conn = sqlite3.connect('credits.db')
    c = conn.cursor()
    
    # Check if credit exists and is active
    c.execute('''
        SELECT * FROM credits 
        WHERE code = ? AND store_id = ? AND status = 'active'
    ''', (code, store_id))
    
    credit = c.fetchone()
    
    if credit:
        # Claim the credit
        c.execute('''
            UPDATE credits 
            SET status = 'claimed', 
                claimed_at = CURRENT_TIMESTAMP,
                claimed_by = ?
            WHERE code = ?
        ''', (customer_name, code))
        conn.commit()
        flash(f'Credit {code} claimed successfully!', 'success')
    else:
        flash(f'Credit {code} not found or already claimed', 'error')
    
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/change_store', methods=['POST'])
def change_store():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    new_store_id = request.form.get('store_id')
    session['store_id'] = new_store_id
    flash(f'Store changed to {new_store_id}', 'success')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    init_db()
    # Use environment variables to control debug mode and host
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', '5000'))
    app.run(debug=debug_mode, host=host, port=port)
