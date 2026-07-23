#!/usr/bin/env python3
"""raven — OSINT & intelligence gathering.

Three modes by input type:
- domain → emails + subdomains + exposure
- email → where it's registered/breached
- username → accounts across platforms

Python 3 stdlib only. No AI, no keys, no external dependencies.

Author: CobraSEC (Jakk @jakkxbt)
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Union


VERSION = "2.0.0"
RESULTS_DIR = Path("raven-results")

# Tool paths
TOOL_PATHS = {
    "subfinder": Path.home() / "go" / "bin" / "subfinder",
    "holehe": Path.home() / ".local" / "bin" / "holehe",
    "sherlock": Path("/usr/bin/sherlock"),
    "theharvester": None,  # Will search in PATH
    "shodan": None,  # Will search in PATH
}


def eprint(msg: str) -> None:
    sys.stderr.write("raven: %s\n" % msg)
    sys.stderr.flush()


def check_tool(name: str) -> Optional[Path]:
    """Check if a tool exists and is executable."""
    path = TOOL_PATHS.get(name)
    
    if path and path.is_file() and os.access(path, os.X_OK):
        return path
    
    # For tools not in fixed paths, search PATH
    if name in ("theharvester", "shodan"):
        for p in os.environ.get("PATH", "").split(os.pathsep):
            tool_path = Path(p) / name
            if tool_path.is_file() and os.access(tool_path, os.X_OK):
                return tool_path
    
    return None


def run_command(cmd: List[str], timeout: int, capture: bool = True) -> tuple[int, str, str]:
    """Run a command, return (exit_code, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            timeout=timeout,
            capture_output=capture,
            text=True,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"command timed out after {timeout}s"
    except FileNotFoundError:
        return -2, "", f"command not found: {cmd[0]}"
    except Exception as e:
        return -3, "", f"unexpected error: {e}"


def detect_target_type(target: str) -> str:
    """Auto-detect target type: domain, email, or username."""
    # Email has @
    if "@" in target:
        return "email"
    
    # Domain has dot and looks like a domain (not a simple username with dots)
    # Domains typically have a TLD of 2-6+ letters after the last dot
    if "." in target:
        parts = target.split(".")
        if len(parts) >= 2:
            tld = parts[-1]
            # TLD is typically 2+ letters and all alphabetic
            if len(tld) >= 2 and tld.isalpha():
                # Additional check: if it starts with http:// or https://, it's definitely a domain
                if target.startswith("http://") or target.startswith("https://"):
                    return "domain"
                # If the part before the first dot looks like a subdomain or domain
                # (not just a single word), it's likely a domain
                if len(parts[0]) > 0 and (len(parts) > 2 or not parts[0].isalnum()):
                    return "domain"
                # If it has multiple dots, it's likely a domain (subdomain.domain.tld)
                if len(parts) > 2:
                    return "domain"
                # If it ends with a common TLD, it's a domain
                common_tlds = {"com", "net", "org", "io", "co", "uk", "us", "de", "fr", "ru", "info", "biz"}
                if tld.lower() in common_tlds:
                    return "domain"
    
    # Default to username
    return "username"


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


def find_emails_domain(domain: str, timeout: int) -> List[str]:
    """Find emails associated with a domain using theHarvester."""
    theharvester = check_tool("theharvester")
    if not theharvester:
        return []
    
    cmd = [
        str(theharvester),
        "-d", domain,
        "-b", "bing,duckduckgo,crtsh",
    ]
    
    exit_code, stdout, stderr = run_command(cmd, timeout)
    
    if exit_code != 0:
        return []
    
    emails = set()
    for line in stdout.splitlines():
        # Extract email addresses
        email_match = re.search(r"[a-zA-Z0-9._%+-]+@" + re.escape(domain), line)
        if email_match:
            emails.add(email_match.group(0))
    
    return sorted(list(emails))


def find_subdomains(domain: str, timeout: int) -> List[str]:
    """Find subdomains using subfinder."""
    subfinder = check_tool("subfinder")
    if not subfinder:
        eprint("subfinder not found - skipping subdomain discovery")
        raise SystemExit(1)
    
    cmd = [str(subfinder), "-silent", "-d", domain]
    exit_code, stdout, stderr = run_command(cmd, timeout)
    
    if exit_code != 0:
        eprint(f"subfinder failed (exit {exit_code}): {stderr.strip()}")
        raise SystemExit(1)
    
    subs = [line.strip() for line in stdout.strip().splitlines() if line.strip()]
    return subs


def check_exposure(domain: str, timeout: int) -> List[Dict[str, str]]:
    """Check domain exposure using shodan."""
    shodan = check_tool("shodan")
    if not shodan:
        return []
    
    cmd = ["shodan", "domain", domain]
    exit_code, stdout, stderr = run_command(cmd, timeout)
    
    if exit_code != 0:
        return []
    
    # Parse shodan output (simplified)
    exposures = []
    for line in stdout.splitlines():
        if ":" in line and not line.startswith("Error"):
            parts = line.split(":", 1)
            if len(parts) == 2:
                exposures.append({
                    "key": parts[0].strip(),
                    "value": parts[1].strip(),
                })
    
    return exposures


def scan_email(email: str, timeout: int) -> List[Dict[str, str]]:
    """Scan email for registrations using holehe."""
    holehe = check_tool("holehe")
    if not holehe:
        eprint("holehe not found - skipping email scan")
        raise SystemExit(1)
    
    cmd = [
        str(holehe),
        "--only-used",
        "--no-color",
        email,
    ]
    
    exit_code, stdout, stderr = run_command(cmd, timeout)
    
    if exit_code != 0:
        eprint(f"holehe failed (exit {exit_code}): {stderr.strip()}")
        raise SystemExit(1)
    
    registrations = []
    current_site = None
    
    for line in stdout.splitlines():
        line = line.strip()
        
        # Parse holehe output
        # Format typically: [*] Checking site.com
        #             [+] email@site.com is registered
        if line.startswith("[*]"):
            current_site = line.replace("[*]", "").strip()
        elif line.startswith("[+]") and "registered" in line.lower():
            if current_site:
                registrations.append({
                    "site": current_site,
                    "status": "registered",
                    "email": email,
                })
                current_site = None
    
    return registrations


def scan_username(username: str, timeout: int) -> List[Dict[str, str]]:
    """Scan username across platforms using sherlock."""
    sherlock = check_tool("sherlock")
    if not sherlock:
        eprint("sherlock not found - skipping username scan")
        raise SystemExit(1)
    
    cmd = [
        str(sherlock),
        username,
        "--print-found",
        "--timeout", str(min(timeout, 10)),  # Sherlock has its own timeout per site
        "--no-color",
    ]
    
    exit_code, stdout, stderr = run_command(cmd, timeout)
    
    if exit_code != 0:
        eprint(f"sherlock failed (exit {exit_code}): {stderr.strip()}")
        raise SystemExit(1)
    
    accounts = []
    
    for line in stdout.splitlines():
        line = line.strip()
        
        # Parse sherlock output
        # Format: [*] Checking username
        #         [+] Found: https://site.com/username
        if "[+] Found:" in line or "[+] " in line:
            # Extract URL
            url_match = re.search(r"https?://[^\s]+", line)
            if url_match:
                url = url_match.group(0)
                # Extract site name from URL
                site = url.split("//")[-1].split("/")[0]
                accounts.append({
                    "platform": site,
                    "url": url,
                    "username": username,
                })
    
    return accounts


def scan_domain(domain: str, timeout: int) -> RavenResult:
    """Scan a domain for emails, subdomains, and exposure."""
    result = RavenResult(target=domain, target_type="domain")
    
    # Step 1: Find emails
    print("[*] Finding emails associated with domain")
    try:
        emails = find_emails_domain(domain, timeout)
        result.emails = emails
        print(f"    Found {len(emails)} emails")
    except Exception as e:
        result.errors.append(f"Email search failed: {e}")
        print(f"    [!] Email search failed: {e}")
    
    # Step 2: Find subdomains
    print(f"[*] Finding subdomains (subfinder)")
    try:
        subdomains = find_subdomains(domain, timeout)
        result.subdomains = subdomains
        print(f"    Found {len(subdomains)} subdomains")
    except SystemExit:
        raise
    except Exception as e:
        result.errors.append(f"Subdomain search failed: {e}")
        print(f"    [!] Subdomain search failed: {e}")
    
    # Step 3: Check exposure
    print("[*] Checking domain exposure (shodan)")
    try:
        exposures = check_exposure(domain, timeout)
        result.exposures = exposures
        print(f"    Found {len(exposures)} exposure indicators")
    except Exception as e:
        result.errors.append(f"Exposure check failed: {e}")
        print(f"    [!] Exposure check failed: {e}")
    
    return result


def scan_email_target(email: str, timeout: int) -> RavenResult:
    """Scan an email for registrations."""
    result = RavenResult(target=email, target_type="email")
    
    print("[*] Scanning email registrations (holehe)")
    try:
        registrations = scan_email(email, timeout)
        result.registrations = registrations
        print(f"    Found {len(registrations)} registrations")
    except SystemExit:
        raise
    except Exception as e:
        result.errors.append(f"Email scan failed: {e}")
        print(f"    [!] Email scan failed: {e}")
    
    return result


def scan_username_target(username: str, timeout: int) -> RavenResult:
    """Scan a username across platforms."""
    result = RavenResult(target=username, target_type="username")
    
    print("[*] Scanning username across platforms (sherlock)")
    try:
        accounts = scan_username(username, timeout)
        result.accounts = accounts
        print(f"    Found {len(accounts)} accounts")
    except SystemExit:
        raise
    except Exception as e:
        result.errors.append(f"Username scan failed: {e}")
        print(f"    [!] Username scan failed: {e}")
    
    return result


def format_result(result: RavenResult) -> str:
    """Format result as human-readable text."""
    lines = []
    lines.append(f"Target: {result.target}")
    lines.append(f"Type: {result.target_type}")
    lines.append("")
    
    if result.emails:
        lines.append(f"Emails ({len(result.emails)}):")
        for email in result.emails:
            lines.append(f"  - {email}")
        lines.append("")
    
    if result.subdomains:
        lines.append(f"Subdomains ({len(result.subdomains)}):")
        for sub in result.subdomains[:50]:  # Limit to 50
            lines.append(f"  - {sub}")
        if len(result.subdomains) > 50:
            lines.append(f"  ... and {len(result.subdomains) - 50} more")
        lines.append("")
    
    if result.exposures:
        lines.append(f"Exposure Indicators ({len(result.exposures)}):")
        for exp in result.exposures[:20]:
            lines.append(f"  - {exp.get('key', '')}: {exp.get('value', '')}")
        if len(result.exposures) > 20:
            lines.append(f"  ... and {len(result.exposures) - 20} more")
        lines.append("")
    
    if result.registrations:
        lines.append(f"Registrations ({len(result.registrations)}):")
        for reg in result.registrations[:50]:
            lines.append(f"  - {reg.get('site', '')}: {reg.get('status', '')}")
        if len(result.registrations) > 50:
            lines.append(f"  ... and {len(result.registrations) - 50} more")
        lines.append("")
    
    if result.accounts:
        lines.append(f"Accounts ({len(result.accounts)}):")
        for acc in result.accounts[:50]:
            lines.append(f"  - {acc.get('platform', '')}: {acc.get('url', '')}")
        if len(result.accounts) > 50:
            lines.append(f"  ... and {len(result.accounts) - 50} more")
        lines.append("")
    
    if result.errors:
        lines.append(f"Errors ({len(result.errors)}):")
        for err in result.errors:
            lines.append(f"  - {err}")
        lines.append("")
    
    if not any([result.emails, result.subdomains, result.exposures, 
                result.registrations, result.accounts]):
        lines.append("No results found.")
    
    return "\n".join(lines)


def format_result_json(result: RavenResult) -> str:
    """Format result as JSON."""
    data = {
        "target": result.target,
        "type": result.target_type,
        "emails": result.emails,
        "subdomains": result.subdomains,
        "exposures": result.exposures,
        "registrations": result.registrations,
        "accounts": result.accounts,
        "errors": result.errors,
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


def save_results(result: RavenResult, output_dir: Path, as_json: bool) -> None:
    """Save results to files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    safe_name = result.target.replace("@", "_").replace(".", "_")[:100]
    base_name = f"{safe_name}_{ts}"
    
    # Save text report
    txt_path = output_dir / f"{base_name}.txt"
    txt_path.write_text(format_result(result) + "\n", encoding="utf-8")
    
    # Save JSON if requested
    if as_json:
        json_path = output_dir / f"{base_name}.json"
        json_path.write_text(format_result_json(result) + "\n", encoding="utf-8")
        eprint(f"Results saved to {json_path}")
    else:
        eprint(f"Results saved to {txt_path}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="raven",
        description=(
            "OSINT & intelligence gathering: domains, emails, usernames. "
            "Auto-detects target type and runs appropriate scans."
        ),
        epilog=(
            "Examples:\n"
            "  raven example.com              # Domain scan\n"
            "  raven user@example.com         # Email scan\n"
            "  raven johndoe                  # Username scan\n"
            "  raven example.com --json       # JSON output\n"
            "  raven user@example.com -o scans\n"
            "\n"
            "Required tools:\n"
            "  - subfinder (~/go/bin/): subdomain discovery\n"
            "  - holehe (~/.local/bin/): email registration scan\n"
            "  - sherlock (/usr/bin/): username search\n"
            "  - theHarvester (PATH): email discovery (optional)\n"
            "  - shodan (PATH): exposure check (optional)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "target",
        help="Target: domain, email, or username (auto-detected)",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format and save .json file",
    )
    p.add_argument(
        "-o",
        "--output",
        metavar="DIR",
        help="Output directory for results (default: ./raven-results)",
    )
    p.add_argument(
        "--timeout",
        type=int,
        default=60,
        metavar="SECONDS",
        help="Timeout for tools in seconds (default: 60)",
    )
    p.add_argument(
        "--version",
        action="version",
        version=f"raven {VERSION}",
    )
    return p


def print_banner() -> None:
    """Print the RAVEN banner."""
    if sys.stdout.isatty():
        banner = r"""
   __    __            _____             
  / /_  / /____  ____/ / (_)___  _____ 
 / __ \/ __/ _ \/ __  / / / __ \/ ___/
/ /_/ / /_/  __/ /_/ / / / /_/ / /    
/_.___/\__/\___/\__,_/_/_/\____/_/     
"""
        print(banner)
    print("  OSINT & target intelligence · emails · subdomains · leaks")
    print("              ·  C o b r a S E C  ·")
    print("  authorised engagements only — you set the scope")
    print()


def main(argv: List[str] | None = None) -> int:
    args = build_parser().parse_args(argv if argv is not None else None)
    
    # Validate timeout
    if args.timeout <= 0:
        eprint("--timeout must be positive")
        return 1
    
    print_banner()
    print(f"[*] Target: {args.target}")
    print(f"[*] Timeout: {args.timeout}s")
    print()
    
    # Detect target type
    target_type = detect_target_type(args.target)
    print(f"[*] Detected target type: {target_type}")
    print()
    
    # Run appropriate scan
    try:
        if target_type == "domain":
            result = scan_domain(args.target, args.timeout)
        elif target_type == "email":
            result = scan_email_target(args.target, args.timeout)
        else:  # username
            result = scan_username_target(args.target, args.timeout)
    except SystemExit:
        return 1
    
    # Display results
    print()
    print("[+] RESULTS")
    print(format_result(result))
    
    # Save results
    output_dir = Path(args.output) if args.output else RESULTS_DIR
    save_results(result, output_dir, args.json)
    
    # Print JSON if requested
    if args.json:
        print()
        print("[+] JSON OUTPUT")
        print(format_result_json(result))
    
    print()
    print("[+] RAVEN sweep complete.")
    
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as e:
        eprint(f"fatal: {e}")
        raise SystemExit(1)
