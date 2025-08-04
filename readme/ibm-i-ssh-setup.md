# IBM i SSH Server Setup Guide

## Overview
This document provides step-by-step instructions for enabling SSH access on IBM i systems, allowing secure remote access and automation capabilities.

## Prerequisites
- Access to IBM i system via 5250 emulator
- User profile with appropriate authorities (*IOSYSCFG special authority typically required)
- IBM i Access Client Solutions (ACS) connected to target system

## Server-Side Setup Process

### Step 1: Access 5250 Emulator
1. In IBM i Access Client Solutions
2. Navigate to **General > 5250 Emulator**
3. Connect to your IBM i system
4. Sign on with appropriate user profile

### Step 2: Verify SSH Components
Execute the following command to check if SSH components are installed:
```
WRKRDBDIRE RDB(LOCAL)
```
**OR**
```
GO LICPGM
```
Then look for:
- **5733-SC1** (IBM Portable Application Solutions Environment)
- **5770-DG1** (HTTP Server)

### Step 3: Start SSH Server
Execute this command:
```
STRTCPSVR *SSHD
```

**Expected Results:**
- Command should complete without errors
- SSH daemon will start on port 22

**Possible Issues:**
- If command fails, SSH may not be installed
- Check system messages with `DSPMSG QSYSOPR`

### Step 4: Enable SSH Auto-Start
Execute this command:
```
CHGTCPSVR *SSHD AUTOSTART(*YES)
```

**Purpose:** Ensures SSH starts automatically after system restart

### Step 5: Verify SSH is Running
Execute this command:
```
NETSTAT *CNN
```

**What to Look For:**
- Entries showing port 22 in **Listen** state
- Should see something like: `*.ssh` or `*:22` in LISTEN status

### Step 6: Configure Subsystem (if needed)
If SSH doesn't start, you may need to ensure QUSRWRK subsystem is active:
```
WRKACTJOB SBS(QUSRWRK)
```

If not active:
```
STRSBS QUSRWRK
```

## Security Considerations

### User Profile Requirements
- User must exist on IBM i system
- User must have appropriate authorities
- Consider creating dedicated SSH users

### Security Settings
Check current SSH configuration:
```
WRKLNK '/QOpenSys/QIBM/UserData/SC1/OpenSSH/etc/sshd_config'
```

### Firewall Considerations
Ensure port 22 is open if firewalls are configured

## Client-Side Testing

### From Mac Terminal
Once server setup is complete, test connection:
```bash
ssh username@ibm-i-hostname
```

### From ACS SSH Terminal
You can also test using ACS:
1. General > SSH Terminal
2. Enter hostname and credentials

## Troubleshooting

### Common Issues

**SSH Server Won't Start:**
- Check if components are installed: `GO LICPGM`
- Verify subsystem is active: `WRKACTJOB SBS(QUSRWRK)`
- Check system messages: `DSPMSG QSYSOPR`

**Connection Refused:**
- Verify SSH is listening: `NETSTAT *CNN`
- Check firewall settings
- Confirm hostname/IP is correct

**Authentication Issues:**
- Verify user profile exists
- Check user profile status (not disabled)
- Confirm password is correct

### Diagnostic Commands
```
WRKACTJOB SBS(QUSRWRK)          # Check SSH jobs
DSPMSG QSYSOPR                  # System messages
WRKRDBDIRE RDB(LOCAL)           # Installed components
NETSTAT *CNN                    # Network connections
```

## Automation Implications

### SSH Access Benefits
- Remote command execution
- Secure file transfer (SCP/SFTP)
- Automation script execution
- Remote monitoring capabilities

### Integration Opportunities
- Python/Node.js automation scripts
- Ansible playbooks
- CI/CD pipeline integration
- Monitoring system integration

## Document Status
- **Created:** 2025-08-04
- **Context:** Claude Code generated initial steps, documented for knowledge base
- **Next Steps:** Test implementation and document results
- **Related:** [IBM i ACS Overview](ibm-i-acs-overview.md), [Session Continuity](session-continuity.md)

## Session Notes
- Generated from Claude Code assistance
- User needs to execute commands via 5250 emulator
- Next: Test SSH connection from Mac once server setup complete
