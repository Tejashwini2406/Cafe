document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const username = this.username.value;
    const password = this.password.value;
    const role = this.role.value;
    const res = await fetch('http://localhost:5000/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password, role })
    });
    const data = await res.json();
    const msgDiv = document.getElementById('loginMsg');
    if (res.ok) {
        msgDiv.textContent = 'Login successful!';
        // Redirect based on role
        setTimeout(() => {
            if (data.is_admin) {
                window.location.href = 'admin_dashboard.html';
            } else {
                window.location.href = 'user_dashboard.html';
            }
        }, 800);
    } else {
        msgDiv.textContent = data.error || 'Login failed.';
    }
});
