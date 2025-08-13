// QR Scanner JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const sessionSelect = document.getElementById('sessionSelect');
    const scannerContainer = document.getElementById('scannerContainer');
    const startScanBtn = document.getElementById('startScanBtn');
    const stopScanBtn = document.getElementById('stopScanBtn');
    const scanNextBtn = document.getElementById('scanNextBtn');
    const scanResults = document.getElementById('scanResults');
    const resultContent = document.getElementById('resultContent');
    const recentRedemptions = document.getElementById('recentRedemptions');

    let html5QrCode = null;
    let isScanning = false;

    // Session selection change
    sessionSelect.addEventListener('change', function() {
        if (this.value) {
            scannerContainer.style.display = 'block';
            startScanBtn.style.display = 'inline-block';
            initializeScanner();
        } else {
            scannerContainer.style.display = 'none';
            stopScanning();
        }
    });

    // Start scanning button
    startScanBtn.addEventListener('click', startScanning);

    // Stop scanning button
    stopScanBtn.addEventListener('click', stopScanning);

    // Scan next button
    scanNextBtn.addEventListener('click', function() {
        scanResults.style.display = 'none';
        scanNextBtn.style.display = 'none';
        startScanning();
    });

    // Initialize scanner
    function initializeScanner() {
        if (html5QrCode) {
            try {
                html5QrCode.clear();
            } catch (e) {
                console.log('Scanner already cleared');
            }
        }
        
        // Check if Html5Qrcode is available
        if (typeof Html5Qrcode === 'undefined') {
            console.error('Html5Qrcode library not loaded');
            showResult('QR Scanner library not loaded. Please refresh the page.', 'danger');
            return;
        }
        
        html5QrCode = new Html5Qrcode("qr-reader");
    }

    // Start scanning
    async function startScanning() {
        if (isScanning) return;

        const selectedSession = sessionSelect.value;
        if (!selectedSession) {
            showResult('Please select a session first', 'danger');
            return;
        }

        // Check if library is loaded
        if (typeof Html5Qrcode === 'undefined') {
            showResult('QR Scanner library not available. Please refresh the page.', 'danger');
            return;
        }

        try {
            const cameras = await Html5Qrcode.getCameras();
            if (cameras && cameras.length > 0) {
                const cameraId = cameras[0].id;
                
                await html5QrCode.start(
                    cameraId,
                    {
                        fps: 10,
                        qrbox: { width: 250, height: 250 }
                    },
                    onScanSuccess,
                    onScanFailure
                );

                isScanning = true;
                startScanBtn.style.display = 'none';
                stopScanBtn.style.display = 'inline-block';
                scanNextBtn.style.display = 'none';
                scanResults.style.display = 'none';
            } else {
                showResult('No cameras found. Please ensure camera access is granted.', 'danger');
            }
        } catch (error) {
            console.error('Error starting scanner:', error);
            showResult('Error starting camera: ' + error.message, 'danger');
        }
    }

    // Stop scanning
    async function stopScanning() {
        if (!isScanning) return;

        try {
            await html5QrCode.stop();
            isScanning = false;
            startScanBtn.style.display = 'inline-block';
            stopScanBtn.style.display = 'none';
        } catch (error) {
            console.error('Error stopping scanner:', error);
        }
    }

    // Handle successful scan
    async function onScanSuccess(decodedText, decodedResult) {
        // Stop scanning immediately
        await stopScanning();

        const selectedSession = sessionSelect.value;

        try {
            const response = await fetch('/api/validate_qr', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    qr_data: decodedText,
                    selected_session: selectedSession
                })
            });

            const result = await response.json();

            if (result.success) {
                showResult(result.message, 'success');
                // Play success sound
                playAudioFeedback('success');
                // Update recent redemptions
                updateRecentRedemptions();
            } else {
                showResult(result.message, 'danger');
                // Play failure sound
                playAudioFeedback('failure');
            }

            // Show scan next button
            scanNextBtn.style.display = 'inline-block';

        } catch (error) {
            console.error('Error validating QR:', error);
            showResult('Error validating QR code', 'danger');
            playAudioFeedback('failure');
            scanNextBtn.style.display = 'inline-block';
        }
    }

    // Handle scan failure
    function onScanFailure(error) {
        // Do nothing on scan failure (camera is still scanning)
    }

    // Show scan result
    function showResult(message, type) {
        resultContent.className = `alert alert-${type}`;
        resultContent.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>
            ${message}
        `;
        scanResults.style.display = 'block';
    }

    // Update recent redemptions
    async function updateRecentRedemptions() {
        try {
            const response = await fetch('/api/get_recent_redemptions');
            const result = await response.json();

            if (result.success) {
                recentRedemptions.innerHTML = '';
                
                if (result.redemptions.length > 0) {
                    result.redemptions.forEach(redemption => {
                        const redemptionItem = document.createElement('div');
                        redemptionItem.className = 'redemption-item mb-3';
                        redemptionItem.innerHTML = `
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <h6 class="mb-1">${redemption.session_name}</h6>
                                    <p class="mb-1 text-muted small">${redemption.participant_email}</p>
                                    <small class="text-muted">${new Date(redemption.redeemed_at).toLocaleTimeString()}</small>
                                </div>
                                <i class="fas fa-check-circle text-success"></i>
                            </div>
                        `;
                        recentRedemptions.appendChild(redemptionItem);
                    });
                } else {
                    recentRedemptions.innerHTML = '<p class="text-muted">No redemptions yet</p>';
                }
            }
        } catch (error) {
            console.error('Error updating recent redemptions:', error);
        }
    }

    // Play audio feedback
    function playAudioFeedback(type) {
        if (typeof playAudio === 'function') {
            playAudio(type);
        }
    }

    // Update recent redemptions every 30 seconds
    setInterval(updateRecentRedemptions, 30000);
});
