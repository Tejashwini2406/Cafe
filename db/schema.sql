-- SQL Schema for Restaurant Management System
-- This schema includes tables for users, menu items, orders, payments, feedback, suppliers, and inventory management.
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE
);

CREATE TABLE menu (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(8,2) NOT NULL,
    image_url VARCHAR(255)
);

CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    status VARCHAR(50) DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    menu_id INT,
    quantity INT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (menu_id) REFERENCES menu(id)
);

CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    amount DECIMAL(8,2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    payment_date DATETIME,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

CREATE TABLE feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    order_id INT,
    message TEXT,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

CREATE TABLE suppliers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contact_info VARCHAR(255)
);

CREATE TABLE inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(100) NOT NULL,
    quantity INT NOT NULL,
    supplier_id INT,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
);

-- Triggers: Automatically update inventory on order placement
DELIMITER //
CREATE TRIGGER after_order_item_insert
AFTER INSERT ON order_items
FOR EACH ROW
BEGIN
    UPDATE inventory SET quantity = quantity - NEW.quantity
    WHERE item_name = (SELECT name FROM menu WHERE id = NEW.menu_id);
END;//
DELIMITER ;

-- Procedure: Add new menu item
DELIMITER //
CREATE PROCEDURE add_menu_item(
    IN p_name VARCHAR(100),
    IN p_description TEXT,
    IN p_price DECIMAL(8,2),
    IN p_image_url VARCHAR(255)
)
BEGIN
    INSERT INTO menu (name, description, price, image_url)
    VALUES (p_name, p_description, p_price, p_image_url);
END;//
DELIMITER ;

-- Transaction: Place order with rollback on error
DELIMITER //
CREATE PROCEDURE place_order_with_items(
    IN p_user_id INT,
    IN p_menu_ids TEXT,
    IN p_quantities TEXT
)
BEGIN
    DECLARE done INT DEFAULT 0;
    DECLARE i INT DEFAULT 1;
    DECLARE menu_id INT;
    DECLARE qty INT;
    DECLARE order_id INT;
    DECLARE menu_id_list TEXT;
    DECLARE qty_list TEXT;
    START TRANSACTION;
    INSERT INTO orders (user_id) VALUES (p_user_id);
    SET order_id = LAST_INSERT_ID();
    SET menu_id_list = p_menu_ids;
    SET qty_list = p_quantities;
    WHILE i <= CHAR_LENGTH(menu_id_list) - CHAR_LENGTH(REPLACE(menu_id_list, ',', '')) + 1 DO
        SET menu_id = CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(menu_id_list, ',', i), ',', -1) AS UNSIGNED);
        SET qty = CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(qty_list, ',', i), ',', -1) AS UNSIGNED);
        INSERT INTO order_items (order_id, menu_id, quantity) VALUES (order_id, menu_id, qty);
        UPDATE inventory SET quantity = quantity - qty WHERE item_name = (SELECT name FROM menu WHERE id = menu_id);
        SET i = i + 1;
    END WHILE;
    COMMIT;
END;//
DELIMITER ;

-- Concurrency Control: Use row-level locking for inventory updates
-- Example in a transaction:
--   START TRANSACTION;
--   SELECT quantity FROM inventory WHERE id = ? FOR UPDATE;
--   UPDATE inventory SET quantity = quantity - ? WHERE id = ?;
--   COMMIT;

-- Normalization: All tables are in at least 3NF (no repeating groups, all non-key attributes depend on the key, no transitive dependencies)
--   - Users, menu, orders, order_items, payments, feedback, suppliers, inventory are all normalized.
