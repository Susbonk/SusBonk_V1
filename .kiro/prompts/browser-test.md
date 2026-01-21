# Browser Automation Test

A prompt for running browser automation tests using `agent-browser`. Use this to test UI flows, verify page states, and automate browser interactions.

## When to Use

- Testing login/authentication flows
- Verifying UI elements and interactions
- Automating form submissions
- Taking screenshots for verification
- E2E testing of web interfaces

## Core Workflow

1. **Navigate to URL**
   ```bash
   agent-browser open <url>
   ```

2. **Get interactive elements snapshot**
   ```bash
   agent-browser snapshot -i --json
   ```
   This returns elements with refs like `@e1`, `@e2` for easy interaction.

3. **Interact with elements using refs**
   ```bash
   agent-browser click @e1
   agent-browser fill @e2 "text value"
   ```

4. **Re-snapshot after page changes**
   ```bash
   agent-browser snapshot -i --json
   ```

## Essential Commands

| Command | Purpose |
|---------|---------|
| `agent-browser open <url>` | Navigate to URL |
| `agent-browser snapshot -i` | Get accessibility tree with element refs |
| `agent-browser click @e1` | Click element by ref |
| `agent-browser fill @e1 "text"` | Fill input with text |
| `agent-browser screenshot` | Take screenshot (base64 to stdout) |
| `agent-browser screenshot path.png` | Save screenshot to file |
| `agent-browser get text @e1` | Get element text content |
| `agent-browser is visible @e1` | Check if element is visible |
| `agent-browser wait --text "Welcome"` | Wait for text to appear |
| `agent-browser close` | Close browser session |

## Instructions

When the user wants to test a browser flow:

1. First confirm the target URL and the test objective
2. Use `agent-browser open <url>` to navigate
3. Use `agent-browser snapshot -i` to understand the page structure
4. Identify target elements using their refs (`@e1`, `@e2`, etc.)
5. Execute interactions step-by-step, re-snapshotting after state changes
6. Use screenshots to verify visual state when needed
7. Report the test results with any issues found

## Tips

- Use `--json` flag for machine-readable output
- The daemon persists between commands for fast operations
- Use `agent-browser wait` before interacting with dynamic content
- For complex selectors: `agent-browser find text "Submit" click`
