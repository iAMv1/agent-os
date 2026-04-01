---
name: security-auditor
description: Use when you need to perform security audits, identify vulnerabilities, and harden applications against attacks. Covers OWASP Top 10, dependency scanning, configuration review, and security best practices.
when_to_use: Before production deployments, after major code changes, during security review cycles, when evaluating third-party dependencies, after security incidents, or when compliance requires a security assessment.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - WebSearch
arguments:
  - target
  - depth
  - framework
argument-hint: "[directory-or-file] [quick|standard|comprehensive] [owasp|cis|nist|comprehensive]"
---

# Security Auditor

Systematic security auditing that identifies vulnerabilities, misconfigurations, and attack vectors. Based on OWASP Top 10, industry standards, and real-world attack patterns.

<HARD-GATE>
Do NOT mark a security audit as complete without checking all OWASP Top 10 categories. Do NOT downplay a critical finding. Do NOT suggest fixes without verifying they actually resolve the vulnerability. Do NOT audit without considering the threat model.
</HARD-GATE>

## The Iron Law

Every security finding must include: the vulnerability class, the exact location, a proof-of-concept or exploit scenario, the potential impact, and a verified fix.

## When to Use

- Before deploying to production
- After significant code changes
- During scheduled security review cycles
- When evaluating third-party code or dependencies
- After a security incident
- When compliance requires a security assessment
- When onboarding new team members to security practices

## When NOT to Use

- Trivial changes with no security surface
- When you need an immediate emergency fix (audit after)
- For purely static content with no user interaction
- When a professional penetration test is legally required

## Threat Modeling

1. **Define the threat model**
   ```
   Threat Model:
   ├── Assets: What are we protecting?
   │   ├── Data (PII, credentials, financial)
   │   ├── Systems (servers, databases, APIs)
   │   └── Reputation (trust, compliance)
   ├── Attackers: Who might attack?
   │   ├── External attackers (hackers, competitors)
   │   ├── Malicious insiders
   │   └── Accidental misuse
   ├── Attack Vectors: How could they attack?
   │   ├── Network (MITM, DDoS)
   │   ├── Application (injection, auth bypass)
   │   ├── Social engineering (phishing)
   │   └── Supply chain (compromised dependencies)
   └── Impact: What happens if they succeed?
       ├── Data breach
       ├── Service disruption
       └── Financial/reputational damage
   ```

## The Process

### Phase 1: OWASP Top 10 Audit

2. **A01: Broken Access Control**
   - Verify authorization checks on every endpoint
   - Check for IDOR (Insecure Direct Object References)
   - Verify admin functions are protected
   - Check CORS configuration
   - Verify rate limiting is in place

3. **A02: Cryptographic Failures**
   - No plaintext passwords (use bcrypt, argon2)
   - TLS everywhere (no HTTP for sensitive data)
   - Strong encryption algorithms (AES-256, RSA-2048+)
   - No hardcoded secrets or keys
   - Proper key rotation strategy

4. **A03: Injection**
   - SQL: parameterized queries only, no string concatenation
   - NoSQL: parameterized queries, no $where with user input
   - Command: avoid shell execution, use safe APIs
   - XSS: output encoding, CSP headers, template auto-escaping
   - LDAP/SSRF: validate and sanitize all inputs

5. **A04: Insecure Design**
   - Business logic vulnerabilities
   - Missing security controls in design
   - Insecure default configurations
   - Lack of threat modeling

6. **A05: Security Misconfiguration**
   - Default credentials changed
   - Unnecessary features disabled
   - Error messages don't leak internals
   - Security headers set (CSP, X-Frame-Options, HSTS)
   - Directory listing disabled
   - HTTP methods restricted

7. **A06: Vulnerable and Outdated Components**
   - Check dependency versions for known CVEs
   - Remove unused dependencies
   - Pin dependency versions
   - Monitor for new vulnerabilities

8. **A07: Identification and Authentication Failures**
   - Strong password requirements
   - Multi-factor authentication available
   - Session management secure (HttpOnly, Secure, SameSite)
   - Brute force protection
   - Credential recovery is secure

9. **A08: Software and Data Integrity Failures**
   - CI/CD pipeline integrity
   - Signed packages and artifacts
   - No insecure deserialization
   - Integrity checks for critical data

10. **A09: Security Logging and Monitoring Failures**
    - Authentication attempts logged
    - Authorization failures logged
    - Input validation failures logged
    - Logs don't contain sensitive data
    - Alerting on suspicious activity

11. **A10: Server-Side Request Forgery (SSRF)**
    - Validate all URLs from user input
    - Block access to internal IPs (10.x, 172.16.x, 192.168.x, 127.x)
    - Use allowlists for external requests
    - Disable HTTP redirects in server-side requests

### Phase 2: Dependency & Configuration Audit

12. **Dependency scanning**
    ```
    Scan Commands:
    ├── npm:    npm audit
    ├── pip:    pip-audit, safety check
    ├── cargo:  cargo audit
    ├── go:     go list -m -u
    └── generic: Snyk, Trivy, Dependabot

    Check for:
    ├── Known CVEs
    ├── Unmaintained packages
    ├── Suspicious packages (typosquatting)
    └── License compliance
    ```

13. **Configuration review**
    - Environment variables not committed
    - `.env` files in `.gitignore`
    - Secrets management (Vault, AWS Secrets Manager)
    - No secrets in code, comments, or commit history
    - Infrastructure as code scanned for misconfigurations

### Phase 3: Code-Level Security Review

14. **Input validation**
    - All user input validated at the boundary
    - Type checking, length limits, format validation
    - Allowlists over blocklists
    - Validation on both client and server

15. **Output encoding**
    - HTML context: HTML entity encoding
    - JavaScript context: JavaScript escaping
    - URL context: URL encoding
    - CSS context: CSS escaping

16. **Error handling**
    - Generic error messages to users
    - Detailed errors only in logs
    - No stack traces in production responses
    - Proper HTTP status codes

### Phase 4: Security Headers & Hardening

17. **HTTP Security Headers**
    ```
    Required Headers:
    ├── Content-Security-Policy: Restrict resource loading
    ├── X-Content-Type-Options: nosniff
    ├── X-Frame-Options: DENY or SAMEORIGIN
    ├── Strict-Transport-Security: max-age=31536000; includeSubDomains
    ├── X-XSS-Protection: 0 (rely on CSP instead)
    ├── Referrer-Policy: strict-origin-when-cross-origin
    └── Permissions-Policy: Restrict browser features
    ```

18. **Cookie security**
    - `Secure` flag (HTTPS only)
    - `HttpOnly` flag (no JavaScript access)
    - `SameSite=Strict` or `Lax`
    - Appropriate `Path` and `Domain`
    - Short expiration for session cookies

## Anti-Slop Rules

<Good>
- "src/auth.ts:45 — CRITICAL (A07): Password hashed with MD5. MD5 is cryptographically broken. Fix: Use bcrypt with cost factor 12: `bcrypt.hash(password, 12)`."
- "src/api/users.js:23 — HIGH (A01): Missing authorization check on GET /users/:id. Any authenticated user can access any user's data. Fix: Add `requireOwnership(req, req.params.id)` middleware."
- "package.json — MEDIUM (A06): lodash@4.17.15 has known prototype pollution vulnerability (CVE-2020-28500). Fix: Update to lodash@4.17.21+."
</Good>

<Bad>
- "The code looks secure"
- "Maybe add some input validation"
- "Check for security issues"
- "Consider using HTTPS"
- Any finding without a specific vulnerability class (OWASP category)
- Any finding without a concrete exploit scenario
- Any finding without a verified fix
</Bad>

## Severity Classification

| Severity | Impact | Examples | Action |
|----------|--------|----------|--------|
| **Critical** | Full system compromise, data breach | SQL injection, auth bypass, RCE | Fix immediately, block deployment |
| **High** | Significant data exposure or control | IDOR, XSS, weak crypto | Fix before production |
| **Medium** | Partial information disclosure | Verbose errors, missing headers | Fix in next sprint |
| **Low** | Defense-in-depth improvement | Missing security header | Schedule for remediation |
| **Info** | Security best practice | Logging improvement | Document and track |

## Security Audit Report Template

```
Security Audit: [Target]
Date: [date]
Auditor: [who]
Framework: [OWASP/CIS/NIST]

## Executive Summary
- Overall risk level: [Critical/High/Medium/Low]
- Total findings: N
- Critical: N | High: N | Medium: N | Low: N | Info: N

## Threat Model
[Assets, attackers, attack vectors, impact]

## Findings
### [FINDING-001] Title
- **Category**: [OWASP category]
- **Severity**: [Critical/High/Medium/Low/Info]
- **Location**: [file:line or URL]
- **Description**: [What the vulnerability is]
- **Exploit Scenario**: [How it could be exploited]
- **Impact**: [What happens if exploited]
- **Fix**: [Specific remediation with code]
- **Status**: [Open/In Progress/Fixed/Verified]

## Dependency Scan Results
[Known vulnerabilities in dependencies]

## Configuration Issues
[Misconfigurations found]

## Recommendations
[Prioritized list of actions]
```

## Integration

Related skills: `code-reviewer`, `risk-assessment`, `quality-assurance`, `devops-engineer`
