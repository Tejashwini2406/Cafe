from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_mail import Mail, Message
import mariadb
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get('SECRET_KEY', 'devsecret')

# MariaDB connection
conn = mariadb.connect(
    user='root',
    password='pp',
    host='localhost',
    port=3306,
    database='CafeOrderSystem'
)
cursor = conn.cursor()

# Flask-Mail config (use a test SMTP or console for dev)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'email@gmail.com'
app.config['MAIL_PASSWORD'] = 'ncj'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

serializer = URLSafeTimedSerializer(app.secret_key)

@app.route('/')
def index():
    return 'Cafe Order Management System API is running.'

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    username = data['username']
    password = data['password']
    email = data['email']
    is_admin = data.get('is_admin', False)
    password_hash = generate_password_hash(password)
    try:
        cursor.execute("INSERT INTO users (username, password_hash, email, is_admin) VALUES (?, ?, ?, ?)",
                       (username, password_hash, email, is_admin))
        conn.commit()
        # Send real verification email
        token = serializer.dumps(email, salt='email-verify')
        verify_url = f"http://localhost:5000/api/verify_email?token={token}"
        msg = Message('Cafe Email Verification', recipients=[email])
        msg.body = f'Hi {username}, please verify your email by clicking this link: {verify_url}'
        mail.send(msg)
        return jsonify({'message': 'Signup successful, please check your email to verify.'}), 201
    except mariadb.IntegrityError:
        return jsonify({'error': 'Username or email already exists.'}), 409

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']
    cursor.execute("SELECT id, password_hash, is_admin, is_verified FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    if user and check_password_hash(user[1], password):
        if not user[3]:
            return jsonify({'error': 'Email not verified.'}), 403
        session['user_id'] = user[0]
        session['is_admin'] = user[2]
        return jsonify({'message': 'Login successful', 'is_admin': user[2]}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/verify_email', methods=['GET'])
def verify_email():
    token = request.args.get('token')
    try:
        email = serializer.loads(token, salt='email-verify', max_age=3600)
    except Exception:
        return 'Verification link is invalid or expired.', 400
    cursor.execute("UPDATE users SET is_verified=1 WHERE email=?", (email,))
    conn.commit()
    return 'Email verified! You can now log in.'

@app.route('/api/menu', methods=['GET'])
def get_menu():
    cursor.execute("SELECT id, name, description, price, image_url FROM menu")
    items = [
        {
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'price': float(row[3]),
            'image_url': row[4]
        } for row in cursor.fetchall()
    ]
    return jsonify(items)

@app.route('/api/order', methods=['POST'])
def place_order():
    data = request.json
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
    items = data.get('items', [])
    if not items:
        return jsonify({'error': 'No items in order'}), 400
    cursor.execute("INSERT INTO orders (user_id) VALUES (?)", (user_id,))
    order_id = cursor.lastrowid
    for item in items:
        cursor.execute("INSERT INTO order_items (order_id, menu_id, quantity) VALUES (?, ?, ?)",
                       (order_id, item['menu_id'], item['quantity']))
    conn.commit()
    return jsonify({'message': 'Order placed!', 'order_id': order_id}), 201

@app.route('/api/my_orders', methods=['GET'])
def my_orders():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify([])
    cursor.execute("SELECT id, status FROM orders WHERE user_id=?", (user_id,))
    orders = []
    for order in cursor.fetchall():
        order_id, status = order
        cursor.execute("SELECT m.name, oi.quantity, m.price FROM order_items oi JOIN menu m ON oi.menu_id=m.id WHERE oi.order_id=?", (order_id,))
        items = [{'name': i[0], 'quantity': i[1], 'price': float(i[2])} for i in cursor.fetchall()]
        total = sum(i['price'] * i['quantity'] for i in items)
        orders.append({'id': order_id, 'status': status, 'items': items, 'total': total})
    return jsonify(orders)

@app.route('/api/feedback', methods=['POST'])
def feedback():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
    data = request.json
    message = data.get('message')
    rating = data.get('rating')
    cursor.execute("INSERT INTO feedback (user_id, message, rating) VALUES (?, ?, ?)", (user_id, message, rating))
    conn.commit()
    return jsonify({'message': 'Feedback submitted!'}), 201

@app.route('/api/pay', methods=['POST'])
def pay():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
    data = request.json
    order_id = data.get('order_id')
    amount = data.get('amount')
    cursor.execute("INSERT INTO payments (order_id, amount, status, payment_date) VALUES (?, ?, 'completed', CURRENT_TIMESTAMP)", (order_id, amount))
    conn.commit()
    return jsonify({'message': 'Payment successful!'})

# Admin endpoints
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_admin'):
            return jsonify({'error': 'Admin only'}), 403
        return f(*args, **kwargs)
    return decorated

@app.route('/api/admin/orders', methods=['GET'])
@admin_required
def admin_orders():
    cursor.execute("SELECT id, user_id, status FROM orders")
    orders = []
    for order in cursor.fetchall():
        order_id, user_id, status = order
        cursor.execute("SELECT m.name, oi.quantity, m.price FROM order_items oi JOIN menu m ON oi.menu_id=m.id WHERE oi.order_id=?", (order_id,))
        items = [{'name': i[0], 'quantity': i[1], 'price': float(i[2])} for i in cursor.fetchall()]
        total = sum(i['price'] * i['quantity'] for i in items)
        orders.append({'id': order_id, 'user_id': user_id, 'status': status, 'items': items, 'total': total})
    return jsonify(orders)

@app.route('/api/admin/orders', methods=['POST'])
@admin_required
def add_order():
    data = request.json
    user_id = data.get('user_id')
    items = data.get('items', [])
    if not user_id or not items:
        return jsonify({'error': 'User ID and items required'}), 400
    cursor.execute("INSERT INTO orders (user_id) VALUES (?)", (user_id,))
    order_id = cursor.lastrowid
    for item in items:
        cursor.execute("INSERT INTO order_items (order_id, menu_id, quantity) VALUES (?, ?, ?)",
                       (order_id, item['menu_id'], item['quantity']))
    conn.commit()
    return jsonify({'message': 'Order added', 'order_id': order_id}), 201

@app.route('/api/admin/orders/<int:order_id>', methods=['DELETE'])
@admin_required
def delete_order(order_id):
    cursor.execute("DELETE FROM order_items WHERE order_id=?", (order_id,))
    cursor.execute("DELETE FROM payments WHERE order_id=?", (order_id,))
    cursor.execute("DELETE FROM orders WHERE id=?", (order_id,))
    conn.commit()
    return jsonify({'message': 'Order deleted'})

@app.route('/api/admin/payments', methods=['GET'])
@admin_required
def admin_payments():
    cursor.execute("SELECT id, order_id, amount, status FROM payments")
    payments = [{'id': row[0], 'order_id': row[1], 'amount': float(row[2]), 'status': row[3]} for row in cursor.fetchall()]
    return jsonify(payments)

@app.route('/api/admin/payments/<int:payment_id>/refund', methods=['POST'])
@admin_required
def refund_payment(payment_id):
    cursor.execute("UPDATE payments SET status='refunded' WHERE id=?", (payment_id,))
    conn.commit()
    return jsonify({'message': 'Payment refunded'})

@app.route('/api/admin/suppliers', methods=['GET'])
@admin_required
def admin_suppliers():
    cursor.execute("SELECT id, name, contact_info FROM suppliers")
    suppliers = [{'id': row[0], 'name': row[1], 'contact_info': row[2]} for row in cursor.fetchall()]
    return jsonify(suppliers)

@app.route('/api/admin/suppliers', methods=['POST'])
@admin_required
def add_supplier():
    data = request.json
    cursor.execute("INSERT INTO suppliers (name, contact_info) VALUES (?, ?)", (data['name'], data['contact_info']))
    conn.commit()
    return jsonify({'message': 'Supplier added'})

@app.route('/api/admin/suppliers/<int:supplier_id>', methods=['DELETE'])
@admin_required
def delete_supplier(supplier_id):
    cursor.execute("DELETE FROM inventory WHERE supplier_id=?", (supplier_id,))
    cursor.execute("DELETE FROM suppliers WHERE id=?", (supplier_id,))
    conn.commit()
    return jsonify({'message': 'Supplier deleted'})

@app.route('/api/admin/inventory', methods=['GET'])
@admin_required
def admin_inventory():
    cursor.execute("SELECT i.id, i.item_name, i.quantity, s.name FROM inventory i LEFT JOIN suppliers s ON i.supplier_id=s.id")
    inventory = [{'id': row[0], 'item_name': row[1], 'quantity': row[2], 'supplier_name': row[3]} for row in cursor.fetchall()]
    return jsonify(inventory)

@app.route('/api/admin/inventory', methods=['POST'])
@admin_required
def add_inventory():
    data = request.json
    cursor.execute("INSERT INTO inventory (item_name, quantity, supplier_id) VALUES (?, ?, ?)", (data['item_name'], data['quantity'], data['supplier_id']))
    conn.commit()
    return jsonify({'message': 'Inventory item added'})

@app.route('/api/admin/inventory/<int:inventory_id>', methods=['DELETE'])
@admin_required
def delete_inventory(inventory_id):
    cursor.execute("DELETE FROM inventory WHERE id=?", (inventory_id,))
    conn.commit()
    return jsonify({'message': 'Inventory item deleted'})

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def admin_users():
    cursor.execute("SELECT id, username, email, is_admin, is_verified FROM users")
    users = [{'id': row[0], 'username': row[1], 'email': row[2], 'is_admin': bool(row[3]), 'is_verified': bool(row[4])} for row in cursor.fetchall()]
    return jsonify(users)

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    cursor.execute("DELETE FROM feedback WHERE user_id=?", (user_id,))
    cursor.execute("DELETE FROM orders WHERE user_id=?", (user_id,))
    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    return jsonify({'message': 'User deleted'})

@app.route('/api/admin/users/<int:user_id>/admin', methods=['POST'])
@admin_required
def toggle_admin(user_id):
    is_admin = request.json.get('is_admin', False)
    cursor.execute("UPDATE users SET is_admin=? WHERE id=?", (is_admin, user_id))
    conn.commit()
    return jsonify({'message': 'Admin status updated'})

@app.route('/api/admin/users', methods=['POST'])
@admin_required
def admin_add_user():
    data = request.json
    username = data['username']
    password = data['password']
    email = data['email']
    is_admin = data.get('is_admin', False)
    password_hash = generate_password_hash(password)
    try:
        cursor.execute("INSERT INTO users (username, password_hash, email, is_admin, is_verified) VALUES (?, ?, ?, ?, 1)",
                       (username, password_hash, email, is_admin))
        conn.commit()
        return jsonify({'message': 'User added'}), 201
    except mariadb.IntegrityError:
        return jsonify({'error': 'Username or email already exists.'}), 409

# ...existing code for payments, suppliers, inventory...

if __name__ == '__main__':
    app.run(debug=True)
