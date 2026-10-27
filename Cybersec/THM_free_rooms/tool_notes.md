# tool_notes.md


### [nuclei](https://github.com/projectdiscovery/nuclei)

`apt install nuclei` and `nuclei -update-templates` to update templates

single

`nuclei -u http://TARGET_IP`

mass scan

`nuclei -l urls.txt -o output.txt`


### [arjun](https://github.com/s0md3v/Arjun/wiki/Usage)

```
tool for finding hidden HTTP parameters  
possible injection - eg. SQLi, XSS, LFI, RCE, etc. in GET and POST requests
```

`arjun -u http://TARGET_IP`

possible other flags:
- `-m GET` / `-m POST`  
-  `-o output.txt`
- `-t 10` (threads)
- 



### [nikto](https://cirt.net/nikto2-docs/usage.html#id2780332)

`nikto -h TARGET_IP -p PORT1,PORT2`