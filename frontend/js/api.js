import { getAuthToken, removeAuthToken } from './utils.js';

export const BASE_URL = 'http://127.0.0.1:8000';

/**
 * Reusable API request client.
 * Automatically sets content headers, injects Authorization token, and manages 401 redirect states.
 */
export async function apiRequest(endpoint, options = {}) {
    const token = getAuthToken();
    
    const headers = {
        'Content-Type': 'application/json',
        ...(options.headers || {})
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const url = `${BASE_URL}${endpoint}`;
    
    try {
        const response = await fetch(url, {
            ...options,
            headers
        });
        
        if (response.status === 401) {
            // Unauthorized - purge expired/invalid credentials and eject to login page
            removeAuthToken();
            const path = window.location.pathname;
            if (!path.includes('login.html') && !path.includes('register.html') && !path.includes('index.html') && path !== '/') {
                window.location.href = 'login.html';
            }
        }
        
        return response;
    } catch (error) {
        console.error(`API Fetch Error [${endpoint}]:`, error);
        throw error;
    }
}
