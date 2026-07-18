import { apiRequest } from './api.js';
import { getAuthToken, isTokenExpired, removeAuthToken, showToast } from './utils.js';

document.addEventListener('DOMContentLoaded', async () => {
    const token = getAuthToken();

    // Page Authentication Gatekeeper
    if (!token || isTokenExpired(token)) {
        removeAuthToken();
        window.location.href = 'login.html';
        return;
    }

    // Bind Logout Interaction
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            removeAuthToken();
            showToast('Logged out successfully.', 'success');
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 800);
        });
    }

    // Retrieve and Populate Current User Details from /me
    try {
        const response = await apiRequest('/me');
        if (response.ok) {
            const user = await response.json();
            
            const userUsernameEl = document.getElementById('user-username');
            const userRoleEl = document.getElementById('user-role');
            const welcomeNameEl = document.getElementById('welcome-name');

            if (userUsernameEl) userUsernameEl.textContent = user.username;
            if (userRoleEl) {
                userRoleEl.textContent = user.role;
                // Dynamically class user badges
                let badgeClass = 'bg-primary';
                if (user.role === 'admin') badgeClass = 'bg-danger';
                else if (user.role === 'executive') badgeClass = 'bg-info text-dark';
                
                userRoleEl.className = `badge ${badgeClass} text-capitalize`;
            }
            if (welcomeNameEl) welcomeNameEl.textContent = user.username;
        } else {
            removeAuthToken();
            window.location.href = 'login.html';
        }
    } catch (err) {
        console.error('Failed to load user session:', err);
        showToast('Connection to identity server failed.', 'error');
    }
});
