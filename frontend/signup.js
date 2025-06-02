document.getElementById('signupForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const username = this.username.value;
    const password = this.password.value;
    const email = this.email.value;
    const is_admin = this.role.value === 'admin';
    const res = await fetch('http://localhost:5000/api/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password, email, is_admin })
    });
    const data = await res.json();
    const msgDiv = document.getElementById('signupMsg');
    if (res.ok) {
        msgDiv.textContent = 'Signup successful! Please check your email to verify.';
    } else {
        msgDiv.textContent = data.error || 'Signup failed.';
    }
});
