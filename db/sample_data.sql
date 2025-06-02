-- Sample data for CafeOrderSystem

-- Users
INSERT INTO users (username, password_hash, email, is_admin, is_verified) VALUES
('admin', '$pbkdf2-sha256$29000$sampleadminhash', 'admin@cafe.com', 1, 1),
('user1', '$pbkdf2-sha256$29000$sampleuser1hash', 'user1@cafe.com', 0, 1),
('user2', '$pbkdf2-sha256$29000$sampleuser2hash', 'user2@cafe.com', 0, 1);

-- Menu
INSERT INTO menu (name, description, price, image_url) VALUES
('Espresso', 'Strong and bold espresso shot', 80.00, NULL),
('Cappuccino', 'Espresso with steamed milk and foam', 120.00, NULL),
('Latte', 'Smooth espresso with milk', 130.00, NULL),
('Mocha', 'Espresso with chocolate and milk', 140.00, NULL),
('Brownie', 'Chocolate fudge brownie', 60.00, NULL);

-- Suppliers
INSERT INTO suppliers (name, contact_info) VALUES
('Coffee Beans Co.', 'beans@supplier.com'),
('Dairy Fresh', 'milk@supplier.com');

-- Inventory
INSERT INTO inventory (item_name, quantity, supplier_id) VALUES
('Coffee Beans', 100, 1),
('Milk', 50, 2),
('Chocolate', 30, 1);

-- Orders
INSERT INTO orders (user_id, status) VALUES
(2, 'pending'),
(3, 'completed');

-- Order Items
INSERT INTO order_items (order_id, menu_id, quantity) VALUES
(1, 1, 2),
(1, 2, 1),
(2, 3, 1),
(2, 5, 2);

-- Payments
INSERT INTO payments (order_id, amount, status, payment_date) VALUES
(1, 280.00, 'pending', NULL),
(2, 250.00, 'completed', NOW());

-- Feedback
INSERT INTO feedback (user_id, message, rating) VALUES
(2, 'Great coffee and service!', 5),
(3, 'Loved the brownie!', 4);
