# RAVEN User Guide

## Overview
RAVEN is an OSINT (Open Source Intelligence) tool that automates the gathering of intelligence on targets across three modes: domains, emails, and usernames. It orchestrates multiple specialized tools into a unified workflow with structured output.

## What RAVEN Does

### Domain Mode
When you provide a domain (e.g., `example.com`), RAVEN:
1. **Finds emails** associated with the domain using theHarvester
2. **Discovers subdomains** using subfinder
3. **Checks exposure** indicators using shodan

### Email Mode
When you provide an email address (e.g., `user@example.com`), RAVEN:
1. **Scans registrations** across hundreds of websites using holehe
2. **Identifies breaches** where the email is registered
3. **Reports platforms** where the email is in use

### Username Mode
When you provide a username (e.g., `johndoe`), RAVEN:
1. **Searches platforms** across the internet using sherlock
2. **Finds accounts** with that username
3. **Provides URLs** to discovered profiles

## Installation

### Prerequisites
RAVEN requires these tools to be installed:

```bash
# Subfinder (Go binary)
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

# Holehe (Python tool)
pipx install holehe

# Sherlock (Python tool)
pip install sherlock-project

# theHarvester (Python tool) - optional for email discovery
pip install theHarvester

# Shodan CLI (Python tool) - optional for exposure checks
pip install shodan
```

### RAVEN Installation
```bash
# Make executable
chmod +x raven.py

# Optional: Add to PATH
ln -s $(pwd)/raven.py /usr/local/bin/raven
```

## Quick Start

### Basic Domain Scan
```bash
./raven.py example.com
```
This will:
1. Auto-detect it's a domain
2. Find emails, subdomains, and exposure
3. Display results in a structured format
4. Save results to `./raven-results/`

### Basic Email Scan
```bash
./raven.py user@example.com
```
This will:
1. Auto-detect it's an email
2. Scan for registrations across platforms
3. Display where the email is registered
4. Save results to `./raven-results/`

### Basic Username Scan
```bash
./raven.py johndoe
```
This will:
1. Auto-detect it's a username
2. Search for accounts across platforms
3. Display discovered accounts with URLs
4. Save results to `./raven-results/`

## Understanding the Output

### Console Output
```
  OSINT & target intelligence · emails · subdomains · leaks
              ·  C o b r a S E C  ·
  authorised engagements only — you set the scope

[*] Target: example.com
[*] Timeout: 60s

[*] Detected target type: domain

[*] Finding emails associated with domain
    Found 5 emails
[*] Finding subdomains (subfinder)
    Found 23 subdomains
[*] Checking domain exposure (shodan)
    Found 3 exposure indicators

[+] RESULTS
Target: example.com
Type: domain

Emails (5):
  - contact@example.com
  - info@example.com
  - support@example.com
  - admin@example.com
  - webmaster@example.com

Subdomains (23):
  - www.example.com
  - mail.example.com
  - api.example.com
  ...

Exposure Indicators (3):
  - ISP: Example Corporation
  - Country: US
  - Ports: 80, 443, 8080

[+] RAVEN sweep complete.
```

### Result Files
- **TXT file**: Human-readable formatted text
- **JSON file**: Structured data for parsing/automation
- **Naming**: `{target}_{timestamp}.{ext}`

### Interpreting Results
- **Emails**: Addresses associated with the domain
- **Subdomains**: Discovered subdomains (may include inactive ones)
- **Exposure**: Information about the domain's internet presence
- **Registrations**: Websites where an email is registered
- **Accounts**: Social media and platform accounts for a username

## Common Use Cases

### Bug Bounty Recon
```bash
# Discover attack surface for a target
./raven.py target.com --json -o bugbounty/$(date +%Y%m%d)

# Find email addresses for phishing simulation
./raven.py company.com
```

### Security Research
```bash
# Investigate a suspicious email
./raven.py suspicious@email.com

# Track a username across platforms
./raven.py target_username
```

### Asset Inventory
```bash
# Map all subdomains for a company
./raven.py enterprise.com -o inventory

# Find all registrations for a corporate email
./raven.py user@company.com
```

### Threat Intelligence
```bash
# Investigate a potential threat actor
./raven.py threat_actor_username

# Check domain exposure and subdomains
./raven.py suspicious-domain.com
```

## Performance Considerations

### Execution Times
- **Domain mode**: 30-90 seconds
- **Email mode**: 60-180 seconds (checks hundreds of sites)
- **Username mode**: 60-300 seconds (checks many platforms)

### Speed vs. Thoroughness
- **Faster**: Use shorter timeouts
- **More thorough**: Use longer timeouts
- **Quick check**: Domain mode with default timeout
- **Deep dive**: Email/username modes with extended timeout

### Timeout Settings
```bash
# Quick scan (may miss some results)
./raven.py target.com --timeout 30

# Standard scan (default)
./raven.py target.com --timeout 60

# Thorough scan (for slow targets)
./raven.py target.com --timeout 120
```

## Troubleshooting

### Tool Not Found
```
raven: subfinder not found - skipping subdomain discovery
```
**Solution**: Install the missing tool

### Timeout Errors
```
raven: command timed out after 60s
```
**Solution**: Increase timeout with `--timeout`

### No Results Found
```
[*] Found 0 emails
[*] Found 0 subdomains
```
**Possible causes**:
- Target has no associated data
- Tools rate-limited
- Network issues
- Target is new or obscure

### Wrong Type Detection
```
[*] Detected target type: username
# (but you wanted domain scan)
```
**Solution**: Ensure domain has proper format (e.g., `example.com`, not `example`)

## Best Practices

1. **Start with default scan**: Use basic command first, then add flags as needed
2. **Save results**: Use `-o` to organize scans by project/target
3. **Use JSON for automation**: `--json` for programmatic processing
4. **Respect rate limits**: Don't run repeatedly against same target
5. **Validate findings**: Manual verification before reporting
6. **Check scope**: Ensure you're authorized to gather this intelligence
7. **Combine results**: Cross-reference findings from different modes

## Security Notes

- **Passive reconnaissance**: Most tools don't directly touch the target
- **Active queries**: Some tools make external requests to various services
- **Authorization**: Only gather intelligence on targets you have permission to research
- **Detection**: OSINT activities can be detected by service providers
- **Rate limiting**: Tools have built-in rate limits, but be cautious
- **Data sensitivity**: Results may contain sensitive information

## Legal and Ethical Use

RAVEN is an OSINT tool for authorized security testing and research only:
- Bug bounty programs (within scope)
- Security research (with permission)
- Threat intelligence gathering
- Asset inventory for owned infrastructure
- Incident response investigations

**Unauthorized intelligence gathering may be illegal and unethical.**

## Advanced Usage

### Combining with Other Tools
```bash
# Feed subdomains to vulnerability scanner
./raven.py target.com --json | jq -r '.subdomains[]' | nuclei -t cves/

# Check email breaches with additional tools
./raven.py user@example.com
# Then use haveibeenpwned for additional breach data
```

### Custom Output Processing
```bash
# Extract only email addresses
./raven.py domain.com --json | jq -r '.emails[]'

# Extract only account URLs
./raven.py username --json | jq -r '.accounts[].url'

# Count findings by type
./raven.py target.com --json | jq '[.emails, .subdomains, .exposures] | map(length) | add'
```

### Integration Notebooks
JSON output can be easily parsed in Jupyter notebooks or other analysis tools for deeper investigation.

## Support and Contributing

This tool is part of CobraSEC's offensive security toolkit.
For issues, questions, or contributions: https://github.com/jakkxbt

## Version History

- **2.0.0**: Complete rewrite in Python, proper CLI, JSON output, auto-detection
- **1.x**: Original bash version
