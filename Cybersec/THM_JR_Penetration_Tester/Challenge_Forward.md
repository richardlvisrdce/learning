ATTACKER: 10.113.117.155
TARGET: 10.113.135.232

### setup

we start with some creds:

USER > ctf.local\j.smith
PASS > JSmith@IT2024

**Note** : the actual username is j.smith (for RDP and stuff)

we want to do:
1) lateral movement
2) privilege escalation and beyond (get Admin)


I will mostly be using commands from the AD-Basic+Authenticated_Enumeration.md, specifically the authenticated ones

### ActiveDirectory module


`Get-Module -ListAvailable ActiveDirectory`

if available, `Import-Module ActiveDirectory` to import it

user enum: `Get-ADUser -Filter *`

this gave us quite some info

there is:
 - Administrator (we want that)
 - Guest (we don't care)
 - krbtgt (Kerberos)
    - it has Enabled: False, so probably not useful for us
 - some other normal users
 - svc.helpdesk (could be useful for lateral)

`Get-ADUser -Identity Administrator -Properties LastLogonDate,MemberOf,Title,Description,PwdLastSet`

okay Administrator is the only admin

CN=Administrator,CN=Users,DC=ctf,DC=local 

we will go with bloodhound

first confirm domain name is real:

`systeminfo | findstr /B "Domain"`

yes, it's ctf.local

okay, bloodhound is not installed and I don't want to research it yet, we will try impacket first

let's get password policy:

`Get-ADDefaultDomainPasswordPolicy`

MinPasswordLength : 7
ComplexityEnabled : True
LockoutDuration : 00:30:00
LockoutThreshold : 0

okay, no bruteforce I guess

quick nmap so I dont wanna waste time:

`nmap -p 88,135,139,389,445 -sV -sC 10.113.135.232`

there is Kerberos, RPC, netbios-ssn, LDAP

### LDAP

is anonymous LDAP bind enabled?

`ldapsearch -x -H ldap://10.113.135.232 -s base`

yes

query user info with:

`ldapsearch -x -H ldap://10.113.135.232 -b "dc=ctf,dc=local" "(objectClass=person)"`

nope, does not work

### classic enum4linux situation:

`enum4linux-ng -u j.smith -p JSmith@IT2024 -A 10.113.135.232`

the only user that looks interesting is:
```
username: r.williams
  name: (null)
  acb: '0x00000210'
  description: Help Desk Senior
```

there are some shares seen via RPC
 - ADMIN$ (completely denied)
 - C$ (completely denied)
 - Downloads (mapping and listing OK)
 - NETLOGON and SYSVOL (mapping and listing OK)

### but wait..

then I remembered this is tryhackme, so I opened files app

there was Database.kdbx (keepass database = passwords) in Documents

I open it with keepass, master password being ...

drumroll ...

blank password

User Name \ Password

Michael321 \ 12345

Help Desk: t.jones \ Helpdesk01!

that is what I call juicy lateral schmoovement (make it stop pls)

I RDP into the target with t.jones / Helpdesk01!

this guy had absolutely nothing and had "joe shmoe" privileges - dead end

we can try his password with the other helpdesk dudes

specifically, r.williams

### r.williams

`nxc smb 10.113.135.232 -d ctf.local -u r.williams -p 'Helpdesk01!'`

works  ! !

RDP into him

check fucking files app

he sees DC01 in Network, so he is cool

also going from his r.williams.CTF user to r.williams we see this:

```
PS C:\Users\r.williams\Desktop> cat .\Automation-Notice.txt

HelpDesk Automation Notice
==========================
A background process handles automatic ticket processing and
service account maintenance for the HelpDesk system. 

The automation runs periodically and stores temporary working files in C:\Windows\Temp. 
```

`cd 'C:\Windows\Temp'`

ok, we will first see how the service is called and who it runs as

hmm  `cat .\HelpDesk-Auth.b64`

```
<some very large hash I guess>
```

-- break time --



`nano /etc/hosts` append this: `10.112.151.130 ctf.local`

`xfreerdp /u:r.williams /v:ctf.local`

enter password: Helpdesk01!

on attacker, we copied Powermad.ps1 from github - [link](https://github.com/Kevin-Robertson/Powermad/blob/master/Powermad.ps1)

`python3 -m http.server 8000`

something's terribly wrong with this CTF, I spent an hour trying to get the script wtffffff and it don't work. 

IDK why tryhackme decided not to let us use Impacket, Bloodhound or anything else 

Would love to see the official writeup with manual typing of hundreds of commands

I found no exploitable services or processes and deem the "script way" the only way to do this, as I read all the writeups and everybody uses those 

the only thing that kind of worked was evil-winrm and enum4linux for enumeration but that gave us 0 practical escalation results so I give up

[some guy's writeup](https://musyokaian.medium.com/forward-tryhakme-challenge-15e05a0f532d)



