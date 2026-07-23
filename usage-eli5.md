# RAVEN — Explain Like I'm 5 (ELI5) Guide

## What is RAVEN?

RAVEN is like a detective helper that looks for information about people, websites, and email addresses on the internet. Think of it as a magnifying glass that helps you see where information is hiding.

## The Three Detective Modes

### Mode 1: The Website Detective (Domain)
**When you use:** A website name like `example.com`

**What it does:**
1. **Finds email addresses** - Looks for email addresses that belong to this website
2. **Finds sub-websites** - Discovers smaller websites that are part of the big website (like `mail.example.com` or `shop.example.com`)
3. **Checks exposure** - Sees what information about this website is visible on the internet

**Real example:**
```
You type: raven.py vulnweb.com

RAVEN finds:
- No email addresses
- 12 sub-websites (like www.vulnweb.com, test.vulnweb.com)
- No exposure information

This tells you: This website has 12 parts but doesn't show email addresses publicly
```

### Mode 2: The Email Detective (Email)
**When you use:** An email address like `user@example.com`

**What it does:**
1. **Checks registrations** - Looks at hundreds of websites to see if this email is used there
2. **Finds accounts** - Tells you where this email has created accounts
3. **Shows platforms** - Lists the websites and apps where this email is registered

**Real example:**
```
You type: raven.py test@example.com

RAVEN finds:
- This email is registered on 15 websites
- It has accounts on Facebook, Twitter, Amazon, etc.
- These are the websites where this email is active

This tells you: Where this person uses this email address
```

### Mode 3: The Username Detective (Username)
**When you use:** A username like `johndoe`

**What it does:**
1. **Searches everywhere** - Looks at social media, forums, websites, and apps
2. **Finds profiles** - Discovers where this username is used
3. **Gives links** - Provides direct links to the profiles it finds

**Real example:**
```
You type: raven.py testuser

RAVEN finds:
- 189 accounts with this username
- Profiles on Reddit, GitHub, Twitter, Instagram, etc.
- Direct links to each profile

This tells you: Where this username appears online and what accounts exist
```

## How to Use RAVEN (Step by Step)

### Step 1: Decide what you want to find
- Want to know about a website? → Use the website name
- Want to know about an email? → Use the email address
- Want to know about a username? → Use the username

### Step 2: Run the command
```bash
# For a website
./raven.py example.com

# For an email
./raven.py user@example.com

# For a username
./raven.py johndoe
```

### Step 3: Read the results
RAVEN will show you what it found and save it to a file

## What the Flags Do (Explained Simply)

### `--json`
**What it means:** "Give me the results in a computer-friendly format"

**When to use:** When you want to use the results in another program or script

**Real example:**
```bash
# Normal output (human-readable)
./raven.py example.com
# Shows: nicely formatted text

# JSON output (computer-readable)
./raven.py example.com --json
# Shows: structured data that programs can understand
```

### `-o` or `--output`
**What it means:** "Save the results in this specific folder"

**When to use:** When you want to organize your results in different places

**Real example:**
```bash
# Save in default folder (raven-results)
./raven.py example.com
# Results go to: ./raven-results/

# Save in custom folder
./raven.py example.com -o my-investigation
# Results go to: ./my-investigation/
```

### `--timeout`
**What it means:** "Wait this many seconds before giving up"

**When to use:** When things are taking too long or when you want to be thorough

**Real example:**
```bash
# Quick scan (wait 30 seconds)
./raven.py example.com --timeout 30
# Faster but might miss some results

# Thorough scan (wait 120 seconds)
./raven.py example.com --timeout 120
# Slower but more complete
```

## Real Example: Complete Walkthrough

### Scenario: You want to investigate `vulnweb.com`

#### Step 1: Run the command
```bash
./raven.py vulnweb.com
```

#### Step 2: Watch RAVEN work
```
RAVEN says:
  OSINT & target intelligence · emails · subdomains · leaks
              ·  C o b r a S E C  ·
  authorised engagements only — you set the scope

[*] Target: vulnweb.com
[*] Timeout: 60s

[*] Detected target type: domain  ← RAVEN figured out this is a website

[*] Finding emails associated with domain
    Found 0 emails  ← RAVEN looked for emails but found none

[*] Finding subdomains (subfinder)
    Found 12 subdomains  ← RAVEN found 12 parts of the website

[*] Checking domain exposure (shodan)
    Found 0 exposure indicators  ← RAVEN checked for public info but found none
```

#### Step 3: Read the results
```
[+] RESULTS
Target: vulnweb.com
Type: domain

Subdomains (12):  ← Here's what RAVEN found
  - antivirus1.vulnweb.com
  - phptest.vulnweb.com
  - testasp.vulnweb.com
  - testpphp.vulnweb.com
  - testsp.vulnweb.com
  - u003etestasp.vulnweb.com
  - rest.vulnweb.com
  - testaspnet.vulnweb.com
  - testhtml5.vulnweb.com
  - testhmtml5.vulnweb.com
  - testphp.vulnweb.com
  - www.vulnweb.com

[+] RAVEN sweep complete.
```

#### Step 4: Find your saved results
```bash
# RAVEN saves results automatically
ls raven-results/
# You'll see: vulnweb_com_20240722-150000.txt
```

#### Step 5: What does this tell you?
- This website has 12 different parts (subdomains)
- It doesn't publicly show email addresses
- It doesn't have much public exposure information
- It looks like a testing website (names like "testphp", "testasp")

## Another Real Example: Email Investigation

### Scenario: You want to check where `test@example.com` is registered

#### Step 1: Run the command
```bash
./raven.py test@example.com
```

#### Step 2: Watch RAVEN work
```
[*] Detected target type: email  ← RAVEN figured out this is an email

[*] Scanning email registrations (holehe)
    Found 15 registrations  ← RAVEN found 15 places where this email is used
```

#### Step 3: Read the results
```
Registrations (15):
  - Facebook: registered
  - Twitter: registered
  - Amazon: registered
  - Netflix: registered
  ... (and 11 more)
```

#### Step 4: What does this tell you?
- This email is actively used on 15 major websites
- The person who owns this email has accounts on popular services
- You can use this information to understand their online presence

## Common Questions (ELI5)

### Q: How does RAVEN know if it's a website, email, or username?
**A:** RAVEN looks at the text you give it:
- If it has `@` → It's an email
- If it has `.` and looks like a website → It's a domain
- Everything else → It's a username

### Q: Why does it take so long?
**A:** RAVEN has to check hundreds of websites and services. It's like asking hundreds of librarians to look through their books. It takes time!

### Q: What if RAVEN finds nothing?
**A:** That's okay! It means:
- The target might be new
- The target might not be very popular
- The information might be private
- The target might not exist

### Q: Can I use RAVEN on anything I want?
**A:** No! You can only use RAVEN on:
- Websites you own
- Email addresses you have permission to check
- Usernames you're allowed to investigate
- Targets within bug bounty programs

**Important:** Using RAVEN without permission can be illegal!

### Q: What do I do with the results?
**A:** You can:
- Save them for later reference
- Use them to understand your target better
- Share them with your team (if allowed)
- Use them to plan security testing
- Help protect the target

### Q: Why are some results limited to 50 items?
**A:** To keep the output readable! RAVEN says "and X more" when there are lots of results. Use `--json` to see everything.

## Tips for Beginners

1. **Start simple**: Use the basic command first, then add flags
2. **Be patient**: RAVEN takes time to check everything
3. **Save your results**: Use `-o` to keep things organized
4. **Read the output**: RAVEN tells you what it's doing step by step
5. **Ask for help**: Use `--help` if you forget something

## Remember

- RAVEN is a tool to help you find information
- Always get permission before using it
- Be responsible with what you find
- Have fun learning about OSINT!

**Happy investigating! 🦅**
