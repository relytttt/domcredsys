# Domain Credit System (domcredsys)

A web application for managing store credits with 3-character alphanumeric codes.

## Features

- **Manager Login**: Secure authentication (username: `admin`, password: `4757`)
- **Store Selection**: Select and switch between stores (default: `98175`)
- **Create Credits**: Generate credits with unique 3-character codes
- **Claim Credits**: Redeem credits using the code
- **View Credits**: See all credits with status tracking

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Access the web interface at: `http://localhost:5000`

## Usage

1. **Login**: Use credentials `admin` / `4757` with store ID (default: `98175`)
2. **Create Credit**: Enter amount and optional notes to generate a unique 3-character code
3. **Claim Credit**: Enter the 3-character code and customer name to redeem
4. **View Credits**: See all active and claimed credits for the selected store
5. **Change Store**: Switch between different store locations

## Database

The application uses SQLite (`credits.db`) to store:
- Credit codes (3-character alphanumeric)
- Credit amounts
- Store associations
- Status (active/claimed)
- Timestamps and customer information
