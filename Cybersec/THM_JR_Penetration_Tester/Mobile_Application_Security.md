
# Mobile Pentesting Meth-OD-ology
## The phases

### 1) Recoinaissance
    - gather info
### 2) Static analysis
    - examine the app without running it
    - inspect compiled code
    - quick and effective findings
### 3) Dynamic analysis
    - run the app and observe its behavior
    - interact with it as an actual user
    - can find things static analysis can't
### 4) Reporting
    - document findings and recommendations
    - guidance should be actionable and clear

## [OWASP Mobile Top 10](https://owasp.org/www-project-mobile-top-10/)
 - very good resource
 - works as a universal checklist

## Testing approaches

1) Black box
    - no knowledge of the app
    - only have the app
2) Grey box
    - have some knowledge of the app
    - eg. credentials to test authenticated functionality + a bit of source code
3) White box
    - have full access to source code and architecture details
    - time consuming but very thorough

## Scope
 - remember to always stay in pre-defined scope
 - test versions ABC, allowed actions are XYZ

---

# Static analysis
```
unpacking an application package, reading its manifest or Info.plist

searching for hardcoded secrets and using automated tools such as MobSF to surface common issues across both Android and iOS
```

`decompiler` unpacks the binary to some human-readable code

note: decompilers are not perfect, the code will not be 100% same as source code

the app's configuration is in the `manifest` file

Android: manifest
iOS: Info.plist

## common findings:
### 1) Over-requested permissions

applications should only request permissions they actually need

broad permissions mean more damage when compromised

### 2) Exported components

exported components are accessible to other applications

exported components handling sensitive data or privileged actions are a direct attack surface

### 3) Insecure configuration flags

settings in the manifest should be secured to prevent weakening security

## MobSF
 - Mobile Security Framework
 - open-source automated tool for static analysis of Android and iOS apps

---

# Dynamic analysis
```
intercepting network traffic, working around SSL pinning

using runtime instrumentation and reviewing application logs for sensitive data leakage
```

### Traffic interception
 - each request and response is important
 - eg. which chinese server is the app talking to, how much my data is being sold for, ....

### SSL Pinning
 - the app only trusts a specific certificate/s

 - it will not work with any other certificate, no matter what CA issued it

 - to bypass SSL pinning, we can use [Objection](https://github.com/sensepost/objection), it does not even require source code.

### runtime instrumentation
 - ataching to the app while it is running and observing/modifying its behavior from the outside
 
 - [Frida](https://frida.re/) can help us to:
    
    - see through the app's logic and flow
    
    - bypass authentication
    
    - extract data the application holds in memory

### Insecure logging
 - the app should not log sensitive data, but it often does - left-over from debugging phases

 - eg. logging usernames, tokens, passwords to a log file that any app can read (oopsies)

# Common mobile vulnerabilities

### 1) Insecure data storage
 - sensitive data should not be stored in plaintext or in world-readable files on the device

 - eg. storing passwords, tokens, or personal information in unencrypted files or databases

### 2) Improper platform usage
 - asking for unnecessary permissions or insecure data passing between components

### 3) Insecure auth and session management
 - similar to web app vulnerabilities
 - eg. weak session tokens that don't expire, very gullible biometric checks (eg. trusting OS without verifying)

### 4) Exposed application components
 - mainly exported components that handle sensitive data

### 5) Insufficient binary protections
 - not checking at least these three boxes:
    - has the code been obfuscated?
    - is there anti-tampering protection?
    - does the app check for root/jailbreak?
 
 - eg. bank apps should definitely be wary of jailbroken devices and ideally refuse to run on them

---

```
we then used mobSF to analyze an .apk file and it was pretty disturbing and quite surprising that it is free to use (ran locally).

the app had a score of 40/100:
- over-requested permissions (OWASP M8)

- debug enabled

- AdminPanelActivity is exported (anyone can bypass authentication and access it)

- hardoced API key found in Java source

- database password was hardcoded in DatabaseHelper.java

- NSAllowsArbitraryLoads set to true in Info.plist (iOS manifest) which allows insecure HTTP connections

- and many more...
```