# Domain Credit System (domcredsys)

A web application for managing store credits with 3-character alphanumeric codes.

## Features

- **Manager Login**: Secure authentication with configurable credentials
- **Store Selection**: Select and switch between stores
- **Create Credits**: Generate credits with unique 3-character codes
- **Claim Credits**: Redeem credits using the code
- **View Credits**: See all credits with status tracking

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. **Setup Supabase Database**:
   - Create a Supabase project at [supabase.com](https://supabase.com)
   - Run this SQL in the Supabase SQL Editor to create the credits table:
   ```sql
   CREATE TABLE credits (
       id SERIAL PRIMARY KEY,
       code TEXT UNIQUE NOT NULL,
       amount REAL NOT NULL,
       store_id TEXT NOT NULL,
       status TEXT DEFAULT 'active',
       created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
       claimed_at TIMESTAMP WITH TIME ZONE,
       claimed_by TEXT,
       notes TEXT
   );
   ```

3. **Configure environment variables**:
   - Copy `.env.example` to `.env`
   - Update with your Supabase credentials and preferences:
   ```bash
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-public-key
   SECRET_KEY=your-secret-key-here
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=your-password
   DEFAULT_STORE=98175
   ```

4. Run the application:
```bash
python app.py
```

5. Access the web interface at: `http://localhost:5000`

## Deployment on Vercel

1. **Add environment variables in Vercel**:
   - `SUPABASE_URL` - Your Supabase project URL
   - `SUPABASE_KEY` - Your Supabase anon/public key
   - `SECRET_KEY` - A random secret string for Flask sessions
   - `ADMIN_USERNAME` - Admin login username
   - `ADMIN_PASSWORD` - Admin login password
   - `DEFAULT_STORE` - Default store ID

2. Deploy to Vercel using the Vercel CLI or GitHub integration

## Usage

1. **Login**: Use your configured admin credentials with store ID
2. **Create Credit**: Enter amount and optional notes to generate a unique 3-character code
3. **Claim Credit**: Enter the 3-character code and customer name to redeem
4. **View Credits**: See all active and claimed credits for the selected store
5. **Change Store**: Switch between different store locations

## Configuration

The application can be configured using environment variables:

- `SUPABASE_URL`: Your Supabase project URL (required)
- `SUPABASE_KEY`: Your Supabase anon/public key (required)
- `SECRET_KEY`: Flask session secret key (required for production)
- `ADMIN_USERNAME`: Admin login username (default: admin)
- `ADMIN_PASSWORD`: Admin login password (default: 4757)
- `DEFAULT_STORE`: Default store ID (default: 98175)
- `FLASK_DEBUG`: Enable debug mode (default: False)
- `FLASK_HOST`: Server host address (default: 127.0.0.1)
- `FLASK_PORT`: Server port (default: 5000)

## Database

The application uses Supabase (PostgreSQL) to store:
- Credit codes (3-character alphanumeric)
- Credit amounts
- Store associations
- Status (active/claimed)
- Timestamps and customer information
