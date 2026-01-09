/**
 * Progress tracking for conversion tasks
 */
(function() {
    'use strict';

    // taskId is set in the template
    if (typeof taskId === 'undefined') return;

    var progressFill = document.getElementById('progress-fill');
    var progressText = document.getElementById('progress-text');
    var progressDetail = document.getElementById('progress-detail');
    var progressStatus = document.getElementById('progress-status');
    var errorMessage = document.getElementById('error-message');
    var errorText = document.getElementById('error-text');

    var pollInterval = 1000; // 1 second
    var maxRetries = 300; // 5 minutes max
    var retryCount = 0;

    function pollStatus() {
        fetch('/api/v1/tasks/' + taskId + '/status')
            .then(function(response) {
                if (!response.ok) {
                    throw new Error('Failed to fetch status');
                }
                return response.json();
            })
            .then(function(data) {
                updateProgress(data);

                if (data.status === 'SUCCESS') {
                    // Redirect to result page
                    window.location.href = '/result/' + taskId;
                } else if (data.status === 'FAILURE') {
                    showError(data.error || 'Conversion failed');
                } else if (retryCount < maxRetries) {
                    // Continue polling
                    retryCount++;
                    setTimeout(pollStatus, pollInterval);
                } else {
                    showError('Conversion timed out. Please try again.');
                }
            })
            .catch(function(error) {
                console.error('Polling error:', error);
                if (retryCount < maxRetries) {
                    retryCount++;
                    setTimeout(pollStatus, pollInterval * 2);
                } else {
                    showError('Connection lost. Please refresh the page.');
                }
            });
    }

    function updateProgress(data) {
        var progress = data.progress || 0;
        progressFill.style.width = progress + '%';

        if (data.message) {
            progressText.textContent = data.message;
        }

        if (data.current_sheet) {
            progressDetail.textContent = 'Processing: ' + data.current_sheet;
        } else if (data.total_sheets > 0) {
            progressDetail.textContent = data.total_sheets + ' sheet(s) found';
        }
    }

    function showError(message) {
        progressStatus.style.display = 'none';
        errorMessage.style.display = 'block';
        errorText.textContent = message;
    }

    // Start polling
    pollStatus();
})();
