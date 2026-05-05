// Configuration
try {
    importScripts('config.js');
} catch (e) {
    console.error('Failed to load config.js', e);
}

const API_URL = (typeof CONFIG !== 'undefined') ? CONFIG.API_URL : 'http://localhost:5000/submit-url';

async function submitUrl(url) {
    const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            url,
            source: 'extension-manual'
        })
    });

    const data = await response.json();
    if (!response.ok || !data.success) {
        throw new Error(data.message || 'Failed to submit URL');
    }
    return data;
}

// Manual submissions from popup only.
// Auto-detection was intentionally removed to reduce permissions and avoid
// reporting URLs without clear user intent.
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'submitUrl') {
        submitUrl(request.url)
            .then(data => sendResponse({ success: true, data }))
            .catch(error => sendResponse({ success: false, error: error.message }));

        return true;
    }
});
