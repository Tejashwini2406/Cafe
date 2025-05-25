from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS
import hashlib
from flask_jwt_extended import JWTManager, create_access_token

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "your_super_secret_key"  # Change this for production
jwt = JWTManager(app)

CORS(app)  # Enables frontend communication

# Database Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="T&p@2006",
    database="cafe_db"
)
cursor = db.cursor(dictionary=True)
if not db.is_connected():
    print("Database connection failed. Attempting to reconnect...")
    db.reconnect()

# Home Route
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Cafe Order System!"})

# Fetch Available Menu Items (Matches Frontend `script.js`)
@app.route('/menu', methods=['GET'])
def get_menu():
    db.ping(reconnect=True)  # Ensure connection is alive before execution
    cursor = db.cursor(dictionary=True)  # Fresh cursor for every request
    cursor.execute("SELECT item_id, name, price FROM MENU_ITEM WHERE is_available = 1")
    menu_items = cursor.fetchall()
    return jsonify(menu_items)

# Customer Login (Formatted for `Login.js`)
@app.route('/login', methods=['POST'])
def login_customer():
    db.ping(reconnect=True)  # Ensure connection is alive before execution
    cursor = db.cursor(dictionary=True)  # Create a fresh cursor for each request
    data = request.json
    email = data.get("email")
    password = data.get("password")
    hashed_password = hashlib.sha256(password.encode()).hexdigest()  # Hash user input

    cursor.execute("SELECT * FROM CUSTOMER WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user and user["password"] == hashed_password:  # Compare hashed passwords
        access_token = create_access_token(identity=user["customer_id"])
        return jsonify({"message": "Login successful!", "access_token": access_token})
    return jsonify({"error": "Invalid credentials"}), 401

# Register New Customer (Matches `Register.js`)
@app.route('/register', methods=['POST'])
def register_customer():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    
    # Hash password using SHA-256
    password = data.get("password")
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    cursor.execute("INSERT INTO CUSTOMER (name, email, phone, password) VALUES (%s, %s, %s, %s)", 
                   (name, email, phone, hashed_password))
    db.commit()
    return jsonify({"message": "Registration successful!"})

# Place an Order (Matches `order.html`)
@app.route('/order', methods=['POST'])
def place_order():
    db.ping(reconnect=True)  # Ensure connection is alive before execution
    cursor = db.cursor(dictionary=True)  # Create a fresh cursor for each request

    data = request.json
    customer_id = data.get("customer_id")
    total_amount = data.get("total_amount")
    payment_method = data.get("payment_method")

    # Ensure customer exists before placing the order
    cursor.execute("SELECT * FROM CUSTOMER WHERE customer_id = %s", (customer_id,))
    customer = cursor.fetchone()
    
    if not customer:
        return jsonify({"error": "Invalid customer ID"}), 400

    cursor.execute("INSERT INTO orders (customer_id, total_amount, payment_method, status) VALUES (%s, %s, %s, 'Pending')",
                   (customer_id, total_amount, payment_method))
    db.commit()
    
    return jsonify({"message": "Order placed successfully!"})
# Close Database Connection when Flask Stops
@app.teardown_appcontext
def close_connection(exception=None):
    if db.is_connected():
        cursor.close()
        db.close()

if __name__ == '__main__':
    app.run(debug=True)
