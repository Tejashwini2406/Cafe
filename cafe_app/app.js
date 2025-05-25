// This file contains the JavaScript code for the application, handling functionality and interactivity.

document.addEventListener('DOMContentLoaded', () => {
    const navLinks = document.querySelectorAll('.top-nav a');

    navLinks.forEach(link => {
        link.addEventListener('click', (event) => {
            event.preventDefault();
            const targetId = link.getAttribute('href').substring(1);
            const targetSection = document.getElementById(targetId);

            if (targetSection) {
                targetSection.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});