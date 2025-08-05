# SSH Setup - Troubleshooting Session

## Command Execution Attempt
**Date:** 2025-08-05 08:37:39 AM
**Method:** SQL Scripts interface
**User:** ROBERT (535921/QUSER/QZDASOINIT)

## Command Tried
```sql
CALL QSYS2.QCMDEXC('STRTCPSVR *SSHD');
```

## Error Response
```
SQL State: 38501
Vendor Code: -443
Message: [CPF0006] Errors occurred in command.
Cause: If the wrong length was passed on one part of the command, other messages are issued because the wrong part of the command is being analyzed.
Recovery: See the previously listed messages in the job log. Correct the errors and then try the command again.
Failed statements: 1
```

## Analysis
This error suggests either:
1. **SSH components not installed** on this system
2. **Insufficient authority** for user ROBERT to start TCP servers
3. **Command syntax issue** in SQL context

## Next Steps to Try

### Option 1: Check SSH Installation Status
```sql
CALL QSYS2.QCMDEXC('WRKRDBDIRE RDB(LOCAL)');
```

### Option 2: Check TCP Server Status
```sql
CALL QSYS2.QCMDEXC('NETSTAT *CNN');
```

### Option 3: Check Licensed Programs
```sql
CALL QSYS2.QCMDEXC('GO LICPGM');
```

### Option 4: Try Via 5250 Emulator Instead
Switch to the 5250 emulator session and:
1. Exit the Infor menu (type 'X' or find exit option)
2. Get to command line (===>)
3. Try: `STRTCPSVR *SSHD`

## Alternative: Check What TCP Servers Are Available
```sql
CALL QSYS2.QCMDEXC('WRKRDBDIRE RDB(*ALL)');
```

## System Context
- **System:** S7891490 at 10.0.0.7
- **HTTP Server:** ✅ Running (confirmed by web documentation access)
- **SSH Server:** ❓ Status unknown, likely not installed or not started
- **Database:** ✅ Working (SQL connection active)

## Next Actions
1. Try checking what TCP servers are currently running
2. Verify SSH components are installed
3. If SSH not available, focus on HTTP/web-based automation instead
4. Document available integration methods

## Alternative Integration Paths
Since HTTP server is confirmed working:
- **Web services** may be available
- **REST APIs** potentially accessible
- **HTTP-based automation** possible
- **Database direct access** via SQL (already working)

## Document Status
- **Created:** 2025-08-05
- **Issue:** SSH server start failed
- **Next:** Investigate available TCP services and alternative access methods
