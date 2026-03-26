"""
Test Blueprint Engine components
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.blueprints.parser import BlueprintParser
from core.blueprints.validator import BlueprintValidator
from core.blueprints.loader import AppAwareBlueprintLoader
from core.blueprints.models import ProjectContext


def test_blueprint_engine():
    """Test complete Blueprint Engine workflow"""
    print("=" * 60)
    print("Testing Blueprint Engine")
    print("=" * 60)
    
    # 1. Test Parser
    print("\n1️⃣  Testing Blueprint Parser...")
    parser = BlueprintParser()
    
    try:
        blueprint_file = Path("apps/app1/blueprints/login_test.yaml")
        blueprint = parser.parse_file(blueprint_file)
        
        print(f"✅ Parsed blueprint: {blueprint.metadata.name}")
        print(f"   - Blueprint ID: {blueprint.blueprint_id}")
        print(f"   - Type: {blueprint.type}")
        print(f"   - App ID: {blueprint.metadata.app_id}")
        print(f"   - Priority: {blueprint.metadata.priority}")
        print(f"   - Tags: {', '.join(blueprint.metadata.tags)}")
        print(f"   - Steps: {len(blueprint.steps)}")
        
    except Exception as e:
        print(f"❌ Parser failed: {e}")
        return False
    
    # 2. Test Validator
    print("\n2️⃣  Testing Blueprint Validator...")
    validator = BlueprintValidator()
    
    is_valid = validator.validate(blueprint)
    report = validator.get_report()
    
    if is_valid:
        print("✅ Blueprint is valid!")
        print(report)
    else:
        print("❌ Blueprint validation failed!")
        print(report)
        return False
    
    # 3. Test App-Aware Loader
    print("\n3️⃣  Testing App-Aware Blueprint Loader...")
    
    try:
        # Create ProjectContext for app1
        context = ProjectContext(
            app_id="app1",
            blueprint_path=Path("apps/app1/blueprints"),
            snapshots_path=Path("apps/app1/snapshots"),
            logs_path=Path("apps/app1/logs"),
            memory_path=Path("core/memory/app1_memory.db")
        )
        
        # Create app-aware loader
        loader = AppAwareBlueprintLoader(context)
        
        # Load blueprint
        loaded_blueprint = loader.load("login_test.yaml")
        
        print(f"✅ Loaded blueprint via AppAwareBlueprintLoader")
        print(f"   - Name: {loaded_blueprint.metadata.name}")
        print(f"   - App ID verified: {loaded_blueprint.metadata.app_id}")
        print(f"   - Steps loaded: {len(loaded_blueprint.steps)}")
        
        # Test app_id isolation
        print("\n4️⃣  Testing App ID Isolation...")
        print("   Attempting to load blueprint with wrong app_id...")
        
        # Create context for app2
        wrong_context = ProjectContext(
            app_id="app2",
            blueprint_path=Path("apps/app1/blueprints"),  # Wrong path!
            snapshots_path=Path("apps/app2/snapshots"),
            logs_path=Path("apps/app2/logs"),
            memory_path=Path("core/memory/app2_memory.db")
        )
        
        wrong_loader = AppAwareBlueprintLoader(wrong_context)
        
        try:
            # This should fail - blueprint is for app1, not app2
            wrong_loader.load("login_test.yaml")
            print("   ❌ ERROR: App ID isolation failed! Should have rejected blueprint.")
            return False
        except ValueError as e:
            if "app_id mismatch" in str(e):
                print(f"   ✅ App ID isolation working! Correctly rejected: {str(e)[:80]}...")
            else:
                raise
        
    except Exception as e:
        print(f"❌ Loader failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 5. Display loaded blueprint details
    print("\n5️⃣  Blueprint Details:")
    print(f"   Steps in '{loaded_blueprint.metadata.name}':")
    for idx, step in enumerate(loaded_blueprint.steps, 1):
        print(f"      {idx}. {step.action.upper()}", end="")
        if step.selector:
            print(f" → {step.selector}", end="")
        if step.value:
            print(f" = {step.value}", end="")
        print()
    
    print(f"\n   Expected Outcomes:")
    for key, value in loaded_blueprint.expected.items():
        print(f"      - {key}: {value}")
    
    print("\n" + "=" * 60)
    print("✅ All Blueprint Engine tests passed!")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = test_blueprint_engine()
    sys.exit(0 if success else 1)
