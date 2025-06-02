document.addEventListener('DOMContentLoaded', async () => {
    // Fetch and display users
    const res = await fetch('http://localhost:5000/api/admin/users', { credentials: 'include' });
    const users = await res.json();
    const userList = document.getElementById('user-list');
    userList.innerHTML = users.map(u => `
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
});

document.getElementById('addUserForm').onsubmit = async function(e) {
    e.preventDefault();
    const username = this.username.value;
    const password = this.password.value;
    const email = this.email.value;
    const is_admin = this.is_admin.value === '1';
    await fetch('http://localhost:5000/api/admin/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ username, password, email, is_admin })
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
