`nmap -A -p- -v`

we have http server

`gobuster dir -u -w -x .js, .php`

info.php  
here we got include_path = .:/usr/share/php

we have PHP 8.3.6  
i tried `searchsploit PHP | grep "8.3.6"`  
too many results  

i tried to access a possible old version of the API endpoint  
10.112.176.195/index.php/v1/api  

there is absolutely nothing to latch onto... just another login form

bruteforce using ffuf, cause why not ffuf

i will try the help@support.thm account as the only username we have

`ffuf -w usernames.txt:W1,/usr/share/wordlists/rockyou.txt:W2 -X POST -d "email=W1&password=W2" -H "Content-Type: application/x-www-form-urlencoded" -u http://10.112.176.195/index.php -fc 200`

hell yeah f*uck yeah xoxoxoxoxox
we got em

**help@support.thm:snoopy**

we can now select "skin" (background color) - lets try to inject that  
`http://10.112.176.195/dashboard.php?skin=green`

there is a weird parameter `IsITUser:68934a3e9455fa72420237eb05902327`  
I had to consult the internet and it looks like MD5

encoding `"false"` using cyberchef, we get the exact same value

lets try to change it to true [like this in cyberchef](https://gchq.github.io/CyberChef/#recipe=MD5()&input=dHJ1ZQ)
MD5 hashed value 'true' is b326b5062b2f0e69046810717534cb09

we had to do this in browser -> storage -> change the cookie value -> refresh

now we see an internal user api with text:  
"As a helpdesk user, you can query your own profile: /user/3"

going to site `http://10.112.176.195/api.php/user/3`, we see:

API Request

GET /user/3

API Response

```

{
    "email": "help@support.thm",
    "2FA": false,
    "admin": false
}

```

changing the user ID does nothing, path traversal either puts us to 404 or the dashboard for login  
we could try gobustering some more endpoints, but we would need to set the cookies and that is too much work (for now)

OK, I came back tmrw and the user ID injection somehow started working  
`http://10.112.176.195/user/1`

so now we have admin email  
`specialadmin@support.thm`

there is only one more thing that looks very vulnerable  
the background color (skin) parameter

if we take a closer look where it's stored  
`http://10.112.176.195/skins/`
we see that the "skins" are actually PHP files  
the server appends .php to the skin (in the URL you just see green, but it's green.php)  

probably local file inclusion (LFI) - this was just trial and error, but

we came up with that the server uses realpath to the skins folder (var/www/html/skins/)

there is some basic check so we dont easily go outside var/www/html/

because it appends .php (i couldnt stop it from doing that), we can only access php files

so i tried all php files that gobuster found and the last one worked  
`http://10.112.176.195/dashboard.php?skin=../config`  
(note that we only see the result in page source, not on the page)

we found admins password ??? support@110  
but the credentials dont work

after watching a [youtube video](https://www.youtube.com/watch?v=qrg0cObFVIc)
at 24:42 he says that support@110 doesnt work but support110 does
for absolutely no reason at all, tryhackme has this weird kink with passwords/password lists

we log in as admin, get admin flag
now we need contents of /home/ubuntu/user.txt

as admin we have 1 more button and that is date/time display
inspecting the network traffic and the specific post request, we see

Form data  
sys: "date"

let's edit and resend it, changing the Body (where the sys parameter is) to something better

let's try `sys: "ls /home/ubuntu/user.txt"`  
bruh. "only date command is allowed"  
lets chain it

`date;ls /home/ubuntu/user.txt`

does nothing

lets try `date | cat /home/ubuntu/user.txt`

*** this should've worked but didnt on my machine, so after a restart and it still not working, I just read the flag
fuck this room, waste of time (common tryhackme bug)