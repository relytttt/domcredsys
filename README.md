# Domain Credit System (domcredsys)

A comprehensive web application for managing item-based store credits with user authentication, role-based access control, and multi-store support.

## Features

### User Management
- **User Authentication**: Login with 3-character user codes and passwords
- **Role-Based Access Control**: Admin and regular user roles
- **Password Management**: Users can change their own passwords
- **Store Assignments**: Users can only access stores they are assigned to

### Credit Management (Item-Based)
- **Create Credits**: Generate credits with items, reason, and date of issue
- **Claim Credits**: Redeem credits using unique 3-character codes
- **Status Tracking**: Active and claimed status for all credits
- **Store-Specific**: Credits are associated with specific stores

### Admin Panel
- **User Management**: Create, view, and delete user accounts
- **Store Management**: Create, view, and delete stores
- **User-Store Assignments**: Assign and unassign users to stores
- **Overview Dashboard**: Statistics on users, stores, credits, and assignments

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. **Setup Supabase Database**:
   - Create a Supabase project at [supabase.com](https://supabase.com)
   - Run the SQL commands from `schema.sql` in the Supabase SQL Editor
   - This will create all required tables and insert the default admin user

3. **Configure environment variables**:
   - Copy `.env.example` to `.env`
   - Update with your Supabase credentials:
   ```bash
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-public-key
   SECRET_KEY=your-secret-key-here
   ```

4. Run the application:
```bash
python app.py
```

5. Access the web interface at: `http://localhost:5000`

## Default Admin Access

After running `schema.sql`, a default admin user is created:
- **User Code**: `ADM`
- **Password**: `4757`

**Important**: Change the admin password after first login!

## Database Schema

The system uses four main tables:

### 1. `users` table
Stores user accounts with codes, passwords, and admin status.

### 2. `stores` table
Stores store information with unique store IDs and names.

### 3. `user_stores` table
Many-to-many relationship between users and stores for access control.

### 4. `credits` table
Stores credit information including items, reason, date of issue, and claim status.

See `schema.sql` for complete table definitions.

## Usage

### Regular Users

1. **Login**: Enter your 3-character code and password
2. **Select Store**: Choose from your assigned stores in the dropdown
3. **Create Credit**: 
   - Enter items description
   - Provide reason for credit
   - Select date of issue (defaults to today)
   - System generates unique 3-character code
4. **Claim Credit**: 
   - Enter the 3-character credit code
   - Provide customer name
   - Credit is marked as claimed
5. **View Credits**: See all credits for your selected store
6. **Change Password**: Update your password from the navigation menu

### Admin Users

Admins have access to all user features plus:

1. **User Management**:
   - Create new users with 3-character codes
   - Set admin privileges
   - Delete users (except yourself)

2. **Store Management**:
   - Create new stores with IDs and names
   - Delete stores

3. **User-Store Assignments**:
   - Assign users to stores
   - Remove user-store assignments
   - View all assignments

4. **Access All Stores**: Admins can view and manage credits for all stores

## Application Routes

### Authentication
- `/login` - Login page
- `/logout` - Logout and clear session
- `/change-password` - Change user password

### Dashboard
- `/` - Redirect to dashboard or login
- `/dashboard` - Main dashboard with credit management
- `/select-store` - Change currently selected store
- `/create-credit` - Create a new credit
- `/claim-credit` - Claim an existing credit

### Admin Panel (Admin Only)
- `/admin` - Admin dashboard overview
- `/admin/users` - User management
- `/admin/users/create` - Create new user
- `/admin/users/<code>/delete` - Delete user
- `/admin/stores` - Store management
- `/admin/stores/create` - Create new store
- `/admin/stores/<store_id>/delete` - Delete store
- `/admin/assignments` - User-store assignments
- `/admin/assignments/create` - Create assignment
- `/admin/assignments/delete` - Delete assignment

## Deployment on Vercel

1. **Add environment variables in Vercel**:
   - `SUPABASE_URL` - Your Supabase project URL
   - `SUPABASE_KEY` - Your Supabase anon/public key
   - `SECRET_KEY` - A random secret string for Flask sessions

2. Deploy to Vercel using the Vercel CLI or GitHub integration

3. **Important**: Run the SQL commands from `schema.sql` in your Supabase SQL Editor before using the application

## Configuration

The application can be configured using environment variables:

- `SUPABASE_URL`: Your Supabase project URL (required)
- `SUPABASE_KEY`: Your Supabase anon/public key (required)
- `SECRET_KEY`: Flask session secret key (required for production)
- `FLASK_DEBUG`: Enable debug mode (default: False)
- `FLASK_HOST`: Server host address (default: 127.0.0.1)
- `FLASK_PORT`: Server port (default: 5000)

## Security Features

- Password-protected user authentication
- Role-based access control (admin vs regular user)
- Store-level access control (users only see assigned stores)
- Session-based authentication
- SQL injection protection via Supabase client
- CSRF protection via Flask sessions

## Credits Table Structure

Credits are now **item-based** (not dollar-based) and include:
- **code**: Unique 3-character identifier
- **items**: Description of items being credited
- **reason**: Reason for the credit
- **date_of_issue**: When the credit was issued
- **store_id**: Associated store
- **status**: active or claimed
- **created_by**: User who created the credit
- **claimed_by**: Customer who claimed the credit
- **claimed_at**: When the credit was claimed
