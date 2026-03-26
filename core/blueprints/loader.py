"""
Blueprint Loader - Load blueprints with app-awareness
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
import logging
from .parser import BlueprintParser
from .validator import BlueprintValidator
from .models import Blueprint, ProjectContext


class BlueprintLoader:
    """
    Load and manage blueprints
    
    Features:
    - Load single blueprint
    - Load all blueprints from directory
    - Validate on load
    - Cache loaded blueprints
    """
    
    def __init__(self, validate: bool = True):
        self.parser = BlueprintParser()
        self.validator = BlueprintValidator()
        self.validate_on_load = validate
        self.cache: Dict[str, Blueprint] = {}
        self.logger = logging.getLogger(__name__)
    
    def load(self, file_path: Path, use_cache: bool = True) -> Blueprint:
        """
        Load a single blueprint
        
        Args:
            file_path: Path to blueprint file
            use_cache: Use cached version if available
        
        Returns:
            Blueprint object
        
        Raises:
            ValueError: If blueprint is invalid
        """
        file_path = Path(file_path)
        cache_key = str(file_path.absolute())
        
        # Check cache
        if use_cache and cache_key in self.cache:
            self.logger.debug(f"Loading from cache: {file_path.name}")
            return self.cache[cache_key]
        
        # Parse blueprint
        self.logger.info(f"Loading blueprint: {file_path}")
        blueprint = self.parser.parse_file(file_path)
        
        # Validate if enabled
        if self.validate_on_load:
            is_valid = self.validator.validate(blueprint)
            if not is_valid:
                report = self.validator.get_report()
                raise ValueError(f"Blueprint validation failed:\n{report}")
            
            # Log warnings even if valid
            if self.validator.warnings:
                for warning in self.validator.warnings:
                    self.logger.warning(str(warning))
        
        # Cache and return
        self.cache[cache_key] = blueprint
        return blueprint
    
    def load_directory(self, directory: Path, pattern: str = "*.yaml") -> List[Blueprint]:
        """
        Load all blueprints from directory
        
        Args:
            directory: Directory to scan
            pattern: Glob pattern for files (default: *.yaml)
        
        Returns:
            List of Blueprint objects
        """
        directory = Path(directory)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        blueprints = []
        for file_path in directory.glob(pattern):
            try:
                blueprint = self.load(file_path)
                blueprints.append(blueprint)
            except Exception as e:
                self.logger.error(f"Failed to load {file_path}: {e}")
        
        self.logger.info(f"Loaded {len(blueprints)} blueprints from {directory}")
        return blueprints
    
    def clear_cache(self):
        """Clear blueprint cache"""
        self.cache.clear()
        self.logger.debug("Blueprint cache cleared")


class AppAwareBlueprintLoader:
    """
    App-aware blueprint loader with ProjectContext
    
    CRITICAL: Ensures multi-app isolation by:
    - Loading blueprints only for specific app_id
    - Validating app_id matches
    - Using ProjectContext for all operations
    """
    
    def __init__(self, context: ProjectContext, validate: bool = True):
        self.context = context
        self.loader = BlueprintLoader(validate=validate)
        self.logger = logging.getLogger(__name__)
    
    def load(self, blueprint_name: str) -> Blueprint:
        """
        Load blueprint for this app
        
        Args:
            blueprint_name: Name of blueprint file (with or without extension)
        
        Returns:
            Blueprint object
        
        Raises:
            ValueError: If blueprint app_id doesn't match context
        """
        # Add .yaml extension if not present
        if not blueprint_name.endswith(('.yaml', '.yml', '.json')):
            blueprint_name = f"{blueprint_name}.yaml"
        
        # Construct full path
        file_path = self.context.blueprint_path / blueprint_name
        
        # Load blueprint
        blueprint = self.loader.load(file_path)
        
        # CRITICAL: Verify app_id matches
        if blueprint.metadata.app_id != self.context.app_id:
            raise ValueError(
                f"Blueprint app_id mismatch! "
                f"Expected '{self.context.app_id}', "
                f"got '{blueprint.metadata.app_id}'. "
                f"This blueprint belongs to a different app."
            )
        
        self.logger.info(
            f"Loaded blueprint '{blueprint.metadata.name}' "
            f"for app '{self.context.app_id}'"
        )
        
        return blueprint
    
    def load_all(self, pattern: str = "*.yaml") -> List[Blueprint]:
        """
        Load all blueprints for this app
        
        Args:
            pattern: Glob pattern for files
        
        Returns:
            List of blueprints (only those matching app_id)
        """
        # Load all blueprints from app's directory
        all_blueprints = self.loader.load_directory(
            self.context.blueprint_path,
            pattern
        )
        
        # Filter by app_id (safety check)
        app_blueprints = []
        for blueprint in all_blueprints:
            if blueprint.metadata.app_id == self.context.app_id:
                app_blueprints.append(blueprint)
            else:
                self.logger.warning(
                    f"Skipping blueprint '{blueprint.metadata.name}' - "
                    f"wrong app_id (expected {self.context.app_id}, "
                    f"got {blueprint.metadata.app_id})"
                )
        
        self.logger.info(
            f"Loaded {len(app_blueprints)} blueprints for app '{self.context.app_id}'"
        )
        
        return app_blueprints
    
    def get_by_priority(self, priority: str) -> List[Blueprint]:
        """Get all blueprints of specific priority"""
        blueprints = self.load_all()
        return [bp for bp in blueprints if bp.metadata.priority == priority]
    
    def get_by_tag(self, tag: str) -> List[Blueprint]:
        """Get all blueprints with specific tag"""
        blueprints = self.load_all()
        return [bp for bp in blueprints if tag in bp.metadata.tags]
    
    def get_by_type(self, blueprint_type: str) -> List[Blueprint]:
        """Get all blueprints of specific type"""
        blueprints = self.load_all()
        return [bp for bp in blueprints if bp.type == blueprint_type]


# Convenience functions
def load_blueprint_for_app(app_id: str, blueprint_name: str, 
                          apps_root: Path = Path("apps")) -> Blueprint:
    """
    Convenience function to load a blueprint for a specific app
    
    Usage:
        blueprint = load_blueprint_for_app('app1', 'login_test')
    """
    from .models import ProjectContext
    
    # Create context
    app_path = apps_root / app_id
    context = ProjectContext(
        app_id=app_id,
        blueprint_path=app_path / "blueprints",
        snapshots_path=app_path / "snapshots",
        logs_path=app_path / "logs",
        memory_path=Path(f"core/memory/{app_id}_memory.db")
    )
    
    # Load blueprint
    loader = AppAwareBlueprintLoader(context)
    return loader.load(blueprint_name)
