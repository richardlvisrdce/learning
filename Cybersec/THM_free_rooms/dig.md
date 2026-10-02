# Dig dug

this is a dig room, which is a command I haven't used much so I include a quick intro


### basic structure 
`dig @<DNS_SERVER> <DOMAIN> <RECORD_TYPE>`


### examples

basic-est IPv4 ('A' record query)

`dig example.thm`


short flag to reduce fluff (works with any other query)

`dig example.thm +short`


reverse translation (what domain is this IP linked to?)

`dig -x 10.10.X.X`


using a specific DNS server

`dig @10.10.X.X example.thm`


searching for any record type (can also be TXT, MX, ..)

`dig @10.10.X.X example.thm ANY`


extract whole DNS zone (whole DB)

`dig axfr @10.10.X.X megacorp.thm`


---
---

the room itself was extremely easy (I ran one command only), so pretty sad but at least we learned about dig ;)