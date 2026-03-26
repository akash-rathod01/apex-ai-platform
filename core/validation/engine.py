"""
Validation Engine - Deterministic test validation WITHOUT AI
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ValidationStatus(Enum):
    """Validation result status"""
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    ERROR = "error"


@dataclass
class Evidence:
    """
    Evidence collected during test execution
    
    This is what the test execution produced - the ACTUAL results
    """
    evidence_type: str  # ui, api, performance, security
    timestamp: datetime
    data: Dict[str, Any] = field(default_factory=dict)
    screenshots: List[str] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """
    Result of deterministic validation
    
    CRITICAL: This is deterministic - no AI interpretation
    """
    status: ValidationStatus
    expected: Dict[str, Any]
    actual: Dict[str, Any]
    passed_checks: List[str] = field(default_factory=list)
    failed_checks: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    evidence: Optional[Evidence] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def is_pass(self) -> bool:
        """Check if validation passed"""
        return self.status == ValidationStatus.PASS
    
    @property
    def summary(self) -> str:
        """Get validation summary"""
        return (
            f"{self.status.value.upper()}: "
            f"{len(self.passed_checks)} passed, "
            f"{len(self.failed_checks)} failed"
        )


class DeterministicValidator:
    """
    Base class for deterministic validators
    
    NO AI - pure logic-based validation
    """
    
    def validate(self, expected: Dict[str, Any], evidence: Evidence) -> ValidationResult:
        """
        Validate evidence against expected outcome
        
        Args:
            expected: Expected outcome from blueprint
            evidence: Actual evidence collected during test
        
        Returns:
            ValidationResult with pass/fail
        """
        raise NotImplementedError("Subclasses must implement validate()")
    
    def _compare_value(self, expected: Any, actual: Any, check_name: str) -> tuple[bool, str]:
        """
        Compare expected vs actual value
        
        Returns:
            (passed, message)
        """
        if expected == actual:
            return True, f"{check_name}: {actual} (matches expected)"
        else:
            return False, f"{check_name}: expected '{expected}', got '{actual}'"


class UIValidator(DeterministicValidator):
    """
    Validate UI test results
    
    Checks:
    - Element visibility
    - Element text content
    - URL matches
    - Page title
    - Element attributes
    """
    
    def validate(self, expected: Dict[str, Any], evidence: Evidence) -> ValidationResult:
        """Validate UI evidence"""
        actual = evidence.data
        passed = []
        failed = []
        errors = []
        
        # Check URL
        if 'url' in expected:
            success, msg = self._validate_url(expected['url'], actual.get('url'))
            (passed if success else failed).append(msg)
        
        # Check elements
        if 'elements' in expected:
            for elem_check in expected['elements']:
                success, msg = self._validate_element(elem_check, actual.get('elements', {}))
                (passed if success else failed).append(msg)
        
        # Check page title
        if 'title' in expected:
            success, msg = self._compare_value(
                expected['title'],
                actual.get('title'),
                'Page title'
            )
            (passed if success else failed).append(msg)
        
        # Determine status
        if errors:
            status = ValidationStatus.ERROR
        elif failed:
            status = ValidationStatus.FAIL
        else:
            status = ValidationStatus.PASS
        
        return ValidationResult(
            status=status,
            expected=expected,
            actual=actual,
            passed_checks=passed,
            failed_checks=failed,
            errors=errors,
            evidence=evidence
        )
    
    def _validate_url(self, expected_url: str, actual_url: str) -> tuple[bool, str]:
        """Validate URL matches"""
        if not actual_url:
            return False, "URL check: No URL captured in evidence"
        
        # Exact match or contains
        if expected_url == actual_url:
            return True, f"URL: {actual_url} (exact match)"
        elif expected_url in actual_url:
            return True, f"URL: {actual_url} (contains expected)"
        else:
            return False, f"URL: expected '{expected_url}', got '{actual_url}'"
    
    def _validate_element(self, elem_check: Dict[str, Any], 
                         elements: Dict[str, Any]) -> tuple[bool, str]:
        """Validate element properties"""
        selector = elem_check.get('selector')
        elem_data = elements.get(selector, {})
        
        # Check visibility
        if 'visible' in elem_check:
            expected_visible = elem_check['visible']
            actual_visible = elem_data.get('visible', False)
            if expected_visible != actual_visible:
                return False, f"Element '{selector}': expected visible={expected_visible}, got {actual_visible}"
        
        # Check text content
        if 'text' in elem_check:
            expected_text = elem_check['text']
            actual_text = elem_data.get('text', '')
            if expected_text != actual_text:
                return False, f"Element '{selector}': expected text '{expected_text}', got '{actual_text}'"
        
        # Check contains
        if 'contains' in elem_check:
            expected_contains = elem_check['contains']
            actual_text = elem_data.get('text', '')
            if expected_contains not in actual_text:
                return False, f"Element '{selector}': text doesn't contain '{expected_contains}'"
        
        return True, f"Element '{selector}': all checks passed"


class APIValidator(DeterministicValidator):
    """
    Validate API test results
    
    Checks:
    - HTTP status code
    - Response headers
    - Response body structure
    - Response time
    """
    
    def validate(self, expected: Dict[str, Any], evidence: Evidence) -> ValidationResult:
        """Validate API evidence"""
        actual = evidence.data
        passed = []
        failed = []
        errors = []
        
        # Check status code
        if 'status' in expected:
            success, msg = self._compare_value(
                expected['status'],
                actual.get('status'),
                'HTTP Status'
            )
            (passed if success else failed).append(msg)
        
        # Check headers
        if 'headers' in expected:
            for header, value in expected['headers'].items():
                actual_headers = actual.get('headers', {})
                success, msg = self._compare_value(
                    value,
                    actual_headers.get(header),
                    f'Header "{header}"'
                )
                (passed if success else failed).append(msg)
        
        # Check response body
        if 'body' in expected:
            success, msg = self._validate_body(expected['body'], actual.get('body', {}))
            (passed if success else failed).append(msg)
        
        # Check response time
        if 'max_response_time' in expected:
            actual_time = actual.get('response_time_ms', 0)
            max_time = expected['max_response_time']
            if actual_time <= max_time:
                passed.append(f"Response time: {actual_time}ms (within {max_time}ms)")
            else:
                failed.append(f"Response time: {actual_time}ms exceeds {max_time}ms")
        
        # Determine status
        if errors:
            status = ValidationStatus.ERROR
        elif failed:
            status = ValidationStatus.FAIL
        else:
            status = ValidationStatus.PASS
        
        return ValidationResult(
            status=status,
            expected=expected,
            actual=actual,
            passed_checks=passed,
            failed_checks=failed,
            errors=errors,
            evidence=evidence
        )
    
    def _validate_body(self, expected_body: Dict[str, Any], 
                      actual_body: Dict[str, Any]) -> tuple[bool, str]:
        """Validate response body structure"""
        for key, expected_value in expected_body.items():
            if key not in actual_body:
                return False, f"Response body: missing key '{key}'"
            
            actual_value = actual_body[key]
            if expected_value != actual_value:
                return False, f"Response body: key '{key}' expected '{expected_value}', got '{actual_value}'"
        
        return True, "Response body: all keys match"


class PerformanceValidator(DeterministicValidator):
    """
    Validate performance test results
    
    Checks:
    - Response time thresholds
    - Throughput metrics
    - Resource usage
    """
    
    def validate(self, expected: Dict[str, Any], evidence: Evidence) -> ValidationResult:
        """Validate performance evidence"""
        actual = evidence.data
        passed = []
        failed = []
        errors = []
        
        metrics = expected.get('metrics', {})
        actual_metrics = actual.get('metrics', {})
        
        # Check each metric
        for metric_name, threshold in metrics.items():
            actual_value = actual_metrics.get(metric_name)
            
            if actual_value is None:
                errors.append(f"Metric '{metric_name}': not captured in evidence")
                continue
            
            # Check threshold
            if 'max' in threshold:
                if actual_value <= threshold['max']:
                    passed.append(f"{metric_name}: {actual_value} (within {threshold['max']})")
                else:
                    failed.append(f"{metric_name}: {actual_value} exceeds {threshold['max']}")
            
            if 'min' in threshold:
                if actual_value >= threshold['min']:
                    passed.append(f"{metric_name}: {actual_value} (above {threshold['min']})")
                else:
                    failed.append(f"{metric_name}: {actual_value} below {threshold['min']}")
        
        # Determine status
        if errors:
            status = ValidationStatus.ERROR
        elif failed:
            status = ValidationStatus.FAIL
        else:
            status = ValidationStatus.PASS
        
        return ValidationResult(
            status=status,
            expected=expected,
            actual=actual,
            passed_checks=passed,
            failed_checks=failed,
            errors=errors,
            evidence=evidence
        )


class ValidationEngine:
    """
    Main validation engine - routes to correct validator
    
    CRITICAL: NO AI - pure deterministic logic
    """
    
    def __init__(self):
        self.validators = {
            'ui': UIValidator(),
            'api': APIValidator(),
            'performance': PerformanceValidator(),
        }
    
    def validate(self, blueprint_type: str, expected: Dict[str, Any], 
                 evidence: Evidence) -> ValidationResult:
        """
        Validate evidence against expected outcome
        
        Args:
            blueprint_type: Type of test (ui, api, performance)
            expected: Expected outcome from blueprint
            evidence: Actual evidence from test execution
        
        Returns:
            ValidationResult
        """
        validator = self.validators.get(blueprint_type)
        
        if not validator:
            return ValidationResult(
                status=ValidationStatus.ERROR,
                expected=expected,
                actual={},
                errors=[f"No validator for type '{blueprint_type}'"]
            )
        
        return validator.validate(expected, evidence)
