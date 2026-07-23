# RAVEN Usage Reference

## Command Syntax
```bash
raven.py [OPTIONS] TARGET
```

## Arguments

### Required
- **TARGET**: Target to scan (auto-detected as domain, email, or username)

### Optional Flags

#### `--json`
Output results in JSON format and save `.json` file.

**Effect**:
- Saves both `.txt` and `.json` files
- Prints JSON to console
- Enables programmatic processing

**Example**:
```bash
--json
```

#### `--output`, `-o` DIR
Custom output directory for results.

**Default**: `./raven-results/`

**Behavior**:
- Creates directory if it doesn't exist
- Saves timestamped results inside
- Overwrites no existing files

**Example**:
```bash
-o my-scans
--output /path/to/results
```

#### `--timeout` SECONDS
Timeout for tool execution.

**Default**: `60` seconds

**Applies to**:
- theHarvester execution
- Subfinder execution
- Shodan execution
- Holehe execution
- Sherlock execution

**Increase for**:
- Slow targets
- Large result sets
- Network delays

**Example**:
```bash
--timeout 120
```

#### `--version`
Show version information and exit.

**Output**: `raven 2.0.0`

#### `--help`, `-h`
Show help message and exit.

## Examples

### Domain Scans
```bash
# Basic domain scan
./raven.py example.com

# Domain scan with JSON output
./raven.py example.com --json

# Domain scan with custom output directory
./raven.py example.com -o domain-scans

# Domain scan with extended timeout
./raven.py slow-target.com --timeout 120
```

### Email Scans
```bash
# Basic email scan
./raven.py user@example.com

# Email scan with JSON output
./raven.py user@example.com --json

# Email scan with custom output
./raven.py user@example.com -o email-scans

# Email scan with extended timeout
./raven.py user@example.com --timeout 180
```

### Username Scans
```bash
# Basic username scan
./raven.py johndoe

# Username scan with JSON output
./raven.py johndoe --json

# Username scan with custom output
./raven.py johndoe -o username-scans

# Username scan with extended timeout
./raven.py johndoe --timeout 300
```

### Advanced Usage
```bash
# Comprehensive domain scan
./raven.py target.com --json -o thorough-scan --timeout 120

# Quick email check
./raven.py suspicious@email.com --timeout 30

# Username investigation with JSON
./raven.py target_user --json -o investigation

# All options combined
./raven.py target.com --json -o results --timeout 180
```

## Exit Codes

- `0`: Success
- `1`: Tool execution failure
- `2`: Invalid arguments or missing tools

## Output Files

### Naming Convention
```
{safe_target}_{timestamp}.{ext}
```

**Examples**:
- `example_com_20240722-150000.txt`
- `user_example_com_20240722-150000.json`
- `johndoe_20240722-150000.txt`

**Safe target**: Replaces `@` and `.` with `_`

### File Contents

#### TXT File
Human-readable formatted output:
```
Target: example.com
Type: domain

Emails (5):
  - contact@example.com
  - info@example.com

Subdomains (23):
  - www.example.com
  - mail.example.com

Exposure Indicators (3):
  - ISP: Example Corp
  - Country: US
```

#### JSON File
Structured data:
```json
{
  "target": "example.com",
  "type": "domain",
  "emails": ["contact@example.com"],
  "subdomains": ["www.example.com"],
  "exposures": [{"key": "ISP", "value": "Example Corp"}],
  "registrations": [],
  "accounts": [],
  "errors": []
}
```

## Tool Requirements

RAVEN requires these tools:

| Tool | Purpose | Required | Location |
|------|---------|----------|----------|
| subfinder | Subdomain discovery | Yes (domain mode) | ~/go/bin/ |
| holehe | Email registration scan | Yes (email mode) | ~/.local/bin/ |
| sherlock | Username search | Yes (username mode) | /usr/bin/ |
| theHarvester | Email discovery | Optional (domain mode) | PATH |
| shodan | Exposure check | Optional (domain mode) | PATH |

### Installation
```bash
# Required tools
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
pipx install holehe
pip install sherlock-project

# Optional tools
pip install theHarvester
pip install shodan
```

## Performance

### Typical Execution Times
| Mode | Target | Time (approx) |
|------|--------|---------------|
| Domain | example.com | 30-90s |
| Email | user@example.com | 60-180s |
| Username | johndoe | 60-300s |

### Factors Affecting Speed
- Number of results
- Tool performance
- Network conditions
- Timeout setting
- Target popularity

## Common Patterns

### Bug Bounty Recon
```bash
./raven.py target.com --json -o bugbounty/$(date +%Y%m%d)
```

### Security Investigation
```bash
./raven.py suspicious@email.com -o investigation
```

### Asset Mapping
```bash
./raven.py company.com --json -o inventory
```

### Username Tracking
```bash
./raven.py target_username -o tracking
```

### Daily Monitoring
```bash
./raven.py target.com -o daily/$(date +%Y%m%d)
```

## Troubleshooting Commands

### Verify Tools
```bash
ls -la ~/go/bin/subfinder ~/.local/bin/holehe /usr/bin/sherlock
which theHarvester shodan
```

### Test Tools Manually
```bash
~/go/bin/subfinder -silent -d example.com
~/.local/bin/holehe --only-used user@example.com
/usr/bin/sherlock johndoe --print-found --timeout 10
theHarvester -d example.com -b bing,duckduckgo
shodan domain example.com
```

### Check Permissions
```bash
chmod +x raven.py
```

### Debug Mode
Add verbosity flags to underlying tools if needed (modify tool paths in code).

## Integration Examples

### With Nuclei
```bash
# Scan subdomains for vulnerabilities
./raven.py target.com --json | jq -r '.subdomains[]' | nuclei -t cves/ -o vulns.txt
```

### With jq (JSON Processing)
```bash
# Extract all emails
./raven.py domain.com --json | jq -r '.emails[]'

# Extract account URLs
./raven.py username --json | jq -r '.accounts[].url'

# Count findings
./raven.py target.com --json | jq '[.emails, .subdomains, .accounts] | map(length)'
```

### With Bash Loops
```bash
# Multiple targets
for target in target1.com target2.com target3.com; do
    ./raven.py "$target" -o "scans/$target"
done
```

## Limitations

- Single target per execution
- No parallel scanning
- No resume capability
- Fixed tool locations
- No custom tool configurations
- No result deduplication
- Rate limiting by external services

## Target Type Detection

### Detection Rules
1. **Email**: Contains `@` symbol
2. **Domain**: Contains `.` and looks like a domain (valid TLD)
3. **Username**: Everything else

### Examples
| Input | Detected Type |
|-------|---------------|
| `user@example.com` | email |
| `example.com` | domain |
| `sub.example.com` | domain |
| `johndoe` | username |
| `john.doe` | username |
| `test_user-123` | username |

## Version

Current: **2.0.0**

Changes from 1.x:
- Complete rewrite in Python
- Proper argparse CLI
- JSON output support
- Better error handling
- Structured result files
- Auto-detection of target type
- Exit codes
