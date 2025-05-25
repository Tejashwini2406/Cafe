// Fetch menu items from Flask
fetch("http://127.0.0.1:5000/menu")
    .then(response => response.json())
    .then(data => {
        const menuList = document.getElementById("menu-list");
        data.forEach(item => {
            let li = document.createElement("li");
            li.textContent = `${item.name} - $${item.price}`;
            menuList.appendChild(li);
        });
    })
    .catch(error => console.error("Error fetching menu:", error));

// Place an order
function placeOrder() {
    const customerId = document.getElementById("customerId").value.trim();
    const totalAmount = document.getElementById("totalAmount").value.trim();
    const paymentMethod = document.getElementById("paymentMethod").value.trim();

    if (!customerId || !totalAmount || !paymentMethod) {
        document.getElementById("order-message").textContent = "All fields are required.";
        return;
    }

    fetch("http://127.0.0.1:5000/order", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ customer_id: customerId, total_amount: totalAmount, payment_method: paymentMethod })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById("order-message").textContent = `Error: ${data.error}`;
        } else {
            document.getElementById("order-message").textContent = data.message;
        }
    })
    .catch(error => {
        console.error("Error placing order:", error);
        document.getElementById("order-message").textContent = "Failed to place order.";
    });
}
function handleLogin() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    fetch("http://127.0.0.1:5000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("login-message").textContent = data.message;
        if (data.access_token) {
            localStorage.setItem("token", data.access_token);  // Store JWT token
        }
    })
    .catch(error => console.error("Error during login:", error));
}
