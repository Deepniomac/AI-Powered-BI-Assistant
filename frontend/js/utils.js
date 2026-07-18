/**
 * Parse JWT token string and decode its payload safely.
 */
export function parseJwt(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        return JSON.parse(jsonPayload);
    } catch (e) {
        return null;
    }
}

/**
 * Checks if a JWT token is expired based on its 'exp' field.
 */
export function isTokenExpired(token) {
    const payload = parseJwt(token);
    if (!payload || !payload.exp) return true;
    const now = Math.floor(Date.now() / 1000);
    return payload.exp < now;
}

/**
 * Renders a premium dynamic alert/toast in the upper-right corner.
 */
export function showToast(message, type = 'success') {
    const existing = document.querySelector('.custom-alert');
    if (existing) {
        existing.remove();
    }

    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} custom-alert shadow-lg glass-card text-light`;
    alertDiv.setAttribute('role', 'alert');
    
    const borderColor = type === 'error' ? '#f87171' : '#34d399';
    alertDiv.style.borderLeft = `4px solid ${borderColor}`;
    alertDiv.style.background = 'rgba(17, 24, 39, 0.95)';
    alertDiv.style.backdropFilter = 'blur(10px)';
    
    alertDiv.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="bi ${type === 'error' ? 'bi-exclamation-triangle-fill text-danger' : 'bi-check-circle-fill text-success'} me-3 fs-5"></i>
            <div style="font-weight: 500;">${message}</div>
        </div>
    `;

    document.body.appendChild(alertDiv);

    // Fade out and remove after 4 seconds
    setTimeout(() => {
        alertDiv.style.opacity = '0';
        alertDiv.style.transition = 'opacity 0.5s ease-out';
        setTimeout(() => alertDiv.remove(), 500);
    }, 4000);
}

/**
 * Retrieves authentication token from local storage.
 */
export function getAuthToken() {
    return localStorage.getItem('token');
}

/**
 * Sets authentication token in local storage.
 */
export function setAuthToken(token) {
    localStorage.setItem('token', token);
}

/**
 * Removes authentication token from local storage.
 */
export function removeAuthToken() {
    localStorage.removeItem('token');
}
