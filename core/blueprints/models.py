"""
Blueprint Models - Data structures for test blueprints
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from pathlib import Path


class BlueprintType(Enum):
    """Blueprint test types"""
    UI = "ui"
    API = "api"
    PERFORMANCE = "performance"
    SECURITY = "security"
    E2E = "e2e"


class ActionType(Enum):
    """Available test actions"""
    NAVIGATE = "navigate"
    CLICK = "click"
    FILL = "fill"
    SELECT = "select"
    WAIT = "wait"
    ASSERT = "assert"
    API_CALL = "api_call"
    SCREENSHOT = "screenshot"


@dataclass
class BlueprintMetadata:
    """Blueprint metadata"""
    name: str
    app_id: str
    priority: str = "medium"  # low, medium, high, critical
    tags: List[str] = field(default_factory=list)
    author: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class BlueprintStep:
    """Single test step in blueprint"""
    action: str
    target: Optional[str] = None
    selector: Optional[str] = None
    value: Optional[Any] = None
    expected: Optional[Dict[str, Any]] = None
    timeout: int = 5000
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate step after initialization"""
        if self.action not in [a.value for a in ActionType]:
            raise ValueError(f"Invalid action: {self.action}")


@dataclass
class Blueprint:
    """
    Complete test blueprint
    
    This is the source of truth for test execution.
    NO test scripts are stored - everything is generated from this.
    """
    blueprint_id: str
    version: str
    type: str  # ui, api, performance, security
    metadata: BlueprintMetadata
    steps: List[BlueprintStep]
    expected: Dict[str, Any] = field(default_factory=dict)
    setup: Optional[List[BlueprintStep]] = None
    teardown: Optional[List[BlueprintStep]] = None
    
    # Runtime context (not from YAML)
    source_file: Optional[Path] = None
    
    def __post_init__(self):
        """Validate blueprint after initialization"""
        if self.type not in [t.value for t in BlueprintType]:
            raise ValueError(f"Invalid blueprint type: {self.type}")
    
    @property
    def app_id(self) -> str:
        """Get application ID from metadata"""
        return self.metadata.app_id
    
    @property
    def is_ui_test(self) -> bool:
        """Check if this is a UI test"""
        return self.type == BlueprintType.UI.value
    
    @property
    def is_api_test(self) -> bool:
        """Check if this is an API test"""
        return self.type == BlueprintType.API.value
    
    @property
    def is_performance_test(self) -> bool:
        """Check if this is a performance test"""
        return self.type == BlueprintType.PERFORMANCE.value
    
    @property
    def is_security_test(self) -> bool:
        """Check if this is a security test"""
        return self.type == BlueprintType.SECURITY.value


@dataclass
class ProjectContext:
    """
    Application context for multi-app isolation
    
    CRITICAL: Every operation MUST have a ProjectContext
    This ensures complete isolation between applications
    """
    app_id: str
    blueprint_path: Path
    snapshots_path: Path
    logs_path: Path
    memory_path: Path
    
    # Tool configuration (per-app)
    ui_tools: List[str] = field(default_factory=list)
    api_tools: List[str] = field(default_factory=list)
    perf_tools: List[str] = field(default_factory=list)
    security_tools: List[str] = field(default_factory=list)
    
    # LLM configuration
    llm_model: str = "qwen2.5:3b"
    llm_provider: str = "ollama"
    
    @classmethod
    def from_app_id(cls, app_id: str, base_path: Optional[Path] = None):
        """Create ProjectContext from app_id"""
        if base_path is None:
            base_path = Path.cwd()
        
        app_path = base_path / "apps" / app_id
        
        return cls(
            app_id=app_id,
            blueprint_path=app_path / "blueprints",
            snapshots_path=app_path / "snapshots",
            logs_path=app_path / "logs",
            memory_path=base_path / "core" / "memory" / f"{app_id}_memory.db",
            ui_tools=["playwright"],  # Default tools
            api_tools=["requests"],
            perf_tools=["k6"],
            security_tools=["zap"],
        )
