# Copilot Instructions — Blueprint Engine (APEX AI Platform)

## ✅ Purpose
The Blueprint Engine is the **source of truth** for all test logic.  
It replaces traditional test scripts with **declarative, maintainable, versioned test blueprints**.

Copilot MUST treat the Blueprint Engine as:
- **Declarative** → NOT executable code
- **Stable** → NOT frequently rewritten by AI
- **Minimal** → Only test intent, NOT implementation
- **Versioned** → Changes tracked
- **Multi-app capable** → Isolated per application

**Blueprints represent WHAT to test, not HOW to test.**

---

## ✅ What Blueprints Contain

### Core Blueprint Elements
- **Test metadata** (id, name, tags, priority, version)
- **Flow steps** (high-level user actions)
- **Expected outcomes** (assertions, validations)
- **API expectations** (contracts, response schemas)
- **Business rules** (domain-specific logic)
- **Environment overrides** (dev, qa, staging, prod-safe)
- **Performance SLAs** (response times, throughput)
- **Security expectations** (auth, headers, compliance)
- **Snapshots metadata** (baseline references)
- **Risk/coverage annotations** (criticality, coverage areas)

### Blueprint Example
```yaml
# ========================================
# Blueprint: User Login Flow
# ========================================
id: LOGIN_001
version: 1.2.0
name: "Standard User Login"
type: ui_flow
priority: critical
tags: [auth, smoke, regression]

# Test flow (declarative steps)
flow:
  - step: navigate
    url: "/login"
  - step: input
    field: "email"
    value: "${TEST_USER_EMAIL}"
  - step: input
    field: "password"
    value: "${TEST_USER_PASSWORD}"
  - step: click
    target: "#login-button"
  - step: wait
    for: "navigation"

# Expected outcomes (deterministic)
expected:
  url: "/dashboard"
  status_code: 200
  elements_present:
    - "#welcome-message"
    - "#user-profile"
  elements_absent:
    - ".error-message"
  local_storage:
    authToken: exists
    userId: exists

# Business rules
rules:
  authentication:
    method: "jwt"
    token_storage: "localStorage"
    session_duration: 3600
  authorization:
    required_role: "user"

# Performance expectations
performance:
  page_load_time_max: 2000  # ms
  api_response_time_max: 500

# Security expectations
security:
  headers_required:
    - "X-Frame-Options"
    - "Content-Security-Policy"
  no_sensitive_data_in_url: true
  https_only: true

# Environment-specific overrides
environments:
  dev:
    base_url: "http://localhost:3000"
  qa:
    base_url: "https://qa.example.com"
  staging:
    base_url: "https://staging.example.com"

# Metadata
metadata:
  owner: "qa-team"
  created: "2026-01-15"
  last_modified: "2026-03-20"
  jira_ticket: "QA-1234"
  risk_level: "high"
  coverage_areas: ["authentication", "session-management"]
```

---

## ✅ Blueprint Engine Responsibilities

### What the Blueprint Engine DOES
1. **Load blueprints** from filesystem (YAML/JSON)
2. **Parse blueprint syntax** into structured data
3. **Validate blueprint structure** against schema
4. **Version blueprints** with semantic versioning
5. **Resolve environment variables** and overrides
6. **Provide blueprint queries** (by tag, priority, risk)
7. **Track blueprint changes** (git-based versioning)
8. **Generate blueprint metadata** (coverage maps, dependency graphs)
9. **Support multi-application isolation** (separate blueprint namespaces)

### What the Blueprint Engine DOES NOT DO
- ❌ Execute tests (agents do this)
- ❌ Generate test scripts (agents + LLM do this)
- ❌ Make pass/fail decisions (validation engine does this)
- ❌ Call APIs or browsers (plugins do this)
- ❌ Store test results (observability system does this)
- ❌ Decide which tests to run (test selection logic does this)

---

## ✅ Blueprint Schema

### Blueprint YAML Schema
```yaml
# Required fields
id: string                    # Unique blueprint identifier
version: semver               # Semantic version (1.0.0)
name: string                  # Human-readable name
type: enum                    # ui_flow, api, performance, security
priority: enum                # critical, high, medium, low

# Optional fields
description: string
tags: array[string]
owner: string
jira_ticket: string

# Flow definition
flow: array[step]             # Ordered list of test steps
  - step: string              # Step type (navigate, click, input, etc.)
    ... additional fields

# Expected outcomes
expected: object
  url: string
  status_code: integer
  elements_present: array[string]
  elements_absent: array[string]
  api_response: object
  data: object

# Business rules
rules: object
  ... domain-specific rules

# Performance SLAs
performance: object
  page_load_time_max: integer
  api_response_time_max: integer
  throughput_min: integer

# Security expectations
security: object
  headers_required: array[string]
  auth_method: string
  compliance: array[string]

# Environment overrides
environments: object
  [env_name]: object
    ... overrides

# Metadata
metadata: object
  owner: string
  created: date
  last_modified: date
  risk_level: enum
  coverage_areas: array[string]
```

---

## ✅ Blueprint Loader Implementation

### Blueprint Loader Class
```python
class BlueprintLoader:
    """Load and manage test blueprints"""
    
    def __init__(self, blueprints_dir: str = "core/blueprints"):
        self.blueprints_dir = blueprints_dir
        self.schema_validator = BlueprintSchemaValidator()
        self.cache = {}
    
    def load(self, blueprint_id: str, version: str = None) -> Blueprint:
        """Load blueprint by ID and optional version"""
        
        # Check cache
        cache_key = f"{blueprint_id}:{version or 'latest'}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Find blueprint file
        blueprint_path = self._find_blueprint_file(blueprint_id, version)
        if not blueprint_path:
            raise BlueprintNotFoundError(f"Blueprint {blueprint_id} not found")
        
        # Load YAML
        with open(blueprint_path) as f:
            blueprint_data = yaml.safe_load(f)
        
        # Validate against schema
        validation_result = self.schema_validator.validate(blueprint_data)
        if not validation_result.valid:
            raise BlueprintValidationError(
                f"Invalid blueprint: {validation_result.errors}"
            )
        
        # Parse into Blueprint object
        blueprint = Blueprint.from_dict(blueprint_data)
        blueprint.file_path = blueprint_path
        
        # Resolve environment variables
        blueprint = self._resolve_variables(blueprint)
        
        # Cache
        self.cache[cache_key] = blueprint
        
        return blueprint
    
    def load_by_tags(self, tags: List[str]) -> List[Blueprint]:
        """Load all blueprints matching tags"""
        blueprints = []
        
        for blueprint_file in self._discover_blueprints():
            blueprint = self.load_from_file(blueprint_file)
            if any(tag in blueprint.tags for tag in tags):
                blueprints.append(blueprint)
        
        return blueprints
    
    def load_by_priority(self, priority: str) -> List[Blueprint]:
        """Load blueprints by priority level"""
        blueprints = []
        
        for blueprint_file in self._discover_blueprints():
            blueprint = self.load_from_file(blueprint_file)
            if blueprint.priority == priority:
                blueprints.append(blueprint)
        
        return blueprints
    
    def _find_blueprint_file(self, blueprint_id: str, version: str = None) -> str:
        """Find blueprint file by ID and version"""
        
        # Search in blueprints directory
        for root, dirs, files in os.walk(self.blueprints_dir):
            for file in files:
                if file.endswith(('.yaml', '.yml', '.json')):
                    file_path = os.path.join(root, file)
                    
                    # Quick parse to check ID
                    with open(file_path) as f:
                        data = yaml.safe_load(f)
                    
                    if data.get('id') == blueprint_id:
                        if version is None or data.get('version') == version:
                            return file_path
        
        return None
    
    def _resolve_variables(self, blueprint: Blueprint) -> Blueprint:
        """Resolve environment variables in blueprint"""
        
        # Get environment
        env = os.getenv('TEST_ENV', 'qa')
        
        # Apply environment-specific overrides
        if env in blueprint.environments:
            overrides = blueprint.environments[env]
            blueprint = self._apply_overrides(blueprint, overrides)
        
        # Resolve ${VAR} references
        blueprint_dict = blueprint.to_dict()
        resolved_dict = self._resolve_env_vars(blueprint_dict)
        
        return Blueprint.from_dict(resolved_dict)
    
    def _resolve_env_vars(self, data: dict) -> dict:
        """Recursively resolve ${VAR} references"""
        
        if isinstance(data, dict):
            return {k: self._resolve_env_vars(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._resolve_env_vars(item) for item in data]
        elif isinstance(data, str) and data.startswith('${') and data.endswith('}'):
            var_name = data[2:-1]
            return os.getenv(var_name, data)
        else:
            return data
```

---

## ✅ Blueprint Validation

### Schema Validator
```python
class BlueprintSchemaValidator:
    """Validate blueprints against schema"""
    
    def __init__(self):
        self.schema = self._load_schema()
    
    def validate(self, blueprint_data: dict) -> ValidationResult:
        """Validate blueprint structure"""
        
        errors = []
        
        # Required fields
        required = ['id', 'version', 'name', 'type', 'flow']
        for field in required:
            if field not in blueprint_data:
                errors.append(f"Missing required field: {field}")
        
        # Version format (semver)
        if 'version' in blueprint_data:
            if not self._is_valid_semver(blueprint_data['version']):
                errors.append(f"Invalid version format: {blueprint_data['version']}")
        
        # Type validation
        valid_types = ['ui_flow', 'api', 'performance', 'security', 'integration']
        if 'type' in blueprint_data:
            if blueprint_data['type'] not in valid_types:
                errors.append(f"Invalid type: {blueprint_data['type']}")
        
        # Priority validation
        valid_priorities = ['critical', 'high', 'medium', 'low']
        if 'priority' in blueprint_data:
            if blueprint_data['priority'] not in valid_priorities:
                errors.append(f"Invalid priority: {blueprint_data['priority']}")
        
        # Flow validation
        if 'flow' in blueprint_data:
            if not isinstance(blueprint_data['flow'], list):
                errors.append("Flow must be an array of steps")
            else:
                for i, step in enumerate(blueprint_data['flow']):
                    if not isinstance(step, dict) or 'step' not in step:
                        errors.append(f"Invalid step at index {i}")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors
        )
    
    def _is_valid_semver(self, version: str) -> bool:
        """Check if version follows semantic versioning"""
        import re
        pattern = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?(\+[a-zA-Z0-9.]+)?$'
        return bool(re.match(pattern, version))
```

---

## ✅ Blueprint Versioning

### Version Management
```python
class BlueprintVersionManager:
    """Manage blueprint versions with git"""
    
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.git = GitWrapper(repo_path)
    
    def save_version(self, blueprint: Blueprint, commit_message: str):
        """Save blueprint with version control"""
        
        # Save blueprint file
        blueprint_path = os.path.join(
            self.repo_path,
            "core/blueprints",
            f"{blueprint.id}.blueprint.yaml"
        )
        
        with open(blueprint_path, 'w') as f:
            yaml.dump(blueprint.to_dict(), f, sort_keys=False)
        
        # Git commit
        self.git.add(blueprint_path)
        self.git.commit(commit_message)
        self.git.tag(f"{blueprint.id}-v{blueprint.version}")
    
    def get_version_history(self, blueprint_id: str) -> List[VersionInfo]:
        """Get version history for blueprint"""
        
        blueprint_path = f"core/blueprints/{blueprint_id}.blueprint.yaml"
        commits = self.git.log(blueprint_path)
        
        versions = []
        for commit in commits:
            content = self.git.show(commit.hash, blueprint_path)
            blueprint_data = yaml.safe_load(content)
            
            versions.append(VersionInfo(
                version=blueprint_data.get('version'),
                commit_hash=commit.hash,
                author=commit.author,
                date=commit.date,
                message=commit.message
            ))
        
        return versions
    
    def rollback_to_version(self, blueprint_id: str, version: str):
        """Rollback blueprint to specific version"""
        
        # Find commit with this version
        history = self.get_version_history(blueprint_id)
        target_commit = None
        
        for v in history:
            if v.version == version:
                target_commit = v.commit_hash
                break
        
        if not target_commit:
            raise VersionNotFoundError(f"Version {version} not found")
        
        # Checkout file from that commit
        blueprint_path = f"core/blueprints/{blueprint_id}.blueprint.yaml"
        self.git.checkout(target_commit, blueprint_path)
        
        # Commit rollback
        self.git.commit(f"Rollback {blueprint_id} to version {version}")
```

---

## ✅ Blueprint Queries

### Advanced Blueprint Queries
```python
class BlueprintQuery:
    """Query blueprints with advanced filters"""
    
    def __init__(self, loader: BlueprintLoader):
        self.loader = loader
    
    def find_by_coverage_area(self, area: str) -> List[Blueprint]:
        """Find blueprints covering specific area"""
        results = []
        
        for blueprint in self._get_all_blueprints():
            coverage = blueprint.metadata.get('coverage_areas', [])
            if area in coverage:
                results.append(blueprint)
        
        return results
    
    def find_by_risk_level(self, risk: str) -> List[Blueprint]:
        """Find blueprints by risk level"""
        results = []
        
        for blueprint in self._get_all_blueprints():
            if blueprint.metadata.get('risk_level') == risk:
                results.append(blueprint)
        
        return results
    
    def find_impacted_by_files(self, changed_files: List[str]) -> List[Blueprint]:
        """Find blueprints impacted by file changes"""
        
        # Use coverage mapping to determine impact
        coverage_map = self._build_coverage_map()
        
        impacted = set()
        for file in changed_files:
            if file in coverage_map:
                impacted.update(coverage_map[file])
        
        return [self.loader.load(bp_id) for bp_id in impacted]
    
    def get_regression_suite(self) -> List[Blueprint]:
        """Get all blueprints for regression testing"""
        return self.loader.load_by_tags(['regression'])
    
    def get_smoke_suite(self) -> List[Blueprint]:
        """Get smoke test blueprints"""
        return self.loader.load_by_tags(['smoke'])
    
    def get_critical_tests(self) -> List[Blueprint]:
        """Get all critical priority tests"""
        return self.loader.load_by_priority('critical')
```

---

## ✅ Blueprint-to-Test Generation

### How Agents Use Blueprints
```python
# ✅ CORRECT: Blueprint-driven test generation
class QAAgent(BaseAgent):
    def execute_test(self, blueprint_id: str):
        # 1. Load blueprint (declarative)
        blueprint = self.blueprint_loader.load(blueprint_id)
        
        # 2. Generate test implementation (LLM)
        test_script = self.llm_adapter.generate(
            prompt=self._blueprint_to_prompt(blueprint),
            provider="openai"
        )
        
        # 3. Execute via plugin
        playwright = self.plugins.load("playwright")
        evidence = playwright.execute(test_script)
        
        # 4. Validate against blueprint expectations
        result = self.validation_engine.validate(
            evidence=evidence,
            expected=blueprint.expected,
            rules=blueprint.rules
        )
        
        return result

# ❌ INCORRECT: Hardcoded test logic
def execute_test():
    driver.get("https://example.com/login")  # Hardcoded
    driver.find_element_by_id("email").send_keys("test@test.com")  # Hardcoded
    # ... more hardcoded logic
```

---

## ✅ Multi-Application Blueprint Isolation

### Application-Specific Blueprint Structure
```
apps/                          # ← Multi-tenant isolation
   app1/                       # Application 1 (isolated tenant)
      blueprints/              # Only app1's blueprints
         auth/
            login.blueprint.yaml
            logout.blueprint.yaml
         checkout/
            checkout_flow.blueprint.yaml
      metadata/                # App1-specific metadata
      logs/                    # App1-specific logs
      snapshots/               # App1-specific baselines
   app2/                       # Application 2 (isolated tenant)
      blueprints/              # Only app2's blueprints
         api/
            user_api.blueprint.yaml
      metadata/                # App2-specific metadata
      logs/                    # App2-specific logs
      snapshots/               # App2-specific baselines
   app3/
      blueprints/
      metadata/
      logs/
      snapshots/
```

**Critical Rules:**
- ✅ Each app has its own blueprint namespace
- ✅ Blueprints never cross app boundaries
- ✅ Loader always requires app_id/ProjectContext
- ❌ Never load blueprints globally
- ❌ Never mix app1 and app2 blueprints

### Application-Aware Loader with ProjectContext
```python
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class ProjectContext:
    """Context for isolated application operations"""
    app_id: str
    blueprint_path: Path
    env_config: Path
    snapshots_path: Path
    logs_path: Path
    metadata_path: Path
    plugins: list
    llm_model: str
    memory_path: Path
    environment: str

class AppAwareBlueprintLoader(BlueprintLoader):
    """Load blueprints with ProjectContext isolation"""
    
    def load_for_context(
        self, 
        blueprint_id: str, 
        context: ProjectContext
    ) -> Blueprint:
        """Load blueprint scoped to ProjectContext"""
        
        # Load from context-specific path
        blueprint_path = context.blueprint_path / f"{blueprint_id}.yaml"
        
        if not blueprint_path.exists():
            raise BlueprintNotFoundError(
                f"Blueprint {blueprint_id} not found in {context.blueprint_path}"
            )
        
        # Load and parse
        blueprint = self._parse_yaml(blueprint_path)
        
        # Resolve environment variables from context
        blueprint = self._resolve_environment(
            blueprint, 
            context.env_config,
            context.environment
        )
        
        # Validate against context-specific schema
        self._validate_schema(blueprint, context.metadata_path / "schema.json")
        
        return blueprint
    
    def load_all_for_context(self, context: ProjectContext) -> List[Blueprint]:
        """Load all blueprints for a specific app"""
        
        blueprints = []
        
        # Walk context-specific blueprint directory
        for blueprint_file in context.blueprint_path.rglob("*.yaml"):
            try:
                blueprint = self._parse_yaml(blueprint_file)
                blueprint = self._resolve_environment(
                    blueprint,
                    context.env_config,
                    context.environment
                )
                blueprints.append(blueprint)
            except Exception as e:
                logger.warning(f"Failed to load {blueprint_file}: {e}")
        
        return blueprints

# ✅ CORRECT: Context-aware usage
class QAAgent(BaseAgent):
    def execute_test(self, blueprint_id: str, context: ProjectContext):
        # Load blueprint from context-specific path
        blueprint = self.blueprint_loader.load_for_context(
            blueprint_id,
            context
        )
        
        # Generate test (scoped to app)
        test = self.generate_test(blueprint, context)
        
        return test

# ❌ WRONG: Global loading (no context)
class QAAgent(BaseAgent):
    def execute_test(self, blueprint_id: str):
        # Which app is this for?!
        blueprint = self.blueprint_loader.load(blueprint_id)  # WRONG!
```

---

## ✅ What Copilot MUST Generate

### Generate These Types of Code
- ✅ **Blueprint parser functions** - YAML/JSON parsers with validation
- ✅ **Normalized blueprint data models** - Structured Python classes/dataclasses
- ✅ **Mapping functions:**
  - `blueprint → UI test steps` - Extract flow as agent-consumable steps
  - `blueprint → API calls` - Extract endpoints, methods, contracts
  - `blueprint → perf plan` - Extract SLAs, load models, scenarios
  - `blueprint → security checks` - Extract security expectations, headers, auth
- ✅ **Versioning utilities** - Git-based tracking, semver validation
- ✅ **Blueprint validation logic** - Schema validation, field constraints
- ✅ **Blueprint diff tools** - Compare versions, detect breaking changes
- ✅ **Schema validators** - JSON Schema validation, custom rules
- ✅ **Blueprint loader implementations** - Caching, environment resolution
- ✅ **Blueprint query utilities** - Filter by tags, priority, risk, coverage
- ✅ **Environment variable resolvers** - Handle ${VAR} substitutions
- ✅ **Coverage map builders** - Track which blueprints cover which features

---

## ✅ What Copilot MUST NOT Generate

### ❌ FORBIDDEN Patterns

#### ❌ NO Permanent Test Scripts
```python
# ❌ BAD: Storing test scripts in blueprints
blueprint = {
    "id": "LOGIN_001",
    "script": """
        selenium.get('http://example.com')
        selenium.click('#button')
    """  # FORBIDDEN! Tests are generated on-demand
}
```

#### ❌ NO Hardcoded Selectors (Outside Blueprints)
```python
# ❌ BAD: Hardcoded selectors in blueprint engine
def parse_blueprint(bp):
    # Blueprint engine should not know about specific selectors
    if "#login-button" in bp:
        return "login test"  # WRONG!
```

#### ❌ NO UI Logic Inside Blueprint Engine
```python
# ❌ BAD: Mixing execution logic with blueprint
blueprint = {
    "id": "LOGIN_001",
    "execute": lambda: driver.get("/login")  # FORBIDDEN!
}

# ❌ BAD: Blueprint engine executing UI actions
def load_and_execute(blueprint_id):
    bp = load_blueprint(blueprint_id)
    playwright.goto(bp.url)  # WRONG! Agents execute, not blueprint engine
```

#### ❌ NO Tool-Specific Test Cases
```python
# ❌ BAD: Playwright-specific code in blueprint
blueprint = {
    "playwright_script": "page.click('#button')"  # FORBIDDEN!
}

# ❌ BAD: JMeter-specific config in blueprint engine
def convert_to_jmeter(bp):
    return JMeterTestPlan(...)  # WRONG! Agent does this
```

#### ❌ NO Monolithic Code
```python
# ❌ BAD: Giant blueprint engine class (3000+ lines)
class BlueprintEngine:
    def load(self): ...
    def validate(self): ...
    def execute(self): ...  # WRONG!
    def generate_playwright(self): ...  # WRONG!
    def generate_jmeter(self): ...  # WRONG!
    def run_tests(self): ...  # WRONG!
    # 2800 more lines...
```

#### ❌ NO Pass/Fail Decisions
```python
# ❌ BAD: Making pass/fail decisions in blueprint engine
def load_blueprint(id):
    blueprint = parse_yaml(id)
    if blueprint.expected.url == actual_url:
        return "PASS"  # WRONG! Validation engine decides
```

---

## ✅ Blueprint File Organization

### Recommended Structure
```
core/blueprints/
├── schema/
│   ├── blueprint.schema.json      # JSON schema
│   └── step_types.schema.json     # Step definitions
├── templates/
│   ├── ui_flow.template.yaml      # Blueprint templates
│   ├── api.template.yaml
│   └── performance.template.yaml
├── app1/                          # Per-application blueprints
│   ├── auth/
│   ├── checkout/
│   └── admin/
├── shared/                        # Shared blueprints
│   └── health_check.blueprint.yaml
└── archived/                      # Deprecated blueprints
    └── old_login.blueprint.yaml
```

---

## ✅ Checklist for Blueprint Engine Code

- [ ] Loads blueprints from YAML/JSON
- [ ] Validates against schema
- [ ] Supports semantic versioning
- [ ] Resolves environment variables
- [ ] Caches loaded blueprints
- [ ] Supports multi-application isolation
- [ ] Queries by tags, priority, risk
- [ ] Tracks changes with git
- [ ] Never executes tests
- [ ] Never makes pass/fail decisions
- [ ] Purely data/configuration layer
- [ ] Is modular (< 500 lines per file)

---

## ✅ Critical Architectural Rules

### Rule 1: Blueprints Must Be Lightweight and Declarative
```yaml
# ✅ GOOD: Lightweight, declarative
flow:
  - step: navigate
    url: "/login"
  - step: click
    target: "#login-button"

# ❌ BAD: Heavy, imperative
flow:
  - step: execute_python
    code: |
      driver = webdriver.Chrome()
      driver.get('http://example.com/login')
      driver.find_element_by_id('login-button').click()
```

### Rule 2: Only Blueprint Engine Reads/Writes Blueprints
```python
# ✅ GOOD: Agent uses blueprint engine
blueprint = blueprint_engine.load("LOGIN_001")
agent.generate_test(blueprint)

# ❌ BAD: Agent directly reads blueprint
with open("blueprints/login.yaml") as f:
    blueprint = yaml.load(f)  # WRONG!
```

### Rule 3: Agents Receive Normalized Blueprint Objects
```python
# ✅ GOOD: Normalized object
@dataclass
class NormalizedBlueprint:
    id: str
    flow_steps: List[Step]
    expected_outcomes: ExpectedOutcomes
    # ... clean, typed interface

# ❌ BAD: Raw YAML dict
def generate_test(blueprint: dict):  # WRONG!
    # Agent shouldn't parse raw YAML
    steps = blueprint['flow']  # Fragile!
```

### Rule 4: Blueprints MUST Remain Stable During App Changes
```yaml
# ✅ GOOD: Intent-based (stable)
flow:
  - step: click
    target: "login_button"  # Semantic identifier
    locator_strategy: "auto"  # Agent figures out actual selector

# ❌ BAD: Implementation-based (brittle)
flow:
  - step: click
    target: "#app > div.auth > button[data-id='btn-123']"
    # Breaks when CSS changes!
```

### Rule 5: All Test Logic Is Generated On-Demand
```python
# ✅ GOOD: On-demand generation
blueprint = blueprint_engine.load("LOGIN_001")
test_code = qa_agent.generate_playwright_test(blueprint)
execute_once_and_discard(test_code)

# ❌ BAD: Permanent test storage
test_code = qa_agent.generate_playwright_test(blueprint)
save_to_repo("tests/login_test.py", test_code)  # FORBIDDEN!
```

### Rule 6: Blueprint Updates Must Use Versioning + Validation
```python
# ✅ GOOD: Versioned update
blueprint_engine.update_blueprint(
    blueprint_id="LOGIN_001",
    changes={"priority": "critical"},
    version_bump="patch",  # 1.2.0 → 1.2.1
    validate=True
)

# ❌ BAD: Direct file edit
with open("blueprints/login.yaml", "w") as f:
    f.write(modified_content)  # No validation! No versioning!
```

---

## 🎯 Remember

> **Blueprints are declarative, not executable.**  
> **Blueprint Engine loads and parses, never executes.**  
> **Agents generate tests FROM blueprints.**  
> **Validation Engine validates AGAINST blueprints.**  
> **Only Blueprint Engine touches blueprint files.**  
> **Test logic is ALWAYS generated on-demand, NEVER stored.**

---

## � Integration Points

The Blueprint Engine integrates with these systems:

### 1. Validation Engine (Expected Outcomes)
```python
# Blueprint provides expected outcomes
blueprint = blueprint_engine.load("LOGIN_001")
expected = blueprint.expected  # URL, elements, status codes, etc.

# Validation engine validates against them
result = validation_engine.validate(
    evidence=test_evidence,
    expected=expected  # From blueprint
)
```

### 2. LLM Adapter Layer (Plan Generation)
```python
# Blueprint provides context for AI generation
blueprint = blueprint_engine.load("LOGIN_001")

# LLM generates test plan from blueprint
test_plan = llm_adapter.generate(
    prompt_template="generate_test_plan",
    context={"blueprint": blueprint.to_dict()}
)
```

### 3. Agents (Consume Parsed Blueprint Objects)
```python
# Blueprint Engine provides normalized objects
blueprint = blueprint_engine.load("LOGIN_001")

# QA Agent receives clean, typed object
test_code = qa_agent.generate_ui_test(
    blueprint=blueprint  # NormalizedBlueprint object
)

# Performance Agent uses same blueprint
perf_plan = perf_agent.generate_load_test(
    blueprint=blueprint  # Same interface
)
```

### 4. Test Intelligence Brain (Coverage/Risk Metadata)
```python
# Blueprint provides coverage and risk metadata
blueprint = blueprint_engine.load("LOGIN_001")

# Intelligence brain analyzes coverage
intelligence_brain.update_coverage_map(
    blueprint_id=blueprint.id,
    tags=blueprint.tags,
    priority=blueprint.priority,
    coverage_areas=blueprint.coverage_areas
)

# Risk analysis from blueprint priority
risk_score = intelligence_brain.calculate_risk(
    priority=blueprint.priority,  # critical, high, medium, low
    historical_failures=blueprint.historical_failures
)
```

### Integration Flow
```
┌──────────────────┐
│ Blueprint Engine │ (Loads & parses YAML)
└────────┬─────────┘
         │
         ├──→ [Validation Engine]  (expected outcomes)
         ├──→ [LLM Adapter]        (generation context)
         ├──→ [QA Agent]           (test generation)
         ├──→ [Perf Agent]         (load test generation)
         ├──→ [Security Agent]     (security checks)
         └──→ [Intelligence Brain] (coverage/risk tracking)
```

---

## �📚 Related Documentation

- [Main Platform Instructions](../../.apex_copilot_instructions.md)
- [Agent Instructions](../agents/AGENTS_README.md)
- [Validation Engine](../validation/COPILOT_VALIDATION_ENGINE.md)
- [LLM Adapter](../llm/COPILOT_LLM_ADAPTER.md)

---

*Last updated: 2026-03-26*
