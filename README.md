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

2. Configure environment variables (optional):
```bash
export ADMIN_USERNAME=admin
export ADMIN_PASSWORD=4757
export DEFAULT_STORE=98175
export SECRET_KEY=your-secret-key-here
export FLASK_DEBUG=False
export FLASK_HOST=127.0.0.1
export FLASK_PORT=5000
```

3. Run the application:
```bash
python app.py
```

4. Access the web interface at: `http://localhost:5000`

## Usage

1. **Login**: Use your configured admin credentials with store ID
2. **Create Credit**: Enter amount and optional notes to generate a unique 3-character code
3. **Claim Credit**: Enter the 3-character code and customer name to redeem
4. **View Credits**: See all active and claimed credits for the selected store
5. **Change Store**: Switch between different store locations

## Configuration

The application can be configured using environment variables:

- `ADMIN_USERNAME`: Admin login username (default: admin)
- `ADMIN_PASSWORD`: Admin login password (default: 4757)
- `DEFAULT_STORE`: Default store ID (default: 98175)
- `SECRET_KEY`: Flask session secret key
- `FLASK_DEBUG`: Enable debug mode (default: False)
- `FLASK_HOST`: Server host address (default: 127.0.0.1)
- `FLASK_PORT`: Server port (default: 5000)

## Database

The application uses SQLite (`credits.db`) to store:
- Credit codes (3-character alphanumeric)
- Credit amounts
- Store associations
- Status (active/claimed)
- Timestamps and customer information
