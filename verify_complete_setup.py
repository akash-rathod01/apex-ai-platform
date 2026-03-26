#!/usr/bin/env python3
"""
COMPLETE SETUP VERIFICATION FOR APEX AI PLATFORM
Checks all installed components and provides setup status
"""

import sys
import sqlite3
from pathlib import Path
import subprocess

def check_python_version():
    """Verify Python version"""
    version = sys.version_info
    status = version.major >= 3 and version.minor >= 10
    print(f"{'✅' if status else '❌'} Python {version.major}.{version.minor}.{version.micro}")
    return status

def check_package(package_name, module_name=None):
    """Check if a Python package is installed"""
    if module_name is None:
        module_name = package_name
    try:
        __import__(module_name)
        print(f"✅ {package_name}")
        return True
    except ImportError:
        print(f"❌ {package_name}")
        return False

def check_node_version():
    """Check Node.js version"""
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        version = result.stdout.strip()
        print(f"✅ Node.js {version}")
        return True
    except:
        print("❌ Node.js not found")
        return False

def check_npm_version():
    """Check npm version"""
    try:
        result = subprocess.run(
            ["npm", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        version = result.stdout.strip()
        print(f"✅ npm {version}")
        return True
    except:
        print("❌ npm not found")
        return False

def check_playwright():
    """Check Playwright installation"""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            chromium_path = p.chromium.executable_path
            if Path(chromium_path).exists():
                print(f"✅ Playwright + Chromium")
                return True
            else:
                print("⚠️  Playwright installed, Chromium missing")
                return False
    except Exception as e:
        print(f"❌ Playwright error: {str(e)[:50]}")
        return False

def check_sqlite():
    """Check SQLite"""
    try:
        import sqlite3
        print(f"✅ SQLite {sqlite3.sqlite_version}")
        return True
    except:
        print("❌ SQLite not available")
        return False

def check_database_manager():
    """Check custom database manager"""
    try:
        sys.path.insert(0, str(Path(__file__).parent / "core" / "memory"))
        from database import get_database_manager
        print(f"✅ DatabaseManager (custom)")
        return True
    except Exception as e:
        print(f"❌ DatabaseManager error: {str(e)[:50]}")
        return False

def check_nextjs():
    """Check Next.js installation"""
    try:
        package_json = Path(__file__).parent / "ui" / "web" / "package.json"
        if package_json.exists():
            import json
            with open(package_json, 'r') as f:
                pkg = json.load(f)
                next_version = pkg.get('dependencies', {}).get('next', 'Unknown')
                print(f"✅ Next.js {next_version}")
                return True
        else:
            print("❌ Next.js not found")
            return False
    except Exception as e:
        print(f"❌ Next.js error: {str(e)[:50]}")
        return False

def check_tailwind():
    """Check TailwindCSS"""
    try:
        package_json = Path(__file__).parent / "ui" / "web" / "package.json"
        if package_json.exists():
            import json
            with open(package_json, 'r') as f:
                pkg = json.load(f)
                if 'tailwindcss' in pkg.get('devDependencies', {}):
                    print(f"✅ TailwindCSS")
                    return True
        print("❌ TailwindCSS not found")
        return False
    except:
        print("❌ TailwindCSS check failed")
        return False

def check_shadcn():
    """Check ShadCN UI"""
    try:
        components_path = Path(__file__).parent / "ui" / "web" / "components" / "ui"
        if components_path.exists() and list(components_path.glob("*.tsx")):
            print(f"✅ ShadCN UI components")
            return True
        else:
            print("❌ ShadCN UI components not found")
            return False
    except:
        print("❌ ShadCN UI check failed")
        return False

def main():
    print("=" * 70)
    print("APEX AI PLATFORM — COMPLETE SETUP VERIFICATION")
    print("=" * 70)
    print()
    
    # Core Runtimes
    print("🔧 CORE RUNTIMES:")
    results = []
    results.append(check_python_version())
    results.append(check_node_version())
    results.append(check_npm_version())
    print()
    
    # Python Packages
    print("📦 PYTHON PACKAGES:")
    results.append(check_package("PyYAML", "yaml"))
    results.append(check_package("pytest"))
    results.append(check_package("requests"))
    results.append(check_package("Selenium", "selenium"))
    print()
    
    # Testing Tools
    print("🧪 TESTING TOOLS:")
    results.append(check_playwright())
    print()
    
    # Database
    print("💾 DATABASE & STORAGE:")
    results.append(check_sqlite())
    results.append(check_database_manager())
    print()
    
    # Web UI
    print("🎨 WEB UI FRAMEWORK:")
    results.append(check_nextjs())
    results.append(check_tailwind())
    results.append(check_shadcn())
    print()
    
    # Check created files
    print("📁 CREATED FILES:")
    created_files = [
        ("verify_setup.py", "Basic setup verification"),
        ("test_database.py", "Database test script"),
        ("SETUP_COMPLETE.md", "Setup documentation"),
        ("core/memory/database.py", "Database manager"),
        ("ui/web/package.json", "Next.js configuration"),
        ("ui/web/components/ui/button.tsx", "ShadCN button component"),
    ]
    
    files_ok = True
    for file_path, description in created_files:
        full_path = Path(__file__).parent / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            files_ok = False
    results.append(files_ok)
    print()
    
    # Check database files
    print("💿 DATABASE FILES (created on first use):")
    db_files = [
        "core/memory/app1_memory.db",
        "core/memory/app2_memory.db",
    ]
    
    for db_file in db_files:
        full_path = Path(__file__).parent / db_file
        if full_path.exists():
            size_kb = full_path.stat().st_size / 1024
            print(f"✅ {db_file} ({size_kb:.1f} KB)")
        else:
            print(f"⚠️  {db_file} (will be created on first use)")
    print()
    
    # Summary
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ ALL CHECKS PASSED ({passed}/{total})")
        print()
        print("🚀 APEX AI PLATFORM IS READY FOR DEVELOPMENT!")
        print()
        print("Next steps:")
        print("  1. Start Next.js dev server: cd ui/web && npm run dev")
        print("  2. Test database: python test_database.py")
        print("  3. Build Blueprint Engine using Copilot instructions")
        print("  4. Build Validation Engine using Copilot instructions")
        print("  5. Build core Agents (QA, Perf, Security, DevOps, Docs)")
    else:
        print(f"⚠️  {passed}/{total} CHECKS PASSED")
        print()
        print("Some components may need installation or configuration.")
        print("Review the output above for details.")
    
    print("=" * 70)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
