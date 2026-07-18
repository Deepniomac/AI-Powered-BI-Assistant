import { apiRequest } from './api.js';
import { showToast, setAuthToken } from './utils.js';

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');

    // Handle Login Form Submission
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const usernameInput = document.getElementById('username');
            const passwordInput = document.getElementById('password');

            const payload = {
                username: usernameInput.value.trim(),
                password: passwordInput.value
            };

            const submitBtn = loginForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Authenticating...';

            try {
                const response = await apiRequest('/login', {
                    method: 'POST',
                    body: JSON.stringify(payload)
                });

                const data = await response.json();

                if (response.ok) {
                    // Cache JWT locally
                    setAuthToken(data.access_token);
                    showToast('Authentication successful! Loading dashboard...', 'success');
                    setTimeout(() => {
                        window.location.href = 'dashboard.html';
                    }, 1000);
                } else {
                    showToast(data.detail || 'Authentication failed. Check your credentials.', 'error');
                }
            } catch (err) {
                showToast('Server connection failed. Verify that backend is online.', 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        });
    }

    // Handle Registration Form Submission
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const usernameInput = document.getElementById('username');
            const emailInput = document.getElementById('email');
            const passwordInput = document.getElementById('password');
            const confirmPasswordInput = document.getElementById('confirm-password');
            const roleSelect = document.getElementById('role');

            if (passwordInput.value !== confirmPasswordInput.value) {
                showToast('Passwords do not match.', 'error');
                return;
            }

            const payload = {
                username: usernameInput.value.trim(),
                email: emailInput.value.trim(),
                password: passwordInput.value,
                role: roleSelect ? roleSelect.value : 'analyst'
            };

            const submitBtn = registerForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Creating Account...';

            try {
                const response = await apiRequest('/register', {
                    method: 'POST',
                    body: JSON.stringify(payload)
                });

                const data = await response.json();

                if (response.ok) {
                    showToast('Registration successful! Redirecting to login.', 'success');
                    setTimeout(() => {
                        window.location.href = 'login.html';
                    }, 1500);
                } else {
                    // Extract structured detail array or simple string message
                    const detail = Array.isArray(data.detail) ? data.detail[0]?.msg : data.detail;
                    showToast(detail || 'Registration failed. Check specifications.', 'error');
                }
            } catch (err) {
                showToast('Server connection failed. Verify that backend is online.', 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        });
    }
});
