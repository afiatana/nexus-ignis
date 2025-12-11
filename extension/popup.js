document.getElementById('submitBtn').addEventListener('click', async () => {
    const urlInput = document.getElementById('urlInput');
    const statusDiv = document.getElementById('status');
    const url = urlInput.value.trim();

    if (!url) {
        statusDiv.textContent = 'Please enter a URL';
        statusDiv.style.borderColor = '#ff0000';
        return;
    }

    // Validate URL format
    try {
        new URL(url);
    } catch (e) {
        statusDiv.textContent = 'Invalid URL format';
        statusDiv.style.borderColor = '#ff0000';
        return;
    }

    statusDiv.textContent = 'Submitting...';
    statusDiv.style.borderColor = '#ffaa00';

    // Send to background script
    chrome.runtime.sendMessage(
        { action: 'submitUrl', url: url },
        (response) => {
            if (response && response.success) {
                statusDiv.textContent = '✓ URL Reported Successfully!';
                statusDiv.style.borderColor = '#00ff41';
                urlInput.value = '';

                setTimeout(() => {
                    statusDiv.textContent = 'Dead Link Hunter Active';
                    statusDiv.style.borderColor = '#ffb000';
                }, 3000);
            } else {
                statusDiv.textContent = 'Error: ' + (response?.error || 'Failed to submit');
                statusDiv.style.borderColor = '#ff0000';
            }
        }
    );
});

// Get current tab URL and populate input
chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (tabs[0]) {
        const currentUrl = tabs[0].url;
        // Only populate if it's a http/https URL
        if (currentUrl.startsWith('http')) {
            document.getElementById('urlInput').value = currentUrl;
        }
    }
});
