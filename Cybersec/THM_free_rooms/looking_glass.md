# this room is broken

>> #make THM work again and pls stop putting all things in super premium tier

sudo nmap -sS -p- 10.112.177.147 -o scan.txt

we got a few thousand ports, most of which have "unknown" service running

I learned how to negative match with grep

cat scan.txt | grep -v "unknown"

we still have 378 lines to go through

barely recognize any of the services, so I tried deciphering a few unknown services

nmap -sV -p 10000-10050 10.112.177.147

```bash
PORT      STATE SERVICE VERSION
10000/tcp open  ssh     Dropbear sshd (protocol 2.0)
10001/tcp open  ssh     Dropbear sshd (protocol 2.0)
10002/tcp open  ssh     Dropbear sshd (protocol 2.0)
10003/tcp open  ssh     Dropbear sshd (protocol 2.0)
10004/tcp open  ssh     Dropbear sshd (protocol 2.0)
10005/tcp open  ssh     Dropbear sshd (protocol 2.0)
10006/tcp open  ssh     Dropbear sshd (protocol 2.0)
10007/tcp open  ssh     Dropbear sshd (protocol 2.0)
10008/tcp open  ssh     Dropbear sshd (protocol 2.0)
10009/tcp open  ssh     Dropbear sshd (protocol 2.0)
10010/tcp open  ssh     Dropbear sshd (protocol 2.0)
```

they really like this Dropbear sshd...

it is a lightweight SSH server & client for things like routers, IoT or embedded envs

maybe the hint can help?

>Question Hint

```"O(log n) A looking glass is a mirror."```

what?

There was a guessing game where we had to find the correct Dropbear port among thousands of decoy ports

It was basically binary search, where the response "higher" meant we should try lower and vice-versa.

scripting this is possible, but doing it once by hand is still less work.

we now have to decode this:

```
Solve the challenge to get access to the box
Jabberwocky
'Mdes mgplmmz, cvs alv lsmtsn aowil
Fqs ncix hrd rxtbmi bp bwl arul;
Elw bpmtc pgzt alv uvvordcet,
Egf bwl qffl vaewz ovxztiql.
...
Enter secret:
```

this is probably some alice in wonderland poem, so I tried cyberchef with know pt strings like "the", "Jabberwock" - as seen in the first line

I first thought caesar cipher but it did not match

great website: [dcode.fr](https://www.dcode.fr/cipher-identifier)

I put Jabberwock as a clue, which strongly hinted at vignere cipher

got a hit with HABETCIPHERTHEALP (cheeky basterds with this "the alphabet cipher" combination lol)

```
'Twas brillig, and the slithy toves
Did gyre and gimble in the wabe;
All mimsy were the borogoves,
And the mome raths outgrabe.
Your secret is bewareTheJabberwock
```

we got back "jabberwock:RollingThornsDreamSuggestion"

straight to ssh and after 3x permission denied we succeed

of course user flag was reversed..

so i wrote my worst python ever (why is there no str.reverse() ?) in terminal like a boss

```python
s = "}32a91196REDACTED173d56{mht"
a = ""
for i in range(len(s) - 1, -1, -1):
    a = a + s[i]
print(a)
```

so with this user we found this in /etc/crontab

> @reboot tweedledum bash /home/jabberwock/twasBrillig.sh

jabberwock is us and we can write the script (the script uses `wall` and essentially does nothing)

favourite site incoming (https://www.revshells.com/)

i took the `bash -i` variant and tried "reboot", which we of course can't (we can't run sudo), hmm

a quick look at `cat /etc/cron*/*` also does not help

after some more enumeration, my machine expired and I had to get a new one. Funny thing, we had to do everything again, as port and password were different

this means I had to write the python script for the (reversed) binary port search

and now I am not happy so I brought over LinEnum.sh

only one thing found - I know that Sudo version 1.8.31 can be vulnerable, so let's try exploiting that instead (baron samedit CVE, works only on select distributions)

I was unable to do this safely, as baron samedit was likely not the intended way

from about 10 other writeups either `sudo reboot` worked or there was supposed to be `SUID/SGID (NOPASSWD) /sbin/reboot`. **None of this was true in my experience.**

can't run sudo on jabberwock and unable to exploit vulnerable sudo version. No other way to solve found. As this is an old room, I suspect it is broken.

python script for the port search (ChatGPT helped with the subprocess part):

```python
import subprocess
import time

ip = "10.112.176.167"
username = "root"

def try_ssh(port):
    cmd = [
        "ssh", f"{username}@{ip}",
        "-p", str(port),
        "-o", "HostKeyAlgorithms=+ssh-rsa",
        "-o", "ConnectTimeout=2",
        "-o", "StrictHostKeyChecking=no"
    ]

    try:
        output = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=4
        ).stdout
    except subprocess.TimeoutExpired as e:
        output = e.stdout or b""

    output = output.decode(errors="replace")

    if "Higher" in output:
        return "HIGHER"
    if "Lower" in output:
        return "LOWER"

    if "You've found the real service" in output:
        return "FOUND"

    return "CLOSED"

def bins(start_port, end_port):
    low = start_port
    high = end_port

    while low <= high:
        mid = low + (high - low) // 2
        response = try_ssh(mid)

        if response == "FOUND":
            return mid
        elif response == "HIGHER":
            high = mid - 1
        elif response == "LOWER":
            low = mid + 1
        else:
            print(f"Port {mid}: no valid response")
            return None

        time.sleep(0.1)

    return None

print("Found port", bins(9000, 13999))
```