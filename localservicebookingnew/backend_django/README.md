# Local Service Booking App — Django Backend

## Requirements
- Python 3.10+
- MySQL 8.0+
- pip

## Setup (after cloning)

### 1. Create and activate virtual environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create MySQL database
```sql
CREATE DATABASE service_booking_new CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. Configure environment
```bash
cp .env.example .env
```
Edit `.env` and set your MySQL password and a new SECRET_KEY.

### 5. Run migrations
```bash
python manage.py migrate
```

### 6. Start the server
```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/

Sample provider data is seeded automatically on first visit to any listing page.

## Test credentials (created via /signup.html)
- Register a new account, or use any seeded provider username (e.g. `arun_kumar` / `arun_kumar123`)
