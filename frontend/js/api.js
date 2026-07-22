import { getAuthToken, removeAuthToken } from './utils.js';

export const BASE_URL = 'http://127.0.0.1:8000';

function handleUnauthorizedRedirect() {
    removeAuthToken();
    const path = window.location.pathname;
    if (!path.includes('login.html') && !path.includes('register.html') && !path.includes('index.html') && path !== '/') {
        window.location.href = 'login.html';
    }
}

/**
 * Reusable API request client.
 * Automatically sets content headers, injects Authorization token, and manages 401 redirect states.
 */
export async function apiRequest(endpoint, options = {}) {
    const token = getAuthToken();
    const isFormData = options.body instanceof FormData;

    const headers = {
        ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
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
            handleUnauthorizedRedirect();
        }

        return response;
    } catch (error) {
        console.error(`API Fetch Error [${endpoint}]:`, error);
        throw error;
    }
}

export async function getReports() {
    return apiRequest('/api/reports');
}

export async function deleteReport(reportId) {
    return apiRequest(`/api/reports/${reportId}`, {
        method: 'DELETE'
    });
}

export async function getProcessingResult(reportId) {
    return apiRequest(`/api/reports/${reportId}/process`);
}

export async function processReport(reportId) {
    return apiRequest(`/api/reports/${reportId}/process`, {
        method: 'POST'
    });
}

export function uploadReport(file, onProgress = () => {}) {
    return new Promise((resolve, reject) => {
        const token = getAuthToken();
        const xhr = new XMLHttpRequest();
        const formData = new FormData();
        formData.append('file', file);

        xhr.open('POST', `${BASE_URL}/api/upload`);

        if (token) {
            xhr.setRequestHeader('Authorization', `Bearer ${token}`);
        }

        xhr.upload.onprogress = (event) => {
            if (event.lengthComputable) {
                const percent = Math.round((event.loaded / event.total) * 100);
                onProgress(percent);
            }
        };

        xhr.onload = () => {
            let payload = null;
            try {
                payload = xhr.responseText ? JSON.parse(xhr.responseText) : null;
            } catch (error) {
                payload = null;
            }

            if (xhr.status === 401) {
                handleUnauthorizedRedirect();
            }

            if (xhr.status >= 200 && xhr.status < 300) {
                onProgress(100);
                resolve(payload);
                return;
            }

            reject({
                status: xhr.status,
                detail: payload?.detail || 'Upload failed'
            });
        };

        xhr.onerror = () => {
            reject({ status: 0, detail: 'Network error' });
        };

        xhr.send(formData);
    });
}
