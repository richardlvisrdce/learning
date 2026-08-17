
# The story

### Waterfall model

project management back in the day

hierarchy - everyone has a role and a task

```
analysis
   |
   |-> design
         |
         |-> implementation
                |
                -> testing
                     |
                     |-> deployment
                          |
                          |-> maintenance

```

- inefficient because of the linearity of the process
- bad cross-team flexibility and communication
- responsibilities are not clear, lots of noise

### Agile model

- succesor of waterfall
- most problems solved
- but still not enough

### DevOps
- buzzword

- building trust and better liaising (talking) between developers and other teams

- unites the development and operations teams

- cross-team integration, automation

- eg. developers can be involved in deployment

- bypasses the need of going through all the teams

- saves time

- CI/CD: automatic testing, staging, production processes

- IaC (Infrastructure as Code): infrastructure is defined in code, can be versioned and tested (declarative - eg. terraform, ansible)

# The Infinite Loop

```
 -  plan    -
 -  code    - 
 -  build   -
 -  test    -
 -  release -
 -  deploy  -
 -  operate -
 -  monitor -
```

### 1) CI/CD
Continuous Integration / Continuous delivery

automating the process of:
 - building
 - testing
 - deploying

### 2) IaC
Infrastructure as Code

reusing code used to deploy infrastructure
 - consistent
 - helps with management

### 3) Configuration management
constant and consistent configuration of systems
 - eg. ansible, puppet, chef
 - deploy and configure systems, enforce policies

### 4) Orchestration
automation of workflows (eg. planning, monitoring)
 - stability
 - speedy reaction to problems (eg. failed health checks)

### 5) Monitoring
monitoring, alerting
 - get more data for analysis (eg. root cause analysis)
 - automated responses etc.

### 6) Microservices
many small services instead of a monolith
 - easier to manage, update, scale
 - more choices in tech stack

# shifting left (shitting right)
shift left = shift security to earlier stages
 - security throughout the lifecycle, not at the end
 - secure design, early detection
 - reduce costs, reduce risk, increase quality

# closing notes
```
DevSecOps helps bring down vulnerabilities, maximises test coverage, and intensifies the automation of security frameworks.

relies heavily on automation

security as a shared responsibility (don't make Security Silos)

don't overcomplicate security processes (Stringent Processes)

prioritize risks (stops Lack of visibility)
```

they had a cool static website which changed my cursor to a lightsaber and I had to guess which model was used based on comics lol 10/10