---
description: Compare code against steering documents and latest practices using Context7 MCP
---

Analyze the current codebase for discrepancies between implementation, steering documents, and modern coding practices.

## Analysis Framework

### 1. Steering Document Compliance
- Review all `.kiro/steering/` documents for project standards
- Compare current code against defined patterns and conventions
- Identify deviations from established architecture decisions
- Check adherence to coding standards and style guides

### 2. Context7 MCP Integration
- Query Context7 for latest best practices in the current tech stack
- Compare current implementation with modern patterns
- Identify outdated approaches or deprecated methods
- Find opportunities for improvement using current standards

### 3. Code Quality Assessment
- **Architecture**: Does code follow defined patterns?
- **Security**: Are security best practices implemented?
- **Performance**: Any obvious performance issues?
- **Maintainability**: Is code readable and well-structured?
- **Testing**: Adequate test coverage and quality?

## Output Format

### Discrepancies Found

#### Steering Document Violations
- **File**: `path/to/file.js`
- **Issue**: Brief description of the problem
- **Expected**: What the steering document specifies
- **Actual**: What the code currently does
- **Recommendation**: Specific fix or improvement

#### Modern Practice Gaps
- **Area**: Technology/pattern area (e.g., "State Management", "API Design")
- **Current Approach**: What we're doing now
- **Modern Standard**: What Context7/latest practices recommend
- **Impact**: Why this matters (performance, security, maintainability)
- **Action**: Specific steps to modernize

### Summary Report
- **Total Issues**: Count of discrepancies found
- **Priority Levels**: High/Medium/Low classification
- **Effort Estimate**: Time needed for fixes
- **Next Steps**: Prioritized action items
