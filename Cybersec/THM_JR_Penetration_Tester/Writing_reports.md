# writing pentesting reports


## Audiences:

#### **`Technical stakeholders`**

```

most relevant audience, eg. for web pentesting - developerrs or the app

the report will provide guidance also to the IT support team

```

they want all the vulnerabilities, all issues

don't care about business summary

#### **`Business stakeholders`**

```

Security must enable business, not fight against it.

business people don't want details, they care about business impact and how long till its fixed

```


they want to hear the summary, not details


#### **`Security stakeholders`**

```

security audience - they are interested in the "boring" details of the penetration tes

especially scope, coverage and the next steps once remediation is done

```

care for supporting details - the security part

# report parts



## part 1 - summary

you write this last

#### **2 parts**
 - `Executive summary`
 - `Findings & recommendations`

**Executive summary**
 - for business stakeholders
 - understand impact of findings also in a non-tech way

**Findings & recommendations**
 - for security team
 - measured isolated/combined vulnerabilities and how to fix them

## part 2 - vulnerability write-ups

#### **7 parts**
 - `Title`
 - `Risk rating`
 - `Summary`
 - `Background`
 - `Technical details & evidence`
 - `Impact`
 - `Remediation advice`

\+ optional references

**Title**
 - short, descriptive (eg. "Unauthenticated SQL injection in login form")

**Risk rating**
 - vulnerabilities should be rated in isolation
 - eg. CVSS score, or low/medium/high/critical

**Summary**
 - short, non-technical description of the vulnerability
 - eg. "An unauthenticated attacker can inject SQL commands into the login form, potentially allowing them to access sensitive data."

**Background**
 - additional context and why it matters
 - eg. "The login form does not properly sanitize user input, allowing for SQL injection attacks."

**Technical details & evidence**
 - where and how the vulnerability was found
 - include screenshots, code snippets, and any other relevant evidence

**Impact**
 - what an attacker could *\*realistically\** do with this vulnerability
 - eg. "An attacker could potentially access sensitive user data, including passwords and personal information."

**Remediation advice**
 - how to fix the vulnerability (*adress the root cause, not just the symptoms!*)
 - eg. "Implement proper input validation and sanitization on the login form to prevent SQL injection attacks."

References (optional)
 - links to documentation or other resources on how to fix

## part 3 - supporting details (appendices)

#### **2 parts**
 - `Assesment scope`
 - `Assesment artefacts`

**Assessment scope**
 - what was planned x what was actually tested and why

**Assessment artefacts**
 - what changes were made during testing that could not be cleaned up
 - eg. new accounts, new files, suspicious logs

