
# Cloud
```
cloud is a rented infrastructure

providers: AWS, Azure, Google Cloud, ...

compute, storage and networking is delivered through an API
```

# Service models

### Infrastructure as a Service (IaaS)
 - renting raw computing HW
 - we get a VM, virtual disk, a virtual network and install everything ourselves
 - eg. cloud running our own web stack

### Platform as a Service (PaaS)
 - renting a platform to run our applications
 - we upload our code and it runs

### Software as a Service (SaaS)
 - renting a software application
 - we just log in and it works (like a hotel room)
 - eg. cloud hosted email or office suite

# Deployment models

### Public cloud
 - shared infrastructure, operated by a provider
 
 - customers share the same HW, but are separated by virtualization

### Private cloud
 - dedicated infrastructure, operated by the organization itself

### Hybrid cloud
 - mix of public and private cloud, with some workloads running in each
 
 - connected by a private link or VPN

### Community cloud
 - shared infrastructure, operated by a community of organizations with similar interests or requirements
 
 - eg. government cloud

# Cloud storage and data exposure

### Object storage
```
Object storage is a bunch of containers (buckets) that hold files (objects)

each object is accessible through a URL, structured like: 

https://<provider-endpoint>/<bucket-name>/<object-key>
```
`bucket policies`
 - main access rule
 -  JSON document that defines who has access and what they can do

`ACLs (Access Control Lists)`

 - per-object access rules
 - legacy, simpler, still sometimes used

`Signed URLs`
  - temporary access to a specific object
  - zero credentials required

### How buckets end up public
1) defaults left over from development
2) block-public-access left disabled
3) insecure wildcard principals in bucket policies
4) leaked / long-lasting signed URLs

example: "Principal": "*" makes the bucket effectively public

### Attacker workflow
- automated tools: s3scanner, cloud_enum, curl
1) identify bucket names
    - company-backups
    - company-dev
    - company-prod
    - company-assets

2) Find public provider endpoints
    - HTTP request to their public URL for each bucket name - wait for confirmation

3) List the public bucket
 - GET `https://<provider-endpoint>/<bucket-name>/`
 - `grep` for interesting filenames

4) Download the files
 - take the treasure
 - Backups = Everything in one file.
 - source code, logs, config files
 - customer data for ransomware...

# Cloud networking

`virtual network`

 - also called VPC (Virtual Private Cloud)
 - private network
 - isolated from the public internet but within the provider's infrastructure
 
 - has it's own IP range

`subnet`

- smaller network within the virtual network
- public subnets have a route to the internet via IGW
- private subnets do not and are not directly reachable from the internet

### firewall primitives
`Security Groups (SGs)`
 - stateful firewall rules
 - applied to instances (VMs)
 - inbound and outbound rules
 - only has allow rules (else implicit deny)
 - eg. SSH (port 22) open to 0.0.0.0/0 (anyone)

`Network ACLs (NACLs)`
 - stateless firewall rules
 - applied to subnets
 - allow and deny rules

`Instance Metadata Service (IMDS)`
 - "special endpoint that provides information about the instance to the instance itself"

 - **small HTTP server that hands out credentials to anyone who can reach it**

 - IMDSv1 responds to any plain HTTP GET (bad)
 - IMDSv2 requires a session token first

---