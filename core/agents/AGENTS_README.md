# APEX AI PLATFORM — Copilot System Instructions (GLOBAL)

This repository contains a **Multi-Agent, AI-Powered Full-Stack Testing Platform**.  
Copilot MUST treat these agents as *testing + analysis agents*, NOT deployment AI and NOT generic DevOps orchestration.

## ✅ Core Identity
This system is a:
- Blueprint-based testing engine  
- Multi-agent validation system  
- Deterministic test executor  
- AI-augmented bug analysis platform  
- Plugin-based testing OS  
- Codeless automation platform  
- NOT a CI/CD deployment tool  
- NOT a generic AI assistant  

## ✅ Copilot Must Follow These Core Principles

### 1. Agents NEVER make pass/fail decisions.
They ONLY:
- generate steps  
- analyze logs  
- reason about flows  
- propose fixes  
- validate using deterministic rules  

### 2. Agents work WITH the Blueprint Engine.
Scripts are:
- generated *on demand*  
- auto-healed  
- validated through deterministic logic  
- NOT saved permanently  

### 3. Each agent operates in its own domain.
No mixing QA logic inside Security Agent, etc.

### 4. All AI calls must use the LLM Adapter Layer.
Never call models directly.

### 5. All heavy tools must be used through Plugins.
Never hardcode tool logic into the agents.

### 6. Cross-agent communication must happen via the Runtime.
They don't call each other directly.

### 7. The system is modular and fully upgradable.
Avoid hard dependencies.

## ✅ Agents in This System
- **QA Agent** — UI/API functional testing, flow validation
- **Performance Agent** — Load testing, benchmarking, resource analysis
- **Security Agent** — Vulnerability scanning, penetration testing, compliance
- **DevOps Agent** — Environment setup, deployment validation, infrastructure testing
- **Documentation Agent** — Test documentation, report generation, blueprint analysis

Each agent has its own Copilot spec file that MUST override its behavior.

---

## 🏗️ Agent Architecture

### Agent Lifecycle
```
Blueprint → Agent Runtime → Specialized Agent → LLM Adapter → 
Plugin Loader → Test Execution → Evidence Collection → 
Validation Engine → Results → Auto-Healing (if needed)
```

### Agent Responsibilities

#### All Agents Must:
- ✅ Read from blueprints (source of truth)
- ✅ Generate tests on-demand
- ✅ Use LLM adapter for AI calls
- ✅ Load tools via plugin system
- ✅ Communicate via agent runtime
- ✅ Route results through validation engine
- ✅ Store insights in vector memory
- ✅ Support auto-healing
- ✅ **Require ProjectContext in all methods**
- ✅ **Scope operations to context.app_id**

#### All Agents Must NOT:
- ❌ Make pass/fail decisions (validation engine only)
- ❌ Store test scripts permanently
- ❌ Call LLMs directly (use adapter)
- ❌ Hardcode tool integrations (use plugins)
- ❌ Communicate with each other directly
- ❌ Mix concerns from other agents
- ❌ Execute without blueprint context
- ❌ **Operate without ProjectContext**
- ❌ **Use global paths** (/blueprints, /logs)
- ❌ **Mix data between applications**

---

## 📁 Agent Module Structure

Each agent follows this structure:

```
core/agents/<agent_name>/
├── __init__.py
├── agent.py              # Main agent class
├── config.py             # Agent configuration
├── handlers/             # Event handlers
├── generators/           # Test generation logic
├── analyzers/            # Result analysis
├── utils/                # Agent-specific utilities
├── schemas/              # Data schemas
├── tests/                # Unit tests
└── <AGENT_NAME>_AGENT.md # Copilot instructions
```

### Agent Base Interface

All agents implement:
```python
from dataclasses import dataclass
from pathlib import Path
from typing import List
from abc import ABC, abstractmethod

@dataclass
class ProjectContext:
    """Context for isolated application operations"""
    app_id: str                    # e.g., "app1", "app2", "app3"
    blueprint_path: Path           # /apps/app1/blueprints
    env_config: Path               # /environments/qa/app1.yaml
    snapshots_path: Path           # /apps/app1/snapshots
    logs_path: Path                # /apps/app1/logs
    metadata_path: Path            # /apps/app1/metadata
    plugins: List[str]             # ["playwright", "zap", "jmeter"]
    llm_model: str                 # "qwen-7b" or "gpt-4"
    memory_path: Path              # /core/memory/app1.db
    environment: str               # "dev", "qa", "staging", "prod-safe"

class BaseAgent(ABC):
    def __init__(self, runtime, llm_adapter, plugin_loader):
        self.runtime = runtime
        self.llm = llm_adapter
        self.plugins = plugin_loader
    
    @abstractmethod
    def generate_test(
        self, 
        blueprint: Blueprint, 
        context: ProjectContext  # ← Always require context!
    ) -> Test:
        """Generate test from blueprint within app context"""
        pass
    
    @abstractmethod
    def analyze_results(
        self, 
        evidence: Evidence,
        context: ProjectContext  # ← Always require context!
    ) -> Analysis:
        """Analyze test execution evidence within app context"""
        pass
    
    @abstractmethod
    def propose_healing(
        self, 
        failure: Failure,
        context: ProjectContext  # ← Always require context!
    ) -> HealingStrategy:
        """Propose auto-healing strategy within app context"""
        pass
```

---

## 🏛️ Multi-Application Isolation

### Critical Rule: Agents NEVER Operate Globally

Every agent operation is scoped to a **ProjectContext**:

```python
# ✅ CORRECT: Context-aware agent
class QAAgent(BaseAgent):
    def generate_test(self, blueprint: Blueprint, context: ProjectContext) -> Test:
        # Load blueprints from context-specific path
        related_blueprints = self.load_blueprints(context.blueprint_path)
        
        # Load snapshots from context-specific path
        baselines = self.load_snapshots(context.snapshots_path)
        
        # Use context-specific plugins
        test_tool = self.plugins.load(context.plugins[0])  # e.g., "playwright"
        
        # Generate test
        test = self.llm.generate_test(blueprint, context.llm_model)
        
        # Save logs to context-specific path
        self.save_logs(context.logs_path, test.execution_log)
        
        return test

# ❌ WRONG: Global agent (no context)
class QAAgent(BaseAgent):
    def generate_test(self, blueprint: Blueprint) -> Test:
        # Which app is this for?!
        blueprints = self.load_blueprints("/blueprints")  # WRONG!
        snapshots = self.load_snapshots("/snapshots")     # WRONG!
        # Data from multiple apps gets mixed!
```

### App Isolation Structure

```
apps/
   app1/                    # ← Isolated tenant
      blueprints/           # Only app1's blueprints
      metadata/             # Only app1's metadata
      logs/                 # Only app1's logs
      snapshots/            # Only app1's baselines
   app2/                    # ← Separate isolated tenant
      blueprints/           # Only app2's blueprints
      metadata/             # Only app2's metadata
      logs/                 # Only app2's logs
      snapshots/            # Only app2's baselines
```

**Nothing overlaps. Ever.**

### Agent Operation Example

```python
# System invokes agent with context
def run_qa_tests(app_id: str, environment: str):
    # Build project context
    context = ProjectContext(
        app_id=app_id,
        blueprint_path=Path(f"/apps/{app_id}/blueprints"),
        env_config=Path(f"/environments/{environment}/{app_id}.yaml"),
        snapshots_path=Path(f"/apps/{app_id}/snapshots"),
        logs_path=Path(f"/apps/{app_id}/logs"),
        metadata_path=Path(f"/apps/{app_id}/metadata"),
        plugins=["playwright", "api-client"],
        llm_model="qwen-7b",
        memory_path=Path(f"/core/memory/{app_id}.db"),
        environment=environment
    )
    
    # Load blueprint from context
    blueprint = load_blueprint("LOGIN_001", context.blueprint_path)
    
    # Agent operates within context boundaries
    agent = QAAgent(runtime, llm_adapter, plugin_loader)
    test = agent.generate_test(blueprint, context)
    
    # Results saved to context-specific location
    save_results(context.logs_path / "test_results.json", test.results)
```

### Multi-App Code Generation Rules

**✅ ALWAYS:**
- Require `ProjectContext` in all agent methods
- Use `context.app_id` to scope operations
- Load from `context.blueprint_path`, not `/blueprints`
- Save to `context.logs_path`, not `/logs`
- Load plugins from `context.plugins`
- Use `context.llm_model` for AI calls
- Store memory in `context.memory_path`

**❌ NEVER:**
- Operate without context
- Use global paths (`/blueprints`, `/logs`, `/snapshots`)
- Query across app boundaries
- Mix app1 blueprints with app2 execution
- Share memory between apps
- Create global singletons for app-specific data

---

## 🔄 Agent Communication Flow

Agents communicate ONLY through the Agent Runtime:

```python
# ✅ CORRECT: Via Runtime
result = runtime.invoke_agent("security", {
    "blueprint_id": "auth_test_001",
    "context": execution_context
})

# ❌ INCORRECT: Direct call
from core.agents.security import SecurityAgent
security_agent = SecurityAgent()
result = security_agent.run()  # DON'T DO THIS
```

### Inter-Agent Coordination

When one agent needs another:
```python
# QA Agent needs Security validation
qa_result = qa_agent.execute(blueprint)

# Request security validation via runtime
security_check = runtime.request_validation(
    agent="security",
    evidence=qa_result.evidence,
    validation_type="auth_check"
)
```

---

## 🧠 LLM Integration Guidelines

### Using LLM Adapter

All AI calls go through the adapter:

```python
# ✅ CORRECT: Via LLM Adapter
response = self.llm.generate(
    prompt=prompt_template.format(**context),
    provider="openai",  # or "anthropic", "azure", etc.
    model="gpt-4",
    temperature=0.3,
    max_tokens=2000
)

# ❌ INCORRECT: Direct LLM call
import openai
response = openai.ChatCompletion.create(...)  # DON'T
```

### What LLMs Are Used For

- ✅ Test case generation from blueprints
- ✅ Natural language blueprint parsing
- ✅ Auto-healing script regeneration
- ✅ Log analysis and pattern detection
- ✅ Edge case discovery
- ✅ Test data generation

### What LLMs Are NOT Used For

- ❌ Pass/fail decisions (validation engine)
- ❌ Critical business logic
- ❌ Security decisions
- ❌ Direct test execution
- ❌ Deterministic validation

---

## 🔌 Plugin Integration

### Loading Plugins

Agents use the plugin loader:

```python
# ✅ CORRECT: Via Plugin Loader
playwright = self.plugins.load("playwright", version="1.40.0")
test_result = playwright.execute(test_script)

# ❌ INCORRECT: Hardcoded import
from playwright.sync_api import sync_playwright  # DON'T
```

### Plugin Categories for Each Agent

**QA Agent Plugins:**
- UI testing: Playwright, Selenium, Cypress
- API testing: REST, GraphQL, gRPC clients
- Mobile testing: Appium

**Performance Agent Plugins:**
- Load testing: K6, Locust, JMeter
- Profiling: cProfile, Py-Spy
- Monitoring: Prometheus, Grafana

**Security Agent Plugins:**
- Scanners: OWASP ZAP, Burp Suite
- Static analysis: Bandit, Semgrep
- Dependency check: Safety, Snyk

**DevOps Agent Plugins:**
- Infrastructure: Terraform, Ansible
- Container tools: Docker, Kubernetes
- Cloud CLIs: AWS, Azure, GCP

**Documentation Agent Plugins:**
- Generators: Sphinx, MkDocs
- Diagram tools: Mermaid, PlantUML
- Report builders: Allure, ReportPortal

---

## ✅ Validation Engine Integration

Agents collect evidence, validation engine decides:

```python
# Agent collects evidence
evidence = Evidence(
    test_id=test.id,
    blueprint_id=blueprint.id,
    actual_output=actual,
    logs=execution_logs,
    metrics=performance_metrics,
    screenshots=ui_screenshots
)

# Send to validation engine
result = validation_engine.validate(
    evidence=evidence,
    blueprint=blueprint,
    contract=api_contract,
    baseline=historical_baseline
)

# result.status = PASS | FAIL | NEEDS_HEALING
```

---

## 🎯 Agent-Specific Responsibilities

### QA Agent
- Functional testing (UI, API, integration)
- Flow validation from blueprints
- User journey testing
- Regression testing
- Smoke testing

### Performance Agent
- Load testing
- Stress testing
- Endurance testing
- Spike testing
- Scalability analysis
- Resource profiling

### Security Agent
- Vulnerability scanning
- Penetration testing
- Authentication/authorization testing
- Compliance validation (OWASP, PCI-DSS)
- Secrets detection
- Dependency vulnerability checks

### DevOps Agent
- Environment provisioning
- Deployment validation
- Infrastructure testing
- Configuration validation
- Health checks
- Rollback testing

### Documentation Agent
- Test documentation generation
- Blueprint documentation
- Test report generation
- Coverage reports
- API documentation
- Architecture diagrams

---

## 🚨 Common Mistakes to Avoid

### ❌ Don't Do This

```python
# 1. Storing tests permanently
with open("test_script.py", "w") as f:
    f.write(generated_test)  # NO!

# 2. Making pass/fail decisions
if response.status == 200:
    return TestResult(status="PASS")  # NO! Use validation engine

# 3. Direct agent calls
from core.agents.security import SecurityAgent
sec = SecurityAgent().run()  # NO! Use runtime

# 4. Hardcoded tools
from selenium import webdriver
driver = webdriver.Chrome()  # NO! Use plugin loader

# 5. Direct LLM calls
import anthropic
response = anthropic.complete(...)  # NO! Use LLM adapter
```

### ✅ Do This Instead

```python
# 1. Generate on-demand
test = test_generator.generate_from_blueprint(blueprint)

# 2. Collect evidence, let validator decide
evidence = self.collect_evidence(execution)
return validation_engine.validate(evidence, blueprint)

# 3. Use runtime
result = self.runtime.invoke_agent("security", context)

# 4. Use plugin loader
tool = self.plugins.load("selenium")

# 5. Use LLM adapter
response = self.llm.generate(prompt, provider="anthropic")
```

---

## 📋 Code Generation Checklist for Agents

When generating agent code, ensure:

- [ ] Extends `BaseAgent` class
- [ ] Uses blueprint as source of truth
- [ ] Generates tests on-demand
- [ ] Uses LLM adapter (not direct calls)
- [ ] Loads tools via plugin system
- [ ] Communicates via agent runtime
- [ ] Routes results through validation engine
- [ ] Supports auto-healing
- [ ] Has unit tests
- [ ] Has proper error handling
- [ ] Logs to observability system
- [ ] Stores insights in vector memory
- [ ] Follows single responsibility principle
- [ ] Is provider-agnostic
- [ ] Is modular (< 500 lines per file)

---

## 🎓 Remember

> **Agents are intelligent assistants, NOT decision makers.**  
> **Blueprints define, Agents execute, Validators decide.**  
> **Everything flows through the runtime.**

---

## 📚 Related Documentation

- [Main Platform Instructions](../../.apex_copilot_instructions.md)
- [QA Agent Instructions](qa/QA_AGENT.md)
- [Performance Agent Instructions](performance/PERFORMANCE_AGENT.md)
- [Security Agent Instructions](security/SECURITY_AGENT.md)
- [DevOps Agent Instructions](devops/DEVOPS_AGENT.md)
- [Documentation Agent Instructions](docs/DOCS_AGENT.md)
- [Blueprint Schema](../blueprints/README.md)
- [Plugin Development SDK](../../plugins/sdk/README.md)
- [Validation Engine](../validation/README.md)

---

*Last updated: 2026-03-26*
