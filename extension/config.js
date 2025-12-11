// Configuration for Nexus Ignis Extension
const CONFIG = {
    // IMPORTANT: Update this URL with your actual Railway deployment URL
    API_URL: 'https://your-railway-app.up.railway.app/submit-url'

    // After deploying to Railway, change to:
    // API_URL: 'https://nexus-ignis-production.up.railway.app/submit-url'
};

// Export for use in background.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}
