---
description: Push feature to git with proper branching and dev log follow-up
---

Create a feature branch, commit changes, and ensure proper dev log documentation.

## Git Workflow

### 1. Branch Creation
- Create new branch named after the implemented feature
- Use descriptive, kebab-case naming (e.g., `user-authentication`, `mobile-navigation`)
- Ensure branch is based on latest main/master

### 2. Commit Process
- Stage all relevant changes
- Write clear, descriptive commit message following conventional commits format
- Include context about what was implemented and why

### 3. Push and Documentation
- Push branch to remote repository
- Wait for git hook to trigger dev log update
- Verify dev log entry was added correctly
- Format dev log entry if needed

## Developer Interview

After pushing, conduct a brief interview to gather information for the dev log:

### Technical Questions
- What was the main challenge in implementing this feature?
- What technical decisions did you make and why?
- How long did this feature take to implement?
- What would you do differently next time?

### Context Questions  
- How does this feature fit into the overall product vision?
- What user problem does this solve?
- Are there any dependencies or follow-up tasks needed?
- What testing was performed?

### Development Process
- What tools or resources were most helpful?
- Were there any blockers or unexpected issues?
- How confident are you in the implementation?
- What documentation needs to be updated?

## Dev Log Verification

1. **Wait 30 seconds** for git hook to process
2. **Check DEVLOG.md** for new entry
3. **Verify formatting** matches project standards
4. **Add missing details** from developer interview
5. **Ensure proper structure** with time tracking and technical notes

## Deliverables

- Feature branch created and pushed
- Comprehensive commit message
- Updated dev log with proper formatting
- Developer insights captured for future reference
