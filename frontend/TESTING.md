# Frontend Testing Guide

## 🧪 Test Login Credentials

**IMPORTANT**: This is a temporary bypass for testing the UI only. No real authentication is happening.

### How to Test

1. **Start the dev server**:
   ```bash
   npm run dev
   ```

2. **Access the app**: Open http://localhost:5173

3. **Login with ANY credentials**:
   - Email: `test@susbonk.com` (or any email)
   - Password: `password` (or anything)
   - Click "LOGIN"

4. **Or Register with ANY credentials**:
   - Email: `test@susbonk.com` (or any email)
   - Username: `testuser` (optional)
   - Password: `password` (or anything)
   - Click "REGISTER"

### What Happens

- ✅ Any email/password combination will "log you in"
- ✅ You'll see the Dashboard with empty states
- ✅ You can navigate between tabs (Dashboard, Logs, Settings)
- ✅ You can click "Logout" in the top-right to return to login

### Test Flow

1. **Login Page** → Enter any credentials → Click LOGIN
2. **Onboarding Page** → Click "SUMMON SUSBONK 🔨"
3. **Dashboard** → See empty states:
   - "Add your first group" dropdown
   - "0 Sus Messages Bonked"
   - Empty moderation rules
4. **Logs Tab** → See sample data with "Sample Data - Real logs coming soon" label
5. **Settings Tab** → See:
   - "Trusted Members" (empty)
   - "Custom Rules" (empty)
6. **Logout** → Click logout button in top-right → Returns to login

### What You'll See

#### Empty States
- ✅ No groups: "Add your first group"
- ✅ No trusted members: "No trusted members yet. Members will appear here when they join your group."
- ✅ No custom rules: "No custom rules yet."
- ✅ Bonk count: 0

#### Sample Data
- ✅ Recent Bonks: Shows 10 sample spam messages with "Sample Data" label

### Logout

Click the "Logout" button in the top-right corner of the Dashboard header to return to the login page.

## 🚨 Important Notes

- **This is NOT real authentication** - it's a UI bypass for testing
- **No data is saved** - refresh the page and you'll be logged out
- **No API calls are made** - everything is client-side only
- **All data is empty** - no groups, users, or prompts are loaded

## 🔧 For Development

The test login is implemented in:
- `src/lib/components/Login.svelte` - Sets authState on any login
- `src/lib/components/Register.svelte` - Sets authState on any registration
- `src/lib/components/DashboardHeader.svelte` - Logout button clears authState

This will be replaced with real API calls in the next phase.
