# OS enumeration commands
### hostname
only works in some cases, can provide a meaningful hint - eg. `SQL-PROD-01` is quite informative

---

### uname
`uname -a` gives you system info + details about kernel

---

### /proc/version
kernel vesion, build machine, compiler, ...
```
$ cat /proc/version
Linux version 6.8.0-41-generic (buildd@lcy02-amd64-077) (x86_64-linux-gnu-gcc-13 (Ubuntu 13.2.0-23ubuntu4) 13.2.0, GNU ld (GNU Binutils for Ubuntu) 2.42)
```

---

### /etc/issue
can conatain some OS info, but not always, can be changed

---

### ps
see info about running processes
+ PID (process ID)
+ TTY (terminal type)
+ Time (used CPU time)
+ CMD (command or executable running)

`ps aux` = see processes for all users (basic info)

`ps axjf` =  all processes in a tree format

---

### cron
time-based job scheduler in Linux

`cat /etc/crontab` = see cron jobs

you can also check
`/var/spool/cron/` or `/etc/cron.d/` directories

---

### dpkg
`dpkg -l` = list installed packages and their versions

# User enumeration commands

### id
general info about current user's privilege level
`id` = uid, gid, groups for current user
`id <USER>` = for specific user

---

### env
show environment variables
```
$ env
# PATH can have a compiler or scripting language (eg. python) in it that can be leveraged for privesc
...
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
...
```

---

### history
history of executed commands (can be wiped, but often is not)

can give us a hint about what the system does and sometimes even credentials or internal processes

---

### sudo -l
list all commands your user can run using sudo

---

### /etc/password
discover users on the system
`cat /etc/passwd | cut -d ":" -f 1` = list of all users

`cat /etc/passwd | grep /home` = list of probably human users

---

# Network enumeration commands

### ifconfig
information about the network interfaces of the system

on more modern systems, we use `ip`

`ip addr` = show IP addresses

---

### netstat
info about existing connections

sometimes replaced by `ss` with similar syntax

`netstat -a` = show all connections and listening ports

`netstat -ano` = show all sockets, do not resolve names, display timers

`netstat -tp` = connections with the service name and PID

`netstat -at` or `netstat -au` = show TCP or UDP connections

`netstat -tpln` = listening tcp connections with PID and ports

---

# File enumeration commands

### ls
`ls -la` = list all files in current directory

### find

`find / -name flag.txt 2>/dev/null` = search for flag.txt in entire filesystem

`find / -perm -u=s -type f 2>/dev/null` = find files with SUID bit set

`find / -name pass*.txt 2>/dev/null` = find files starting with pass and ending with .txt

`find / -type f -perm 0777 2>/dev/null` = find all files with 777 permissions (world-readable, writable, executable)

`find / -size +50M 2>/dev/null` = find all files larger than 50MB

`find / -mtime -10 2>/dev/null` = files modified in the last 10 days

`find / -atime -10 2>/dev/null` = files accessed in the last 10 days

`find / -cmin -60 2>/dev/null` = files changed in the last hour