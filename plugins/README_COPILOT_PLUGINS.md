# Copilot Instructions — Plugin Ecosystem

## ✅ Purpose
Provide a lightweight, modular, installable set of integrations for tools that agents use to perform testing and validation.

---

## ✅ Core Plugin Philosophy

### Plugins are Runtime-Loaded Components
Plugins enable the platform to remain:
- **Modular** - Each tool is isolated
- **Extensible** - New tools added without core changes
- **Upgradeable** - Plugin versions managed independently
- **Replaceable** - Swap implementations easily

### Plugins vs Core
- **Core** = Blueprint engine, agents, validation, runtime, memory
- **Plugins** = External tools (Playwright, JMeter, ZAP, etc.)

---

## ✅ Rules for Plugins

### Plugin Architecture Rules
1. **Plugins MUST remain isolated** from each other
2. **Never hardcode plugin logic into agents** (use plugin loader)
3. **Each plugin must have**:
   - Adapter (standardized interface)
   - Metadata (name, version, capabilities)
   - Config (plugin-specific settings)
   - Safe execution wrapper (error handling, timeouts)
4. **Keep plugins small and replaceable**
5. **Plugins should be provider-agnostic where possible**

### Plugin Lifecycle
```
Plugin Discovery → Installation → Validation → Loading → Execution → Cleanup
```

---

## ✅ Plugin Categories

### QA Plugins
- **UI Testing**: Playwright, Selenium, Cypress, Puppeteer
- **API Testing**: REST clients, GraphQL clients, gRPC clients
- **Mobile Testing**: Appium

### API Plugins
- **REST**: Axios, Requests, Fetch API
- **GraphQL**: Apollo Client
- **gRPC**: gRPC clients
- **SOAP**: SOAP clients

### Performance Plugins
- **Load Testing**: k6, JMeter, Locust, Artillery
- **Profiling**: py-spy, cProfile
- **Monitoring**: Prometheus, Grafana, DataDog

### Security Plugins
- **DAST**: OWASP ZAP, Burp Suite
- **SAST**: Bandit, Semgrep, SonarQube
- **Dependency Scanning**: Safety, Snyk, npm audit
- **Network Scanning**: Nmap, Nikto

### DevOps Plugins
- **CI/CD**: GitHub CLI, Jenkins Client, GitLab API
- **Infrastructure**: Terraform, Ansible, Pulumi
- **Containers**: Docker, Kubernetes (kubectl)
- **Cloud**: AWS CLI, Azure CLI, GCP SDK

### AI Plugins
- **LLM Adapters**: OpenAI, Anthropic, Azure OpenAI, Local models
- **Vision**: Image recognition, OCR
- **NLP**: Sentiment analysis, entity extraction

### Community Plugins
- User-contributed plugins
- Third-party integrations
- Custom tool wrappers

---

## ✅ Plugin Structure

### Standard Plugin Layout
```
plugins/<category>/<plugin_name>/
├── __init__.py
├── adapter.py           # Main plugin adapter
├── config.py            # Plugin configuration
├── metadata.json        # Plugin metadata
├── requirements.txt     # Plugin dependencies
├── schemas/             # Input/output schemas
├── utils/               # Plugin-specific utilities
├── tests/               # Plugin unit tests
└── README.md            # Plugin documentation
```

### Plugin Metadata (metadata.json)
```json
{
  "name": "playwright",
  "version": "1.40.0",
  "category": "qa",
  "description": "Modern web UI testing framework",
  "author": "Apex AI Platform",
  "capabilities": [
    "ui_testing",
    "browser_automation",
    "network_interception",
    "visual_regression"
  ],
  "supported_platforms": ["windows", "linux", "macos"],
  "dependencies": {
    "playwright": ">=1.40.0",
    "pillow": ">=10.0.0"
  },
  "config_schema": "schemas/config.schema.json"
}
```

---

## ✅ Plugin Adapter Interface

### Base Plugin Adapter
```python
from abc import ABC, abstractmethod
from typing import Any, Dict

class BasePluginAdapter(ABC):
    """Base class for all plugin adapters"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metadata = self.load_metadata()
        self.validate_config()
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute plugin's main functionality"""
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """Validate plugin configuration"""
        pass
    
    @abstractmethod
    def cleanup(self):
        """Cleanup resources after execution"""
        pass
    
    def load_metadata(self) -> dict:
        """Load plugin metadata"""
        with open("metadata.json") as f:
            return json.load(f)
    
    def get_capability(self, capability: str) -> bool:
        """Check if plugin has capability"""
        return capability in self.metadata.get("capabilities", [])
```

### Example: Playwright Plugin Adapter
```python
class PlaywrightAdapter(BasePluginAdapter):
    """Playwright UI testing plugin"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.browser = None
        self.context = None
        self.page = None
    
    def execute(self, test_script: str, options: Dict = None) -> TestResult:
        """Execute Playwright test script"""
        
        try:
            # Initialize browser
            self._init_browser(options or {})
            
            # Execute test script
            result = self._run_script(test_script)
            
            # Collect evidence
            evidence = self._collect_evidence()
            
            return TestResult(
                status="SUCCESS",
                evidence=evidence,
                metrics=self._get_metrics()
            )
        
        except Exception as e:
            return TestResult(
                status="ERROR",
                error=str(e),
                traceback=traceback.format_exc()
            )
        
        finally:
            self.cleanup()
    
    def validate_config(self) -> bool:
        """Validate Playwright configuration"""
        required = ["browser_type", "headless"]
        for key in required:
            if key not in self.config:
                raise ValueError(f"Missing required config: {key}")
        return True
    
    def cleanup(self):
        """Close browser and cleanup"""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
    
    def _init_browser(self, options: dict):
        """Initialize Playwright browser"""
        from playwright.sync_api import sync_playwright
        
        playwright = sync_playwright().start()
        browser_type = self.config.get("browser_type", "chromium")
        
        self.browser = getattr(playwright, browser_type).launch(
            headless=self.config.get("headless", True),
            **options
        )
        
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
    
    def _run_script(self, script: str):
        """Execute test script"""
        # Execute generated test script
        exec_globals = {"page": self.page, "context": self.context}
        exec(script, exec_globals)
        return exec_globals
    
    def _collect_evidence(self) -> dict:
        """Collect test execution evidence"""
        return {
            "screenshots": self._capture_screenshot(),
            "dom_state": self.page.content(),
            "console_logs": self.page._console_logs,
            "network_logs": self.page._network_logs
        }
```

---

## ✅ Plugin Loader

### Dynamic Plugin Loading
```python
class PluginLoader:
    """Load and manage plugins at runtime"""
    
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = plugin_dir
        self.loaded_plugins = {}
        self.plugin_registry = self._discover_plugins()
    
    def load(self, plugin_name: str, version: str = None) -> BasePluginAdapter:
        """Load plugin by name and version"""
        
        # Check if already loaded
        cache_key = f"{plugin_name}:{version or 'latest'}"
        if cache_key in self.loaded_plugins:
            return self.loaded_plugins[cache_key]
        
        # Find plugin in registry
        plugin_info = self._find_plugin(plugin_name, version)
        if not plugin_info:
            raise PluginNotFoundError(f"Plugin {plugin_name} not found")
        
        # Import plugin module
        plugin_module = self._import_plugin(plugin_info)
        
        # Get adapter class
        adapter_class = getattr(plugin_module, "Adapter")
        
        # Load plugin config
        config = self._load_plugin_config(plugin_info)
        
        # Instantiate adapter
        adapter = adapter_class(config)
        
        # Cache loaded plugin
        self.loaded_plugins[cache_key] = adapter
        
        return adapter
    
    def _discover_plugins(self) -> List[dict]:
        """Discover all available plugins"""
        plugins = []
        
        for category_dir in os.listdir(self.plugin_dir):
            category_path = os.path.join(self.plugin_dir, category_dir)
            
            if not os.path.isdir(category_path):
                continue
            
            for plugin_dir in os.listdir(category_path):
                plugin_path = os.path.join(category_path, plugin_dir)
                metadata_path = os.path.join(plugin_path, "metadata.json")
                
                if os.path.exists(metadata_path):
                    with open(metadata_path) as f:
                        metadata = json.load(f)
                        metadata["path"] = plugin_path
                        metadata["category"] = category_dir
                        plugins.append(metadata)
        
        return plugins
    
    def _find_plugin(self, name: str, version: str = None) -> dict:
        """Find plugin in registry"""
        for plugin in self.plugin_registry:
            if plugin["name"] == name:
                if version is None or plugin["version"] == version:
                    return plugin
        return None
    
    def install_plugin(self, plugin_source: str):
        """Install plugin from source (URL, local path, registry)"""
        # Download/copy plugin
        # Validate metadata
        # Install dependencies
        # Register plugin
        pass
    
    def uninstall_plugin(self, plugin_name: str):
        """Uninstall plugin"""
        # Remove from loaded cache
        # Delete plugin files
        # Unregister from registry
        pass
```

---

## ✅ Plugin Usage in Agents

### Correct Plugin Usage
```python
# ✅ CORRECT: Load via plugin loader
class QAAgent(BaseAgent):
    def execute_ui_test(self, blueprint: Blueprint):
        # Load plugin dynamically
        playwright = self.plugins.load("playwright", version="1.40.0")
        
        # Generate test script
        test_script = self.test_generator.generate(blueprint)
        
        # Execute via plugin
        result = playwright.execute(test_script)
        
        return result

# ❌ INCORRECT: Direct import
from playwright.sync_api import sync_playwright  # DON'T DO THIS

class QAAgent:
    def execute_ui_test(self, blueprint: Blueprint):
        playwright = sync_playwright().start()  # WRONG!
```

---

## ✅ Plugin Configuration

### Plugin Config Schema
```json
{
  "plugin": "playwright",
  "version": "1.40.0",
  "config": {
    "browser_type": "chromium",
    "headless": true,
    "viewport": {
      "width": 1920,
      "height": 1080
    },
    "timeout": 30000,
    "screenshots_on_failure": true,
    "video_recording": false
  },
  "environment_overrides": {
    "production": {
      "headless": true,
      "video_recording": true
    },
    "development": {
      "headless": false,
      "video_recording": false
    }
  }
}
```

---

## ✅ Error Handling in Plugins

### Safe Execution Wrapper
```python
class SafePluginExecutor:
    """Wrap plugin execution with safety measures"""
    
    def execute_safe(
        self,
        plugin: BasePluginAdapter,
        method: str,
        *args,
        timeout: int = 300,
        **kwargs
    ) -> Any:
        """Execute plugin method with timeout and error handling"""
        
        def execute_with_timeout():
            try:
                method_func = getattr(plugin, method)
                return method_func(*args, **kwargs)
            except Exception as e:
                return PluginError(
                    plugin=plugin.metadata["name"],
                    error=str(e),
                    traceback=traceback.format_exc()
                )
        
        # Execute with timeout
        try:
            result = timeout_handler(execute_with_timeout, timeout)
            return result
        except TimeoutError:
            return PluginError(
                plugin=plugin.metadata["name"],
                error=f"Plugin execution timeout after {timeout}s"
            )
        finally:
            # Always cleanup
            try:
                plugin.cleanup()
            except:
                pass
```

---

## ✅ Plugin Marketplace Integration

### Plugin Installation from Marketplace
```python
class PluginMarketplace:
    """Install plugins from marketplace"""
    
    def search(self, query: str, category: str = None) -> List[PluginInfo]:
        """Search marketplace for plugins"""
        pass
    
    def install_from_marketplace(self, plugin_name: str):
        """Install plugin from marketplace"""
        # Download plugin package
        # Verify signature
        # Extract to plugins directory
        # Install dependencies
        # Register in local registry
        pass
    
    def publish_plugin(self, plugin_path: str):
        """Publish plugin to marketplace"""
        # Validate plugin structure
        # Run plugin tests
        # Package plugin
        # Upload to marketplace
        pass
```

---

## ✅ Copilot Code Generation Guidelines for Plugins

### When Generating Plugin Code

#### ✅ DO:
- Extend `BasePluginAdapter`
- Include metadata.json
- Implement `execute`, `validate_config`, `cleanup`
- Handle errors gracefully
- Support configuration overrides
- Include unit tests
- Document capabilities
- Keep plugins focused (single tool/purpose)

#### ❌ DON'T:
- Hardcode plugin logic in agents
- Create monolithic multi-tool plugins
- Skip error handling
- Forget cleanup in finally blocks
- Store state between executions
- Depend on other plugins
- Modify core platform code
- Skip metadata or configuration

---

## 🎯 Remember

> **Plugins are isolated, replaceable tool wrappers.**  
> **Never hardcode plugin logic into agents.**  
> **Load at runtime, execute safely, cleanup always.**

---

## 📚 Related Documentation

- [Main Platform Instructions](../.apex_copilot_instructions.md)
- [Agent Instructions](../core/agents/AGENTS_README.md)
- [Plugin SDK](sdk/README.md)
- [Plugin Development Guide](PLUGIN_DEVELOPMENT.md)

---

*Last updated: 2026-03-26*
