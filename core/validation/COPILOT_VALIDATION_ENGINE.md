# Copilot Instructions — Validation Engine (APEX AI Platform)

## ✅ Purpose
The Validation Engine is the **ONLY component authorized to make pass/fail decisions** in the Apex AI Testing Platform.

This engine is responsible for all **deterministic pass/fail logic**, ensuring that the platform is:
- ✅ **Enterprise-grade** - Reliable, predictable validation
- ✅ **Deterministic** - Rule-based, NOT AI-based decisions
- ✅ **Evidence-based** - Validates against actual execution evidence
- ✅ **Multi-source** - Uses blueprints, contracts, baselines, logs, visual diffs
- ✅ **Transparent** - Clear reasoning for every decision
- ✅ **Auditable** - Full trace of validation logic

**This engine NEVER uses AI to decide correctness.**

---

## ✅ Validation Inputs

The Validation Engine accepts evidence from multiple sources:

### 1. DOM Snapshots
```python
dom_snapshot = {
    "html": "<html>...",
    "elements": ["#login-button", ".welcome-message"],
    "styles": {...},
    "visible_elements": ["#login-button"]
}
```

### 2. API Responses
```python
api_response = {
    "endpoint": "/api/user/profile",
    "status_code": 200,
    "body": {"id": 123, "email": "user@example.com"},
    "headers": {"Content-Type": "application/json"},
    "response_time": 450  # ms
}
```

### 3. Performance Metrics
```python
performance_metrics = {
    "response_time_p50": 350,
    "response_time_p95": 450,
    "response_time_p99": 600,
    "throughput": 1000,  # req/s
    "error_rate": 0.001  # 0.1%
}
```

### 4. Security Scan Results
```python
security_scan = {
    "vulnerabilities": [
        {"severity": "MEDIUM", "type": "XSS", "url": "/search"}
    ],
    "headers": {"X-Frame-Options": "DENY"},
    "ssl_valid": True
}
```

### 5. Blueprint Expected Outcomes
```yaml
expected:
  url: "/dashboard"
  status_code: 200
  elements_present: ["#welcome", "#user-menu"]
  response_time_max: 2000
```

### 6. Business Rules
```python
business_rules = {
    "authentication": {"method": "jwt", "session_duration": 3600},
    "authorization": {"required_role": "user"},
    "data_validation": {"email_format": "RFC5322"}
}
```

### 7. Logs (Client + Server)
```python
logs = {
    "client": ["INFO: Page loaded", "ERROR: Button click failed"],
    "server": ["INFO: Request received", "WARN: Slow query 2500ms"]
}
```

### 8. Database State
```python
db_state = {
    "user_created": True,
    "order_count": 1,
    "transaction_status": "completed"
}
```

### 9. Visual Baseline Comparisons
```python
visual_baseline = {
    "baseline_image": "baseline.png",
    "current_image": "current.png",
    "diff_percentage": 2.5,  # % pixels different
    "structural_diff": False
}
```

### 10. Contract Schemas
```json
{
  "type": "object",
  "required": ["id", "email"],
  "properties": {
    "id": {"type": "integer"},
    "email": {"type": "string", "format": "email"}
  }
}
```

---

## ✅ Core Principle

### CRITICAL RULE
**NO AI/LLM in pass/fail decisions. EVER.**

```python
# ❌ WRONG: LLM-based validation
result = llm.ask("Did this test pass? {evidence}")
if "yes" in result.lower():
    return TestResult(status="PASS")  # FORBIDDEN!

# ✅ CORRECT: Deterministic validation
validator = DeterministicValidator()
result = validator.validate(
    evidence=evidence,
    expected=blueprint.expected,
    contract=api_contract,
    baseline=historical_baseline
)
# result is based on rules, not AI interpretation
```

---

## ✅ Validation Sources

### The Validation Engine Uses Four Sources of Truth

#### 1. Blueprints
Declarative expected outcomes from blueprint YAML.

```yaml
# From blueprint
expected:
  url: "/dashboard"
  status_code: 200
  elements_present: ["#welcome", "#user-menu"]
  response_time_max: 2000
```

#### 2. Contracts
API contracts, schema definitions, interface specifications.

```json
// API Contract
{
  "endpoint": "/api/user/profile",
  "method": "GET",
  "response_schema": {
    "type": "object",
    "required": ["id", "email", "name"],
    "properties": {
      "id": {"type": "integer"},
      "email": {"type": "string", "format": "email"},
      "name": {"type": "string"}
    }
  }
}
```

#### 3. Baselines (**Per-Application**)
Historical passing state from previous test runs. **Each app has its own baselines.**

```json
// Baseline for App1 (stored in apps/app1/snapshots/)
{
  "app_id": "app1",
  "blueprint_id": "LOGIN_001",
  "baseline_timestamp": "2026-03-20T10:00:00Z",
  "response_time_p95": 250,          // App1 is fast (modern SPA)
  "dom_snapshot_hash": "a1b2c3d4",
  "api_responses": {...}
}

// Baseline for App2 (stored in apps/app2/snapshots/)
{
  "app_id": "app2",
  "blueprint_id": "LOGIN_001",
  "baseline_timestamp": "2026-03-20T10:00:00Z",
  "response_time_p95": 800,          // App2 is slower (legacy monolith)
  "dom_snapshot_hash": "x9y8z7w6",   // Different DOM structure
  "api_responses": {...}
}
```

**Why Baselines Are Per-App:**
- ✅ App1's fast performance baseline doesn't cause false failures for App2
- ✅ App1's React DOM structure doesn't conflict with App2's server-side HTML
- ✅ Each app evolves independently with its own performance characteristics

#### 4. Validation Rules (**Per-Application**)
App-specific validation rules from `apps/{app_id}/rules.yaml`.

```yaml
# apps/app1/rules.yaml (Modern SPA - strict rules)
rules:
  performance:
    page_load_max_ms: 1000
    api_response_max_ms: 200
  visual:
    pixel_diff_threshold: 0.01    # 1% tolerance
    structural_diff: strict

# apps/app2/rules.yaml (Legacy app - relaxed rules)
rules:
  performance:
    page_load_max_ms: 3000
    api_response_max_ms: 800
  visual:
    pixel_diff_threshold: 0.05    # 5% tolerance
    structural_diff: relaxed
```

#### 5. Logs
Execution logs for error detection and correlation.

```
# Execution Log
2026-03-26 14:30:15 INFO: Navigated to /login
2026-03-26 14:30:16 WARN: Network request to /api/auth took 2500ms
2026-03-26 14:30:17 ERROR: Element #login-button not found
```

---

## ✅ Validation Engine Architecture

### Core Validator Interface
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum

class ValidationStatus(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NEEDS_HEALING = "NEEDS_HEALING"
    INCONCLUSIVE = "INCONCLUSIVE"

@dataclass
class ValidationResult:
    """Result of deterministic validation"""
    status: ValidationStatus
    passed_checks: List[str]
    failed_checks: List[str]
    warnings: List[str]
    evidence_summary: dict
    reasoning: str  # Human-readable explanation
    confidence: float  # 0.0 - 1.0
    needs_manual_review: bool = False
    auto_healing_suggested: bool = False

@dataclass
class Evidence:
    """Evidence collected from test execution"""
    # UI Evidence
    screenshots: Optional[List[str]] = None
    dom_state: Optional[str] = None
    current_url: Optional[str] = None
    console_logs: Optional[List[str]] = None
    network_logs: Optional[List[dict]] = None
    
    # API Evidence
    api_responses: Optional[List[dict]] = None
    response_times: Optional[Dict[str, float]] = None
    status_codes: Optional[Dict[str, int]] = None
    
    # Performance Evidence
    page_load_time: Optional[float] = None
    resource_timings: Optional[dict] = None
    
    # Security Evidence
    security_headers: Optional[dict] = None
    vulnerabilities: Optional[List[dict]] = None
    
    # Execution Evidence
    execution_logs: Optional[List[str]] = None
    exceptions: Optional[List[dict]] = None
    warnings: Optional[List[str]] = None

class BaseValidator(ABC):
    """Base validator interface"""
    
    @abstractmethod
    def validate(
        self,
        evidence: Evidence,
        blueprint: Blueprint,
        contract: Optional[Contract] = None,
        baseline: Optional[Baseline] = None
    ) -> ValidationResult:
        """Validate evidence deterministically"""
        pass
```

### Deterministic Validation Engine
```python
class DeterministicValidationEngine:
    """Main validation engine - deterministic pass/fail decisions"""
    
    def __init__(self):
        self.ui_validator = UIValidator()
        self.api_validator = APIValidator()
        self.performance_validator = PerformanceValidator()
        self.security_validator = SecurityValidator()
    
    def validate(
        self,
        evidence: Evidence,
        blueprint: Blueprint,
        contract: Optional[Contract] = None,
        baseline: Optional[Baseline] = None
    ) -> ValidationResult:
        """
        Validate test execution evidence deterministically.
        NO AI/LLM involved in decision making.
        """
        
        passed_checks = []
        failed_checks = []
        warnings = []
        
        # 1. Validate against Blueprint expectations
        if blueprint.expected:
            blueprint_result = self._validate_blueprint_expectations(
                evidence, blueprint.expected
            )
            passed_checks.extend(blueprint_result.passed)
            failed_checks.extend(blueprint_result.failed)
            warnings.extend(blueprint_result.warnings)
        
        # 2. Validate against Contract (if API test)
        if contract:
            contract_result = self.api_validator.validate_contract(
                evidence.api_responses, contract
            )
            passed_checks.extend(contract_result.passed)
            failed_checks.extend(contract_result.failed)
        
        # 3. Validate against Baseline (regression check)
        if baseline:
            baseline_result = self._validate_against_baseline(
                evidence, baseline
            )
            passed_checks.extend(baseline_result.passed)
            failed_checks.extend(baseline_result.failed)
            warnings.extend(baseline_result.warnings)
        
        # 4. Check for errors in logs
        if evidence.execution_logs:
            log_errors = self._analyze_logs_for_errors(evidence.execution_logs)
            if log_errors:
                failed_checks.extend(log_errors)
        
        # 5. Check for exceptions
        if evidence.exceptions:
            failed_checks.append(
                f"Exceptions occurred: {len(evidence.exceptions)}"
            )
        
        # Determine final status (deterministic)
        status = self._determine_status(passed_checks, failed_checks, warnings)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            status, passed_checks, failed_checks, warnings
        )
        
        # Calculate confidence (based on evidence completeness)
        confidence = self._calculate_confidence(evidence)
        
        # Check if healing is suggested
        auto_healing = self._should_suggest_healing(failed_checks)
        
        return ValidationResult(
            status=status,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            warnings=warnings,
            evidence_summary=self._summarize_evidence(evidence),
            reasoning=reasoning,
            confidence=confidence,
            auto_healing_suggested=auto_healing
        )
    
    def _validate_blueprint_expectations(
        self,
        evidence: Evidence,
        expected: dict
    ) -> dict:
        """Validate all blueprint expectations deterministically"""
        
        passed = []
        failed = []
        warnings = []
        
        # URL validation
        if 'url' in expected:
            if evidence.current_url == expected['url']:
                passed.append(f"URL matches: {expected['url']}")
            else:
                failed.append(
                    f"URL mismatch: expected {expected['url']}, "
                    f"got {evidence.current_url}"
                )
        
        # Elements present validation
        if 'elements_present' in expected:
            for selector in expected['elements_present']:
                if self._element_exists_in_dom(selector, evidence.dom_state):
                    passed.append(f"Element present: {selector}")
                else:
                    failed.append(f"Element not found: {selector}")
        
        # Elements absent validation
        if 'elements_absent' in expected:
            for selector in expected['elements_absent']:
                if not self._element_exists_in_dom(selector, evidence.dom_state):
                    passed.append(f"Element correctly absent: {selector}")
                else:
                    failed.append(f"Element should not exist: {selector}")
        
        # Status code validation
        if 'status_code' in expected and evidence.status_codes:
            for endpoint, code in evidence.status_codes.items():
                if code == expected['status_code']:
                    passed.append(f"Status code {code} for {endpoint}")
                else:
                    failed.append(
                        f"Status code mismatch for {endpoint}: "
                        f"expected {expected['status_code']}, got {code}"
                    )
        
        # Performance validation
        if 'response_time_max' in expected:
            if evidence.page_load_time:
                if evidence.page_load_time <= expected['response_time_max']:
                    passed.append(
                        f"Page load time OK: {evidence.page_load_time}ms"
                    )
                else:
                    warnings.append(
                        f"Page load time slow: {evidence.page_load_time}ms "
                        f"(max: {expected['response_time_max']}ms)"
                    )
        
        return {
            "passed": passed,
            "failed": failed,
            "warnings": warnings
        }
    
    def _validate_against_baseline(
        self,
        evidence: Evidence,
        baseline: Baseline
    ) -> dict:
        """Check for regressions against baseline"""
        
        passed = []
        failed = []
        warnings = []
        
        # Performance regression check
        if baseline.response_time_p95 and evidence.page_load_time:
            threshold = baseline.response_time_p95 * 1.2  # 20% tolerance
            
            if evidence.page_load_time <= threshold:
                passed.append("No performance regression")
            else:
                failed.append(
                    f"Performance regression: {evidence.page_load_time}ms "
                    f"vs baseline {baseline.response_time_p95}ms"
                )
        
        # DOM snapshot comparison
        if baseline.dom_snapshot_hash and evidence.dom_state:
            current_hash = self._hash_dom(evidence.dom_state)
            
            if current_hash == baseline.dom_snapshot_hash:
                passed.append("DOM state matches baseline")
            else:
                warnings.append("DOM structure changed from baseline")
        
        # API response comparison
        if baseline.api_responses and evidence.api_responses:
            response_diff = self._compare_api_responses(
                evidence.api_responses,
                baseline.api_responses
            )
            
            if response_diff.has_breaking_changes:
                failed.append(f"API breaking changes: {response_diff.changes}")
            elif response_diff.has_changes:
                warnings.append(f"API non-breaking changes: {response_diff.changes}")
            else:
                passed.append("API responses match baseline")
        
        return {
            "passed": passed,
            "failed": failed,
            "warnings": warnings
        }
    
    def _analyze_logs_for_errors(self, logs: List[str]) -> List[str]:
        """Detect errors in execution logs (deterministic)"""
        
        errors = []
        
        error_patterns = [
            r'ERROR:',
            r'FATAL:',
            r'Exception:',
            r'Traceback',
            r'failed to',
            r'could not',
            r'unable to'
        ]
        
        for log_line in logs:
            for pattern in error_patterns:
                if re.search(pattern, log_line, re.IGNORECASE):
                    errors.append(f"Error in logs: {log_line[:100]}")
                    break
        
        return errors
    
    def _determine_status(
        self,
        passed: List[str],
        failed: List[str],
        warnings: List[str]
    ) -> ValidationStatus:
        """Determine final status deterministically"""
        
        # Any failures = FAIL
        if failed:
            # Check if failures are healable
            healable_patterns = [
                "Element not found",
                "Locator",
                "Selector"
            ]
            
            if any(
                any(pattern in failure for pattern in healable_patterns)
                for failure in failed
            ):
                return ValidationStatus.NEEDS_HEALING
            else:
                return ValidationStatus.FAIL
        
        # No failures, but no passes either
        if not passed:
            return ValidationStatus.INCONCLUSIVE
        
        # All checks passed
        return ValidationStatus.PASS
    
    def _generate_reasoning(
        self,
        status: ValidationStatus,
        passed: List[str],
        failed: List[str],
        warnings: List[str]
    ) -> str:
        """Generate human-readable reasoning"""
        
        reasoning = f"Validation Status: {status.value}\n\n"
        
        if passed:
            reasoning += f"✅ Passed Checks ({len(passed)}):\n"
            for check in passed[:5]:  # Top 5
                reasoning += f"  - {check}\n"
            if len(passed) > 5:
                reasoning += f"  ... and {len(passed) - 5} more\n"
            reasoning += "\n"
        
        if failed:
            reasoning += f"❌ Failed Checks ({len(failed)}):\n"
            for check in failed:
                reasoning += f"  - {check}\n"
            reasoning += "\n"
        
        if warnings:
            reasoning += f"⚠️  Warnings ({len(warnings)}):\n"
            for warning in warnings[:3]:  # Top 3
                reasoning += f"  - {warning}\n"
        
        return reasoning
    
    def _calculate_confidence(self, evidence: Evidence) -> float:
        """Calculate confidence based on evidence completeness"""
        
        evidence_score = 0
        total_possible = 0
        
        # UI evidence
        if evidence.dom_state:
            evidence_score += 1
        total_possible += 1
        
        if evidence.current_url:
            evidence_score += 1
        total_possible += 1
        
        if evidence.screenshots:
            evidence_score += 1
        total_possible += 1
        
        # API evidence
        if evidence.api_responses:
            evidence_score += 1
        total_possible += 1
        
        if evidence.status_codes:
            evidence_score += 1
        total_possible += 1
        
        # Logs
        if evidence.execution_logs:
            evidence_score += 1
        total_possible += 1
        
        return evidence_score / total_possible if total_possible > 0 else 0.0
    
    def _should_suggest_healing(self, failed_checks: List[str]) -> bool:
        """Determine if auto-healing should be suggested"""
        
        healable_patterns = [
            "Element not found",
            "Locator",
            "Selector",
            "not clickable",
            "timeout waiting for"
        ]
        
        return any(
            any(pattern.lower() in check.lower() for pattern in healable_patterns)
            for check in failed_checks
        )
```

---

## ✅ Specialized Validators

### API Contract Validator
```python
class APIValidator:
    """Validate API responses against contracts"""
    
    def validate_contract(
        self,
        api_responses: List[dict],
        contract: Contract
    ) -> dict:
        """Validate API responses match contract schema"""
        
        passed = []
        failed = []
        
        for response in api_responses:
            endpoint = response.get('endpoint')
            
            # Status code check
            expected_status = contract.get_expected_status(endpoint)
            actual_status = response.get('status_code')
            
            if actual_status == expected_status:
                passed.append(f"{endpoint}: status {actual_status}")
            else:
                failed.append(
                    f"{endpoint}: status {actual_status}, "
                    f"expected {expected_status}"
                )
            
            # Schema validation
            expected_schema = contract.get_response_schema(endpoint)
            actual_body = response.get('body')
            
            schema_errors = self._validate_json_schema(
                actual_body,
                expected_schema
            )
            
            if not schema_errors:
                passed.append(f"{endpoint}: schema valid")
            else:
                failed.extend([
                    f"{endpoint}: schema error - {error}"
                    for error in schema_errors
                ])
        
        return {"passed": passed, "failed": failed}
    
    def _validate_json_schema(
        self,
        data: dict,
        schema: dict
    ) -> List[str]:
        """Validate JSON data against schema"""
        
        from jsonschema import validate, ValidationError
        
        errors = []
        
        try:
            validate(instance=data, schema=schema)
        except ValidationError as e:
            errors.append(e.message)
        
        return errors
```

### Performance Validator
```python
class PerformanceValidator:
    """Validate performance against SLAs"""
    
    def validate_sla(
        self,
        metrics: PerformanceMetrics,
        sla: PerformanceSLA
    ) -> dict:
        """Validate performance metrics against SLA"""
        
        passed = []
        failed = []
        warnings = []
        
        # Response time SLA
        if metrics.response_time_p95 <= sla.response_time_p95:
            passed.append(
                f"Response time P95: {metrics.response_time_p95}ms "
                f"(SLA: {sla.response_time_p95}ms)"
            )
        else:
            failed.append(
                f"Response time P95 violation: {metrics.response_time_p95}ms "
                f"exceeds SLA {sla.response_time_p95}ms"
            )
        
        # Throughput SLA
        if metrics.requests_per_second >= sla.throughput_min:
            passed.append(
                f"Throughput: {metrics.requests_per_second} req/s "
                f"(min: {sla.throughput_min})"
            )
        else:
            failed.append(
                f"Throughput below SLA: {metrics.requests_per_second} req/s "
                f"(min: {sla.throughput_min})"
            )
        
        # Error rate SLA
        if metrics.error_rate <= sla.error_rate_max:
            passed.append(
                f"Error rate: {metrics.error_rate:.2%} "
                f"(max: {sla.error_rate_max:.2%})"
            )
        else:
            failed.append(
                f"Error rate exceeds SLA: {metrics.error_rate:.2%} "
                f"(max: {sla.error_rate_max:.2%})"
            )
        
        return {"passed": passed, "failed": failed, "warnings": warnings}
```

### Security Validator
```python
class SecurityValidator:
    """Validate security expectations"""
    
    def validate_security(
        self,
        evidence: Evidence,
        security_expectations: dict
    ) -> dict:
        """Validate security against expectations"""
        
        passed = []
        failed = []
        
        # Required headers check
        required_headers = security_expectations.get('headers_required', [])
        actual_headers = evidence.security_headers or {}
        
        for header in required_headers:
            if header in actual_headers:
                passed.append(f"Security header present: {header}")
            else:
                failed.append(f"Missing security header: {header}")
        
        # HTTPS enforcement
        if security_expectations.get('https_only', False):
            if evidence.current_url and evidence.current_url.startswith('https://'):
                passed.append("HTTPS enforced")
            else:
                failed.append("HTTPS not enforced")
        
        # Vulnerability check
        if evidence.vulnerabilities:
            critical_vulns = [
                v for v in evidence.vulnerabilities
                if v.get('severity') == 'CRITICAL'
            ]
            
            if critical_vulns:
                failed.append(
                    f"Critical vulnerabilities found: {len(critical_vulns)}"
                )
        
        return {"passed": passed, "failed": failed}
```

---

## ✅ What Validation Engine DOES

1. ✅ Validates evidence against blueprints (deterministically)
2. ✅ Validates API responses against contracts (JSON Schema, OpenAPI)
3. ✅ Compares against baselines (regression detection)
4. ✅ Analyzes logs for errors (pattern matching)
5. ✅ Checks performance against SLAs (numeric comparison, thresholds)
6. ✅ Validates security expectations (rule-based, plugin outputs)
7. ✅ Performs visual baseline comparisons (pixel diff, structural diff, bounding-box)
8. ✅ Validates business rules (custom logic, compliance)
9. ✅ Generates clear, auditable reasoning
10. ✅ Suggests auto-healing when appropriate (healable failures)
11. ✅ Calculates confidence based on evidence completeness
12. ✅ Provides transparent pass/fail decisions with detailed evidence

---

## ✅ What Validation Engine DOES NOT DO

❌ Use AI/LLM for pass/fail decisions
❌ Make subjective judgments
❌ Execute tests (agents do this)
❌ Generate test scripts (agents + LLM do this)
❌ Store results (observability system does this)
❌ Modify blueprints
❌ Auto-heal tests (just suggests it)

---

## ✅ What Copilot Should Generate

### Generate These Types of Code
- ✅ Deterministic validation logic (rule-based, never AI-based)
- ✅ Modular domain validators (dom, api, perf, security, visual, rules)
- ✅ Schema validators (JSON Schema, OpenAPI contracts)
- ✅ Baseline comparators (regression detection, deviation analysis)
- ✅ Log analyzers (pattern-based error detection)
- ✅ Performance validators (SLA compliance, threshold checks)
- ✅ Security validators (plugin output validation, header checks)
- ✅ Visual diff validators (pixel, structural, bounding-box)
- ✅ Evidence collectors (structured evidence gathering)
- ✅ Confidence calculators (evidence completeness scoring)
- ✅ Reasoning generators (human-readable explanations)
- ✅ Error classifiers (healable, critical, flaky categorization)
- ✅ Assertion utilities (reusable validation helpers)
- ✅ Unified ValidationResult model (standardized output)

---

## ✅ What Copilot Should NOT Generate

### ❌ AVOID These Patterns
```python
# ❌ BAD: LLM-based validation
result = llm.ask("Is this test passing?")

# ❌ BAD: Subjective validation
if "looks good" in evidence:
    return PASS

# ❌ BAD: Non-deterministic validation
if random.random() > 0.5:
    return PASS

# ❌ BAD: Missing transparency
return FAIL  # No reasoning provided
```

---

## ✅ Checklist for Validation Engine Code

- [ ] All validation is deterministic (rule-based, never AI)
- [ ] NO AI/LLM in pass/fail decisions
- [ ] Validates against multiple sources (blueprint, contract, baseline, logs, visual)
- [ ] Modular validators (< 500 lines each: dom, api, perf, security, visual, rules)
- [ ] Uses JSON Schema and OpenAPI contracts for API validation
- [ ] Compares SLA, baseline, deviation, thresholds for performance
- [ ] Uses plugin outputs for security validation (no AI interpretation)
- [ ] Visual diffs use pixel, structural, and bounding-box analysis
- [ ] Provides clear reasoning for decisions
- [ ] Calculates confidence scores based on evidence completeness
- [ ] Suggests auto-healing when appropriate (healable vs critical failures)
- [ ] Returns structured ValidationResult with all required fields
- [ ] Fully auditable (trace all checks and evidence)
- [ ] Handles missing evidence gracefully
- [ ] Classifies failure severity (low, medium, high, critical)
- [ ] Never mixes exception handling with validation logic
- [ ] Tool-agnostic (no Playwright/Selenium/k6-specific code)

---

## 🔗 Integration Points

The Validation Engine integrates with these systems:

### 1. Blueprint Engine (Expected Results)
```python
# Blueprint Engine provides expected outcomes
blueprint = blueprint_engine.load("LOGIN_001")
expected = blueprint.expected

# Validation Engine validates against them
result = validation_engine.validate(
    evidence=execution_evidence,
    expected=expected  # From blueprint
)
```

### 2. Runtime Executors (Actual Results)
```python
# Runtime Executor collects actual evidence
executor = PlaywrightExecutor()
evidence = executor.execute_test(test_script)

# Validation Engine receives actual results
result = validation_engine.validate(
    evidence=evidence,  # Actual results from executor
    expected=blueprint.expected
)
```

### 3. Test Intelligence Brain (Risk Insights)
```python
# Intelligence Brain provides risk context
risk_score = intelligence_brain.get_risk_score("LOGIN_001")

# Validation Engine adjusts severity based on risk
result = validation_engine.validate(
    evidence=evidence,
    expected=blueprint.expected
)

# Adjust severity if high-risk test fails
if result.status == "fail" and risk_score > 0.8:
    result.severity = "critical"
```

### 4. Docs Agent (Reporting)
```python
# Validation Engine provides results
validation_result = validation_engine.validate(...)

# Docs Agent generates reports from results
report = docs_agent.generate_test_report(
    validation_results=[validation_result],
    include_evidence=True,
    format="markdown"
)
```

### 5. Agents (Actions)
```python
# QA Agent executes test
evidence = qa_agent.execute_ui_test(blueprint)

# Validation Engine validates
result = validation_engine.validate(
    evidence=evidence,
    expected=blueprint.expected
)

# If healing needed, QA Agent takes action
if result.needs_auto_healing:
    qa_agent.apply_healing(result.suggested_healing)
```

---

## 🎛️ Multi-Application Isolation in Validation

### App-Specific Baselines & Rules

The Validation Engine **MUST** load baselines and rules specific to the application being tested.

#### Validation Request Structure

```python
@dataclass
class ValidationRequest:
    """Validation request with app isolation"""
    app_id: str                           # Which app?
    blueprint_id: str                     # Which test?
    expected: dict                        # From blueprint
    actual: Evidence                      # From execution
    baselines_path: Path                  # apps/{app_id}/snapshots/
    rules_path: Path                      # apps/{app_id}/rules.yaml
    context: ProjectContext               # Full app context

# Example request for App2
validation_request = ValidationRequest(
    app_id="app2",
    blueprint_id="CHECKOUT_047",
    expected={
        "status_code": 200,
        "response_time_ms": {"max": 500},
        "ui_element": {"selector": "#checkout-btn", "visible": True}
    },
    actual=execution_evidence,
    baselines_path=Path("/apps/app2/snapshots/"),
    rules_path=Path("/apps/app2/rules.yaml"),
    context=context_app2
)
```

#### Loading App-Specific Baselines

```python
class AppAwareValidationEngine(ValidationEngine):
    """Validation engine with multi-app support"""
    
    def validate(
        self,
        context: ProjectContext,      # Always require context!
        blueprint: Blueprint,
        evidence: Evidence
    ) -> ValidationResult:
        """Validate using app-specific baselines and rules"""
        
        # Load app-specific baseline manager
        baseline_mgr = BaselineManager(context)
        
        # Load app-specific rules
        rules = self._load_app_rules(context)
        
        # Load appropriate baselines based on test type
        baselines = {}
        
        if blueprint.test_type == "ui":
            baselines["ui"] = baseline_mgr.load_ui_baseline(blueprint.page)
            baselines["dom"] = baseline_mgr.load_dom_baseline(blueprint.page)
        
        if blueprint.test_type == "api":
            baselines["api"] = baseline_mgr.load_api_baseline(blueprint.endpoint)
        
        # Always load performance baseline
        baselines["performance"] = baseline_mgr.load_perf_baseline(blueprint.id)
        
        # Validate with app-specific context
        result = self._validate_with_baselines(
            blueprint=blueprint,
            evidence=evidence,
            baselines=baselines,
            rules=rules,
            app_id=context.app_id  # Include in result
        )
        
        return result
    
    def _load_app_rules(self, context: ProjectContext) -> dict:
        """Load validation rules for THIS app"""
        rules_file = f"{context.app_path}/rules.yaml"
        
        if not os.path.exists(rules_file):
            # Use default rules
            logger.warning(
                f"No custom rules for {context.app_id}, using defaults"
            )
            return self._get_default_rules()
        
        with open(rules_file, "r") as f:
            rules = yaml.safe_load(f)
        
        # Validate rules structure
        self._validate_rules_schema(rules)
        
        return rules["rules"]
    
    def _validate_with_baselines(
        self,
        blueprint: Blueprint,
        evidence: Evidence,
        baselines: dict,
        rules: dict,
        app_id: str
    ) -> ValidationResult:
        """Core validation logic with app-specific baselines"""
        
        passed_checks = []
        failed_checks = []
        warnings = []
        
        # Performance validation with app-specific baseline
        if "performance" in baselines:
            perf_result = self._validate_performance(
                expected=blueprint.expected.get("performance", {}),
                actual=evidence.performance_metrics,
                baseline=baselines["performance"],
                rules=rules.get("performance", {})
            )
            
            if perf_result["passed"]:
                passed_checks.extend(perf_result["passed"])
            if perf_result["failed"]:
                failed_checks.extend(perf_result["failed"])
            if perf_result["warnings"]:
                warnings.extend(perf_result["warnings"])
        
        # UI validation with app-specific baselines
        if "ui" in baselines:
            ui_result = self._validate_ui(
                expected=blueprint.expected.get("ui", {}),
                actual=evidence.screenshots,
                baseline_image=baselines["ui"],
                baseline_dom=baselines.get("dom"),
                rules=rules.get("visual", {})
            )
            
            passed_checks.extend(ui_result["passed"])
            failed_checks.extend(ui_result["failed"])
            warnings.extend(ui_result["warnings"])
        
        # API validation with app-specific baseline
        if "api" in baselines:
            api_result = self._validate_api(
                expected=blueprint.expected.get("api", {}),
                actual=evidence.api_responses,
                baseline=baselines["api"],
                rules=rules.get("api", {})
            )
            
            passed_checks.extend(api_result["passed"])
            failed_checks.extend(api_result["failed"])
            warnings.extend(api_result["warnings"])
        
        # Determine final status
        status = self._determine_status(
            passed_checks,
            failed_checks,
            warnings
        )
        
        return ValidationResult(
            app_id=app_id,                      # Include app_id!
            blueprint_id=blueprint.id,
            status=status,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            warnings=warnings,
            evidence_summary=self._summarize_evidence(evidence),
            reasoning=self._generate_reasoning(
                status, passed_checks, failed_checks, warnings
            ),
            confidence=self._calculate_confidence(evidence)
        )
    
    def _validate_performance(
        self,
        expected: dict,
        actual: dict,
        baseline: dict,
        rules: dict
    ) -> dict:
        """Validate performance against app-specific baseline and rules"""
        
        passed = []
        failed = []
        warnings = []
        
        # Check against absolute thresholds from rules
        max_response_time = rules.get("api_response_max_ms", 1000)
        if actual.get("response_time_p95", 0) <= max_response_time:
            passed.append(
                f"Response time p95 ({actual['response_time_p95']}ms) "
                f"< max ({max_response_time}ms)"
            )
        else:
            failed.append(
                f"Response time p95 ({actual['response_time_p95']}ms) "
                f"> max ({max_response_time}ms)"
            )
        
        # Check against baseline (regression detection)
        baseline_p95 = baseline.get("response_time_p95", 0)
        if baseline_p95 > 0:
            # 20% regression threshold
            regression_threshold = baseline_p95 * 1.2
            
            if actual["response_time_p95"] > regression_threshold:
                warnings.append(
                    f"Performance regression detected: "
                    f"{actual['response_time_p95']}ms vs "
                    f"baseline {baseline_p95}ms (+{((actual['response_time_p95'] / baseline_p95) - 1) * 100:.1f}%)"
                )
        
        return {
            "passed": passed,
            "failed": failed,
            "warnings": warnings
        }
    
    def _validate_ui(
        self,
        expected: dict,
        actual: List[str],
        baseline_image: bytes,
        baseline_dom: dict,
        rules: dict
    ) -> dict:
        """Validate UI against app-specific baseline and rules"""
        
        passed = []
        failed = []
        warnings = []
        
        # Pixel diff threshold from app rules
        pixel_threshold = rules.get("pixel_diff_threshold", 0.02)  # 2% default
        
        if baseline_image and actual:
            # Compare current screenshot to baseline
            diff_percentage = self._calculate_pixel_diff(
                baseline_image,
                actual[0]
            )
            
            if diff_percentage <= pixel_threshold:
                passed.append(
                    f"Visual diff ({diff_percentage:.2%}) "
                    f"< threshold ({pixel_threshold:.2%})"
                )
            else:
                failed.append(
                    f"Visual diff ({diff_percentage:.2%}) "
                    f"> threshold ({pixel_threshold:.2%})"
                )
        
        # DOM structure comparison
        structural_mode = rules.get("structural_diff", "strict")  # or "relaxed"
        
        if baseline_dom:
            dom_match = self._compare_dom_structures(
                baseline_dom,
                expected.get("dom_snapshot"),
                mode=structural_mode
            )
            
            if dom_match:
                passed.append("DOM structure matches baseline")
            else:
                if structural_mode == "strict":
                    failed.append("DOM structure changed (strict mode)")
                else:
                    warnings.append("DOM structure changed (relaxed mode)")
        
        return {
            "passed": passed,
            "failed": failed,
            "warnings": warnings
        }

# ✅ CORRECT: Validation with app context
validation_engine = AppAwareValidationEngine()

# App1 validation (fast app, strict rules)
result_app1 = validation_engine.validate(
    context=context_app1,
    blueprint=blueprint_app1,
    evidence=evidence_app1
)
# Uses: apps/app1/snapshots/, apps/app1/rules.yaml

# App2 validation (slower app, relaxed rules)
result_app2 = validation_engine.validate(
    context=context_app2,
    blueprint=blueprint_app2,
    evidence=evidence_app2
)
# Uses: apps/app2/snapshots/, apps/app2/rules.yaml

# ❌ WRONG: Global validation (no app context)
result = validation_engine.validate(blueprint, evidence)  # Which app?!
```

### Benefits of App-Specific Validation

**1. Accurate Baseline Comparisons:**
- App1's modern UI baseline doesn't cause false failures for App2's legacy UI
- App1's fast performance baseline doesn't flag App2 as slow

**2. Tailored Validation Rules:**
- App1 can enforce strict visual diff thresholds (1%)
- App2 can use relaxed thresholds (5%) for dynamic content

**3. Independent Evolution:**
- App1 can update performance targets without affecting App2
- Each app's validation rules evolve with the app

**4. Clear Accountability:**
- Validation results include `app_id` for traceability
- Each app team owns their validation rules

---


result = validation_engine.validate(evidence, blueprint.expected)

# If healable failure, QA Agent takes action
if result.status == "fail" and result.self_heal:
    healed_locators = qa_agent.heal_locators(
        failed_selectors=result.failed_checks
    )
    # Retry with healed locators
    evidence = qa_agent.execute_ui_test(blueprint, healed_locators)
    result = validation_engine.validate(evidence, blueprint.expected)
```

### Integration Flow
```
┌────────────────────┐
│ Blueprint Engine   │ (Expected outcomes)
└─────────┬──────────┘
          │
          ├──→ [Agents] ──→ [Runtime Executors]
          │                         │
          │                         ↓
          │                 (Actual evidence)
          │                         │
          └──→ [Validation Engine] ←┘
                      │
                      ├──→ [Intelligence Brain] (Risk scoring)
                      └──→ [Docs Agent]         (Reporting)
```

---

## 🎯 Remember

> **Deterministic ALWAYS, AI NEVER.**  
> **Evidence-based decisions, transparent reasoning.**  
> **Validation engine decides, agents execute, LLMs generate.**

---

## 📚 Related Documentation

- [Main Platform Instructions](../../.apex_copilot_instructions.md)
- [Blueprint Engine](../blueprints/COPILOT_BLUEPRINT_ENGINE.md)
- [LLM Adapter](../llm/COPILOT_LLM_ADAPTER.md)
- [Agent Instructions](../agents/AGENTS_README.md)

---

*Last updated: 2026-03-26*
