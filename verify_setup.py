#!/usr/bin/env python3
"""
Verification Script for Apex AI Platform Setup
Checks all installed tools and dependencies.
"""

import sys
from pathlib import Path

def check_python_version():
    """Verify Python version is 3.10+"""
    version = sys.version_info
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 10:
        return True
    print(f"⚠️  Python 3.10+ required, found {version.major}.{version.minor}")
    return False

def check_package(package_name, module_name=None):
    """Check if a Python package is installed"""
    if module_name is None:
        module_name = package_name
    try:
        __import__(module_name)
        print(f"✅ {package_name}")
        return True
    except ImportError:
        print(f"❌ {package_name} not installed")
        return False

def check_playwright():
    """Verify Playwright and browser installation"""
    try:
        from playwright.sync_api import sync_playwright
        print("✅ Playwright (Python package)")
        
        # Check browser installation
        with sync_playwright() as p:
            chromium_path = p.chromium.executable_path
            if Path(chromium_path).exists():
                print(f"✅ Chromium browser (installed)")
                return True
            else:
                print(f"⚠️  Chromium browser not found")
                return False
    except Exception as e:
        print(f"❌ Playwright error: {e}")
        return False

def main():
    print("=" * 60)
    print("APEX AI PLATFORM - SETUP VERIFICATION")
    print("=" * 60)
    print()
    
    print("📋 Core Runtime:")
    python_ok = check_python_version()
    print()
    
    print("📦 Essential Python Packages:")
    packages = {
        "PyYAML": "yaml",
        "pytest": "pytest",
        "requests": "requests",
    }
    
    packages_ok = all(check_package(name, module) for name, module in packages.items())
    print()
    
    print("🧪 UI Testing Tools:")
    playwright_ok = check_playwright()
    selenium_ok = check_package("Selenium", "selenium")
    print()
    
    print("=" * 60)
    if python_ok and packages_ok and playwright_ok:
        print("✅ ALL CHECKS PASSED - Ready to build Apex AI Platform!")
        print()
        print("Next Steps:")
        print("1. Create Python virtual environment (optional)")
        print("2. Start building core/blueprints engine")
        print("3. Implement core/validation engine")
        print("4. Build core/agents (QA, Perf, Security, DevOps, Docs)")
    else:
        print("⚠️  Some checks failed - review installation")
    print("=" * 60)

if __name__ == "__main__":
    main()
