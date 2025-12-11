// Configuration
try {
    importScripts('config.js');
} catch (e) {
    console.error("Failed to load config.js", e);
}

const API_URL = (typeof CONFIG !== 'undefined') ? CONFIG.API_URL : 'http://localhost:5000/submit-url';

// Background service worker for detecting 404 pages
chrome.webNavigation.onCompleted.addListener(async (details) => {
    // Only process main frame (not iframes)
    if (details.frameId !== 0) return;

    try {
        // Inject content script to check HTTP status
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        if (!tab || tab.id !== details.tabId) return;

        // Check for common 404 indicators in the title and body
        chrome.scripting.executeScript({
            target: { tabId: details.tabId },
            func: detectDeadPage,
            args: [details.url]
        });
    } catch (error) {
        console.error('Error in background script:', error);
    }
});

// Function to be injected into page
function detectDeadPage(currentUrl) {
    const title = document.title.toLowerCase();
    const bodyText = document.body.innerText.toLowerCase();

    // Common 404 indicators
    const indicators = [
        '404',
        'not found',
        'page not found',
        'tidak ditemukan',
        'halaman tidak ditemukan',
        'error 404',
        'page doesn\'t exist',
        'content not available'
    ];

    // Check if page contains 404 indicators
    const is404 = indicators.some(indicator =>
        title.includes(indicator) || bodyText.includes(indicator)
    );

    if (is404) {
        // Send URL to Nexus Ignis API
        fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: currentUrl,
                source: 'extension'
            })
        })
            .then(response => response.json())
            .then(data => {
                console.log('Nexus Ignis: Dead URL reported -', currentUrl);
                // Show notification (optional)
                chrome.notifications.create({
                    type: 'basic',
                    iconUrl: 'icon48.png',
                    title: 'Nexus Ignis',
                    message: '404 page detected and reported!'
                });
            })
            .catch(error => {
                console.error('Failed to report to Nexus Ignis:', error);
            });
    }
}

// Listen for manual submissions from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'submitUrl') {
        fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: request.url,
                source: 'extension'
            })
        })
            .then(response => response.json())
            .then(data => {
                sendResponse({ success: true, data: data });
            })
            .catch(error => {
                sendResponse({ success: false, error: error.message });
            });

        return true; // Keep channel open for async response
    }
});
