"""
Base Agent - Foundation for all AI agents
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

from ..blueprints.models import ProjectContext
from ..memory.database import DatabaseManager


class BaseAgent:
    """
    Base class for all AI agents
    
    CRITICAL Features:
    - ProjectContext for multi-app isolation
    - Memory access via DatabaseManager
    - Logging with app_id context
    - Tool configuration per app
    """
    
    def __init__(self, context: ProjectContext, agent_type: str):
        """
        Initialize base agent
        
        Args:
            context: ProjectContext with app_id and paths
            agent_type: Type of agent (qa, performance, security, etc.)
        """
        self.context = context
        self.agent_type = agent_type
        self.app_id = context.app_id
        
        # Setup logging with app context
        self.logger = logging.getLogger(f"{__name__}.{agent_type}.{self.app_id}")
        
        # Setup memory database with app isolation
        self.db = DatabaseManager(context.memory_path, context.app_id)
        
        # Agent state
        self.session_id = self._generate_session_id()
        self.execution_count = 0
        
        self.logger.info(
            f"{agent_type.upper()} Agent initialized for app '{self.app_id}' "
            f"(session: {self.session_id})"
        )
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{self.agent_type}_{self.app_id}_{timestamp}"
    
    def log_execution(self, action: str, details: Dict[str, Any]):
        """
        Log agent execution
        
        Args:
            action: Action performed
            details: Action details
        """
        self.execution_count += 1
        
        log_entry = {
            'session_id': self.session_id,
            'execution_number': self.execution_count,
            'agent_type': self.agent_type,
            'app_id': self.app_id,
            'action': action,
            'timestamp': datetime.now().isoformat(),
            **details
        }
        
        # Write to log file
        log_file = self.context.logs_path / f"{self.session_id}.json"
        self._append_to_log_file(log_file, log_entry)
        
        self.logger.info(f"Action: {action} | Details: {details}")
    
    def _append_to_log_file(self, log_file: Path, entry: Dict[str, Any]):
        """Append entry to JSON log file"""
        import json
        
        # Ensure log directory exists
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Append entry
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
    
    def save_snapshot(self, snapshot_type: str, data: Dict[str, Any]) -> Path:
        """
        Save snapshot (screenshot, DOM, network trace, etc.)
        
        Args:
            snapshot_type: Type of snapshot (screenshot, dom, network, etc.)
            data: Snapshot data
        
        Returns:
            Path to saved snapshot
        """
        # Ensure snapshot directory exists
        self.context.snapshots_path.mkdir(parents=True, exist_ok=True)
        
        # Generate snapshot filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        snapshot_name = f"{snapshot_type}_{timestamp}"
        
        # Save based on type
        if snapshot_type == 'screenshot':
            # Binary image data
            snapshot_file = self.context.snapshots_path / f"{snapshot_name}.png"
            with open(snapshot_file, 'wb') as f:
                f.write(data['binary'])
        else:
            # JSON data
            import json
            snapshot_file = self.context.snapshots_path / f"{snapshot_name}.json"
            with open(snapshot_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        
        self.logger.debug(f"Saved {snapshot_type} snapshot: {snapshot_file.name}")
        
        return snapshot_file
    
    def get_tool_config(self, tool_type: str) -> List[str]:
        """
        Get tool configuration for this app
        
        Args:
            tool_type: Type of tool (ui, api, performance, security)
        
        Returns:
            List of tool names configured for this app
        """
        tool_map = {
            'ui': self.context.ui_tools,
            'api': self.context.api_tools,
            'performance': self.context.performance_tools,
            'security': self.context.security_tools,
        }
        
        return tool_map.get(tool_type, [])
    
    def cleanup(self):
        """Cleanup agent resources"""
        self.logger.info(
            f"{self.agent_type.upper()} Agent cleanup "
            f"(executed {self.execution_count} actions)"
        )
        
        # Close database connection
        self.db.close()


class AgentCapability:
    """
    Agent capability descriptor
    
    Describes what an agent can do
    """
    
    def __init__(self, name: str, description: str, 
                 required_tools: List[str] = None):
        self.name = name
        self.description = description
        self.required_tools = required_tools or []
    
    def can_execute(self, available_tools: List[str]) -> bool:
        """Check if capability can be executed with available tools"""
        return all(tool in available_tools for tool in self.required_tools)


class AgentRegistry:
    """
    Registry of available agents and their capabilities
    
    Used for agent discovery and selection
    """
    
    def __init__(self):
        self.agents: Dict[str, type] = {}
        self.capabilities: Dict[str, List[AgentCapability]] = {}
    
    def register(self, agent_type: str, agent_class: type, 
                capabilities: List[AgentCapability]):
        """Register an agent"""
        self.agents[agent_type] = agent_class
        self.capabilities[agent_type] = capabilities
    
    def get_agent(self, agent_type: str) -> Optional[type]:
        """Get agent class by type"""
        return self.agents.get(agent_type)
    
    def get_capabilities(self, agent_type: str) -> List[AgentCapability]:
        """Get agent capabilities"""
        return self.capabilities.get(agent_type, [])
    
    def list_agents(self) -> List[str]:
        """List all registered agent types"""
        return list(self.agents.keys())


# Global agent registry
agent_registry = AgentRegistry()
