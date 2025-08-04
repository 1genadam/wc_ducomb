# Knowledge Base Index

This repository serves as a comprehensive knowledge base for IBM i systems, automation, and customer applications. Each document is designed to be self-contained and transferable across Claude chat sessions.

## Document Structure

### /readme/
- **index.md** - This file - master index of all knowledge base documents
- **ibm-i-acs-overview.md** - IBM i Access Client Solutions comprehensive guide
- **ibm-i-ssh-setup.md** - SSH server setup and configuration guide
- **session-continuity.md** - Guidelines for maintaining context across Claude sessions

### Document Categories

#### IBM i Systems
- [IBM i Access Client Solutions Overview](ibm-i-acs-overview.md) - Complete guide to ACS features and capabilities
- [IBM i SSH Setup Guide](ibm-i-ssh-setup.md) - Step-by-step SSH server configuration

#### Automation & Development
- [SSH Setup Guide](ibm-i-ssh-setup.md) - Foundation for remote automation capabilities
- *Additional automation solutions to be added*

#### Customer Applications
- *To be added as we build customer-specific solutions*

## Current Session Progress

### 2025-08-04 Session
- **Completed:** Initial knowledge base structure
- **Completed:** IBM i ACS interface analysis and documentation  
- **Completed:** SSH setup documentation from Claude Code session
- **In Progress:** SSH server configuration on IBM i system
- **Next:** Test SSH connectivity and document results

## Session Continuity Notes

This knowledge base is designed to maintain continuity across Claude chat sessions. When starting a new session:

1. Reference the relevant documents in this `/readme` directory
2. Update the index as new documents are added
3. Ensure all context and decisions are documented in the appropriate files

## Quick Start for New Claude Sessions

When beginning a new Claude session, provide:
1. Link to this repository: https://github.com/1genadam/wc_ducomb
2. Current working context from the most recent documents
3. Specific goals for the session

### Current Context Summary
- Working with IBM i Access Client Solutions (ACS)
- Setting up SSH access for automation capabilities
- Building knowledge base for customer applications
- Next step: Complete SSH server setup via 5250 emulator

## Last Updated
- Created: 2025-08-04
- IBM i ACS Documentation: 2025-08-04
- SSH Setup Documentation: 2025-08-04
- Index Updated: 2025-08-04

## Notes for Immediate Next Steps
User needs to execute SSH setup commands via 5250 emulator:
1. WRKRDBDIRE RDB(LOCAL) - verify SSH components
2. STRTCPSVR *SSHD - start SSH server
3. CHGTCPSVR *SSHD AUTOSTART(*YES) - enable auto-start
4. NETSTAT *CNN - verify SSH is listening on port 22
