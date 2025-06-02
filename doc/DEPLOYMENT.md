# Cafe Order Management System - Deployment Instructions

## Prerequisites
- Python 3.8+
- MariaDB Server
- Node.js (optional, for advanced JS tooling)

## 1. Database Setup
1. Start MariaDB server.
2. Open a MariaDB client (e.g., HeidiSQL, DBeaver, or command line):
   - Run the SQL script to create tables:
     ```sql
     SOURCE db/schema.sql;
     ```
   - Or from command line:
     ```sh
     mariadb -u root -p < db/schema.sql
     ```
   - (Change `root` and password as needed.)

## 2. Backend Setup (Flask)
1. Open a terminal in the `backend` folder:
   ```sh
   cd backend
   python -m venv venv
   venv\Scripts\activate  # On Windows
   pip install -r requirements.txt
   ```
2. Edit `app.py`:
   - Set your MariaDB credentials in the `mariadb.connect` call.
   - Set Flask-Mail SMTP config (or leave as is for dev/testing).
   - Optionally, set a secure `SECRET_KEY`.
3. Run the Flask server:
   ```sh
   python app.py
   ```
   - The API will be available at `http://localhost:5000`

## 3. Frontend Setup
1. Open `frontend/index.html` in your browser for the user interface.
2. For local development, you can use a simple HTTP server:
   ```sh
   cd frontend
   python -m http.server 8080
   ```
   - Then visit `http://localhost:8080` in your browser.

## 4. Usage
- Signup as a user or admin.
- Admins can access `admin_dashboard.html` for management features.
- Users can view orders, give feedback, and place orders from the menu.

## 5. Notes
- For email verification, configure a real SMTP server in `backend/app.py` for production.
- CORS is enabled for local development. Adjust as needed for deployment.
- Replace placeholder images and assets for a polished look.

---
For any issues, check the backend terminal for errors and ensure MariaDB is running.
