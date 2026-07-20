import { apiRequest, deleteReport, getReports, uploadReport } from './api.js';
import { getAuthToken, isTokenExpired, removeAuthToken, showToast } from './utils.js';

const MAX_FILE_SIZE = 100 * 1024 * 1024;
const ALLOWED_EXTENSIONS = ['csv', 'xlsx', 'xls', 'pdf', 'docx'];

let reports = [];
let isUploading = false;

function formatFileSize(bytes) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function formatUploadTime(value) {
    const date = new Date(value);
    return date.toLocaleString();
}

function updateReportMetrics() {
    const countEl = document.getElementById('reports-count');
    const captionEl = document.getElementById('reports-count-caption');

    if (countEl) countEl.textContent = String(reports.length);
    if (!captionEl) return;

    if (reports.length === 0) {
        captionEl.textContent = 'No files uploaded yet';
        return;
    }

    captionEl.textContent = `Latest upload: ${reports[0].original_name}`;
}

function setLoadingState(isLoading) {
    const loadingEl = document.getElementById('reports-loading');
    const emptyEl = document.getElementById('reports-empty');
    const listEl = document.getElementById('reports-list');

    if (loadingEl) loadingEl.classList.toggle('d-none', !isLoading);
    if (isLoading) {
        if (emptyEl) emptyEl.classList.add('d-none');
        if (listEl) listEl.classList.add('d-none');
    }
}

function setUploadProgress(percent) {
    const wrapper = document.getElementById('upload-progress-wrapper');
    const bar = document.getElementById('upload-progress-bar');
    const text = document.getElementById('upload-progress-text');

    if (wrapper) wrapper.classList.remove('d-none');
    if (bar) {
        bar.style.width = `${percent}%`;
        bar.setAttribute('aria-valuenow', String(percent));
    }
    if (text) text.textContent = `${percent}%`;
}

function resetUploadProgress() {
    const wrapper = document.getElementById('upload-progress-wrapper');
    const bar = document.getElementById('upload-progress-bar');
    const text = document.getElementById('upload-progress-text');

    if (wrapper) wrapper.classList.add('d-none');
    if (bar) {
        bar.style.width = '0%';
        bar.setAttribute('aria-valuenow', '0');
    }
    if (text) text.textContent = '0%';
}

function setSelectedFileName(message) {
    const selectedFileEl = document.getElementById('selected-file-name');
    if (selectedFileEl) {
        selectedFileEl.textContent = message;
    }
}

function setUploadBusyState(busy) {
    isUploading = busy;
    const triggerButton = document.getElementById('btn-upload-trigger');
    const chooseButton = document.getElementById('btn-choose-file');
    const dropzone = document.getElementById('upload-dropzone');

    if (triggerButton) triggerButton.disabled = busy;
    if (chooseButton) chooseButton.disabled = busy;
    if (dropzone) dropzone.classList.toggle('is-disabled', busy);
}

function renderReports() {
    const emptyEl = document.getElementById('reports-empty');
    const listEl = document.getElementById('reports-list');

    if (!listEl || !emptyEl) return;

    if (reports.length === 0) {
        emptyEl.classList.remove('d-none');
        listEl.classList.add('d-none');
        listEl.innerHTML = '';
        updateReportMetrics();
        return;
    }

    emptyEl.classList.add('d-none');
    listEl.classList.remove('d-none');
    listEl.innerHTML = reports.map((report) => `
        <article class="report-item">
            <div class="report-item-main">
                <div class="report-item-icon">
                    <i class="bi bi-file-earmark-arrow-up"></i>
                </div>
                <div>
                    <h5>${report.original_name}</h5>
                    <div class="report-item-meta">
                        <span class="badge bg-secondary text-uppercase">${report.file_type}</span>
                        <span>${formatFileSize(report.file_size)}</span>
                        <span>${formatUploadTime(report.upload_time)}</span>
                    </div>
                </div>
            </div>
            <button class="btn btn-outline-danger btn-sm report-delete-btn" data-report-id="${report.id}" type="button">
                <i class="bi bi-trash3 me-1"></i>Delete
            </button>
        </article>
    `).join('');

    updateReportMetrics();
}

async function loadReports(showLoader = true) {
    if (showLoader) {
        setLoadingState(true);
    }

    try {
        const response = await getReports();
        if (!response.ok) {
            const error = await response.json().catch(() => null);
            throw new Error(error?.detail || 'Failed to load reports');
        }

        reports = await response.json();
        renderReports();
    } catch (error) {
        console.error('Failed to load reports:', error);
        showToast(error.message || 'Failed to load reports.', 'error');
    } finally {
        setLoadingState(false);
    }
}

function validateSelectedFile(file) {
    if (!file) {
        showToast('Please choose a file to upload.', 'error');
        return false;
    }

    const extension = file.name.split('.').pop()?.toLowerCase() || '';
    if (!ALLOWED_EXTENSIONS.includes(extension)) {
        showToast('Unsupported file type. Please upload CSV, XLSX, XLS, PDF, or DOCX.', 'error');
        return false;
    }

    if (file.size === 0) {
        showToast('The selected file appears to be empty.', 'error');
        return false;
    }

    if (file.size > MAX_FILE_SIZE) {
        showToast('File exceeds 100MB limit.', 'error');
        return false;
    }

    return true;
}

async function handleFileUpload(file) {
    if (isUploading || !validateSelectedFile(file)) {
        return;
    }

    setUploadBusyState(true);
    setSelectedFileName(`Selected: ${file.name}`);
    setUploadProgress(0);

    try {
        const report = await uploadReport(file, setUploadProgress);
        reports = [report, ...reports];
        renderReports();
        showToast('Report uploaded successfully.', 'success');
        setSelectedFileName(`Uploaded: ${report.original_name}`);
    } catch (error) {
        console.error('Upload failed:', error);

        const messageMap = {
            400: 'File appears to be empty or corrupted.',
            413: 'File exceeds 100MB limit.',
            415: 'Unsupported file type.',
            422: 'Please choose a valid file before uploading.'
        };

        showToast(messageMap[error.status] || error.detail || 'Upload failed.', 'error');
        setSelectedFileName('No file selected');
    } finally {
        setUploadBusyState(false);
        setTimeout(() => {
            resetUploadProgress();
            const input = document.getElementById('report-file-input');
            if (input) input.value = '';
        }, 600);
    }
}

async function handleDeleteReport(reportId) {
    try {
        const response = await deleteReport(reportId);
        if (!response.ok) {
            const error = await response.json().catch(() => null);
            throw new Error(error?.detail || 'Failed to delete report');
        }

        reports = reports.filter((report) => report.id !== reportId);
        renderReports();
        showToast('Report deleted successfully.', 'success');
    } catch (error) {
        console.error('Delete failed:', error);
        showToast(error.message || 'Failed to delete report.', 'error');
    }
}

function bindUploadInteractions() {
    const fileInput = document.getElementById('report-file-input');
    const triggerButton = document.getElementById('btn-upload-trigger');
    const chooseButton = document.getElementById('btn-choose-file');
    const dropzone = document.getElementById('upload-dropzone');
    const refreshButton = document.getElementById('btn-refresh-reports');
    const listEl = document.getElementById('reports-list');

    const openPicker = () => {
        if (!isUploading && fileInput) {
            fileInput.click();
        }
    };

    triggerButton?.addEventListener('click', openPicker);
    chooseButton?.addEventListener('click', openPicker);

    fileInput?.addEventListener('change', async (event) => {
        const [file] = event.target.files || [];
        if (!file) return;
        await handleFileUpload(file);
    });

    dropzone?.addEventListener('click', openPicker);
    dropzone?.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            openPicker();
        }
    });

    ['dragenter', 'dragover'].forEach((eventName) => {
        dropzone?.addEventListener(eventName, (event) => {
            event.preventDefault();
            if (!isUploading) {
                dropzone.classList.add('is-dragover');
            }
        });
    });

    ['dragleave', 'drop'].forEach((eventName) => {
        dropzone?.addEventListener(eventName, (event) => {
            event.preventDefault();
            dropzone.classList.remove('is-dragover');
        });
    });

    dropzone?.addEventListener('drop', async (event) => {
        const [file] = event.dataTransfer?.files || [];
        if (!file) return;
        await handleFileUpload(file);
    });

    refreshButton?.addEventListener('click', () => {
        loadReports(true);
    });

    listEl?.addEventListener('click', async (event) => {
        const deleteButton = event.target.closest('.report-delete-btn');
        if (!deleteButton) return;

        const reportId = Number(deleteButton.dataset.reportId);
        if (!reportId) return;

        deleteButton.disabled = true;
        await handleDeleteReport(reportId);
        deleteButton.disabled = false;
    });
}

document.addEventListener('DOMContentLoaded', async () => {
    const token = getAuthToken();

    if (!token || isTokenExpired(token)) {
        removeAuthToken();
        window.location.href = 'login.html';
        return;
    }

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
                let badgeClass = 'bg-primary';
                if (user.role === 'admin') badgeClass = 'bg-danger';
                else if (user.role === 'executive') badgeClass = 'bg-info';

                userRoleEl.className = `badge ${badgeClass} text-capitalize`;
            }
            if (welcomeNameEl) welcomeNameEl.textContent = user.username;
        } else {
            removeAuthToken();
            window.location.href = 'login.html';
            return;
        }
    } catch (err) {
        console.error('Failed to load user session:', err);
        showToast('Connection to identity server failed.', 'error');
        return;
    }

    bindUploadInteractions();
    await loadReports(true);
});
