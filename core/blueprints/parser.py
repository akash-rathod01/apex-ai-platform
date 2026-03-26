"""
Blueprint Parser - Parse YAML/JSON blueprints
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, Union
from .models import Blueprint, BlueprintStep, BlueprintMetadata


class BlueprintParser:
    """
    Parse YAML/JSON blueprints into Blueprint objects
    
    Supports:
    - YAML files (.yaml, .yml)
    - JSON files (.json)
    - Validation during parsing
    """
    
    def __init__(self):
        self.supported_versions = ["1.0", "1.1"]
    
    def parse_file(self, file_path: Union[str, Path]) -> Blueprint:
        """
        Parse blueprint from file
        
        Args:
            file_path: Path to blueprint file (.yaml or .json)
        
        Returns:
            Blueprint object
        
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Blueprint file not found: {file_path}")
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse based on extension
        if file_path.suffix in ['.yaml', '.yml']:
            data = yaml.safe_load(content)
        elif file_path.suffix == '.json':
            data = json.loads(content)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        # Convert to Blueprint object
        blueprint = self.parse_dict(data)
        blueprint.source_file = file_path
        
        return blueprint
    
    def parse_dict(self, data: Dict[str, Any]) -> Blueprint:
        """
        Parse blueprint from dictionary
        
        Args:
            data: Blueprint data as dictionary
        
        Returns:
            Blueprint object
        """
        # Validate version
        version = data.get('version', '1.0')
        if version not in self.supported_versions:
            raise ValueError(
                f"Unsupported blueprint version: {version}. "
                f"Supported: {self.supported_versions}"
            )
        
        # Parse metadata
        metadata_data = data.get('metadata', {})
        metadata = BlueprintMetadata(
            name=metadata_data.get('name', 'Unnamed Test'),
            app_id=metadata_data.get('app_id', 'unknown'),
            priority=metadata_data.get('priority', 'medium'),
            tags=metadata_data.get('tags', []),
            author=metadata_data.get('author'),
            created_at=metadata_data.get('created_at'),
            updated_at=metadata_data.get('updated_at'),
        )
        
        # Parse steps
        steps_data = data.get('steps', [])
        steps = [self._parse_step(step_data) for step_data in steps_data]
        
        # Parse setup/teardown (optional)
        setup = None
        if 'setup' in data:
            setup = [self._parse_step(step) for step in data['setup']]
        
        teardown = None
        if 'teardown' in data:
            teardown = [self._parse_step(step) for step in data['teardown']]
        
        # Create Blueprint
        blueprint = Blueprint(
            blueprint_id=data['blueprint_id'],
            version=version,
            type=data['type'],
            metadata=metadata,
            steps=steps,
            expected=data.get('expected', {}),
            setup=setup,
            teardown=teardown,
        )
        
        return blueprint
    
    def _parse_step(self, step_data: Dict[str, Any]) -> BlueprintStep:
        """Parse single test step"""
        return BlueprintStep(
            action=step_data['action'],
            target=step_data.get('target'),
            selector=step_data.get('selector'),
            value=step_data.get('value'),
            expected=step_data.get('expected'),
            timeout=step_data.get('timeout', 5000),
            metadata=step_data.get('metadata', {}),
        )
    
    def parse_string(self, content: str, format: str = 'yaml') -> Blueprint:
        """
        Parse blueprint from string
        
        Args:
            content: Blueprint content as string
            format: 'yaml' or 'json'
        
        Returns:
            Blueprint object
        """
        if format == 'yaml':
            data = yaml.safe_load(content)
        elif format == 'json':
            data = json.loads(content)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return self.parse_dict(data)


# Convenience function
def load_blueprint(file_path: Union[str, Path]) -> Blueprint:
    """
    Convenience function to load a blueprint
    
    Usage:
        blueprint = load_blueprint('apps/app1/blueprints/login_test.yaml')
    """
    parser = BlueprintParser()
    return parser.parse_file(file_path)
