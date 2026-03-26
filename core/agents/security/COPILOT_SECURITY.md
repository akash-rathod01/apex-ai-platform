# Copilot Instructions — Security Agent

## ✅ Purpose
Performs **application security scanning**, business-rule violations, and vulnerability assessments.

---

## ✅ Responsibilities

### Core Functions
- **Run security scans** via OWASP ZAP / Nmap / Nikto (through plugins)
- **Interpret Blueprint "security expectations"** from YAML definitions
- **Detect security vulnerabilities** systematically
- **Validate security baselines** against historical data
- **Correlate logs with vulnerabilities** for root cause analysis
- **Generate security reports** with risk scores

### Vulnerability Detection
Detect and report:
- **XSS** (Cross-Site Scripting)
- **SQL Injection**
- **CSRF** (Cross-Site Request Forgery)
- **Broken Access Control**
- **Insecure Redirects**
- **Misconfigured Headers** (CORS, CSP, etc.)
- **Authentication/Authorization flaws**
- **Sensitive Data Exposure**
- **Security Misconfigurations**
- **Using Components with Known Vulnerabilities**

---

## ✅ What NOT to do

### ❌ FORBIDDEN Actions
- ❌ Do NOT run scans on PROD by default (unless explicitly configured)
- ❌ Do NOT attempt exploitation beyond scanning
- ❌ Do NOT guess vulnerability severity (use CVSS/risk scoring)
- ❌ Do NOT make pass/fail decisions (validation engine decides)
- ❌ Do NOT store scan scripts permanently
- ❌ Do NOT hardcode scanner configurations
- ❌ Do NOT bypass security policies
- ❌ Do NOT run destructive tests

---

## ✅ What Copilot Should Generate

### Modular Components
```python
# ✅ GOOD: Security scan orchestration
class SecurityScanner:
    def scan_vulnerabilities(self, blueprint: Blueprint) -> ScanResults:
        """Run security scans based on blueprint"""
        pass
    
    def score_risk(self, vulnerability: Vulnerability) -> RiskScore:
        """Calculate risk score using CVSS"""
        pass
    
    def correlate_with_logs(self, vuln: Vulnerability, logs: List[str]) -> Correlation:
        """Correlate vulnerability with execution logs"""
        pass
```

### Generate These Types of Code
- ✅ Scanning task orchestrators
- ✅ Risk scoring functions (CVSS-based)
- ✅ Correlation logic with perf/API tests
- ✅ Security blueprint mappers
- ✅ Vulnerability parsers (for ZAP, Nmap outputs)
- ✅ Compliance checkers (OWASP Top 10, CWE)
- ✅ Security baseline validators
- ✅ Report generators

---

## ✅ What Copilot Should NOT Generate

### ❌ AVOID These Patterns
```python
# ❌ BAD: Hardcoded scan configuration
zap_config = """
<configuration>
  <target>https://prod.example.com</target>  # Never hardcode prod!
  <attack>aggressive</attack>
</configuration>
"""

# ❌ BAD: Exploitation attempts
def exploit_sql_injection(url):
    # Actual exploitation code  # DON'T DO THIS
    pass

# ❌ BAD: Guessing severity
if "SQL" in vulnerability.type:
    return "CRITICAL"  # Use CVSS scoring instead
```

---

## ✅ Tools Used

### Plugin-Based Tool Access
```python
# ✅ CORRECT: Load via plugin system
zap = self.plugins.load("owasp-zap", version="2.14")
nmap = self.plugins.load("nmap", version="7.94")
nikto = self.plugins.load("nikto", version="2.5")
bandit = self.plugins.load("bandit")  # Python SAST
semgrep = self.plugins.load("semgrep")  # Multi-language SAST

# ❌ INCORRECT: Direct execution
import subprocess
subprocess.run(["zap.sh", "-daemon"])  # DON'T
```

### Primary Tools
- **OWASP ZAP** (via plugin) - Dynamic Application Security Testing (DAST)
- **Nmap** (via plugin) - Port scanning, service detection
- **Nikto** (via plugin) - Web server scanning
- **Bandit** (via plugin) - Python static analysis
- **Semgrep** (via plugin) - SAST for multiple languages
- **Safety** (via plugin) - Dependency vulnerability scanning

---

## ✅ Blueprint-First Architecture

### Reading Security Blueprints
```yaml
# security_auth.blueprint.yaml
blueprint_id: "sec_auth_001"
type: security
target:
  base_url: "${BASE_URL}"
  auth_endpoint: "/api/auth/login"
  protected_endpoints:
    - "/api/user/profile"
    - "/api/admin/settings"

security_expectations:
  authentication:
    - type: JWT
    - secure_storage: true
    - token_expiry: 3600
  
  authorization:
    - rbac_enforced: true
    - principle_of_least_privilege: true
  
  headers:
    - X-Frame-Options: "DENY"
    - Content-Security-Policy: "default-src 'self'"
    - Strict-Transport-Security: "max-age=31536000"
  
  vulnerabilities_to_check:
    - XSS
    - SQL_INJECTION
    - CSRF
    - BROKEN_AUTH
    - SENSITIVE_DATA_EXPOSURE

scan_configuration:
  scan_type: active  # or passive
  depth: moderate    # light, moderate, deep
  exclude_patterns:
    - "/api/admin/delete/*"  # Don't scan destructive endpoints
```

### Blueprint-Driven Execution
```python
# ✅ CORRECT: Blueprint-driven security scanning
blueprint = self.blueprint_loader.load("sec_auth_001")

# Generate scan configuration from blueprint
scan_config = self.config_generator.generate_from_blueprint(blueprint)

# Execute via plugin
zap_plugin = self.plugins.load("owasp-zap")
scan_results = zap_plugin.scan(scan_config)

# Parse and risk-score vulnerabilities
vulnerabilities = self.parser.parse_results(scan_results)
scored_vulns = [self.risk_scorer.score(v) for v in vulnerabilities]

# Validate against security expectations
result = self.validation_engine.validate(
    vulnerabilities=scored_vulns,
    expectations=blueprint.security_expectations,
    baseline=historical_baseline
)
```

---

## ✅ Risk Scoring

### CVSS-Based Risk Scoring
```python
class RiskScorer:
    def calculate_cvss_score(self, vulnerability: Vulnerability) -> CVSSScore:
        """Calculate CVSS score for vulnerability"""
        
        # CVSS v3.1 metrics
        attack_vector = self._assess_attack_vector(vulnerability)
        attack_complexity = self._assess_attack_complexity(vulnerability)
        privileges_required = self._assess_privileges(vulnerability)
        user_interaction = self._assess_user_interaction(vulnerability)
        scope = self._assess_scope(vulnerability)
        confidentiality_impact = self._assess_confidentiality(vulnerability)
        integrity_impact = self._assess_integrity(vulnerability)
        availability_impact = self._assess_availability(vulnerability)
        
        # Calculate base score using CVSS formula
        base_score = self._calculate_base_score(
            attack_vector, attack_complexity, privileges_required,
            user_interaction, scope, confidentiality_impact,
            integrity_impact, availability_impact
        )
        
        return CVSSScore(
            base_score=base_score,
            severity=self._get_severity(base_score),
            vector_string=self._generate_vector_string(...)
        )
    
    def _get_severity(self, score: float) -> str:
        """Map CVSS score to severity"""
        if score >= 9.0:
            return "CRITICAL"
        elif score >= 7.0:
            return "HIGH"
        elif score >= 4.0:
            return "MEDIUM"
        elif score > 0.0:
            return "LOW"
        else:
            return "NONE"
```

---

## ✅ Vulnerability Detection

### Systematic Vulnerability Checking
```python
class VulnerabilityDetector:
    def check_xss(self, target: str) -> List[XSSVulnerability]:
        """Detect XSS vulnerabilities"""
        zap = self.plugins.load("owasp-zap")
        
        scan_config = {
            "target": target,
            "scan_type": "xss",
            "payloads": self._get_xss_payloads()
        }
        
        results = zap.scan(scan_config)
        return self._parse_xss_results(results)
    
    def check_sql_injection(self, target: str) -> List[SQLiVulnerability]:
        """Detect SQL injection vulnerabilities"""
        zap = self.plugins.load("owasp-zap")
        
        scan_config = {
            "target": target,
            "scan_type": "sqli",
            "payloads": self._get_sqli_payloads()
        }
        
        results = zap.scan(scan_config)
        return self._parse_sqli_results(results)
    
    def check_security_headers(self, response: Response) -> List[HeaderIssue]:
        """Check for security header misconfigurations"""
        issues = []
        
        required_headers = {
            "X-Frame-Options": ["DENY", "SAMEORIGIN"],
            "X-Content-Type-Options": ["nosniff"],
            "Strict-Transport-Security": None,  # Should exist
            "Content-Security-Policy": None
        }
        
        for header, expected_values in required_headers.items():
            if header not in response.headers:
                issues.append(HeaderIssue(
                    header=header,
                    issue="MISSING",
                    severity="MEDIUM"
                ))
            elif expected_values and response.headers[header] not in expected_values:
                issues.append(HeaderIssue(
                    header=header,
                    issue="INCORRECT_VALUE",
                    actual=response.headers[header],
                    expected=expected_values,
                    severity="MEDIUM"
                ))
        
        return issues
```

---

## ✅ Security Baseline Validation

### Compare Against Security Baseline
```python
class SecurityBaselineValidator:
    def validate_against_baseline(
        self,
        current_vulns: List[Vulnerability],
        baseline: SecurityBaseline
    ) -> BaselineComparisonResult:
        """Validate current vulnerabilities against baseline"""
        
        new_vulnerabilities = []
        resolved_vulnerabilities = []
        persistent_vulnerabilities = []
        
        current_vuln_ids = {v.id for v in current_vulns}
        baseline_vuln_ids = {v.id for v in baseline.vulnerabilities}
        
        # Find new vulnerabilities (regressions)
        for vuln in current_vulns:
            if vuln.id not in baseline_vuln_ids:
                new_vulnerabilities.append(vuln)
            else:
                persistent_vulnerabilities.append(vuln)
        
        # Find resolved vulnerabilities
        for vuln in baseline.vulnerabilities:
            if vuln.id not in current_vuln_ids:
                resolved_vulnerabilities.append(vuln)
        
        return BaselineComparisonResult(
            new_count=len(new_vulnerabilities),
            resolved_count=len(resolved_vulnerabilities),
            persistent_count=len(persistent_vulnerabilities),
            new_vulnerabilities=new_vulnerabilities,
            resolved_vulnerabilities=resolved_vulnerabilities,
            has_regression=len(new_vulnerabilities) > 0
        )
```

---

## ✅ Environment Safety

### Ensure Safe Scanning
```python
class SecurityAgent(BaseAgent):
    def execute_security_scan(self, blueprint_id: str) -> SecurityResult:
        blueprint = self.blueprint_loader.load(blueprint_id)
        
        # ✅ CRITICAL: Check environment before scanning
        environment = self._get_environment(blueprint.target.base_url)
        
        if environment == "PRODUCTION":
            # Check if prod scanning is explicitly allowed
            if not blueprint.allow_production_scan:
                raise SecurityError(
                    "Production scanning not allowed. "
                    "Set 'allow_production_scan: true' in blueprint to override."
                )
            
            # Use passive scanning only in production
            scan_type = "passive"
        else:
            scan_type = blueprint.scan_configuration.scan_type
        
        # Exclude destructive endpoints
        excluded = blueprint.scan_configuration.exclude_patterns or []
        
        # Execute scan safely
        return self._execute_scan(
            target=blueprint.target,
            scan_type=scan_type,
            excluded_patterns=excluded
        )
```

---

## ✅ Log Correlation

### Correlate Vulnerabilities with Logs
```python
class VulnerabilityCorrelator:
    def correlate_with_logs(
        self,
        vulnerability: Vulnerability,
        execution_logs: List[LogEntry]
    ) -> CorrelationResult:
        """Correlate vulnerability with execution logs for root cause"""
        
        # Find logs around vulnerability detection time
        relevant_logs = self._filter_logs_by_time(
            logs=execution_logs,
            timestamp=vulnerability.detected_at,
            window_seconds=60
        )
        
        # Search for related error patterns
        related_errors = []
        for log in relevant_logs:
            if self._is_related_to_vulnerability(log, vulnerability):
                related_errors.append(log)
        
        # Use LLM to analyze correlation
        if related_errors:
            analysis = self.llm_adapter.generate(
                prompt=f"""
                Vulnerability: {vulnerability.type}
                Location: {vulnerability.location}
                Related logs:
                {self._format_logs(related_errors)}
                
                Analyze the root cause of this vulnerability based on the logs.
                """,
                provider="openai",
                temperature=0.3
            )
        else:
            analysis = "No direct log correlation found"
        
        return CorrelationResult(
            has_correlation=len(related_errors) > 0,
            related_logs=related_errors,
            root_cause_analysis=analysis
        )
```

---

## ✅ Code Generation Examples

### ✅ GOOD: Modular, Blueprint-Driven
```python
class SecurityAgent(BaseAgent):
    def __init__(self, runtime, llm_adapter, plugin_loader):
        super().__init__(runtime, llm_adapter, plugin_loader)
        self.detector = VulnerabilityDetector(plugin_loader)
        self.scorer = RiskScorer()
        self.correlator = VulnerabilityCorrelator(llm_adapter)
    
    def execute_security_scan(self, blueprint_id: str) -> SecurityResult:
        # Load blueprint
        blueprint = self.blueprint_loader.load(blueprint_id)
        
        # Safety check
        self._validate_scan_safety(blueprint)
        
        # Run scans based on blueprint
        vulnerabilities = []
        
        if "XSS" in blueprint.vulnerabilities_to_check:
            xss_vulns = self.detector.check_xss(blueprint.target.base_url)
            vulnerabilities.extend(xss_vulns)
        
        if "SQL_INJECTION" in blueprint.vulnerabilities_to_check:
            sqli_vulns = self.detector.check_sql_injection(blueprint.target.base_url)
            vulnerabilities.extend(sqli_vulns)
        
        # Risk score all vulnerabilities
        scored_vulns = [self.scorer.score(v) for v in vulnerabilities]
        
        # Get baseline and compare
        baseline = self.get_baseline(blueprint_id)
        comparison = self.validate_against_baseline(scored_vulns, baseline)
        
        # Correlate with logs if available
        if blueprint.correlate_with_logs:
            logs = self.get_execution_logs(blueprint_id)
            for vuln in scored_vulns:
                vuln.correlation = self.correlator.correlate_with_logs(vuln, logs)
        
        # Send to validation engine
        return self.validation_engine.validate(
            vulnerabilities=scored_vulns,
            baseline_comparison=comparison,
            expectations=blueprint.security_expectations
        )
```

---

## ✅ File Structure

```
core/agents/security/
├── __init__.py
├── agent.py                      # Main security agent
├── COPILOT_SECURITY.md          # This file
├── config.py
├── detectors/
│   ├── xss_detector.py          # XSS detection
│   ├── sqli_detector.py         # SQL injection detection
│   ├── csrf_detector.py         # CSRF detection
│   └── header_checker.py        # Security headers
├── scanners/
│   ├── zap_scanner.py           # ZAP integration
│   ├── nmap_scanner.py          # Nmap integration
│   └── nikto_scanner.py         # Nikto integration
├── analyzers/
│   ├── risk_scorer.py           # CVSS scoring
│   ├── vulnerability_parser.py  # Parse scan results
│   └── correlator.py            # Log correlation
├── validators/
│   └── baseline_validator.py    # Baseline comparison
└── tests/
    └── test_security_agent.py
```

---

## ✅ Checklist for Security Agent Code

- [ ] Extends `BaseAgent` class
- [ ] Loads security blueprints
- [ ] Validates scan safety (environment checks)
- [ ] Uses plugin loader for scanners
- [ ] Implements CVSS-based risk scoring
- [ ] Detects OWASP Top 10 vulnerabilities
- [ ] Compares against security baselines
- [ ] Correlates with execution logs
- [ ] Uses LLM adapter (not direct calls)
- [ ] Communicates via runtime
- [ ] Excludes destructive tests
- [ ] Generates security reports
- [ ] Is modular (< 500 lines per file)

---

## 🎯 Remember

> **Scan safely, never exploit.**  
> **Risk scoring is deterministic (CVSS), not AI-based.**  
> **Production requires explicit permission.**

---

*Last updated: 2026-03-26*
