from flask import Flask, render_template, request, redirect, url_for, session, flash
from supabase import create_client, Client
import random
import string
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'domcredsys-secret-key-2026')

# Configuration
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '4757')
DEFAULT_STORE = os.environ.get('DEFAULT_STORE', '98175')

# Supabase setup
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables are required")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def generate_code():
    """Generate a random 3-character alphanumeric code"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
        # Check if code already exists
        result = supabase.table('credits').select('code').eq('code', code).execute()
        if not result.data:
            return code

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
    
    # Get credits for current store from Supabase
    result = supabase.table('credits') \
        .select('*') \
        .eq('store_id', store_id) \
        .order('created_at', desc=True) \
        .execute()
    
    credits = result.data
    
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
        
        supabase.table('credits').insert({
            'code': code,
            'amount': amount,
            'store_id': store_id,
            'notes': notes
        }).execute()
        
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
    
    # Check if credit exists and is active
    result = supabase.table('credits') \
        .select('*') \
        .eq('code', code) \
        .eq('store_id', store_id) \
        .eq('status', 'active') \
        .execute()
    
    if result.data:
        # Claim the credit
        supabase.table('credits') \
            .update({
                'status': 'claimed',
                'claimed_at': datetime.now(timezone.utc).isoformat(),
                'claimed_by': customer_name
            }) \
            .eq('code', code) \
            .execute()
        flash(f'Credit {code} claimed successfully!', 'success')
    else:
        flash(f'Credit {code} not found or already claimed', 'error')
    
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
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', '5000'))
    app.run(debug=debug_mode, host=host, port=port)
