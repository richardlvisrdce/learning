# Introduction
### vulnerability-based escalation
 - exploits bugs in software
 - buffer overflows, CVEs
 - unpatched software, less reliable
### configuration-based escalation
 - errors in system set up
 - weak permissions, insecure services, plaintext passwords
 - targets administrator decisions
 - works on fully patched systems
 - most common in practice

# Configuration review
**configuration review is ...**
```
a structured audit of system configuration, 
host's settings, permissions, services, policies
```
### defensive audit
 - identify deviations
 - assess risks + prioritize by severity
 - harden and re-audit

### offensive enumeration
 - identify weaknesses
 - prioritize targets
 - escalate priviliges

# Security baselines & frameworks
**security baselines are ...**
```
a documented standard, defining how a system should be configured to meet an acceptable security level
```

### CIS Benchmarks
Center for Internet Security (CIS)
two profile levels:
- Level 1:
    - practical and broadly applicable reccomendations
    - low risk of breaking/restricting functionality
- Level 2:
    - reccomendations for deeper hardening
    - may break/restrict functionality

### DISA STIGs
Defense Information Systems Agency (DISA) - part of the US Department of Defense
Security Technical Implementation Guides (STIGs)
mandatory prescribed hardening for military and government systems
CAT I: critical - exploitation directly affects C.I.A. (Confidentiality, Integrity, Availability)
CAT II: medium risk
CAT III: low risk

# automated compliance tooling

### Nessus
 - commercial vulnerability scanner by Tenable
 - also has compliance audition functions
 - scan hosts against CIS Benchmarks, DISA STIGs or custom policies
### Lynis
 - open-source local security auditing tool for UNIX systems
 - hardening index score, categorized findings, suggestions
 - defense + offense use cases
### OpenSCAP
 - open-source implementation of SCAP (Security Content Automation Protocol)
 - SCAP - standard for evaluating security configuration policies
 - evaluates against CIS, STIG, ... and produces detailed report for each rule
### CIS-CAT
 - CIS's own compliance auditing tool
 - evaluate against CIS Benchmarks
 - free limited version exists

# Host misconfiguration categories

I will be listing most common misconfigurations with examples

### User and Group Configuration
--> accounts and groups control who can perform which actions

--> we typically follow the principle of least privilege

common misconfigurations:
 - user account in admin groups
 - over-privileged service accounts
 - weak or absent password policies
### File and Directory Permissions
--> which users can read, write, or execute specific files
common misconfigurations:
 - SUID bit set on binaries that don't need it (SUID allows executing a file with permissions of the file owner)
 - sensitive files world-readable, writable, or executable
 - misconfigured ACLs (Access Control Lists, common on Windows)
### Service Configurations
--> long-running processes that perform background tasks on a system
common misconfigurations:
 - unnecessary services running
 - services running with unnecessarily high privileges
### Scheduled Tasks and Cron Jobs
--> task that are set to run automatically at specified times or intervals
common misconfigurations:
 - high privilege tasks with configuration modifiable by low-privilege users

# Enumeration methodology structure

### 1) **Situational awareness** 
- understand the environment, system architecture, and security policies
- identify potential attack vectors and entry points

### 2) **Category-Based Enumeration**
**User and group configuration**
- enumerate all user accounts and their group memberships
- identify admin and root-level accounts
- review password policies and authentication mechanisms
**File and directory permissions**
- search for files with weak permissions
- **Linux:** search for binaries with SUID/SGID bits set
- **Windows:** review ACLs on directories in the System PATH, program installation directories
**Service configurations**
- list all running services and their configurations + who they run as
**Scheduled tasks and cron jobs**
- Enumerate all scheduled jobs and identify those running with elevated privileges
**Credential storage**
- search for accesible credentials in history, environment variables, configuration files, and scripts
- this is a golden mine, finding something is often direct escalation
**Network configuration**
- review firewall rules, open ports, and network services
- think in terms of lateral movement and understanding the host network

### 3) **Prioritisation and Exploitation**
 - use what you found, demonstrate impact where necessary
 - Prioritize findings based on severity and potential impact
 - after using your main weapons, try chaining lower-priority vulnerabilities


 
