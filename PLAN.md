# RAVEN Development Plan

## Objective
Rebuild RAVEN as a REAL, complete, NO-AI CLI tool for OSINT and intelligence gathering with three modes: domain, email, and username scanning.

## Scope
- **Input**: Auto-detected target (domain/email/username)
- **Process**:
  - Domain → emails + subdomains + exposure
  - Email → registrations/breaches
  - Username → accounts across platforms
- **Output**: Structured text + JSON (optional) + saved results files
- **Constraints**: Python 3 stdlib only, no AI/LLM, no external dependencies

## Architecture

### Core Components
1. **Target Detection Layer**
   - Auto-detect target type (domain/email/username)
   - Validate input format
   - Route to appropriate scanner

2. **Tool Orchestration Layer**
   - Subfinder for subdomain discovery
   - HTTPX/theHarvester for email discovery
   - Holehe for email registrations
   - Sherlock for username search
   - Shodan for domain exposure
   - Tool validation and error handling

3. **Data Flow**
   ```
   Target → Type Detection → Scanner → Parser → Results → Display + Save
   ```

4. **CLI Interface**
   - Positional: target (auto-detected)
   - Flags: --json, -o, --timeout
   - Proper --help and --version
   - Exit non-zero on errors

### Error Handling
- Tool not found → Exit with clear message
- Tool timeout → Graceful failure
- Invalid input → Validation before execution
- Empty results → Report but don't fail

## Implementation Steps

### Phase 1: Foundation
- [x] Setup project structure
- [x] Create main CLI with argparse
- [x] Implement target type detection
- [x] Add banner and output formatting
- [x] Create data structures (RavenResult)

### Phase 2: Tool Integration
- [x] Subfinder integration (domain subdomains)
- [x] theHarvester integration (domain emails)
- [x] Shodan integration (domain exposure)
- [x] Holehe integration (email registrations)
- [x] Sherlock integration (username accounts)
- [x] Tool path validation

### Phase 3: Data Processing
- [x] Parse theHarvester email output
- [x] Parse subfinder subdomain output
- [x] Parse shodan exposure output
- [x] Parse holehe registration output
- [x] Parse sherlock account output
- [x] Result aggregation and formatting

### Phase 4: Output and Storage
- [x] Console output with progress steps
- [x] Results directory management
- [x] Timestamped result files
- [x] JSON and TXT file formats
- [x] Human-readable formatting

### Phase 5: Testing and Validation
- [x] Test domain mode (vulnweb.com)
- [x] Test username mode (testuser)
- [x] Test JSON output
- [x] Verify all error paths
- [x] Test timeout handling
- [x] Validate output formats

## Technical Decisions

### Why Python 3 stdlib?
- No external dependencies
- Easy to read and maintain
- Cross-platform compatibility
- Standard argparse for CLI

### Target Type Detection
Priority order:
1. Email: Contains `@`
2. Domain: Has `.` and looks like a domain (TLD validation)
3. Username: Everything else

### Tool Locations
- Subfinder: `~/go/bin/subfinder`
- Holehe: `~/.local/bin/holehe`
- Sherlock: `/usr/bin/sherlock`
- theHarvester: Search in PATH
- Shodan: Search in PATH

### Result Storage
- Timestamped filenames prevent overwrites
- Both human-readable (TXT) and machine-readable (JSON)
- Customizable output directory

## Success Criteria
- [x] Executes real commands against real targets
- [x] Produces actual emails/subdomains/accounts
- [x] Clean --help output
- [x] Proper exit codes
- [x] No fake or guessed data
- [x] Clear error messages
- [x] Results saved to disk
- [x] Auto-detection works correctly
- [x] All three modes functional

## Future Enhancements (Not in Scope)
- Multi-target support
- Concurrent scanning
- Custom tool configurations
- Output filtering/sorting
- Resume interrupted scans
- Additional data sources
- Integration with threat intel feeds
