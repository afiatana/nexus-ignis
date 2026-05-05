# Nexus Ignis Browser Extension Privacy Policy

Nexus Ignis Dead Link Hunter is a manual browser extension for reporting dead links to the Nexus Ignis archive search system.

## Data Sent

The extension sends only the URL you manually submit by clicking **REPORT DEAD LINK**.

Payload example:

```json
{
  "url": "https://example.com/dead-page",
  "source": "extension-manual"
}
```

## Data Not Collected

The extension does not collect:

- browsing history;
- page content;
- cookies;
- login credentials;
- personal form data;
- screenshots;
- keystrokes;
- analytics identifiers.

## Manual-Only Mode

Automatic 404 detection has been removed. The extension submits a URL only when the user explicitly clicks the submit button.

## Permissions

The extension uses minimal permissions:

- `activeTab`: used to prefill the current tab URL in the popup.

The extension does not request `<all_urls>`, `webNavigation`, `scripting`, or notification permissions.

## Server-Side Protection

The Nexus Ignis server validates submitted URLs and rejects localhost, private IP, link-local IP, reserved IP, and unsupported schemes to reduce abuse and SSRF risk.

## Contact

For privacy or security concerns, open a GitHub issue without sensitive details, or contact the repository owner privately through GitHub profile information.
