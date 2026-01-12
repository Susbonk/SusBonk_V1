# Product Overview

## Product Purpose
SusBonk is an easy-to-use web application that blocks spammers and scammers in Telegram and other group chat platforms. It provides granular control through an extensive dashboard while maintaining simplicity for non-technical users. The friendly "doggo bot" automatically handles moderation, letting group communities flourish without spam disruption.

## Target Users
**Primary Users**: Telegram group moderators and owners who are non-technical but frustrated with spam and scam flooding their communities.

**User Needs**:
- Simple "fire and forget" spam protection that works automatically
- Some control over what content gets blocked without technical complexity
- Clean, intuitive dashboard to monitor and adjust settings
- Reliable protection that doesn't interfere with legitimate group activity
- Peace of mind that their community is protected from bad actors

## Key Features
- **Automated Spam Detection**: AI-powered detection of spam and scam messages
- **Unified Logging Platform**: Centralized log ingestion and monitoring with OpenSearch
- **Real-time Monitoring**: Live view of system health and spam detection activity
- **Telegram Bot Integration**: Easy bot setup for Telegram groups
- **User-Friendly Dashboard**: Intuitive web interface for non-technical users
- **Granular Control Settings**: Adjustable sensitivity and blocking rules
- **Whitelist/Blacklist Management**: Easy user and keyword management
- **Activity Reports**: Analytics on group protection effectiveness via OpenSearch Dashboards
- **Multi-Platform Support**: Extensible to other chat platforms beyond Telegram

## Current Implementation Status
**Completed**:
- Unified Rust logging platform with shared types
- HTTP log ingestion service (ingestd) with bulk indexing
- Spam detection and monitoring service (alertd)
- OpenSearch integration with ECS-compliant schema
- Daily index rotation with 7-day retention policy
- Docker Compose orchestration with health checks
- Redis Streams Producer/Worker prototype
- Svelte frontend dashboard with persistent bottom nav
- UI design system with reusable components
- Whitelist management modal
- Collapsible moderation sections

**In Progress**:
- Backend API integration with frontend
- Custom Kiro CLI workflow prompts for testing and deployment

**Planned**:
- Telegram bot integration
- PostgreSQL for user settings and configurations
- Real-time data flow from backend to dashboard

## Business Objectives
- **User Satisfaction**: Provide effective spam protection without complexity
- **Community Growth**: Help Telegram groups grow by maintaining quality discussions
- **Platform Expansion**: Scale to support multiple chat platforms
- **Reliability**: Maintain 99%+ uptime for critical community protection

## User Journey
1. **Setup**: User adds SusBonk bot to their Telegram group
2. **Configuration**: User accesses web dashboard to set basic preferences
3. **Monitoring**: User occasionally checks dashboard to see bot activity
4. **Adjustment**: User fine-tunes settings based on group needs
5. **Maintenance**: Minimal ongoing management as bot learns group patterns

## Success Criteria
- **Spam Reduction**: 95%+ reduction in spam/scam messages reaching groups
- **User Retention**: Users continue using the service after initial setup
- **False Positive Rate**: Less than 2% legitimate messages blocked
- **User Satisfaction**: High ratings for ease of use and effectiveness
- **Community Health**: Increased legitimate user engagement in protected groups
