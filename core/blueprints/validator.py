"""
Blueprint Validator - Validate blueprint structure and content
"""

from typing import List, Dict, Any
from pathlib import Path
from .models import Blueprint, BlueprintType, ActionType


class ValidationError:
    """Single validation error"""
    def __init__(self, message: str, path: str = None, severity: str = "error"):
        self.message = message
        self.path = path
        self.severity = severity  # error, warning, info
    
    def __str__(self):
        if self.path:
            return f"[{self.severity.upper()}] {self.path}: {self.message}"
        return f"[{self.severity.upper()}] {self.message}"


class BlueprintValidator:
    """
    Validate blueprint structure and content
    
    Checks:
    - Required fields present
    - Valid action types
    - Valid blueprint types
    - Selector presence for UI actions
    - Expected values format
    - Timeout values
    """
    
    def __init__(self):
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
    
    def validate(self, blueprint: Blueprint) -> bool:
        """
        Validate a blueprint
        
        Returns:
            True if valid (no errors), False otherwise
            Warnings don't prevent validation from passing
        """
        self.errors = []
        self.warnings = []
        
        # Validate blueprint type
        self._validate_blueprint_type(blueprint)
        
        # Validate metadata
        self._validate_metadata(blueprint)
        
        # Validate steps
        self._validate_steps(blueprint.steps, "steps")
        
        # Validate setup/teardown if present
        if blueprint.setup:
            self._validate_steps(blueprint.setup, "setup")
        if blueprint.teardown:
            self._validate_steps(blueprint.teardown, "teardown")
        
        # Validate expected outcomes
        self._validate_expected(blueprint)
        
        return len(self.errors) == 0
    
    def _validate_blueprint_type(self, blueprint: Blueprint):
        """Validate blueprint type is valid"""
        valid_types = [t.value for t in BlueprintType]
        if blueprint.type not in valid_types:
            self.errors.append(ValidationError(
                f"Invalid blueprint type '{blueprint.type}'. Valid types: {valid_types}",
                "blueprint.type"
            ))
    
    def _validate_metadata(self, blueprint: Blueprint):
        """Validate metadata fields"""
        metadata = blueprint.metadata
        
        # Check required fields
        if not metadata.name or metadata.name.strip() == "":
            self.errors.append(ValidationError(
                "Blueprint name is required",
                "metadata.name"
            ))
        
        if not metadata.app_id or metadata.app_id.strip() == "":
            self.errors.append(ValidationError(
                "App ID is required for multi-app isolation",
                "metadata.app_id"
            ))
        
        # Validate priority
        valid_priorities = ['low', 'medium', 'high', 'critical']
        if metadata.priority not in valid_priorities:
            self.warnings.append(ValidationError(
                f"Priority '{metadata.priority}' not standard. Use: {valid_priorities}",
                "metadata.priority",
                "warning"
            ))
    
    def _validate_steps(self, steps: List, path: str):
        """Validate test steps"""
        if not steps or len(steps) == 0:
            self.errors.append(ValidationError(
                f"At least one step is required",
                path
            ))
            return
        
        for idx, step in enumerate(steps):
            step_path = f"{path}[{idx}]"
            
            # Validate action type
            valid_actions = [a.value for a in ActionType]
            if step.action not in valid_actions:
                self.errors.append(ValidationError(
                    f"Invalid action '{step.action}'. Valid actions: {valid_actions}",
                    f"{step_path}.action"
                ))
            
            # UI actions require selector
            ui_actions = ['click', 'fill', 'select', 'hover', 'drag']
            if step.action in ui_actions and not step.selector:
                self.errors.append(ValidationError(
                    f"Action '{step.action}' requires a selector",
                    f"{step_path}.selector"
                ))
            
            # Fill/select actions require value
            value_actions = ['fill', 'select']
            if step.action in value_actions and step.value is None:
                self.warnings.append(ValidationError(
                    f"Action '{step.action}' typically requires a value",
                    f"{step_path}.value",
                    "warning"
                ))
            
            # Assert actions require expected
            if step.action == 'assert' and not step.expected:
                self.errors.append(ValidationError(
                    "Assert action requires 'expected' field",
                    f"{step_path}.expected"
                ))
            
            # Validate timeout
            if step.timeout and (step.timeout < 0 or step.timeout > 300000):
                self.warnings.append(ValidationError(
                    f"Timeout {step.timeout}ms seems unusual (0-300000ms recommended)",
                    f"{step_path}.timeout",
                    "warning"
                ))
    
    def _validate_expected(self, blueprint: Blueprint):
        """Validate expected outcomes structure"""
        if not blueprint.expected:
            self.warnings.append(ValidationError(
                "No expected outcomes defined - test may not validate properly",
                "expected",
                "warning"
            ))
            return
        
        # Type-specific validation
        if blueprint.type == BlueprintType.UI.value:
            # UI tests should define visual expectations
            if 'elements' not in blueprint.expected and 'url' not in blueprint.expected:
                self.warnings.append(ValidationError(
                    "UI blueprint should define expected.elements or expected.url",
                    "expected",
                    "warning"
                ))
        
        elif blueprint.type == BlueprintType.API.value:
            # API tests should define response expectations
            if 'status' not in blueprint.expected:
                self.warnings.append(ValidationError(
                    "API blueprint should define expected.status",
                    "expected",
                    "warning"
                ))
        
        elif blueprint.type == BlueprintType.PERFORMANCE.value:
            # Performance tests should define metrics
            if 'metrics' not in blueprint.expected:
                self.warnings.append(ValidationError(
                    "Performance blueprint should define expected.metrics",
                    "expected",
                    "warning"
                ))
    
    def get_report(self) -> str:
        """Get validation report as string"""
        lines = []
        
        if self.errors:
            lines.append(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                lines.append(f"  {error}")
        
        if self.warnings:
            lines.append(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                lines.append(f"  {warning}")
        
        if not self.errors and not self.warnings:
            lines.append("\n✅ Blueprint is valid - no errors or warnings")
        
        return "\n".join(lines)


# Convenience function
def validate_blueprint(blueprint: Blueprint) -> tuple[bool, str]:
    """
    Validate a blueprint and return result + report
    
    Returns:
        (is_valid, report_string)
    
    Usage:
        is_valid, report = validate_blueprint(blueprint)
        if not is_valid:
            print(report)
    """
    validator = BlueprintValidator()
    is_valid = validator.validate(blueprint)
    report = validator.get_report()
    return is_valid, report
