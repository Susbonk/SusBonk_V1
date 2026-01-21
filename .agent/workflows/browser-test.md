---
description: Run E2E browser tests using agent-browser CLI
---

# Browser Automation Testing Workflow

Use this workflow to test web UI flows using the `agent-browser` CLI tool.

## Prerequisites

Ensure agent-browser is installed:
```bash
npm install -g agent-browser
agent-browser install  # Download Chromium
```

## Steps

1. **Start a new browser session and navigate to target URL**
   ```bash
   agent-browser open <target_url>
   ```
   Replace `<target_url>` with the URL you want to test (e.g., `http://localhost:5173`)

2. **Take an accessibility snapshot to understand the page**
   ```bash
   agent-browser snapshot -i
   ```
   This returns interactive elements with refs like `@e1`, `@e2` that you can use for interaction.

3. **Interact with elements using refs**
   ```bash
   # Click on an element
   agent-browser click @e1
   
   # Fill a text input
   agent-browser fill @e2 "your text here"
   
   # Wait for dynamic content
   agent-browser wait --text "Expected text"
   ```

4. **Re-snapshot after page state changes**
   ```bash
   agent-browser snapshot -i
   ```
   Always re-snapshot after interactions to get updated element refs.

5. **Verify page state**
   ```bash
   # Check element visibility
   agent-browser is visible @e1
   
   # Get element text
   agent-browser get text @e1
   
   # Get current URL
   agent-browser get url
   ```

6. **Take screenshots for verification**
   ```bash
   # Save to file
   agent-browser screenshot verification.png
   
   # Full page screenshot
   agent-browser screenshot --full full_page.png
   ```

7. **Close the browser when done**
   ```bash
   agent-browser close
   ```

## Common Test Patterns

### Login Flow Test
```bash
agent-browser open http://localhost:5173/login
agent-browser snapshot -i
agent-browser fill @e1 "test@example.com"  # Email field
agent-browser fill @e2 "password123"        # Password field
agent-browser click @e3                     # Login button
agent-browser wait --text "Dashboard"
agent-browser screenshot login_success.png
```

### Form Submission Test
```bash
agent-browser open http://localhost:5173/form
agent-browser snapshot -i
agent-browser find label "Name" fill "John Doe"
agent-browser find label "Email" fill "john@example.com"
agent-browser find text "Submit" click
agent-browser wait --text "Success"
```

## Tips

- Use `--json` flag for machine-readable output: `agent-browser snapshot -i --json`
- The daemon persists between commands for fast operations
- Use semantic locators when possible: `agent-browser find text "Login" click`
- For debugging: `agent-browser eval "console.log(document.title)"`
