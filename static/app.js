// API Configuration
const API_BASE = 'http://127.0.0.1:8001';

// Global State
let selectedFiles = [];
let dashboardData = null;

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    checkAPIStatus();
    loadDashboard();
    setInterval(checkAPIStatus, 30000); // Check every 30s
});

// Navigation
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const page = item.dataset.page;
            switchPage(page);
            
            // Update active state
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
        });
    });
}

function switchPage(pageName) {
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => page.classList.remove('active'));
    
    const targetPage = document.getElementById(`${pageName}-page`);
    if (targetPage) {
        targetPage.classList.add('active');
        
        // Load page-specific data
        if (pageName === 'dashboard') loadDashboard();
        if (pageName === 'patients') loadPatients();
    }
}

// API Status Check
async function checkAPIStatus() {
    const statusDot = document.getElementById('apiStatus');
    try {
        const response = await fetch(`${API_BASE}/health`);
        if (response.ok) {
            statusDot.classList.remove('offline');
        } else {
            statusDot.classList.add('offline');
        }
    } catch (error) {
        statusDot.classList.add('offline');
    }
}

// Dashboard Functions
async function loadDashboard() {
    try {
        const response = await fetch(`${API_BASE}/api/stats`);
        const data = await response.json();
        dashboardData = data;
        
        // Update stats cards
        document.getElementById('totalPatients').textContent = data.total_patients || 0;
        document.getElementById('totalTests').textContent = data.total_tests || 0;
        document.getElementById('abnormalTests').textContent = data.abnormal_count || 0;
        document.getElementById('testTypes').textContent = data.unique_tests || 0;
        
        // Load charts
        loadTestDistributionChart(data.test_distribution || {});
        loadAbnormalChart(data.abnormal_by_test || {});
        
        // Load recent activity
        loadRecentActivity();
    } catch (error) {
        console.error('Failed to load dashboard:', error);
        showError('Failed to load dashboard data');
    }
}

function loadTestDistributionChart(data) {
    const ctx = document.getElementById('testDistributionChart');
    const labels = Object.keys(data).slice(0, 10);
    const values = Object.values(data).slice(0, 10);
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels.map(l => l.replace('_', ' ')),
            datasets: [{
                data: values,
                backgroundColor: [
                    '#6366f1', '#8b5cf6', '#ec4899', '#f43f5e',
                    '#f59e0b', '#10b981', '#3b82f6', '#06b6d4',
                    '#8b5cf6', '#d946ef'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: { color: '#94a3b8', font: { size: 11 } }
                }
            }
        }
    });
}

function loadAbnormalChart(data) {
    const ctx = document.getElementById('abnormalChart');
    const labels = Object.keys(data).slice(0, 8);
    const values = Object.values(data).slice(0, 8);
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels.map(l => l.replace('_', ' ')),
            datasets: [{
                label: 'Abnormal Results',
                data: values,
                backgroundColor: 'rgba(239, 68, 68, 0.8)',
                borderColor: 'rgba(239, 68, 68, 1)',
                borderWidth: 1,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: '#334155' },
                    ticks: { color: '#94a3b8' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8', font: { size: 10 } }
                }
            }
        }
    });
}

async function loadRecentActivity() {
    const container = document.getElementById('recentActivity');
    try {
        const response = await fetch(`${API_BASE}/api/recent-abnormal?limit=10`);
        const data = await response.json();
        
        if (data.results && data.results.length > 0) {
            container.innerHTML = data.results.map(item => `
                <div class="activity-item ${item.abnormal_direction.toLowerCase()}">
                    <div class="activity-icon">
                        <i class="fas fa-exclamation-triangle"></i>
                    </div>
                    <div class="activity-details">
                        <h4>${item.patient_name}</h4>
                        <p>${item.canonical_test.replace(/_/g, ' ')} - ${item.abnormal_direction}</p>
                    </div>
                    <div class="activity-value">
                        <div class="value">${item.value} ${item.unit || ''}</div>
                        <div class="reference">Normal: ${item.reference_min}-${item.reference_max}</div>
                    </div>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">No recent abnormal results</p>';
        }
    } catch (error) {
        console.error('Failed to load activity:', error);
        container.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">Failed to load data</p>';
    }
}

function refreshDashboard() {
    const btn = event.target.closest('button');
    btn.innerHTML = '<i class="fas fa-sync-alt fa-spin"></i> Refreshing...';
    loadDashboard().finally(() => {
        btn.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh';
    });
}

// Chat Functions
function sendSuggestion(text) {
    document.getElementById('chatInput').value = text;
    sendMessage();
}

function handleChatKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

async function sendMessage() {
    const input = document.getElementById('chatInput');
    const query = input.value.trim();
    
    if (!query) return;
    
    // Add user message
    addChatMessage(query, 'user');
    input.value = '';
    
    // Show typing indicator
    const typingId = addTypingIndicator();
    
    try {
        const response = await fetch(`${API_BASE}/api/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator(typingId);
        
        // Add bot response
        if (data.success && data.message) {
            addChatMessage(data.message, 'bot');
        } else {
            addChatMessage(data.message || 'Sorry, I encountered an error processing your request.', 'bot');
        }
    } catch (error) {
        removeTypingIndicator(typingId);
        addChatMessage('Sorry, I cannot connect to the server. Please check if the API is running.', 'bot');
    }
}

function addChatMessage(text, type) {
    const container = document.getElementById('chatMessages');
    const welcome = container.querySelector('.welcome-message');
    if (welcome) welcome.remove();
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    messageDiv.innerHTML = `
        <div class="message-content">
            ${text.replace(/\n/g, '<br>')}
            <div class="message-time">${time}</div>
        </div>
    `;
    
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}

function addTypingIndicator() {
    const container = document.getElementById('chatMessages');
    const id = 'typing-' + Date.now();
    
    const messageDiv = document.createElement('div');
    messageDiv.id = id;
    messageDiv.className = 'message bot';
    messageDiv.innerHTML = `
        <div class="message-content">
            <i class="fas fa-spinner fa-spin"></i> Thinking...
        </div>
    `;
    
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
    
    return id;
}

function removeTypingIndicator(id) {
    const element = document.getElementById(id);
    if (element) element.remove();
}

function clearChat() {
    const container = document.getElementById('chatMessages');
    container.innerHTML = `
        <div class="welcome-message">
            <i class="fas fa-robot"></i>
            <h3>Hello! I'm LabAssist AI</h3>
            <p>Ask me anything about your lab reports:</p>
            <div class="suggestion-chips">
                <button class="chip" onclick="sendSuggestion(this.textContent)">Show patients with low hemoglobin</button>
                <button class="chip" onclick="sendSuggestion(this.textContent)">Who has abnormal WBC?</button>
                <button class="chip" onclick="sendSuggestion(this.textContent)">Show hemoglobin trend for Renuka</button>
                <button class="chip" onclick="sendSuggestion(this.textContent)">List all CBC reports</button>
            </div>
        </div>
    `;
}

// Upload Functions
function handleDragOver(event) {
    event.preventDefault();
    event.currentTarget.classList.add('drag-over');
}

function handleDragLeave(event) {
    event.currentTarget.classList.remove('drag-over');
}

function handleDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('drag-over');
    
    const files = Array.from(event.dataTransfer.files).filter(f => f.type.startsWith('image/'));
    if (files.length > 0) {
        handleFiles(files);
    }
}

function handleFiles(files) {
    selectedFiles = Array.from(files);
    displayPreview();
}

function displayPreview() {
    const previewSection = document.getElementById('uploadPreview');
    const grid = document.getElementById('previewGrid');
    
    grid.innerHTML = '';
    
    selectedFiles.forEach((file, index) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const item = document.createElement('div');
            item.className = 'preview-item';
            item.innerHTML = `
                <img src="${e.target.result}" alt="${file.name}">
                <button class="remove-btn" onclick="removeFile(${index})">
                    <i class="fas fa-times"></i>
                </button>
            `;
            grid.appendChild(item);
        };
        reader.readAsDataURL(file);
    });
    
    previewSection.style.display = selectedFiles.length > 0 ? 'block' : 'none';
}

function removeFile(index) {
    selectedFiles.splice(index, 1);
    displayPreview();
}

function clearUpload() {
    selectedFiles = [];
    document.getElementById('uploadPreview').style.display = 'none';
    document.getElementById('fileInput').value = '';
}

async function uploadFiles() {
    if (selectedFiles.length === 0) return;
    
    const progressSection = document.getElementById('uploadProgress');
    const resultsSection = document.getElementById('uploadResults');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const progressStatus = document.getElementById('progressStatus');
    
    // Hide preview, show progress
    document.getElementById('uploadPreview').style.display = 'none';
    progressSection.style.display = 'block';
    resultsSection.innerHTML = '';
    
    let completed = 0;
    const total = selectedFiles.length;
    const results = [];
    
    for (const file of selectedFiles) {
        progressStatus.textContent = `Processing ${file.name}...`;
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch(`${API_BASE}/api/ocr/upload`, {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            results.push({ file: file.name, success: data.success, message: data.message || 'Processed successfully' });
        } catch (error) {
            results.push({ file: file.name, success: false, message: 'Upload failed: ' + error.message });
        }
        
        completed++;
        const percent = Math.round((completed / total) * 100);
        progressFill.style.width = percent + '%';
        progressText.textContent = percent + '%';
    }
    
    // Show results
    progressStatus.textContent = 'All files processed!';
    setTimeout(() => {
        progressSection.style.display = 'none';
        displayResults(results);
        clearUpload();
    }, 1000);
}

function displayResults(results) {
    const resultsSection = document.getElementById('uploadResults');
    
    resultsSection.innerHTML = `
        <h3 style="margin-bottom: 15px;">Upload Results</h3>
        ${results.map(r => `
            <div class="result-item ${r.success ? 'success' : 'error'}">
                <div class="result-icon">
                    <i class="fas fa-${r.success ? 'check-circle' : 'times-circle'}"></i>
                </div>
                <div>
                    <strong>${r.file}</strong><br>
                    <span style="color: var(--text-secondary); font-size: 13px;">${r.message}</span>
                </div>
            </div>
        `).join('')}
    `;
}

// Patients Functions
async function loadPatients() {
    const tbody = document.getElementById('patientsTableBody');
    
    try {
        const response = await fetch(`${API_BASE}/api/patients`);
        const data = await response.json();
        
        if (data.patients && data.patients.length > 0) {
            tbody.innerHTML = data.patients.map(patient => `
                <tr>
                    <td><strong>${patient.name}</strong></td>
                    <td>${patient.age || 'N/A'}</td>
                    <td>${patient.gender || 'N/A'}</td>
                    <td>${patient.test_count || 0}</td>
                    <td>${patient.latest_test || 'N/A'}</td>
                    <td>
                        <span class="status-badge ${patient.has_abnormal ? 'abnormal' : 'normal'}">
                            ${patient.has_abnormal ? 'Has Abnormal' : 'Normal'}
                        </span>
                    </td>
                    <td>
                        <button class="action-btn" onclick="viewPatient('${patient.name}')">
                            <i class="fas fa-eye"></i> View
                        </button>
                    </td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="7" class="loading-cell">No patients found</td></tr>';
        }
    } catch (error) {
        tbody.innerHTML = '<tr><td colspan="7" class="loading-cell">Failed to load patients</td></tr>';
    }
}

function searchPatients(query) {
    const rows = document.querySelectorAll('.patients-table tbody tr');
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(query.toLowerCase()) ? '' : 'none';
    });
}

async function viewPatient(patientName) {
    const modal = document.getElementById('patientModal');
    const modalBody = document.getElementById('modalBody');
    const modalTitle = document.getElementById('modalPatientName');
    
    modalTitle.textContent = patientName;
    modalBody.innerHTML = '<div class="loading-spinner"><i class="fas fa-spinner fa-spin"></i></div>';
    modal.classList.add('active');
    
    try {
        const response = await fetch(`${API_BASE}/api/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: `Show all tests for ${patientName}` })
        });
        
        const data = await response.json();
        
        if (data.success && data.data) {
            const tests = data.data;
            modalBody.innerHTML = `
                <div style="margin-bottom: 20px;">
                    <p><strong>Total Tests:</strong> ${tests.length}</p>
                    <p><strong>Abnormal Results:</strong> ${tests.filter(t => t.is_abnormal).length}</p>
                </div>
                <h4 style="margin-bottom: 15px;">Test Results</h4>
                ${tests.map(test => `
                    <div class="activity-item ${test.abnormal_direction?.toLowerCase() || ''}">
                        <div class="activity-details">
                            <h4>${test.canonical_test.replace(/_/g, ' ')}</h4>
                            <p>${test.report_date ? new Date(test.report_date).toLocaleDateString() : 'Date not available'}</p>
                        </div>
                        <div class="activity-value">
                            <div class="value" style="color: ${test.is_abnormal ? 'var(--danger-color)' : 'var(--success-color)'}">
                                ${test.value} ${test.unit || ''}
                            </div>
                            <div class="reference">Normal: ${test.reference_min}-${test.reference_max}</div>
                        </div>
                    </div>
                `).join('')}
            `;
        } else {
            modalBody.innerHTML = '<p>No test results found for this patient.</p>';
        }
    } catch (error) {
        modalBody.innerHTML = '<p>Failed to load patient data.</p>';
    }
}

function closePatientModal() {
    document.getElementById('patientModal').classList.remove('active');
}

// Utility Functions
function showError(message) {
    console.error(message);
    // You can add a toast notification here
}

// Close modal on outside click
document.getElementById('patientModal')?.addEventListener('click', (e) => {
    if (e.target.id === 'patientModal') {
        closePatientModal();
    }
});
