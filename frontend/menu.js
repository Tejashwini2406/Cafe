document.addEventListener('DOMContentLoaded', async () => {
    const menuList = document.getElementById('menu-list');
    const res = await fetch('http://localhost:5000/api/menu');
    const menu = await res.json();
    menuList.innerHTML = menu.map(item => `
        <div class="glass menu-item">
            <img src="${item.image_url || 'https://placehold.co/100x100?text=☕'}" alt="${item.name}" class="cute-img" style="width:100px;">
            <h3>${item.name}</h3>
            <p>${item.description}</p>
            <div class="price">₹${item.price}</div>
            <button>Add to Order</button>
        </div>
    `).join('');
});
