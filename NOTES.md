# RAVEN Development Notes

## Tool Locations and Validation
- Subfinder: `~/go/bin/subfinder` (v2.11.0, 42MB)
- Holehe: `~/.local/bin/holehe` (symlink to pipx venv)
- Sherlock: `/usr/bin/sherlock` (225 bytes wrapper)
- theHarvester: `/usr/bin/theHarvester` (in PATH)
- Shodan: `~/.local/bin/shodan` (symlink to pipx venv)

All tools must be executable. Tool validation happens before scanning begins.

## Command Construction

### Subfinder
```bash
subfinder -silent -d <domain>
```
- `-silent`: Minimal output
- `-d`: Target domain
- Output: One subdomain per line

### theHarvester
```bash
theHarvester -d <domain> -b bing,duckduckgo,crtsh
```
- `-d`: Target domain
- `-b`: Data sources (bing, duckduckgo, crtsh)
- Output: Mixed format, need to extract emails

### Shodan
```bash
shodan domain <domain>
```
- Output: Key-value pairs
- Need to parse and extract relevant information

### Holehe
```bash
holehe --only-used --no-color <email>
```
- `--only-used`: Only show registered sites
- `--no-color`: Disable colors for parsing
- Output: Progress + registration status

### Sherlock
```bash
sherlock <username> --print-found --timeout 10 --no-color
```
- `--print-found`: Only show found accounts
- `--timeout`: Per-site timeout
- `--no-color`: Disable colors for parsing
- Output: Found account URLs

## Data Structures

### RavenResult
```python
@dataclass
class RavenResult:
    target: str
    target_type: str
    emails: List[str] = field(default_factory=list)
    subdomains: List[str] = field(default_factory=list)
    exposures: List[Dict[str, str]] = field(default_factory=list)
    registrations: List[Dict[str, str]] = field(default_factory=list)
    accounts: List[Dict[str, str]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
```

### JSON Output Format
```json
{
  "target": "example.com",
  "type": "domain",
  "emails": ["user@example.com"],
  "subdomains": ["www.example.com"],
  "exposures": [{"key": "ISP", "value": "Example Corp"}],
  "registrations": [],
  "accounts": [],
  "errors": []
}
```

## Error Handling Patterns

### Tool Not Found
```python
tool = check_tool("subfinder")
if not tool:
    eprint("subfinder not found - skipping subdomain discovery")
    raise SystemExit(1)
```

### Command Timeout
```python
try:
    result = subprocess.run(cmd, timeout=timeout, ...)
except subprocess.TimeoutExpired:
    return -1, "", f"command timed out after {timeout}s"
```

### Output Parsing
```python
for line in stdout.splitlines():
    line = line.strip()
    # Extract patterns using regex
    email_match = re.search(r"[a-zA-Z0-9._%+-]+@" + re.escape(domain), line)
    if email_match:
        emails.add(email_match.group(0))
```

## Target Type Detection Logic

```python
def detect_target_type(target: str) -> str:
    # Email has @
    if "@" in target:
        return "email"
    
    # Domain has dot and looks like a domain
    if "." in target:
        parts = target.split(".")
        if len(parts) >= 2:
            tld = parts[-1]
            # TLD is typically 2+ letters and all alphabetic
            if len(tld) >= 2 and tld.isalpha():
                # Additional checks for common TLDs
                common_tlds = {"com", "net", "org", "io", "co", "uk", "us", "de", "fr", "ru"}
                if tld.lower() in common_tlds or len(parts) > 2:
                    return "domain"
    
    # Default to username
    return "username"
```

## Output Formatting
- Dynamic content based on target type
- Limit output to 50 items (with "and X more" message)
- ANSI colors only for TTY output
- Banner only for TTY output
- Progress indicators for each scanning phase

## File Naming
- Timestamp: `YYYYMMDD-HHMMSS`
- Safe target name: Replace `@` and `.` with `_`
- Max length: 100 characters
- Format: `{safe_target}_{timestamp}.{ext}`

## Testing Results

### Domain Mode (vulnweb.com)
- Target type detected: domain
- Emails found: 0 (theHarvester found none)
- Subdomains found: 12
- Exposure indicators: 0 (shodan found none)
- Execution time: ~30 seconds

### Username Mode (testuser)
- Target type detected: username
- Accounts found: 189
- Platforms: Reddit, GitHub, Twitter, etc.
- Execution time: ~60 seconds

## Known Limitations
- Single target only (no batch processing)
- Sequential tool execution (no parallelism)
- Limited to tools in specific locations or PATH
- No resume capability
- No custom tool sources
- No result deduplication across tools
- theHarvester may be rate-limited
- shodan requires API key for full results

## Parsing Challenges

### theHarvester
- Mixed output format
- Need to extract emails from text
- May include irrelevant information

### Holehe
- Progress messages mixed with results
- Need to track current site being checked
- Color codes need to be disabled

### Sherlock
- Progress messages mixed with results
- Need to extract URLs from output
- Some platforms may return false positives

### Shodan
- Output format varies
- May require API key for full results
- Error messages need to be handled

## Performance Considerations
- Domain mode: 30-60 seconds (subfinder + theHarvester + shodan)
- Email mode: 60-120 seconds (holehe checks many sites)
- Username mode: 60-180 seconds (sherlock checks many platforms)
- Timeout setting affects each tool independently
- Network conditions significantly impact speed

## Security Notes
- All tools make external requests
- May trigger WAF/IDS detection
- Some tools require API keys (shodan)
- Results may contain sensitive information
- Authorisation required before scanning
