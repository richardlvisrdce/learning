
# Introduction
```
AD breaching is the process of obtaining an initial set of valid AD credentials from scratch
```

we need these low-privilege credentials for enumeration and information that is hidden from unauthenticated users

getting in is often the hardest part of the engagement

### AD attack surface

SMB (TCP 445)
 - file sharing, printers, remote administration
 - good target for password spraying & credential testing

LDAP (TCP 389/636)
 - directory service for managing AD objects
 - misconfigured devices often store LDAP credentials

HTTP/HTTPS (TCP 80/443)
 - web services - internal portals, CI/CD pipelines, device management interfaces
 - credentials in logs, config files, source repos

Kerberos (TCP 88)
 - main authentication protocol for AD
 - can be abused to validate which usernames exist in the domain

DNS (TCP/UDP 53)
 - resolves hostnames within AD
 - leaks info about domain structure - controllers, mail servers

# OSINT
we all love it

### LinkedIn
 - great for finding full names, usernames, email addresses, job titles and reporting structures
 - automated scraping of employee names and wordlist generating: [linkedin2username](https://github.com/initstring/linkedin2username)

### GitHub & GitLab
 - code is sometimes commited using corporate email addresses
 - can reveal corporate email address format or usernames

### Public breach databases
 - Pastebin, HaveIBeenPwned, Breach Directory
 - some scrape dark web aswell - eg. Dehashed
 - onion sites exist for this aswell

### Job listings and corporate websites
 - employee names, tech stack, naming conventions, role descriptions, ...
 - self explanatory


# Enumeration

### Kerbrute

[Kerbrute](https://github.com/ropnop/kerbrute) tells us which usernames exist in the domain

we OSINT'ed a list of usernames and now we try them

command structure:
`kerbrute userenum -d <TARGET_DOMAIN> --dc <DOMAIN_CONTROLLER_IP> <USERNAME_WORDLIST> -o <OUTPUT_FILE>`

we will use:

`kerbrute userenum -d thm.loc --dc 192.168.12.100 /root/usernames.txt -o valid_users.txt`

`cat valid_users.txt | grep "+" | sort -u | wc -l`

we found 43 usernames (the `+` sign indicates a valid username) in first.last format (joe.shmoe)

# Credential discovery

```
initial credentials can often be found in internal services such as Git repositories, CI/CD platforms, and file shares

these are often poorly secured and frequently contain plaintext credentials
```

### Exposed services - goldmine

```
quickly deliver the app mr. developer... security? what security? wait how much will security cost? oh hell no, get to production now! ...
```

Where credentials often are but should not be:
 - Committed to source code repositories
 - Printed in CI/CD build logs
 - Written into configuration files on shared drives
 - Documented on internal wikis

cleanup is often poor, so traces often remain...

### credentials in Git repositories

```
myapp_beta_version_0.0.0

config
  database:
    host: db.thm.loc
    username: dbuser
    password: Password123!

happens to the best of us...
```

Git repos
 - very commonly contain leaked credentials
 
 - git version history contains every change
 
 - especially older versions often contain credentials or sensitive information

 - can be exposed to the public

found an exposed .git directory? look for:
 - commit history (especially older commits)

 - configuration files (eg. `.env`, `web.config`, `appsetings.json`, `database.yaml`)

 - hardcoded secrets - API keys, credentials in source code (YES, this happens)

 - CI/CD pipeline definitions (eg. `Jenkinsfile`, `.gitlab-ci.yml`, `.github/workflows/*.yml`)

#### commands:
 - `git log -p | grep -i "password\|secret\|token\|key\|credential"`

 - [TruffleHog](https://github.com/trufflesecurity/trufflehog) can do this for us

 - eg. `trufflehog git file:///path/to/repo`

### Hunting Credentials in Jenkins

[Jenkins](https://www.jenkins.io/)

```
one of the most popular CI/CD platforms on internal networks

or as we call it: treasure trove for credentials
```

weak or default credentials

anonymous access to dashboards, build logs and job configurations

we look for the same things as in Git repos but in different places...

Places to look:

- Build console output

- Job configuration files (`config.xml`)

- Environment variables (using `env` or `set` commands)

- Workspace files

commands:
 - `curl http://ci.thm.loc/job/JOB_NAME/lastBuild/consoleText | grep -i "password\|secret\|token\|credential"`

# Practical notes

### smb credential testing

first cleanup usernames, eg.

`grep "VALID USERNAME" valid_users.txt | awk '{print $NF}' | sed 's/@thm.loc//' > clean_users.txt`

then we use nxc (netexec) to test them and grep for valid ones

`nxc smb 192.168.12.100 -u clean_users.txt -p 'MegaCorp01!' --continue-on-success | grep "+"`

we can see that 2 users used the default password (MegaCorp01!) ...

### LDAP passback attack

```
redirecting the device's LDAP connection to an attacker-controlled listener
```

0) access the device's web interface and login with default or leaked credentials
1) changing the device's LDAP configuration to point to our own LDAP server

2) trigger a connection test and capture the credentials sent to our LDAP server (nc listener) and use 'em

### Mitigation in keywords
 - secrets management
 - password policies and account lockout
 - device hardening
 - file share security
 - NTLM hardening
 - network segmentation and access control
 - monitoring and alerting

