document.addEventListener('DOMContentLoaded', async () => {
    // Orders
    const ordersRes = await fetch('http://localhost:5000/api/admin/orders', { credentials: 'include' });
    const orders = await ordersRes.json();
    document.getElementById('admin-orders-list').innerHTML = orders.map(order => `
        <div class="glass menu-item">
            <h4>Order #${order.id} (${order.status})</h4>
            <ul>${order.items.map(i => `<li>${i.name} x${i.quantity}</li>`).join('')}</ul>
            <div>Total: ₹${order.total}</div>
            <div class="actions">
                <button onclick="updateOrderStatus(${order.id}, 'completed')">Mark Completed</button>
                <button onclick="deleteOrder(${order.id})" style="background:#b71c1c;">Delete</button>
            </div>
        </div>
    `).join('');

    // Payments
    const paymentsRes = await fetch('http://localhost:5000/api/admin/payments', { credentials: 'include' });
    const payments = await paymentsRes.json();
    document.getElementById('admin-payments-list').innerHTML = payments.map(payment => `
        <div class="glass menu-item">
            <h4>Payment #${payment.id} (Order #${payment.order_id})</h4>
            <div>Amount: ₹${payment.amount}</div>
            <div>Status: ${payment.status}</div>
            <div class="actions">
                <button onclick="refundPayment(${payment.id})" style="background:#b71c1c;">Refund</button>
            </div>
        </div>
    `).join('');

    // Suppliers
    const suppliersRes = await fetch('http://localhost:5000/api/admin/suppliers', { credentials: 'include' });
    const suppliers = await suppliersRes.json();
    document.getElementById('admin-suppliers-list').innerHTML = suppliers.map(s => `
        <div class="glass menu-item">
            <h4>${s.name}</h4>
            <div>Contact: ${s.contact_info}</div>
            <div class="actions">
                <button onclick="deleteSupplier(${s.id})" style="background:#b71c1c;">Delete</button>
            </div>
        </div>
    `).join('');

    document.getElementById('admin-suppliers-list').insertAdjacentHTML('beforeend', `
        <form id="addSupplierForm" class="glass menu-item" style="margin-top:2rem;">
            <h4>Add Supplier</h4>
            <input type="text" name="name" placeholder="Supplier Name" required><br>
            <input type="text" name="contact_info" placeholder="Contact Info" required><br>
            <button type="submit">Add Supplier</button>
        </form>
    `);
    document.getElementById('addSupplierForm').onsubmit = async function(e) {
        e.preventDefault();
        const name = this.name.value;
        const contact_info = this.contact_info.value;
        await fetch('http://localhost:5000/api/admin/suppliers', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ name, contact_info })
        });
        location.reload();
    };

    // Inventory
    const inventoryRes = await fetch('http://localhost:5000/api/admin/inventory', { credentials: 'include' });
    const inventory = await inventoryRes.json();
    document.getElementById('admin-inventory-list').innerHTML = inventory.map(i => `
        <div class="glass menu-item">
            <h4>${i.item_name}</h4>
            <div>Quantity: ${i.quantity}</div>
            <div>Supplier: ${i.supplier_name || 'N/A'}</div>
            <div class="actions">
                <button onclick="deleteInventory(${i.id})" style="background:#b71c1c;">Delete</button>
            </div>
        </div>
    `).join('');
    document.getElementById('admin-inventory-list').insertAdjacentHTML('beforeend', `
        <form id="addInventoryForm" class="glass menu-item" style="margin-top:2rem;">
            <h4>Add Inventory Item</h4>
            <input type="text" name="item_name" placeholder="Item Name" required><br>
            <input type="number" name="quantity" placeholder="Quantity" required><br>
            <select name="supplier_id">
                <option value="">Select Supplier</option>
                ${suppliers.map(s => `<option value="${s.id}">${s.name}</option>`).join('')}
            </select><br>
            <button type="submit">Add Item</button>
        </form>
    `);
    document.getElementById('addInventoryForm').onsubmit = async function(e) {
        e.preventDefault();
        const item_name = this.item_name.value;
        const quantity = this.quantity.value;
        const supplier_id = this.supplier_id.value || null;
        await fetch('http://localhost:5000/api/admin/inventory', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ item_name, quantity, supplier_id })
        });
        location.reload();
    };

    // Users
    const usersRes = await fetch('http://localhost:5000/api/admin/users', { credentials: 'include' });
    const users = await usersRes.json();
    document.getElementById('admin-users-list').innerHTML = users.map(u => `
        <div class="glass menu-item">
            <h4>${u.username} (${u.is_admin ? 'Admin' : 'User'})</h4>
            <div>Email: ${u.email}</div>
            <div>Verified: ${u.is_verified ? 'Yes' : 'No'}</div>
            <div class="actions">
                <button onclick="deleteUser(${u.id})" style="background:#b71c1c;">Delete</button>
                <button onclick="toggleAdmin(${u.id}, ${!u.is_admin})" style="background:#6d4c41;">${u.is_admin ? 'Revoke Admin' : 'Make Admin'}</button>
            </div>
        </div>
    `).join('');

    // Add Order (for admin testing/demo)
    document.getElementById('admin-orders-list').insertAdjacentHTML('beforeend', `
        <form id="addOrderForm" class="glass menu-item" style="margin-top:2rem;">
            <h4>Add Order (Demo)</h4>
            <input type="number" name="user_id" placeholder="User ID" required><br>
            <input type="text" name="menu_ids" placeholder="Menu Item IDs (comma separated)" required><br>
            <input type="text" name="quantities" placeholder="Quantities (comma separated)" required><br>
            <button type="submit">Add Order</button>
        </form>
    `);
    document.getElementById('addOrderForm').onsubmit = async function(e) {
        e.preventDefault();
        const user_id = this.user_id.value;
        const menu_ids = this.menu_ids.value.split(',').map(x => x.trim());
        const quantities = this.quantities.value.split(',').map(x => x.trim());
        const items = menu_ids.map((id, i) => ({ menu_id: parseInt(id), quantity: parseInt(quantities[i]) }));
        await fetch('http://localhost:5000/api/admin/orders', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ user_id, items })
        });
        location.reload();
    };
});

// CRUD functions
window.updateOrderStatus = async function(orderId, status) {
    await fetch('http://localhost:5000/api/admin/order_status', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ order_id: orderId, status })
    });
    location.reload();
};
window.deleteOrder = async function(orderId) {
    await fetch('http://localhost:5000/api/admin/orders/' + orderId, {
        method: 'DELETE',
        credentials: 'include'
    });
    location.reload();
};
window.refundPayment = async function(paymentId) {
    await fetch('http://localhost:5000/api/admin/payments/' + paymentId + '/refund', {
        method: 'POST',
        credentials: 'include'
    });
    location.reload();
};
window.deleteSupplier = async function(supplierId) {
    await fetch('http://localhost:5000/api/admin/suppliers/' + supplierId, {
        method: 'DELETE',
        credentials: 'include'
    });
    location.reload();
};
window.deleteInventory = async function(inventoryId) {
    await fetch('http://localhost:5000/api/admin/inventory/' + inventoryId, {
        method: 'DELETE',
        credentials: 'include'
    });
    location.reload();
};
window.deleteUser = async function(userId) {
    await fetch('http://localhost:5000/api/admin/users/' + userId, {
        method: 'DELETE',
        credentials: 'include'
    });
    location.reload();
};
window.toggleAdmin = async function(userId, makeAdmin) {
    await fetch('http://localhost:5000/api/admin/users/' + userId + '/admin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ is_admin: makeAdmin })
    });
    location.reload();
};
