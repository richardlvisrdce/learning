Windows_Investigation.md

Debb_ill.md

windows investigation


# regedit (open through cmd)

### Run/RunOnce keys - executes programs on login

`HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run`

`HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Run`

### winlogon Userinit - what executes after login

`HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Winlogon\` look for Userinit or Shell values

# apps


eventvwr.msc - event viewer, filter by Event IDs

wf.msc - fiawoll, check rules

taskschd.msc - look through it's active library

services.msc - look for weird names or shady temp dirs

compmgmt.msc - especially path (Local Users and Groups -> Users) for weird accounts

lusrmgr.msc - GUI user management (Groups -> Administrators)

# cmd commmands

### schtasks

for scheduled tasks

`schtasks /query /fo LIST /v`

### net

`net user` for users

`net user <USER>` for more info


# powershell:


### net

`net localgroup` for groups

`net localgroup administrators` for admin group

### scheduled tasks

weird root tasks: `Get-ScheduledTask | Where-Object {$_.TaskPath -eq "\"}`

# other places to look

windows version of /etc/hosts

`cd C:\WINDOWS\System32\drivers\etc` and `cat hosts` if in powershell, else idk and after cd switch to powershell then cat


let's uninstall life now please.
