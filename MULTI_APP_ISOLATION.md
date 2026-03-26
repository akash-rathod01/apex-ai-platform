# Multi-Application Isolation - Architecture Documentation

## 🎯 Critical Architectural Pattern

The Apex AI Platform supports **multi-application isolation** — a multi-tenant pattern where each application operates as an isolated tenant with its own resources.

---

## 📊 Isolation Structure

```
apps/
   app1/                    # ← Application 1 (Isolated Tenant)
      blueprints/           # App1-specific test blueprints
      metadata/             # App1-specific metadata
      logs/                 # App1-specific execution logs
      snapshots/            # App1-specific baseline snapshots
   
   app2/                    # ← Application 2 (Isolated Tenant)
      blueprints/           # App2-specific test blueprints
      metadata/             # App2-specific metadata
      logs/                 # App2-specific execution logs
      snapshots/            # App2-specific baseline snapshots
   
   app3/                    # ← Application 3 (Isolated Tenant)
      blueprints/
      metadata/
      logs/
      snapshots/
```

### Key Principles:
- ✅ **Complete isolation** — Nothing overlaps between apps
- ✅ **Independent configuration** — Each app has its own env configs
- ✅ **Plugin flexibility** — Each app can use different tool sets
- ✅ **LLM flexibility** — Each app can use different AI models
- ✅ **Memory isolation** — Each app has its own memory database
- ❌ **No global operations** — Agents NEVER operate globally
- ❌ **No cross-app queries** — Can't load app1 blueprints with app2 context
- ❌ **No shared state** — Each app has its own memory, logs, snapshots
- ❌ **No shared intelligence** — Test intelligence never crosses app boundaries

---

## 🎛️ ProjectContext Pattern

Every agent operation receives a **ProjectContext** object that defines the application scope:

```python
from dataclasses import dataclass
from pathlib import Path
from typing import List

@dataclass
class ProjectContext:
    """Context for isolated application operations"""
    
    # Application identity
    app_id: str                    # e.g., "app1", "app2", "app3"
    
    # App-specific paths
    blueprint_path: Path           # /apps/app1/blueprints
    env_config: Path               # /environments/qa/app1.yaml
    snapshots_path: Path           # /apps/app1/snapshots
    logs_path: Path                # /apps/app1/logs
    metadata_path: Path            # /apps/app1/metadata
    
    # App-specific tool configuration (per domain)
    ui_tools: List[str]            # ["playwright"] or ["selenium", "cypress"]
    api_tools: List[str]           # ["postman-lite"] or ["rest-assured", "axios"]
    perf_tools: List[str]          # ["jmeter"] or ["k6", "locust"]
    security_tools: List[str]      # ["zap"] or ["burp", "nmap", "nikto"]
    
    # App-specific AI configuration
    llm_model: str                 # "qwen-7b" or "gpt-4"
    memory_path: Path              # /core/memory/app1.db
    
    # Environment
    environment: str               # "dev", "qa", "staging", "prod-safe"

# Example contexts for different apps
context_app1 = ProjectContext(
    app_id="app1",
    blueprint_path=Path("/apps/app1/blueprints"),
    ui_tools=["playwright"],           # App1 uses Playwright
    api_tools=["postman-lite"],        # App1 uses Postman
    perf_tools=["jmeter"],             # App1 uses JMeter
    security_tools=["zap"],            # App1 uses OWASP ZAP
    llm_model="qwen-7b",
    # ...
)

context_app2 = ProjectContext(
    app_id="app2",
    blueprint_path=Path("/apps/app2/blueprints"),
    ui_tools=["selenium", "cypress"],  # App2 uses different tools!
    api_tools=["rest-assured"],        # Different API tool
    perf_tools=["k6", "locust"],       # Different perf tools
    security_tools=["burp", "nmap"],   # Different security tools
    llm_model="gpt-4",                 # Different LLM!
    # ...
)
```

### What ProjectContext Guarantees:

**The agent KNOWS which app it's working for:**
```python
logger.info(f"Executing test for app: {context.app_id}")
# Output: "Executing test for app: app1"
```

**The agent LOADS only that app's data:**
```python
# Only app1's blueprints
blueprints = load_blueprints(context.blueprint_path)  # /apps/app1/blueprints

# Only app1's snapshots
baselines = load_snapshots(context.snapshots_path)    # /apps/app1/snapshots

# Only app1's metadata
metadata = load_metadata(context.metadata_path)       # /apps/app1/metadata
```

**The agent USES only that app's tools:**
```python
# Load UI tool for this app (Playwright for app1)
ui_tool = self.plugins.load(context.ui_tools[0])      # "playwright"

# Load API tool for this app (Postman for app1)
api_tool = self.plugins.load(context.api_tools[0])    # "postman-lite"

# Load perf tool for this app (JMeter for app1)
perf_tool = self.plugins.load(context.perf_tools[0])  # "jmeter"

# Load security tool for this app (ZAP for app1)
sec_tool = self.plugins.load(context.security_tools[0])  # "zap"
```

**The agent SAVES results to the right folder:**
```python
# Save to app1's logs directory
save_logs(context.logs_path / "test_results.json", evidence)

# Save screenshots to app1's snapshots
save_screenshot(context.snapshots_path / "login.png", screenshot)

# Save metadata to app1's metadata directory
save_metadata(context.metadata_path / "test_run.json", metadata)
```

---

### Complete Agent Example:
Load app-specific configuration
    app_config = load_app_config(app_id)
    # Returns:
    # {
    #   "uiTools": ["playwright"],
    #   "apiTools": ["postman-lite"],
    #   "perfTools": ["jmeter"],
    #   "securityTools": ["zap"],
    #   "llmModel": "qwen-7b"
    # }
    
    # 2. Build ProjectContext with app-specific tools
    context = ProjectContext(
        app_id=app_id,
        blueprint_path=Path(f"/apps/{app_id}/blueprints"),
        env_config=Path(f"/environments/{environment}/{app_id}.yaml"),
        snapshots_path=Path(f"/apps/{app_id}/snapshots"),
        logs_path=Path(f"/apps/{app_id}/logs"),
        metadata_path=Path(f"/apps/{app_id}/metadata"),
        ui_tools=app_config["uiTools"],           # ["playwright"]
        api_tools=app_config["apiTools"],         # ["postman-lite"]
        perf_tools=app_config["perfTools"],       # ["jmeter"]
        security_tools=app_config["securityTools"], # ["zap"]
        llm_model=app_config["llmModel"],         # "qwen-7b"ch app
        logger.info(f"Testing {context.app_id}")
        
        # 2. Agent LOADS only that app's data
        related_blueprints = self.load_blueprints(context.blueprint_path)
        baselines = self.load_snapshots(context.snapshots_path)
        
        # 3. Agent USES only that app's tools
        ui_tool = self.plugins.load(context.ui_tools[0])       # Playwright
        api_tool = self.plugins.load(context.api_tools[0])     # Postman
        
        # 4. Generate test using context-specific LLM
        test_script = self.llm.generate(
            blueprint=blueprint,
            model=context.llm_model  # qwen-7b for app1
        )
        
        # 5. Execute test with context-specific tool
        evidence = ui_tool.execute(test_script)
        
        # 6. Agent SAVES results to the right folder
        self.save_logs(
            context.logs_path / "test_results.json", 
            evidence
        )
        
        return test

# ❌ WRONG: Agent operates globally (no context)
class QAAgent(BaseAgent):
    def generate_test(self, blueprint: Blueprint) -> Test:
        # Which app is this for?!
        blueprints = self.load_blueprints("/blueprints")  # WRONG!
        snapshots = self.load_snapshots("/snapshots")     # WRONG!
        # Data from multiple apps gets mixed!
```

---

## 🔄 How System Invokes Agents with Context

```python
def run_tests_for_app(app_id: str, environment: str, blueprint_id: str):
    """Execute tests for a specific application"""
    
    # 1. Build ProjectContext
    context = ProjectContext(
        app_id=app_id,
        blueprint_path=Path(f"/apps/{app_id}/blueprints"),
        env_config=Path(f"/environments/{environment}/{app_id}.yaml"),
        snapshots_path=Path(f"/apps/{app_id}/snapshots"),
        logs_path=Path(f"/apps/{app_id}/logs"),
        metadata_path=Path(f"/apps/{app_id}/metadata"),
        plugins=["playwright", "api-client", "k6"],
        llm_model="qwen-7b",
        memory_path=Path(f"/core/memory/{app_id}.db"),
        environment=environment
    )
    
    # 2. Load blueprint from context-specific path
    blueprint_loader = BlueprintLoader()
    blueprint = blueprint_loader.load_for_context(blueprint_id, context)
    
    # 3. Initialize agent
    qa_agent = QAAgent(runtime, llm_adapter, plugin_loader)
    
    # 4. Execute test with context
    test = qa_agent.generate_test(blueprint, context)
    evidence = qa_agent.execute_test(test, context)
    
    # 5. Validate with context-aware validation
    validation_engine = ValidationEngine()
    result = validation_engine.validate(
        evidence=evidence,
        expected=blueprint.expected,
        context=context
    )
    
    # 6. Save results to context-specific location
    save_results(
        context.logs_path / f"{blueprint_id}_results.json",
        result
    )
    
    return result
```

---

## 📋 Code Generation Rules

### ✅ ALWAYS:
1. **Require `ProjectContext` in all agent methods**
   ```python
   def generate_test(self, blueprint: Blueprint, context: ProjectContext) -> Test:
   ```

2. **Use `context.app_id` to scope operations**
   ```python
   logger.info(f"Generating test for app: {context.app_id}")
   ``` (domain-specific)**
   ```python
   # Load UI tool for this app
   ui_tool = self.plugins.load(context.ui_tools[0])  # ✅ "playwright" for app1
   
   # Load API tool for this app
   api_tool = self.plugins.load(context.api_tools[0])  # ✅ "postman-lite" for app1
   
   # Load perf tool for this app
   perf_tool = self.plugins.load(context.perf_tools[0])  # ✅ "jmeter" for app1
   
   ```python
   blueprints = load_blueprints(context.blueprint_path)  # ✅
   # NOT: load_blueprints("/blueprints")  # ❌
   ```

4. **Save to context-specific paths**
   ```python
   save_logs(context.logs_path / "results.json", data)  # ✅
   # NOT: save_logs("/logs/results.json", data)  # ❌
   ```

5. **Load plugins from context configuration**
   ```python
   tool = self.plugins.load(context.plugins[0])  # ✅
   # NOT: tool = self.plugins.load("playwright")  # ❌ Hardcoded!
   ```

6. **Use context-specific LLM model**
   ```python
   response = self.llm.generate(prompt, model=context.llm_model)  # ✅
   # NOT: response = self.llm.generate(prompt, model="gpt-4")  # ❌ Hardcoded!
   ```

7. **Store memory in context-specific database**
   ```python
   memory = VectorMemory(context.memory_path)  # ✅
   # NOT: memory = VectorMemory("/memory/global.db")  # ❌ Global!
   ```

### ❌ NEVER:
1. **Operate without context**
   ```python
   # ❌ WRONG
   def generate_test(self, blueprint: Blueprint):
       # No context! Which app?
   ```

2. **Use global/absolute paths**
   ```python
   # ❌ WRONG
   blueprints = load_blueprints("/blueprints")
   logs = load_logs("/logs")
   ```

3. **Query across app boundaries**
   ```python
   # ❌ WRONG
   all_blueprints = load_all_blueprints()  # Mixes all apps!
   ```

4. **Mix app1 blueprints with app2 execution**
   ```python
   # ❌ WRONG
   blueprint_app1 = load_blueprint("app1", "LOGIN_001")
   context_app2 = get_context("app2")
   execute_test(blueprint_app1, context_app2)  # WRONG!
   ```

5. **Share memory between apps**
   ```python
   # ❌ WRONG
   global_memory = VectorMemory("/memory/shared.db")  # NO!
   ```

6. **Create global singletons for app-specific data**
   ```python
   # ❌ WRONG
   class GlobalBlueprintCache:
       _instance = None  # Singleton mixing all apps!
   ```

---

## 🔍 Updated Files

The following instruction files now enforce multi-application isolation:

### 1. Main Platform Instructions
**File:** `.apex_copilot_instructions.md`

**Added:**
- Principle 7: Multi-Application Isolation
- ProjectContext architecture documentation
- Multi-app code generation rules
- Examples of correct vs incorrect patterns

### 2. Agent Master Registry
**File:** `core/agents/AGENTS_README.md`

**Added:**
- ProjectContext dataclass definition
- Updated BaseAgent interface (all methods require context)
- Multi-Application Isolation section
- Agent operation examples with context
- Updated responsibilities (must use context, never global operations)

### 3. Blueprint Engine Instructions
**File:** `core/blueprints/COPILOT_BLUEPRINT_ENGINE.md`

**Added:**
- Enhanced multi-application isolation section
- AppAwareBlueprintLoader with ProjectContext
- Context-aware blueprint loading examples
- Updated rules for context-scoped operations

---

## 🎯 Benefits of This Architecture

### 1. **True Multi-Tenancy**
- Run tests for multiple applications simultaneously
- No interference between applications
- Each app can evolve independently

### 2. **Flexible Configuration**
- App1 can use Playwright + OpenAI
- App2 can use Selenium + Qwen
- App3 can use Cypress + Claude
- No conflicts!

### 3. **Data Isolation**
- App1 test failures don't pollute app2 logs
- App1 baselines don't interfere with app2 baselines
- Clear accountability per application

### 4. **Security Boundaries**
- App1 team can't access app2 blueprints
- Role-based access control per app
- Audit trails per application

### 5. **Scalability**
- Add new apps without modifying existing code
- Scale per-app resources independently
- Parallel execution without conflicts

---

## � Per-Application Memory & Test Intelligence

### Memory Isolation Structure

The `core/memory/` folder maintains **complete isolation** between applications:

```
core/memory/
   app1_memory.db           # ← App1's test intelligence
   app2_memory.db           # ← App2's test intelligence
   app3_memory.db           # ← App3's test intelligence
   
   # Each database contains app-specific:
   # - Historical test results
   # - Flakiness patterns
   # - Risk scores per test
   # - Auto-healing strategies
   # - Performance baselines
   # - Error patterns
   # - Test execution history
```

### What's Stored in App-Specific Memory

Each app's memory database stores:

#### 1. **Historical Test Results**
```python
# App1 memory stores app1's history
{
  "blueprint_id": "LOGIN_001",
  "app_id": "app1",
  "last_run": "2026-03-26T14:30:00Z",
  "status": "pass",
  "execution_count": 1523,
  "failure_count": 12,
  "flakiness_score": 0.008  # Less than 1% flaky
}
```

#### 2. **Flakiness Detection**
```python
# Learned pattern: login flaky on Mondays
{
  "blueprint_id": "LOGIN_001",
  "app_id": "app1",
  "flaky_pattern": {
    "day_of_week": "monday",
    "failure_rate": 0.15,
    "suggested_retry": 2
  }
}
```

#### 3. **Risk Scoring**
```python
# High-risk test (frequently fails)
{
  "blueprint_id": "CHECKOUT_001",
  "app_id": "app1",
  "risk_score": 0.85,       # 85% probability of failure
  "priority": "critical",
  "recent_failures": 8,
  "failure_reasons": [
    "payment_gateway_timeout",
    "inventory_sync_issue"
  ]
}
```

#### 4. **Auto-Healing Strategies**
```python
# Learned healing: login button selector changed
{
  "blueprint_id": "LOGIN_001",
  "app_id": "app1",
  "healing_history": [
    {
      "date": "2026-03-20",
      "old_selector": "#login-btn",
      "new_selector": "#btn-login",
      "confidence": 0.95
    }
  ]
}
```

#### 5. **Performance Baselines**
```python
# App1's performance baseline
{
  "blueprint_id": "API_GET_USER",
  "app_id": "app1",
  "baseline_p50": 150,      # ms
  "baseline_p95": 450,      # ms
  "baseline_p99": 800,      # ms
  "last_updated": "2026-03-25"
}
```

### Memory Usage with ProjectContext

```python
class TestIntelligenceBrain:
    """Per-app test intelligence"""
    
    def __init__(self, context: ProjectContext):
        # Load app-specific memory
        self.memory = VectorMemory(context.memory_path)
        self.app_id = context.app_id
    
    def get_flaky_tests(self) -> List[str]:
        """Get flaky tests for THIS app only"""
        return self.memory.query(
            f"SELECT blueprint_id FROM tests "
            f"WHERE app_id = '{self.app_id}' "
            f"AND flakiness_score > 0.1"
        )
    
    def get_risk_score(self, blueprint_id: str) -> float:
        """Get risk score for test in THIS app"""
        record = self.memory.get(
            key=f"{self.app_id}:{blueprint_id}:risk"
        )
        return record["risk_score"] if record else 0.0
    
    def store_test_result(
        self, 
        blueprint_id: str, 
        result: TestResult
    ):
        """Store result for THIS app only"""
        self.memory.store(
            key=f"{self.app_id}:{blueprint_id}:result",
            value={
                "app_id": self.app_id,  # Always scoped to app
                "blueprint_id": blueprint_id,
                "status": result.status,
                "timestamp": result.timestamp,
                # ...
            }
        )
    
    def learn_from_failure(
        self,
        blueprint_id: str,
        failure: Failure
    ):
        """Learn from failure in THIS app"""
        # Update flakiness score
        history = self.memory.get(
            key=f"{self.app_id}:{blueprint_id}:history"
        )
        
        # Calculate new flakiness
        new_flakiness = self._calculate_flakiness(history, failure)
        
        # Store updated intelligence
        self.memory.store(
            key=f"{self.app_id}:{blueprint_id}:flakiness",
            value={"score": new_flakiness}
        )

# ✅ CORRECT: Memory scoped to app
intelligence_app1 = TestIntelligenceBrain(context_app1)
flaky_tests = intelligence_app1.get_flaky_tests()  # Only app1's flaky tests

intelligence_app2 = TestIntelligenceBrain(context_app2)
flaky_tests = intelligence_app2.get_flaky_tests()  # Only app2's flaky tests

# ❌ WRONG: Global memory (mixed apps)
global_memory = VectorMemory("/core/memory/shared.db")  # DON'T!
flaky_tests = global_memory.query("SELECT * FROM tests WHERE flaky = true")
# ^ Returns tests from ALL apps! WRONG!
```

### Why Memory Isolation Matters

#### 1. **Prevents Cross-Contamination**
```python
# App1's payment flow is flaky
intelligence_app1.mark_flaky("PAYMENT_CHECKOUT")

# App2's payment flow is stable
intelligence_app2.get_risk_score("PAYMENT_CHECKOUT")  # Returns 0.0
# Correct! App2's test is not affected by app1's flakiness
```

#### 2. **Accurate Risk Scoring**
```python
# App1 has 1000 tests, 10% failure rate
app1_risk = intelligence_app1.get_average_risk()  # 0.10

# App2 has 50 tests, 2% failure rate
app2_risk = intelligence_app2.get_average_risk()   # 0.02

# If memory was shared, app1's failures would inflate app2's risk!
```

#### 3. **Independent Learning**
```python
# App1 learns: login button frequently changes
intelligence_app1.learn_pattern({
    "test": "LOGIN",
    "pattern": "button_selector_unstable"
})

# App2 doesn't have this problem
# App2's memory remains clean, not polluted by app1's issues
```

#### 4. **Test Selection Optimization**
```python
# App1: Select stable tests for smoke suite
stable_tests_app1 = intelligence_app1.get_tests(
    flakiness_threshold=0.05,
    risk_threshold=0.3
)  # Returns 800 tests

# App2: Different selection based on app2's data
stable_tests_app2 = intelligence_app2.get_tests(
    flakiness_threshold=0.05,
    risk_threshold=0.3
)  # Returns 45 tests

# Each app optimizes based on its own intelligence!
```

### Memory Database Schema

```sql
-- Each app_memory.db has its own tables

CREATE TABLE test_history (
    id INTEGER PRIMARY KEY,
    app_id TEXT NOT NULL,              -- Always 'app1', 'app2', etc.
    blueprint_id TEXT NOT NULL,
    status TEXT,                       -- 'pass', 'fail'
    timestamp DATETIME,
    execution_time_ms INTEGER,
    evidence_hash TEXT,
    CONSTRAINT unique_app_test UNIQUE(app_id, blueprint_id, timestamp)
);

CREATE TABLE flakiness (
    id INTEGER PRIMARY KEY,
    app_id TEXT NOT NULL,
    blueprint_id TEXT NOT NULL,
    flakiness_score REAL,              -- 0.0 - 1.0
    failure_count INTEGER,
    total_count INTEGER,
    last_updated DATETIME,
    CONSTRAINT unique_app_flaky UNIQUE(app_id, blueprint_id)
);

CREATE TABLE risk_scores (
    id INTEGER PRIMARY KEY,
    app_id TEXT NOT NULL,
    blueprint_id TEXT NOT NULL,
    risk_score REAL,                   -- 0.0 - 1.0
    priority TEXT,                     -- 'low', 'medium', 'high', 'critical'
    recent_failures INTEGER,
    calculated_at DATETIME,
    CONSTRAINT unique_app_risk UNIQUE(app_id, blueprint_id)
);

CREATE TABLE healing_strategies (
    id INTEGER PRIMARY KEY,
    app_id TEXT NOT NULL,
    blueprint_id TEXT NOT NULL,
    old_selector TEXT,
    new_selector TEXT,
    confidence REAL,
    applied_at DATETIME,
    success_count INTEGER
);

CREATE TABLE performance_baselines (
    id INTEGER PRIMARY KEY,
    app_id TEXT NOT NULL,
    blueprint_id TEXT NOT NULL,
    metric_name TEXT,                  -- 'response_time_p50', 'p95', 'p99'
    baseline_value REAL,
    last_updated DATETIME,
    CONSTRAINT unique_app_baseline UNIQUE(app_id, blueprint_id, metric_name)
);
```

Each app's database is completely isolated. No cross-references. No joins across apps.

---
## 📸 Per-Application Snapshots, Baselines & Logs

### Snapshot & Baseline Isolation

Massive enterprise systems rely on baseline comparisons for visual, DOM, API, and performance testing. **Cross-contamination between apps would cause false positives/negatives.**

```
apps/
   app1/
      snapshots/
         ui/
            login_page_baseline.png         # App1's UI baseline
            dashboard_dom_baseline.json     # App1's DOM structure
         api/
            get_user_response_baseline.json # App1's API baseline
         performance/
            login_p95_baseline.json         # App1 perf baseline: 250ms
      logs/
         execution_2026_03_26_14_30.log     # App1's test logs
         error_trace_2026_03_26.log         # App1's error logs
      metadata/
         test_coverage.json                 # App1's coverage metrics
         risk_matrix.json                   # App1's risk scores
   
   app2/
      snapshots/
         ui/
            login_page_baseline.png         # App2's UI baseline (DIFFERENT!)
            dashboard_dom_baseline.json     # App2's DOM (DIFFERENT!)
         api/
            get_user_response_baseline.json # App2's API (DIFFERENT!)
         performance/
            login_p95_baseline.json         # App2 perf baseline: 800ms (DIFFERENT!)
      logs/
         execution_2026_03_26_14_32.log     # App2's test logs
      metadata/
         test_coverage.json                 # App2's coverage
```

### Why Baseline Isolation Matters

#### 1. **Visual Regression Testing**
```python
# App1: E-commerce site with modern design
baseline_app1 = load_baseline(
    f"{context_app1.snapshots_path}/ui/checkout_page.png"
)
# Baseline shows: modern card UI, blue buttons

# App2: Legacy banking app with old design
baseline_app2 = load_baseline(
    f"{context_app2.snapshots_path}/ui/transfer_page.png"
)
# Baseline shows: table-based layout, gray buttons

# If baselines were shared, app2's test would fail against app1's baseline!
```

#### 2. **DOM Structure Comparison**
```python
# App1: React SPA with virtual DOM
dom_baseline_app1 = {
    "app_id": "app1",
    "page": "login",
    "structure": {
        "root": "div#root",
        "form": "form[data-testid='login-form']",
        "button": "button[type='submit']"
    }
}

# App2: Server-side rendered app with different selectors
dom_baseline_app2 = {
    "app_id": "app2",
    "page": "login",
    "structure": {
        "root": "body",
        "form": "form#login-form",
        "button": "input[type='submit']"
    }
}

# Completely different DOM structures!
# Validation must compare app1 against app1's baseline, not app2's
```

#### 3. **API Response Baselines**
```python
# App1: Microservices API (JSON HAL format)
api_baseline_app1 = {
    "app_id": "app1",
    "endpoint": "/api/users/123",
    "baseline_response": {
        "_links": {"self": {"href": "/api/users/123"}},
        "id": 123,
        "name": "string",
        "email": "string"
    }
}

# App2: Monolith API (plain JSON)
api_baseline_app2 = {
    "app_id": "app2",
    "endpoint": "/users/123",
    "baseline_response": {
        "userId": 123,
        "fullName": "string",
        "emailAddress": "string",
        "accountStatus": "string"
    }
}

# Different response formats! Must validate against app-specific baseline
```

#### 4. **Performance Baselines**
```python
# App1: Fast modern app (CDN, React, optimized)
perf_baseline_app1 = {
    "app_id": "app1",
    "page": "login",
    "p50_ms": 120,
    "p95_ms": 250,
    "p99_ms": 400
}

# App2: Legacy app (monolith, server-side rendering)
perf_baseline_app2 = {
    "app_id": "app2",
    "page": "login",
    "p50_ms": 450,
    "p95_ms": 800,
    "p99_ms": 1200
}

# If baselines were shared:
# - App1 would ALWAYS fail (actual: 250ms vs app2 baseline: 800ms = faster = "improvement"?)
# - App2 would ALWAYS fail (actual: 800ms vs app1 baseline: 250ms = "regression"!)
```

### Loading Baselines with ProjectContext

```python
class BaselineManager:
    """Per-app baseline management"""
    
    def __init__(self, context: ProjectContext):
        self.context = context
        self.snapshots_path = context.snapshots_path
    
    def load_ui_baseline(self, page: str) -> bytes:
        """Load UI baseline for THIS app"""
        baseline_path = (
            f"{self.snapshots_path}/ui/{page}_baseline.png"
        )
        return self._load_file(baseline_path)
    
    def load_dom_baseline(self, page: str) -> dict:
        """Load DOM baseline for THIS app"""
        baseline_path = (
            f"{self.snapshots_path}/ui/{page}_dom_baseline.json"
        )
        return self._load_json(baseline_path)
    
    def load_api_baseline(self, endpoint: str) -> dict:
        """Load API baseline for THIS app"""
        # Sanitize endpoint for filename
        filename = endpoint.replace("/", "_").replace(":", "_")
        baseline_path = (
            f"{self.snapshots_path}/api/{filename}_baseline.json"
        )
        return self._load_json(baseline_path)
    
    def load_perf_baseline(self, test_id: str) -> dict:
        """Load performance baseline for THIS app"""
        baseline_path = (
            f"{self.snapshots_path}/performance/{test_id}_baseline.json"
        )
        return self._load_json(baseline_path)
    
    def update_baseline(
        self,
        baseline_type: str,  # "ui", "api", "performance"
        identifier: str,
        data: Union[bytes, dict]
    ):
        """Update baseline for THIS app"""
        baseline_path = (
            f"{self.snapshots_path}/{baseline_type}/{identifier}_baseline"
        )
        
        # Add extension based on type
        if baseline_type == "ui":
            baseline_path += ".png"
            self._save_file(baseline_path, data)
        else:
            baseline_path += ".json"
            self._save_json(baseline_path, data)

# ✅ CORRECT: Baselines scoped to app
baseline_mgr_app1 = BaselineManager(context_app1)
ui_baseline = baseline_mgr_app1.load_ui_baseline("login")  # App1's baseline

baseline_mgr_app2 = BaselineManager(context_app2)
ui_baseline = baseline_mgr_app2.load_ui_baseline("login")  # App2's baseline

# ❌ WRONG: Global baseline (mixed apps)
global_baseline = load_baseline("/baselines/login.png")  # Which app?!
```

### Log Isolation

```python
class LogManager:
    """Per-app log management"""
    
    def __init__(self, context: ProjectContext):
        self.context = context
        self.logs_path = context.logs_path
    
    def log_execution(
        self,
        blueprint_id: str,
        result: TestResult
    ):
        """Log execution for THIS app"""
        log_file = (
            f"{self.logs_path}/"
            f"execution_{datetime.now().strftime('%Y_%m_%d_%H_%M')}.log"
        )
        
        with open(log_file, "a") as f:
            f.write(
                f"[{self.context.app_id}] "
                f"Blueprint: {blueprint_id} | "
                f"Status: {result.status} | "
                f"Duration: {result.duration_ms}ms\n"
            )
    
    def log_error(
        self,
        blueprint_id: str,
        error: Exception
    ):
        """Log error for THIS app"""
        error_file = (
            f"{self.logs_path}/"
            f"error_trace_{datetime.now().strftime('%Y_%m_%d')}.log"
        )
        
        with open(error_file, "a") as f:
            f.write(
                f"[{self.context.app_id}] "
                f"Blueprint: {blueprint_id}\n"
                f"Error: {str(error)}\n"
                f"Traceback: {traceback.format_exc()}\n\n"
            )

# Logs are always app-scoped
logger_app1 = LogManager(context_app1)
logger_app1.log_execution("LOGIN_001", result)  # → apps/app1/logs/

logger_app2 = LogManager(context_app2)
logger_app2.log_execution("LOGIN_001", result)  # → apps/app2/logs/
```

---

## ⚖️ Validation Rules Are Application-Bound

The **Validation Engine** receives app-specific baselines and rules for accurate pass/fail decisions.

### Validation Input Structure

```python
validation_request = {
    "app_id": "app2",                           # Which app?
    "blueprint_id": "CHECKOUT_047",             # Which test?
    "expected": {                               # From blueprint
        "status_code": 200,
        "response_time_ms": {"max": 500},
        "ui_element": {"selector": "#checkout-btn", "visible": True}
    },
    "actual": {                                 # From execution
        "status_code": 200,
        "response_time_ms": 320,
        "ui_element": {"selector": "#checkout-btn", "visible": True}
    },
    "baselines": "/apps/app2/snapshots/",       # App2's baselines
    "rules": "/apps/app2/rules.yaml"            # App2's custom rules
}
```

### App-Specific Validation Rules

Each app can define custom validation rules:

```
apps/
   app1/
      rules.yaml                # App1's validation rules
   app2/
      rules.yaml                # App2's validation rules (DIFFERENT!)
```

**App1's rules (modern SPA):**
```yaml
# apps/app1/rules.yaml
rules:
  performance:
    page_load_max_ms: 1000        # Strict (fast app)
    api_response_max_ms: 200
  
  visual:
    pixel_diff_threshold: 0.01    # 1% tolerance
    structural_diff: strict
  
  api:
    required_headers:
      - Content-Type
      - X-Request-ID
      - Cache-Control
    schema_validation: strict
```

**App2's rules (legacy monolith):**
```yaml
# apps/app2/rules.yaml
rules:
  performance:
    page_load_max_ms: 3000        # Relaxed (slower app)
    api_response_max_ms: 800
  
  visual:
    pixel_diff_threshold: 0.05    # 5% tolerance (more dynamic content)
    structural_diff: relaxed
  
  api:
    required_headers:
      - Content-Type
    schema_validation: relaxed    # Legacy APIs have inconsistent schemas
```

### Validation Engine with App-Specific Rules

```python
class ValidationEngine:
    """Deterministic validation with app-specific rules"""
    
    def validate(
        self,
        context: ProjectContext,
        blueprint: Blueprint,
        actual_result: ExecutionResult
    ) -> ValidationResult:
        """Validate using THIS app's baselines and rules"""
        
        # Load app-specific rules
        rules = self._load_rules(f"{context.app_path}/rules.yaml")
        
        # Load app-specific baselines
        baseline_mgr = BaselineManager(context)
        
        validators = []
        
        # UI validation (if applicable)
        if blueprint.test_type == "ui":
            ui_baseline = baseline_mgr.load_ui_baseline(blueprint.page)
            dom_baseline = baseline_mgr.load_dom_baseline(blueprint.page)
            
            validators.append(
                UIValidator(
                    expected=blueprint.expected,
                    actual=actual_result.ui_snapshot,
                    ui_baseline=ui_baseline,
                    dom_baseline=dom_baseline,
                    rules=rules["visual"]  # App-specific visual rules
                )
            )
        
        # Performance validation
        perf_baseline = baseline_mgr.load_perf_baseline(blueprint.id)
        validators.append(
            PerformanceValidator(
                expected=blueprint.expected.performance,
                actual=actual_result.metrics,
                baseline=perf_baseline,
                rules=rules["performance"]  # App-specific perf rules
            )
        )
        
        # API validation (if applicable)
        if blueprint.test_type == "api":
            api_baseline = baseline_mgr.load_api_baseline(blueprint.endpoint)
            
            validators.append(
                APIValidator(
                    expected=blueprint.expected.api,
                    actual=actual_result.api_response,
                    baseline=api_baseline,
                    rules=rules["api"]  # App-specific API rules
                )
            )
        
        # Run all validators
        results = [v.validate() for v in validators]
        
        # Aggregate results
        return ValidationResult(
            app_id=context.app_id,
            blueprint_id=blueprint.id,
            status="pass" if all(r.passed for r in results) else "fail",
            validator_results=results
        )

# ✅ CORRECT: Validation with app-specific baselines/rules
engine = ValidationEngine()

result_app1 = engine.validate(
    context=context_app1,
    blueprint=blueprint_app1,
    actual_result=execution_result
)
# Uses: apps/app1/snapshots/, apps/app1/rules.yaml

result_app2 = engine.validate(
    context=context_app2,
    blueprint=blueprint_app2,
    actual_result=execution_result
)
# Uses: apps/app2/snapshots/, apps/app2/rules.yaml

# ❌ WRONG: Global validation (no app context)
result = engine.validate(blueprint, execution_result)  # Which app's rules?!
```

---

## 🌍 Environment Management Keeps Apps Separate

Each application has its own environment profiles for dev, QA, staging, and production:

```
environments/
   dev/
      app1.yaml                 # App1 dev config
      app2.yaml                 # App2 dev config
      app3.yaml                 # App3 dev config
   
   qa/
      app1.yaml                 # App1 QA config
      app2.yaml                 # App2 QA config
   
   stage/
      app1.yaml                 # App1 staging config
      app2.yaml                 # App2 staging config
   
   prod-safe/
      app1.yaml                 # App1 prod (read-only) config
      app2.yaml                 # App2 prod (read-only) config
```

### Why Environment Isolation Matters

#### 1. **Different APIs per App**
```yaml
# environments/dev/app1.yaml (E-commerce app)
environment:
  name: dev
  app_id: app1
  api:
    base_url: https://api-dev.ecommerce.com
    endpoints:
      login: /auth/login
      products: /api/v2/products
      cart: /api/v2/cart
      checkout: /api/v2/checkout
  authentication:
    type: oauth2
    client_id: "app1-dev-client"
```

```yaml
# environments/dev/app2.yaml (Banking app)
environment:
  name: dev
  app_id: app2
  api:
    base_url: https://banking-api-dev.corp.com
    endpoints:
      login: /v1/auth
      accounts: /v1/accounts
      transfer: /v1/transfer
      balance: /v1/balance
  authentication:
    type: basic_auth      # Different auth!
    realm: "Banking API"
```

#### 2. **Different Login Flows**
```yaml
# environments/qa/app1.yaml
login_flow:
  url: https://app1-qa.com/login
  steps:
    - action: fill
      selector: input[name="email"]
      value: "qa_user@test.com"
    - action: fill
      selector: input[name="password"]
      value: "{{ENV.APP1_QA_PASSWORD}}"
    - action: click
      selector: button[type="submit"]
```

```yaml
# environments/qa/app2.yaml
login_flow:
  url: https://app2-qa.corp.com/auth
  steps:
    - action: fill
      selector: "#username"           # Different selector!
      value: "qa_bank_user"
    - action: fill
      selector: "#password"
      value: "{{ENV.APP2_QA_PASSWORD}}"
    - action: click
      selector: "#login-button"
    - action: wait_for
      selector: "#dashboard"          # Extra step!
```

#### 3. **Different Data Rules**
```yaml
# environments/stage/app1.yaml (E-commerce)
data_rules:
  user_creation:
    email_domain: "@test-ecommerce.com"
    password_min_length: 8
  product_constraints:
    price_min: 0.01
    price_max: 10000.00
  payment:
    test_card: "4111111111111111"
```

```yaml
# environments/stage/app2.yaml (Banking)
data_rules:
  account_creation:
    account_number_format: "^[0-9]{10}$"
    routing_number: "123456789"
  transfer_constraints:
    min_amount: 1.00
    max_amount: 5000.00       # Different limits!
    daily_limit: 10000.00
  compliance:
    kyc_required: true
    aml_check: true
```

### Environment Loader with ProjectContext

```python
class EnvironmentManager:
    """Per-app environment management"""
    
    def __init__(self, context: ProjectContext):
        self.context = context
        self.app_id = context.app_id
    
    def load_environment(self, env_name: str) -> dict:
        """Load environment config for THIS app"""
        env_file = f"environments/{env_name}/{self.app_id}.yaml"
        
        if not os.path.exists(env_file):
            raise FileNotFoundError(
                f"Environment config not found: {env_file}"
            )
        
        with open(env_file, "r") as f:
            env_config = yaml.safe_load(f)
        
        # Validate app_id matches
        if env_config["environment"]["app_id"] != self.app_id:
            raise ValueError(
                f"Environment config app_id mismatch: "
                f"expected {self.app_id}, got {env_config['environment']['app_id']}"
            )
        
        return env_config
    
    def get_api_config(self, env_name: str) -> dict:
        """Get API configuration for THIS app in THIS environment"""
        env = self.load_environment(env_name)
        return env["environment"]["api"]
    
    def get_login_flow(self, env_name: str) -> dict:
        """Get login flow for THIS app in THIS environment"""
        env = self.load_environment(env_name)
        return env.get("login_flow", {})
    
    def get_data_rules(self, env_name: str) -> dict:
        """Get data rules for THIS app in THIS environment"""
        env = self.load_environment(env_name)
        return env.get("data_rules", {})

# ✅ CORRECT: Environment scoped to app
env_mgr_app1 = EnvironmentManager(context_app1)
api_config = env_mgr_app1.get_api_config("dev")  # App1's dev API config

env_mgr_app2 = EnvironmentManager(context_app2)
api_config = env_mgr_app2.get_api_config("dev")  # App2's dev API config (DIFFERENT!)

# ❌ WRONG: Global environment (mixed apps)
api_config = load_env("dev", "api")  # Which app?!
```

### Benefits of Environment Isolation

**1. No Cross-Contamination:**
- App1's dev credentials don't leak to App2
- App1's API endpoints don't interfere with App2's tests

**2. Independent Evolution:**
- App1 can update to OAuth2 while App2 stays on Basic Auth
- App1 can add new environments without affecting App2

**3. Clear Accountability:**
- Each app team owns their environment configs
- Changes to app1/dev.yaml don't affect app2

**4. Security Boundaries:**
- App1 team can't access app2's production secrets
- Role-based access per app/environment combination

---
## �🧪 Testing Multi-App Isolation

### Test 1: Context Enforcement
```python
# Test that agents reject operations without context
agent = QAAgent()
blueprint = Blueprint(id="TEST_001")

# Should raise error:
try:
    agent.generate_test(blueprint)  # No context!
    assert False, "Should have raised error"
except TypeError:
    pass  # ✅ Correct - context required
```

### Test 2: Path Isolation
```python
# Test that paths are scoped correctly
context_app1 = ProjectContext(app_id="app1", ...)
context_app2 = ProjectContext(app_id="app2", ...)

# Should load different blueprints
blueprint_app1 = loader.load_for_context("LOGIN_001", context_app1)
blueprint_app2 = loader.load_for_context("LOGIN_001", context_app2)

assert blueprint_app1.path.startswith("/apps/app1")
assert blueprint_app2.path.startswith("/apps/app2")
assert blueprint_app1 != blueprint_app2  # Different data
```

### Test 3: Memory Isolation
```python
# Test that memory is isolated per app
memory_app1 = VectorMemory(context_app1.memory_path)
memory_app2 = VectorMemory(context_app2.memory_path)

memory_app1.store("test_key", "app1_value")
memory_app2.store("test_key", "app2_value")

# Should be isolated
assert memory_app1.retrieve("test_key") == "app1_value"
assert memory_app2.retrieve("test_key") == "app2_value"
```

---

## 📚 Summary

**ProjectContext is mandatory for all agent operations.**

This ensures:
- ✅ Complete application isolation
- ✅ No accidental cross-app data leakage
- ✅ Clear accountability per application
- ✅ Flexible per-app configuration
- ✅ Secure multi-tenant architecture

**Copilot will now generate code that:**
- Always requires ProjectContext
- Never uses global paths
- Never mixes data between applications
- Properly scopes all operations

---

**Last Updated:** 2026-03-26  
**Platform:** Apex AI Testing Platform  
**Architecture Version:** 2.0.0 (Multi-App Isolation)
