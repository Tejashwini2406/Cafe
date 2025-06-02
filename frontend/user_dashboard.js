document.addEventListener('DOMContentLoaded', async () => {
    // Fetch and display user's orders
    const res = await fetch('http://localhost:5000/api/my_orders', { credentials: 'include' });
    const orders = await res.json();
    const ordersList = document.getElementById('orders-list');
    if (orders.length === 0) {
        ordersList.textContent = 'No orders yet.';
    } else {
        ordersList.innerHTML = orders.map(order => `
            <div class="glass menu-item">
                <h4>Order #${order.id} (${order.status})</h4>
                <ul>${order.items.map(i => `<li>${i.name} x${i.quantity}</li>`).join('')}</ul>
                <div>Total: ₹${order.total}</div>
            </div>
        `).join('');
    }
});

document.getElementById('feedbackForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const message = this.message.value;
    const rating = this.rating.value;
    const res = await fetch('http://localhost:5000/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ message, rating })
    });
    const data = await res.json();
    const msgDiv = document.getElementById('feedbackMsg');
    if (res.ok) {
        msgDiv.textContent = 'Thank you for your feedback!';
        this.reset();
    } else {
        msgDiv.textContent = data.error || 'Failed to submit feedback.';
    }
});
