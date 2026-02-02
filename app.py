from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from supabase import create_client, Client
import random
import string
import os
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
from functools import wraps

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'domcredsys-secret-key-2026')

# Supabase setup
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables are required")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Decorators for authentication and authorization
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_code' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_code' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('login'))
        if not session.get('is_admin', False):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


# Helper functions
def generate_code():
    """Generate a random 3-character alphanumeric code"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
        # Check if code already exists
        result = supabase.table('credits').select('code').eq('code', code).execute()
        if not result.data:
            return code

def get_user_stores(user_code):
    """Get all stores assigned to a user"""
    if session.get('is_admin', False):
        # Admin can see all stores
        result = supabase.table('stores').select('*').order('name').execute()
        return result.data
    else:
        # Regular users see only assigned stores
        result = supabase.table('user_stores') \
            .select('store_id, stores(*)') \
            .eq('user_code', user_code) \
            .execute()
        return [item['stores'] for item in result.data if item['stores']]

# Authentication routes
@app.route('/')
def index():
    if 'user_code' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        password = request.form.get('password', '')
        
        if len(code) != 4 or not code.isdigit():
            flash('Code must be exactly 4 digits', 'error')
            return render_template('login.html')
        
        # Validate against users table
        result = supabase.table('users') \
            .select('*') \
            .eq('code', code) \
            .eq('password', password) \
            .execute()
        
        if result.data:
            user = result.data[0]
            session['user_code'] = user['code']
            session['is_admin'] = user['is_admin']
            session['display_name'] = user.get('display_name', user['code'])
            
            # Set first assigned store as selected_store
            stores = get_user_stores(user['code'])
            if stores:
                session['selected_store'] = stores[0]['store_id']
            else:
                session['selected_store'] = None
            
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid code or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Verify current password
        result = supabase.table('users') \
            .select('*') \
            .eq('code', session['user_code']) \
            .eq('password', current_password) \
            .execute()
        
        if not result.data:
            flash('Current password is incorrect', 'error')
            return render_template('change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return render_template('change_password.html')
        
        if len(new_password) < 4:
            flash('Password must be at least 4 characters', 'error')
            return render_template('change_password.html')
        
        # Update password
        supabase.table('users') \
            .update({'password': new_password}) \
            .eq('code', session['user_code']) \
            .execute()
        
        flash('Password changed successfully', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('change_password.html')

# Dashboard routes
@app.route('/dashboard')
@login_required
def dashboard():
    user_code = session['user_code']
    is_admin = session.get('is_admin', False)
    selected_store = session.get('selected_store')
    display_name = session.get('display_name', user_code)
    
    # Get user's stores
    stores = get_user_stores(user_code)
    
    # Get credits for selected store with creator display names
    credits = []
    if selected_store:
        result = supabase.table('credits') \
            .select('*, users!credits_created_by_fkey(display_name)') \
            .eq('store_id', selected_store) \
            .order('created_at', desc=True) \
            .execute()
        
        # Flatten the user data and parse items
        for credit in result.data:
            if credit.get('users'):
                credit['creator_display_name'] = credit['users'].get('display_name', credit['created_by'])
            else:
                credit['creator_display_name'] = credit['created_by']
            
            # Parse items JSON to display
            items_str = credit.get('items', '')
            try:
                # Try to parse as JSON array
                items_list = json.loads(items_str)
                if isinstance(items_list, list):
                    credit['items_display'] = ', '.join(items_list)
                else:
                    credit['items_display'] = items_str
            except (json.JSONDecodeError, TypeError):
                # Not JSON, treat as plain string
                credit['items_display'] = items_str
                
        credits = result.data
    
    return render_template('dashboard.html', 
                         credits=credits, 
                         stores=stores,
                         selected_store=selected_store,
                         user_code=user_code,
                         display_name=display_name,
                         is_admin=is_admin)

@app.route('/select-store', methods=['POST'])
@login_required
def select_store():
    new_store_id = request.form.get('store_id')
    
    # Verify user has access to this store
    stores = get_user_stores(session['user_code'])
    store_ids = [s['store_id'] for s in stores]
    
    if new_store_id in store_ids:
        session['selected_store'] = new_store_id
        flash(f'Store changed to {new_store_id}', 'success')
    else:
        flash('You do not have access to that store', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/create-credit', methods=['POST'])
@login_required
def create_credit():
    items_json = request.form.get('items', '').strip()
    reason = request.form.get('reason', '').strip()
    date_of_issue = request.form.get('date_of_issue', '').strip()
    selected_store = session.get('selected_store')
    
    if not selected_store:
        flash('Please select a store first', 'error')
        return redirect(url_for('dashboard'))
    
    if not items_json or not reason:
        flash('Items and reason are required', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        # Parse items JSON or accept as string
        items_str = items_json
        if items_json.startswith('['):
            items_list = json.loads(items_json)
            if not items_list or not isinstance(items_list, list):
                flash('At least one item is required', 'error')
                return redirect(url_for('dashboard'))
            # Store as JSON string
            items_str = json.dumps(items_list)
        # else: it's a plain string, use as is for backward compatibility
        
        code = generate_code()
        
        credit_data = {
            'code': code,
            'items': items_str,
            'reason': reason,
            'store_id': selected_store,
            'created_by': session['user_code']
        }
        
        # Only add date_of_issue if provided, otherwise use database default (today)
        if date_of_issue:
            credit_data['date_of_issue'] = date_of_issue
        
        supabase.table('credits').insert(credit_data).execute()
        
        flash(f'Credit created successfully! Code: {code}', 'success')
    except json.JSONDecodeError:
        flash('Invalid items format', 'error')
    except Exception as e:
        flash(f'Error creating credit: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/claim-credit', methods=['POST'])
@login_required
def claim_credit():
    code = request.form.get('code', '').upper().strip()
    selected_store = session.get('selected_store')
    user_code = session.get('user_code')
    # Fallback chain: display_name → user_code → 'Unknown User'
    # Note: 'Unknown User' should never occur due to validation below, but included for defensive programming
    display_name = session.get('display_name') or user_code or 'Unknown User'
    
    if not user_code:
        flash('User session invalid. Please log in again.', 'error')
        return redirect(url_for('login'))
    
    if not selected_store:
        flash('Please select a store first', 'error')
        return redirect(url_for('dashboard'))
    
    if len(code) != 3:
        flash('Code must be exactly 3 characters', 'error')
        return redirect(url_for('dashboard'))
    
    # Check if credit exists and is active
    result = supabase.table('credits') \
        .select('*') \
        .eq('code', code) \
        .eq('store_id', selected_store) \
        .eq('status', 'active') \
        .execute()
    
    if result.data:
        # Claim the credit with user information
        supabase.table('credits') \
            .update({
                'status': 'claimed',
                'claimed_at': datetime.now(timezone.utc).isoformat(),
                'claimed_by': display_name,
                'claimed_by_user': user_code
            }) \
            .eq('code', code) \
            .execute()
        flash(f'Credit {code} claimed successfully!', 'success')
    else:
        flash(f'Credit {code} not found or already claimed', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/unclaim-credit', methods=['POST'])
@login_required
def unclaim_credit():
    code = request.form.get('code', '').upper().strip()
    selected_store = session.get('selected_store')
    user_code = session.get('user_code')
    is_admin = session.get('is_admin', False)
    
    if not selected_store:
        flash('Please select a store first', 'error')
        return redirect(url_for('dashboard'))
    
    if len(code) != 3:
        flash('Code must be exactly 3 characters', 'error')
        return redirect(url_for('dashboard'))
    
    # Check if credit exists and is claimed
    result = supabase.table('credits') \
        .select('*') \
        .eq('code', code) \
        .eq('store_id', selected_store) \
        .eq('status', 'claimed') \
        .execute()
    
    if result.data:
        credit = result.data[0]
        claimed_by_user_value = credit.get('claimed_by_user')
        # Authorization logic:
        # - Users can unclaim credits they claimed (claimed_by_user matches user_code)
        # - Admins can unclaim any credit
        # - Legacy credits (claimed_by_user=None) can only be unclaimed by admins
        # This matches the frontend logic in dashboard.html
        if (claimed_by_user_value and claimed_by_user_value == user_code) or is_admin:
            # Unclaim the credit
            supabase.table('credits') \
                .update({
                    'status': 'active',
                    'claimed_at': None,
                    'claimed_by': None,
                    'claimed_by_user': None
                }) \
                .eq('code', code) \
                .execute()
            flash(f'Credit {code} unclaimed successfully!', 'success')
        else:
            flash(f'You can only unclaim credits that you claimed', 'error')
    else:
        flash(f'Credit {code} not found or not claimed', 'error')
    
    return redirect(url_for('dashboard'))

# Admin routes
@app.route('/admin')
@admin_required
def admin_index():
    # Get statistics
    users_count = len(supabase.table('users').select('id').execute().data)
    stores_count = len(supabase.table('stores').select('id').execute().data)
    credits_count = len(supabase.table('credits').select('id').execute().data)
    assignments_count = len(supabase.table('user_stores').select('id').execute().data)
    
    return render_template('admin/index.html',
                         users_count=users_count,
                         stores_count=stores_count,
                         credits_count=credits_count,
                         assignments_count=assignments_count)

@app.route('/admin/users', methods=['GET'])
@admin_required
def admin_users():
    result = supabase.table('users').select('*').order('created_at', desc=True).execute()
    users = result.data
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/create', methods=['POST'])
@admin_required
def admin_users_create():
    code = request.form.get('code', '').strip()
    password = request.form.get('password', '').strip()
    display_name = request.form.get('display_name', '').strip()
    is_admin = request.form.get('is_admin') == 'on'
    
    if len(code) != 4 or not code.isdigit():
        flash('Code must be exactly 4 digits', 'error')
        return redirect(url_for('admin_users'))
    
    if len(password) < 4:
        flash('Password must be at least 4 characters', 'error')
        return redirect(url_for('admin_users'))
    
    if not display_name:
        flash('Display name is required', 'error')
        return redirect(url_for('admin_users'))
    
    try:
        supabase.table('users').insert({
            'code': code,
            'password': password,
            'display_name': display_name,
            'is_admin': is_admin
        }).execute()
        flash(f'User {display_name} ({code}) created successfully', 'success')
    except Exception as e:
        flash(f'Error creating user: {str(e)}', 'error')
    
    return redirect(url_for('admin_users'))

@app.route('/admin/users/<code>/delete', methods=['POST'])
@admin_required
def admin_users_delete(code):
    # Prevent deleting yourself
    if code == session['user_code']:
        flash('Cannot delete your own account', 'error')
        return redirect(url_for('admin_users'))
    
    try:
        supabase.table('users').delete().eq('code', code).execute()
        flash(f'User {code} deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting user: {str(e)}', 'error')
    
    return redirect(url_for('admin_users'))

@app.route('/admin/stores', methods=['GET'])
@admin_required
def admin_stores():
    result = supabase.table('stores').select('*').order('created_at', desc=True).execute()
    stores = result.data
    return render_template('admin/stores.html', stores=stores)

@app.route('/admin/stores/create', methods=['POST'])
@admin_required
def admin_stores_create():
    store_id = request.form.get('store_id', '').strip()
    name = request.form.get('name', '').strip()
    
    if not store_id or not name:
        flash('Store ID and name are required', 'error')
        return redirect(url_for('admin_stores'))
    
    try:
        supabase.table('stores').insert({
            'store_id': store_id,
            'name': name
        }).execute()
        flash(f'Store {store_id} created successfully', 'success')
    except Exception as e:
        flash(f'Error creating store: {str(e)}', 'error')
    
    return redirect(url_for('admin_stores'))

@app.route('/admin/stores/<store_id>/delete', methods=['POST'])
@admin_required
def admin_stores_delete(store_id):
    try:
        supabase.table('stores').delete().eq('store_id', store_id).execute()
        flash(f'Store {store_id} deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting store: {str(e)}', 'error')
    
    return redirect(url_for('admin_stores'))

@app.route('/admin/assignments', methods=['GET'])
@admin_required
def admin_assignments():
    # Get all assignments with user and store details
    result = supabase.table('user_stores') \
        .select('*, users(*), stores(*)') \
        .order('id', desc=True) \
        .execute()
    assignments = result.data
    
    # Get all users and stores for dropdowns
    users = supabase.table('users').select('*').order('code').execute().data
    stores = supabase.table('stores').select('*').order('name').execute().data
    
    return render_template('admin/assignments.html', 
                         assignments=assignments,
                         users=users,
                         stores=stores)

@app.route('/admin/assignments/create', methods=['POST'])
@admin_required
def admin_assignments_create():
    user_code = request.form.get('user_code')
    store_id = request.form.get('store_id')
    
    if not user_code or not store_id:
        flash('User and store are required', 'error')
        return redirect(url_for('admin_assignments'))
    
    try:
        supabase.table('user_stores').insert({
            'user_code': user_code,
            'store_id': store_id
        }).execute()
        flash(f'Assignment created successfully', 'success')
    except Exception as e:
        flash(f'Error creating assignment: {str(e)}', 'error')
    
    return redirect(url_for('admin_assignments'))

@app.route('/admin/assignments/delete', methods=['POST'])
@admin_required
def admin_assignments_delete():
    assignment_id = request.form.get('assignment_id')
    
    try:
        supabase.table('user_stores').delete().eq('id', assignment_id).execute()
        flash(f'Assignment deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting assignment: {str(e)}', 'error')
    
    return redirect(url_for('admin_assignments'))

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', '5000'))
    app.run(debug=debug_mode, host=host, port=port)
