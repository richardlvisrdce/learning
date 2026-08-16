


this ""writeup"" combines 2 rooms that were both bugged that I couldnt reach the machines after 3+ hours of debugging over 3 days. I will just list some probably useful commands.

tryhackme support of course take their sweet time to respond ... so yeah.

# Enumeration
```
gather as much information as possible about the domain
```

will help us down the pentest road to:
 - get initial foothold (eg. user credentials)
 - identify vulnerabilities
 - find attack paths

bugged room...


identify the domain controller (DC) and its IP address
`nmap -p 88,135,139,389,445 -sV -sC -iL hosts.txt`


### SMB

listing SMB shares

`smbclient -L //10.211.11.10 -N`

or with smbmap

cd /Desktop/Tools/Miscellaneous/smbmap#

`./smbmap.py -H 10.211.11.10`

access an SMB share

`smbclient //10.211.11.10/SharedFiles -N`

### LDAP

is anonymous LDAP bind enabled?

`ldapsearch -x -H ldap://10.211.11.10 -s base`

if yes you should see lots of data

query user info with:

`ldapsearch -x -H ldap://10.211.11.10 -b "dc=tryhackme,dc=loc" "(objectClass=person)"`

We can run the following command to get as much information as possible from the DC:

enum4linux-ng -A 10.211.11.10 -oA results.txt

### RPC 

verify null session acccess

`rpcclient -U "" 10.211.11.10 -N`

if yes we can use `enumdomusers` while in the rpcclient shell to enumerate users


### Kerbrute Installation

1.) Download a precompiled binary for your OS - https://github.com/ropnop/kerbrute/releases.(opens in new tab)

2.) Rename kerbrute_linux_amd64 to kerbrute

3.) Run chmod +x kerbrute to make kerbrute executable.

eg. `./kerbrute userenum --dc 10.211.11.10 -d tryhackme.loc users.txt`

# Password spraying

### password policy

this has to come first, so we can use more specific passwords for spraying

`rpcclient -U "" 10.211.11.10 -N` then `getdompwinfo` :

```
rpcclient $> getdompwinfo
min_password_length: 12
password_properties: 0x00000001
	DOMAIN_PASSWORD_COMPLEX
```

---

crackmapexec can do enumeration, command execution and other Windows attacks:

`crackmapexec smb 10.211.11.10 --pass-pol`

---

---

# Authenticated enumeration

after authenticating...

### classics

`whoami /all` =  detailed info about our groups and privileges

`systeminfo` =  detailed info about the system

`systeminfo | findstr /B "Domain"` or `systeminfo | findstr /B "OS"` =  get domain name and OS info

`set` =  get environment variables

`dir env:` or `Get-ChildItem env:` =  get environment variables in PowerShell

### net

`net help` = net is a CLI tool for managing Windows networks

`net group /domain` =  list all groups in the domain

`net group <Group Name> / domain` eg. `net group "Domain Admins" /domain` =  list all members of a group

`net localgroup` =  list all local groups

`net sessions` =  list all active SMB sessions in the network

### other

`quser` or `query user` =  list all users logged in to the system

`tasklist` =  list all running processes

`wmic service get Name,StartName` =  list all services and the account they run under

`Get-WmiObject Win32_Service | select Name, StartName` = alternative PowerShell command to the above


### BloodHound

```
potent tool for Active Directory (AD) enumeration

kinda revolutionary in 2016 - graphs for defenders & attackers

map permissions, group memberships, and trust relationships in a graph rather than relying on isolated lists
```

all collection methods + store in zip:

`bloodhound-python -u asrepuser1 -p qwerty123! -d tryhackme.loc -ns 10.211.12.10 -c All --zip`

## powershell


#### AD module

`Get-Module -ListAvailable ActiveDirectory`

if available, `Import-Module ActiveDirectory` to import it

user enum: `Get-ADUser -Filter *`

concise, specific info about a user:

`Get-ADUser -Identity Administrator -Properties LastLogonDate,MemberOf,Title,Description,PwdLastSet`

only names: `Get-ADGroup -Filter * | Select Name`

password policy: `Get-ADDefaultDomainPasswordPolicy`

fuck TryHackMe, all my homies hate TryHackMe