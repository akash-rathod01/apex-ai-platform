# Copilot Instructions — QA Agent

## ✅ Purpose
The QA Agent is responsible for **UI + API E2E test generation, healing, and execution**, based on blueprints.

---

## ✅ Responsibilities

### Core Functions
- **Interpret Blueprint YAML** into runnable UI/API test logic
- **Generate Playwright/Selenium test steps ON DEMAND** (never store permanently)
- **Heal broken locators automatically** when DOM changes are detected
- **Generate end-to-end user journey logic** from blueprint flows
- **Validate results** using the Validation Engine (NO AI guessing)

### Defect Detection Via
- DOM diffs (structural changes)
- API response changes (contract violations)
- Workflow deviations (blueprint vs actual flow)
- Visual comparisons (screenshot diffs)
- Logs (error patterns, warnings)

---

## ✅ What NOT to do

### ❌ FORBIDDEN Actions
- ❌ Do NOT store scripts permanently
- ❌ Do NOT decide pass/fail by itself (validation engine decides)
- ❌ Do NOT hardcode tool commands (use plugin loader)
- ❌ Do NOT assume business rules — read them from blueprint
- ❌ Do NOT create monolithic test files
- ❌ Do NOT use direct LLM calls (use LLM adapter)
- ❌ Do NOT hardcode selectors in code
- ❌ Do NOT bypass the agent runtime

---

## ✅ What Copilot Should Generate

### Modular Components
```python
# ✅ GOOD: Modular helper functions
class QATestGenerator:
    def generate_ui_test(self, blueprint: Blueprint) -> UITest:
        """Generate UI test from blueprint on-demand"""
        pass
    
    def heal_locator(self, failed_locator: str, context: dict) -> str:
        """Auto-heal broken selector using LLM adapter"""
        pass
    
    def validate_api_contract(self, response: Response, contract: Contract) -> bool:
        """Validate API response against contract"""
        pass
```

### Generate These Types of Code
- ✅ Modular helper functions for UI & API execution
- ✅ Blueprint → execution transformations
- ✅ Locator auto-healing utilities
- ✅ API contract validation adapters
- ✅ Regression selection logic
- ✅ Error classification logic
- ✅ DOM diff analyzers
- ✅ Visual comparison wrappers
- ✅ Journey flow interpreters

---

## ✅ What Copilot Should NOT Generate

### ❌ AVOID These Patterns
```python
# ❌ BAD: Giant monolithic scripts
def test_entire_application():
    # 1000+ lines of hardcoded test logic
    selenium.get("https://example.com")
    selenium.find_element_by_id("button1").click()
    # ... 997 more lines
    
# ❌ BAD: Hardcoded selectors
SELECTORS = {
    "login_button": "#login-btn",  # Don't hardcode
    "username_field": "input[name='user']"
}

# ❌ BAD: Static scenario files
with open("test_scenario.json", "w") as f:
    json.dump(test_data, f)  # Don't store
```

---

## ✅ Tools Used

### Plugin-Based Tool Access
```python
# ✅ CORRECT: Load via plugin system
playwright = self.plugins.load("playwright", version="1.40.0")
selenium = self.plugins.load("selenium", version="4.15.0")
api_client = self.plugins.load("rest-client")
visual_diff = self.plugins.load("percy")

# ❌ INCORRECT: Direct imports
from playwright.sync_api import sync_playwright  # DON'T
```

### Primary Tools
- **Playwright** (via plugin loader) - Modern UI testing
- **Selenium** (via plugin loader) - Legacy UI testing
- **API testing plugins** - REST, GraphQL, gRPC
- **Visual diff plugins** - Percy, Applitools
- **Mobile testing** - Appium (via plugin)

---

## ✅ Blueprint-First Architecture

### Reading Blueprints
```python
# ✅ CORRECT: Blueprint-driven
blueprint = self.blueprint_loader.load("user_login_flow.blueprint.yaml")
test = self.test_generator.generate_from_blueprint(blueprint)
evidence = test.execute()
result = self.validation_engine.validate(evidence, blueprint)

# ❌ INCORRECT: Hardcoded logic
def test_login():
    driver.get("https://app.com/login")  # Hardcoded
    driver.find_element_by_id("user").send_keys("admin")  # Hardcoded
```

### Blueprint Structure Example
```yaml
# Blueprint defines behavior, agent generates test
blueprint_id: "checkout_flow_001"
flow:
  - step: navigate
    url: "${BASE_URL}/cart"
  - step: click
    locator: "[data-testid='checkout-btn']"
  - step: fill_form
    fields:
      email: "${USER_EMAIL}"
      card: "${TEST_CARD}"
  - step: verify
    expected_url: "/confirmation"
    expected_text: "Order confirmed"
```

---

## ✅ Auto-Healing Logic

### Locator Healing Example
```python
class LocatorHealer:
    def heal(self, failed_locator: str, page_html: str) -> str:
        """Use LLM to find updated locator"""
        prompt = f"""
        The locator '{failed_locator}' failed.
        Here is the current page HTML:
        {page_html[:2000]}
        
        Find the most likely replacement locator.
        """
        
        # ✅ Use LLM adapter
        suggestion = self.llm_adapter.generate(
            prompt=prompt,
            provider="openai",
            temperature=0.3
        )
        
        # Validate suggestion works
        if self.validate_locator(suggestion):
            return suggestion
        
        return None
```

---

## ✅ Validation Engine Integration

### Evidence Collection
```python
# Agent collects evidence, doesn't decide
evidence = Evidence(
    test_id=test.id,
    blueprint_id=blueprint.id,
    
    # UI Evidence
    screenshots=screenshot_paths,
    dom_state=page.content(),
    console_logs=browser.get_logs(),
    
    # API Evidence
    api_responses=api_calls,
    response_times=timing_data,
    
    # Flow Evidence
    steps_executed=actual_steps,
    steps_expected=blueprint.steps,
    
    # Error Evidence
    exceptions=caught_exceptions,
    warnings=warning_messages
)

# ✅ Send to validation engine (deterministic)
result = self.validation_engine.validate(
    evidence=evidence,
    blueprint=blueprint,
    contract=api_contract,
    baseline=historical_baseline
)

# result.status will be: PASS | FAIL | NEEDS_HEALING
```

---

## ✅ LLM Integration

### Correct LLM Usage
```python
# ✅ CORRECT: Via LLM adapter
test_steps = self.llm_adapter.generate(
    prompt=blueprint_to_prompt(blueprint),
    provider="anthropic",
    model="claude-3-sonnet",
    temperature=0.2
)

# ❌ INCORRECT: Direct call
import anthropic
client = anthropic.Anthropic()  # DON'T DO THIS
```

### When to Use LLM
- ✅ Generate test steps from natural language blueprints
- ✅ Heal broken locators
- ✅ Generate test data
- ✅ Analyze error logs for patterns
- ✅ Suggest edge cases

### When NOT to Use LLM
- ❌ Pass/fail decisions (validation engine only)
- ❌ Critical assertions
- ❌ Security validations
- ❌ Actual test execution

---

## ✅ Code Generation Examples

### ✅ GOOD: Modular, Blueprint-Driven
```python
class QAAgent(BaseAgent):
    def __init__(self, runtime, llm_adapter, plugin_loader):
        super().__init__(runtime, llm_adapter, plugin_loader)
        self.blueprint_loader = BlueprintLoader()
        self.test_generator = TestGenerator(llm_adapter)
        self.healer = LocatorHealer(llm_adapter)
    
    def execute_test(self, blueprint_id: str) -> TestResult:
        # Load blueprint
        blueprint = self.blueprint_loader.load(blueprint_id)
        
        # Generate test on-demand
        test = self.test_generator.generate_from_blueprint(blueprint)
        
        # Execute via plugin
        playwright = self.plugins.load("playwright")
        evidence = playwright.execute(test)
        
        # Validate deterministically
        return self.validation_engine.validate(evidence, blueprint)
    
    def auto_heal(self, failure: TestFailure) -> HealingStrategy:
        # Analyze failure
        if failure.type == "LOCATOR_NOT_FOUND":
            new_locator = self.healer.heal(
                failed_locator=failure.locator,
                page_html=failure.context.html
            )
            return HealingStrategy(
                action="UPDATE_LOCATOR",
                old=failure.locator,
                new=new_locator
            )
        
        # Regenerate test from blueprint
        if failure.type == "WORKFLOW_DEVIATION":
            return HealingStrategy(
                action="REGENERATE_TEST",
                blueprint_id=failure.blueprint_id
            )
```

### ❌ BAD: Monolithic, Hardcoded
```python
# ❌ DON'T DO THIS
def run_all_qa_tests():
    driver = webdriver.Chrome()  # Hardcoded
    driver.get("https://myapp.com")  # Hardcoded
    
    # 500 lines of hardcoded steps
    driver.find_element_by_id("login").click()
    driver.find_element_by_name("user").send_keys("admin")
    # ... more hardcoded logic
    
    # Wrong: Making pass/fail decision
    if driver.current_url == "https://myapp.com/dashboard":
        return "PASS"  # Don't do this!
```

---

## ✅ Agent Communication

### Via Runtime Only
```python
# ✅ CORRECT: Request security validation via runtime
security_result = self.runtime.request_validation(
    agent="security",
    evidence=qa_evidence,
    validation_type="auth_security_check"
)

# ❌ INCORRECT: Direct agent call
from core.agents.security import SecurityAgent
sec_agent = SecurityAgent()  # DON'T
result = sec_agent.validate()  # DON'T
```

---

## ✅ Testing Modes

### Supported Test Types
```python
class QAAgent:
    def smoke_test(self, blueprint_id: str):
        """Quick critical path validation"""
        pass
    
    def regression_test(self, changed_files: List[str]):
        """Test affected areas based on code changes"""
        pass
    
    def e2e_journey(self, user_persona: str):
        """Full user journey from blueprint"""
        pass
    
    def api_contract_test(self, api_spec: OpenAPISpec):
        """Validate API responses against contract"""
        pass
    
    def visual_regression(self, baseline_id: str):
        """Compare screenshots against baseline"""
        pass
```

---

## ✅ File Structure

### QA Agent Module Organization
```
core/agents/qa/
├── __init__.py
├── agent.py                 # Main QA agent class
├── COPILOT_QA.md           # This file
├── config.py               # Agent configuration
├── generators/
│   ├── ui_generator.py     # UI test generation
│   ├── api_generator.py    # API test generation
│   └── flow_generator.py   # Journey flow generation
├── healers/
│   ├── locator_healer.py   # Auto-heal broken locators
│   └── flow_healer.py      # Auto-heal broken flows
├── analyzers/
│   ├── dom_analyzer.py     # DOM diff analysis
│   ├── visual_analyzer.py  # Screenshot comparison
│   └── api_analyzer.py     # API response analysis
├── utils/
│   ├── blueprint_parser.py
│   └── evidence_collector.py
├── schemas/
│   └── qa_schemas.py       # Data models
└── tests/
    └── test_qa_agent.py    # Unit tests
```

---

## ✅ Checklist for QA Agent Code

When generating QA agent code, ensure:

- [ ] Extends `BaseAgent` class
- [ ] Loads blueprints (never hardcodes flows)
- [ ] Generates tests on-demand
- [ ] Uses plugin loader for tools
- [ ] Uses LLM adapter (not direct calls)
- [ ] Collects evidence comprehensively
- [ ] Routes to validation engine for decisions
- [ ] Supports auto-healing
- [ ] Communicates via runtime
- [ ] Handles UI and API testing
- [ ] Supports visual regression
- [ ] Logs to observability system
- [ ] Stores insights in vector memory
- [ ] Has comprehensive error handling
- [ ] Is modular (< 500 lines per file)

---

## 🎯 Remember

> **QA Agent generates and executes, Validation Engine decides.**  
> **Blueprints define flows, Agent orchestrates tools.**  
> **Auto-healing regenerates, never patches permanently.**

---

## 📚 Related Documentation

- [Main Agent Instructions](../AGENTS_README.md)
- [Blueprint Schema](../../blueprints/README.md)
- [Validation Engine](../../validation/README.md)
- [Plugin Development](../../../plugins/sdk/README.md)
- [LLM Adapter](../../llm/README.md)

---

*Last updated: 2026-03-26*
