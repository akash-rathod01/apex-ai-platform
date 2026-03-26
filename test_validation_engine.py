"""
Test Validation Engine
"""

import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.validation.engine import (
    ValidationEngine,
    Evidence,
    ValidationStatus
)


def test_ui_validation():
    """Test UI validation"""
    print("=" * 60)
    print("Testing UI Validator")
    print("=" * 60)
    
    # Create validation engine
    engine = ValidationEngine()
    
    # Expected outcome (from blueprint)
    expected = {
        'url': 'https://example.com/dashboard',
        'elements': [
            {'selector': '.dashboard', 'visible': True},
            {'selector': '.user-profile', 'visible': True, 'contains': 'testuser'}
        ],
        'title': 'Dashboard - Example App'
    }
    
    # Actual evidence (from test execution) - PASSING
    passing_evidence = Evidence(
        evidence_type='ui',
        timestamp=datetime.now(),
        data={
            'url': 'https://example.com/dashboard',
            'title': 'Dashboard - Example App',
            'elements': {
                '.dashboard': {'visible': True, 'text': ''},
                '.user-profile': {'visible': True, 'text': 'Welcome, testuser!'}
            }
        },
        screenshots=['screenshot_001.png']
    )
    
    # Validate PASSING case
    print("\n1️⃣  Testing PASSING validation...")
    result = engine.validate('ui', expected, passing_evidence)
    
    print(f"   Status: {result.status.value.upper()}")
    print(f"   ✅ Passed checks ({len(result.passed_checks)}):")
    for check in result.passed_checks:
        print(f"      - {check}")
    
    if result.failed_checks:
        print(f"   ❌ Failed checks ({len(result.failed_checks)}):")
        for check in result.failed_checks:
            print(f"      - {check}")
    
    assert result.is_pass, "Expected validation to pass"
    print(f"\n   ✅ Test passed as expected!")
    
    # Actual evidence (from test execution) - FAILING
    failing_evidence = Evidence(
        evidence_type='ui',
        timestamp=datetime.now(),
        data={
            'url': 'https://example.com/login',  # Wrong URL!
            'title': 'Login Page',  # Wrong title!
            'elements': {
                '.dashboard': {'visible': False},  # Not visible!
                '.user-profile': {'visible': True, 'text': 'Guest'}  # Wrong text!
            }
        },
        screenshots=['screenshot_002.png']
    )
    
    # Validate FAILING case
    print("\n2️⃣  Testing FAILING validation...")
    result = engine.validate('ui', expected, failing_evidence)
    
    print(f"   Status: {result.status.value.upper()}")
    
    if result.passed_checks:
        print(f"   ✅ Passed checks ({len(result.passed_checks)}):")
        for check in result.passed_checks:
            print(f"      - {check}")
    
    print(f"   ❌ Failed checks ({len(result.failed_checks)}):")
    for check in result.failed_checks:
        print(f"      - {check}")
    
    assert not result.is_pass, "Expected validation to fail"
    print(f"\n   ✅ Test failed as expected (deterministic detection worked)!")


def test_api_validation():
    """Test API validation"""
    print("\n" + "=" * 60)
    print("Testing API Validator")
    print("=" * 60)
    
    engine = ValidationEngine()
    
    # Expected outcome
    expected = {
        'status': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': {
            'success': True,
            'user_id': 123
        },
        'max_response_time': 500
    }
    
    # Passing evidence
    passing_evidence = Evidence(
        evidence_type='api',
        timestamp=datetime.now(),
        data={
            'status': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Server': 'nginx'
            },
            'body': {
                'success': True,
                'user_id': 123,
                'timestamp': '2026-03-26T10:00:00Z'
            },
            'response_time_ms': 245
        }
    )
    
    print("\n1️⃣  Testing PASSING API validation...")
    result = engine.validate('api', expected, passing_evidence)
    
    print(f"   Status: {result.status.value.upper()}")
    print(f"   ✅ Passed checks ({len(result.passed_checks)}):")
    for check in result.passed_checks:
        print(f"      - {check}")
    
    assert result.is_pass, "Expected API validation to pass"
    print(f"\n   ✅ API validation passed!")
    
    # Failing evidence
    failing_evidence = Evidence(
        evidence_type='api',
        timestamp=datetime.now(),
        data={
            'status': 404,  # Wrong status!
            'headers': {
                'Content-Type': 'text/html'  # Wrong content type!
            },
            'body': {},
            'response_time_ms': 750  # Too slow!
        }
    )
    
    print("\n2️⃣  Testing FAILING API validation...")
    result = engine.validate('api', expected, failing_evidence)
    
    print(f"   Status: {result.status.value.upper()}")
    print(f"   ❌ Failed checks ({len(result.failed_checks)}):")
    for check in result.failed_checks:
        print(f"      - {check}")
    
    assert not result.is_pass, "Expected API validation to fail"
    print(f"\n   ✅ API validation failed as expected!")


def test_performance_validation():
    """Test Performance validation"""
    print("\n" + "=" * 60)
    print("Testing Performance Validator")
    print("=" * 60)
    
    engine = ValidationEngine()
    
    # Expected outcome
    expected = {
        'metrics': {
            'response_time_ms': {'max': 1000},
            'throughput_rps': {'min': 100},
            'cpu_percent': {'max': 80}
        }
    }
    
    # Passing evidence
    passing_evidence = Evidence(
        evidence_type='performance',
        timestamp=datetime.now(),
        data={
            'metrics': {
                'response_time_ms': 450,
                'throughput_rps': 250,
                'cpu_percent': 65
            }
        }
    )
    
    print("\n1️⃣  Testing PASSING performance validation...")
    result = engine.validate('performance', expected, passing_evidence)
    
    print(f"   Status: {result.status.value.upper()}")
    print(f"   ✅ Passed checks ({len(result.passed_checks)}):")
    for check in result.passed_checks:
        print(f"      - {check}")
    
    assert result.is_pass, "Expected performance validation to pass"
    print(f"\n   ✅ Performance validation passed!")


def main():
    """Run all validation tests"""
    print("\n🧪 Testing Validation Engine\n")
    
    try:
        test_ui_validation()
        test_api_validation()
        test_performance_validation()
        
        print("\n" + "=" * 60)
        print("✅ All Validation Engine tests passed!")
        print("=" * 60)
        print("\nValidation Engine is DETERMINISTIC - no AI, pure logic ✓")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
