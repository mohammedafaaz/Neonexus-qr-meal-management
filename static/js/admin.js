// Admin Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const sessionForm = document.getElementById('sessionForm');
    const qrForm = document.getElementById('qrForm');
    const deleteAllBtn = document.getElementById('deleteAllBtn');
    const selectAllBtn = document.getElementById('selectAllBtn');
    const deselectAllBtn = document.getElementById('deselectAllBtn');
    const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));

    // Session creation form
    sessionForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const sessionName = document.getElementById('sessionName').value.trim();
        if (!sessionName) {
            showAlert('Please enter a session name', 'danger');
            return;
        }

        loadingModal.show();

        try {
            const formData = new FormData();
            formData.append('session_name', sessionName);

            const response = await fetch('/api/create_session', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            loadingModal.hide();

            if (result.success) {
                showAlert(result.message, 'success');
                document.getElementById('sessionName').value = '';
                // Reload page to update sessions list
                setTimeout(() => window.location.reload(), 1000);
            } else {
                showAlert(result.message, 'danger');
            }
        } catch (error) {
            loadingModal.hide();
            showAlert('Error creating session', 'danger');
            console.error('Error:', error);
        }
    });

    // QR code sending form
    qrForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const participantEmail = document.getElementById('participantEmail').value.trim();
        const selectedSessions = Array.from(document.querySelectorAll('.session-checkbox:checked'))
                                      .map(cb => cb.value);

        if (!participantEmail) {
            showAlert('Please enter participant email', 'danger');
            return;
        }

        if (selectedSessions.length === 0) {
            showAlert('Please select at least one session', 'danger');
            return;
        }

        loadingModal.show();

        try {
            const formData = new FormData();
            formData.append('participant_email', participantEmail);
            selectedSessions.forEach(session => {
                formData.append('selected_sessions', session);
            });

            const response = await fetch('/api/send_qr', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            loadingModal.hide();

            if (result.success) {
                showAlert(result.message, 'success');
                document.getElementById('participantEmail').value = '';
                document.querySelectorAll('.session-checkbox').forEach(cb => cb.checked = false);
                // Update statistics
                updateStats();
            } else {
                showAlert(result.message, 'danger');
            }
        } catch (error) {
            loadingModal.hide();
            showAlert('Error sending QR codes', 'danger');
            console.error('Error:', error);
        }
    });

    // Select all sessions
    selectAllBtn.addEventListener('click', function() {
        document.querySelectorAll('.session-checkbox').forEach(cb => cb.checked = true);
    });

    // Deselect all sessions
    deselectAllBtn.addEventListener('click', function() {
        document.querySelectorAll('.session-checkbox').forEach(cb => cb.checked = false);
    });

    // Delete all data
    deleteAllBtn.addEventListener('click', function() {
        if (confirm('Are you sure you want to delete ALL sessions and statistics? This action cannot be undone!')) {
            deleteAllData();
        }
    });

    // Update statistics
    async function updateStats() {
        try {
            const response = await fetch('/api/get_stats');
            const result = await response.json();

            if (result.success) {
                document.getElementById('stat-total').textContent = result.stats.total;
                document.getElementById('stat-redeemed').textContent = result.stats.redeemed;
                document.getElementById('stat-remaining').textContent = result.stats.remaining;
            }
        } catch (error) {
            console.error('Error updating stats:', error);
        }
    }

    // Delete all data
    async function deleteAllData() {
        loadingModal.show();

        try {
            const response = await fetch('/api/delete_all', {
                method: 'POST'
            });

            const result = await response.json();
            loadingModal.hide();

            if (result.success) {
                showAlert(result.message, 'success');
                // Reload page after delay
                setTimeout(() => window.location.reload(), 1000);
            } else {
                showAlert(result.message, 'danger');
            }
        } catch (error) {
            loadingModal.hide();
            showAlert('Error deleting data', 'danger');
            console.error('Error:', error);
        }
    }

    // Show alert message
    function showAlert(message, type) {
        // Remove existing alerts
        const existingAlerts = document.querySelectorAll('.alert-auto');
        existingAlerts.forEach(alert => alert.remove());

        // Create new alert
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show alert-auto`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Insert at top of container
        const container = document.querySelector('.container');
        container.insertBefore(alert, container.firstChild);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }

    // Update stats every 30 seconds
    setInterval(updateStats, 30000);
});
