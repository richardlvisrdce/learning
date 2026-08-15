Great room, can recommend 10/10
there is a static website at the end which helped connect the information


# Why defend? I am big ataker
```
being a pentester without understanding defence ..

is like hunting for deer without knowing what a deer looks like.
```

1) stealth
    - knowing what triggers alerts helps us to avoid them
    - eg. replacing bruteforce with password spraying

2) better reporting
    - knowing what the defenders did wrong is important for the client

3) realistic testing
    - we can adapt to defenses
    - purple team engagements produce best security outcomes

`red team` = offensive team - exploits, impact, BurpSuite

`blue team` = defensive team - monitoring, analysis, SIEMs

`purple team` = combination of both - shared knowledge, better security outcomes

# SOC tiers

### L1 - Triage analyst
 - monitor alerts
 - very high volume of alerts
 - classification, false positives
 - escalate dangerous-looking alerts

### L2 - Incident handler
 - deep-analysis of escalated alerts
 - what is affected, containment actions
 - more tools and knowledge than L1

### L3 - Threat hunter / Senior analyst
 -  proactive hunting for signs of compromise
 - build rules, do advanced forensics
 - cares about what the automated tools missed

1) monitor and review
2) triage & classify
3) investigate context
4) decide on escalation

# before we start

`MTTD` = mean time to detect
 - time between compromise and detection
 - IBM 2025 said average is 180 days
 - M-Trends 2026 said 14 days

`MTTR` = mean time to respond
 - detection to containment
 - IBM 2025 says 60 days

`alert fatigue` = too many alerts, analysts get tired and miss things

 - if 9/10 alerts are false positives, analysts will start ignoring them

### SIEM 
 - Security Information and Event Management system

 - collects logs from multiple sources, normalizes them, and correlates events to detect threats

 - does not replace skilled analysts


# Splunk

```
index, search, monitor, analyze, and visualize machine-generated big data in real time.

commonly used as a SIEM platform 
```

we have a botsv1 dataset we will be working with

group events by sourcetype and count them:

`index=botsv1 | stats count by sourcetype`

viewing raw events:

`index=botsv1 sourcetype=WinEventLog:Security | head 10`

event volume over time (1 hour buckets):

`index=botsv1 sourcetype=WinEventLog:Security | timechart span=1h count`

detecting automated tols via IPS:

```
index=botsv1 sourcetype=fgt_utm subtype=ips
| stats count by srcip
| sort -count
| head 1
```

this gave us the top 1 source IP that seems malicious

web directory bture-forcing:

note that the count has to be fine-tuned for small or large datasets

```
index=botsv1 sourcetype=iis sc_status=404
| stats count by c_ip
| where count > 100
| sort -count
```

# Incident response lifecycle

```
how to not get your shit robbed

we know your boss is an a-hole but what if it was your a-hole that was being breached?

in all cases you want to have a plan before-hand

and a plan for after ass-well
```

### NIST rev 2 lifecycle

1) Preparation
 - policies, procedures, playbooks, training, tools and stools

2) Detection & Analysis
 - identify and analyze potential incidents

3) Containment, Eradication & Recovery
 - stop the bleeding
 - contain the incident (please), remove the threat, and restore systems

4) Post-Incident Activity
 - lessons learned, improve defenses (aikido and stuff), update playbooks (don't go into a gay club on monday)

### SANS PICERL model
- Preparation
- Identification
- Containment
- Eradication
- Recovery
- Lessons Learned

# Other useful sources

MITRE ATT&CK

David Bianco's Pyramid of Pain (2013)