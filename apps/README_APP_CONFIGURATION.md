# Application Configuration Guide

## 📁 App-Specific Configuration Structure

Each application in the Apex AI Platform is **completely isolated** with its own configuration, tools, and data.

```
apps/
   app1/
      config.yaml               # ← App-specific configuration
      blueprints/               # App-specific test blueprints
      metadata/                 # App-specific metadata
      logs/                     # App-specific logs
      snapshots/                # App-specific baselines
   app2/
      config.yaml               # ← Different configuration!
      blueprints/
      metadata/
      logs/
      snapshots/
```

---

## ⚙️ App Configuration File

Each app has a `config.yaml` that defines:
- Which testing tools to use
- Which LLM model to use
- Environment-specific settings
- Plugin preferences

### Example: `apps/app1/config.yaml`

```yaml
# Application: app1
# Purpose: E-commerce web application

app:
  id: app1
  name: "E-commerce Platform"
  type: web
  
# Tool Configuration (per testing domain)
tools:
  uiTools:
    - playwright              # Primary UI automation
  
  apiTools:
    - postman-lite            # API testing
  
  perfTools:
    - jmeter                  # Load testing
  
  securityTools:
    - zap                     # Security scanning

# AI Model Configuration
llm:
  model: qwen-7b              # Local model for cost efficiency
  temperature: 0.3            # Low temperature for deterministic generation
  max_tokens: 2000

# Memory Configuration
memory:
  enabled: true
  db_path: /core/memory/app1.db
  vector_store: chroma

# Environment-specific overrides
environments:
  dev:
    base_url: http://localhost:3000
    parallel_tests: 5
  
  qa:
    base_url: https://qa.ecommerce.example.com
    parallel_tests: 10
  
  staging:
    base_url: https://staging.ecommerce.example.com
    parallel_tests: 15
  
  prod-safe:
    base_url: https://www.ecommerce.example.com
    parallel_tests: 3
    read_only: true           # No mutations in prod
```

### Example: `apps/app2/config.yaml`

```yaml
# Application: app2
# Purpose: Banking API backend

app:
  id: app2
  name: "Banking API"
  type: api
  
# Tool Configuration (DIFFERENT from app1!)
tools:
  uiTools: []                 # No UI tests for API-only app
  
  apiTools:
    - rest-assured            # Different API tool
    - postman-lite
  
  perfTools:
    - k6                      # Different perf tool
    - locust
  
  securityTools:
    - burp                    # Different security tools
    - nmap
    - nikto

# AI Model Configuration (DIFFERENT from app1!)
llm:
  model: gpt-4                # Using remote model for complex API logic
  temperature: 0.2
  max_tokens: 3000

# Memory Configuration
memory:
  enabled: true
  db_path: /core/memory/app2.db
  vector_store: pinecone      # Different vector store

# Environment-specific overrides
environments:
  dev:
    base_url: http://localhost:8080
    api_version: v2
  
  qa:
    base_url: https://api-qa.bank.example.com
    api_version: v2
  
  prod-safe:
    base_url: https://api.bank.example.com
    api_version: v2
    read_only: true
    require_2fa: true         # Extra security for banking
```

---

## 🎯 How Configuration Drives Isolation

### 1. Tool Selection Per App

```python
# Load app1 configuration
app1_config = load_config("app1")
# Returns: {"uiTools": ["playwright"], "apiTools": ["postman-lite"], ...}

# Load app2 configuration
app2_config = load_config("app2")
# Returns: {"uiTools": [], "apiTools": ["rest-assured", "postman-lite"], ...}

# Create contexts
context_app1 = ProjectContext(
    app_id="app1",
    ui_tools=app1_config["tools"]["uiTools"],      # ["playwright"]
    api_tools=app1_config["tools"]["apiTools"],    # ["postman-lite"]
    # ...
)

context_app2 = ProjectContext(
    app_id="app2",
    ui_tools=app2_config["tools"]["uiTools"],      # [] (no UI tests)
    api_tools=app2_config["tools"]["apiTools"],    # ["rest-assured", "postman-lite"]
    # ...
)
```

### 2. Agent Uses Context to Load Tools

```python
class QAAgent(BaseAgent):
    def generate_ui_test(self, blueprint: Blueprint, context: ProjectContext):
        # Agent KNOWS which app it's working for
        logger.info(f"Generating UI test for {context.app_id}")
        
        # Agent LOADS only that app's tools
        if not context.ui_tools:
            raise ValueError(f"{context.app_id} has no UI tools configured")
        
        # Agent USES only that app's tool
        ui_tool = self.plugins.load(context.ui_tools[0])  # Playwright for app1
        
        # Generate and execute
        test = self.generate_test(blueprint, context)
        evidence = ui_tool.execute(test)
        
        # Agent SAVES results to the right folder
        self.save_results(context.logs_path / "ui_test_results.json", evidence)
        
        return evidence
```

---

## 🔄 Configuration Loading Flow

```
1. System receives request: "Run tests for app1"
   ↓
2. Load app1/config.yaml
   {
     "tools": {
       "uiTools": ["playwright"],
       "apiTools": ["postman-lite"],
       "perfTools": ["jmeter"],
       "securityTools": ["zap"]
     },
     "llm": {"model": "qwen-7b"}
   }
   ↓
3. Build ProjectContext with app1's tools
   context = ProjectContext(
     app_id="app1",
     ui_tools=["playwright"],
     api_tools=["postman-lite"],
     perf_tools=["jmeter"],
     security_tools=["zap"],
     llm_model="qwen-7b"
   )
   ↓
4. Pass context to agent
   agent.generate_test(blueprint, context)
   ↓
5. Agent loads ONLY app1's tools from context
   playwright = plugins.load(context.ui_tools[0])
   ↓
6. Execute test with app1's tool
   evidence = playwright.execute(test)
   ↓
7. Save to app1's log directory
   save_logs(context.logs_path, evidence)
```

---

## ✅ Benefits of Per-App Configuration

### 1. **Flexibility**
- App1 can use Playwright while App2 uses Selenium
- App1 can use local LLM while App2 uses GPT-4
- Different apps = different needs = different tools

### 2. **Cost Optimization**
- Simple apps use free local models (Qwen)
- Complex apps use premium models (GPT-4)
- Only pay for what each app needs

### 3. **Tool Compatibility**
- Legacy apps use older tools (Selenium)
- Modern apps use newer tools (Playwright)
- No conflicts!

### 4. **Security**
- Banking apps use Burp Suite Pro
- E-commerce apps use OWASP ZAP (free)
- Each app gets appropriate security level

### 5. **Upgrade Isolation**
- Upgrade app1's tools without affecting app2
- Test new tools on one app first
- Gradual migration across apps

---

## 📋 Configuration Schema

```yaml
# Complete schema for apps/{app_id}/config.yaml

app:
  id: string                  # Unique app identifier
  name: string                # Human-readable name
  type: enum                  # web, api, mobile, desktop
  description: string         # App description

tools:
  uiTools: list[string]       # ["playwright", "selenium", "cypress"]
  apiTools: list[string]      # ["postman-lite", "rest-assured", "axios"]
  perfTools: list[string]     # ["k6", "jmeter", "locust"]
  securityTools: list[string] # ["zap", "burp", "nmap", "nikto"]

llm:
  model: string               # "qwen-7b", "gpt-4", "claude-3"
  temperature: float          # 0.0 - 1.0
  max_tokens: int             # 1000 - 8000
  provider: string            # "local", "openai", "anthropic"

memory:
  enabled: bool               # true/false
  db_path: string             # Path to vector DB
  vector_store: string        # "chroma", "pinecone", "weaviate"

environments:
  dev:
    base_url: string
    parallel_tests: int
    # ... other env-specific settings
  qa:
    base_url: string
    parallel_tests: int
  staging:
    base_url: string
    parallel_tests: int
  prod-safe:
    base_url: string
    parallel_tests: int
    read_only: bool           # Prevent mutations in prod
```

---

## 🛠️ Creating Configuration for New App

### Step 1: Create App Directory
```bash
mkdir -p apps/app3/blueprints
mkdir -p apps/app3/metadata
mkdir -p apps/app3/logs
mkdir -p apps/app3/snapshots
```

### Step 2: Create Configuration File
```bash
touch apps/app3/config.yaml
```

### Step 3: Define Configuration
```yaml
# apps/app3/config.yaml
app:
  id: app3
  name: "Mobile App"
  type: mobile

tools:
  uiTools:
    - appium              # Mobile automation
  apiTools:
    - postman-lite
  perfTools:
    - k6
  securityTools:
    - zap

llm:
  model: qwen-7b
  temperature: 0.3

environments:
  dev:
    base_url: http://localhost:4000
  qa:
    base_url: https://qa-mobile.example.com
```

### Step 4: Verify Configuration
```python
# Test loading
config = load_config("app3")
assert config["app"]["id"] == "app3"
assert "appium" in config["tools"]["uiTools"]
```

---

## 🎯 Key Takeaways

1. **Each app has its own `config.yaml`**
2. **Configuration defines tools per domain** (UI, API, perf, security)
3. **ProjectContext is built from configuration**
4. **Agents use context to load correct tools**
5. **Complete isolation** — app1 tools ≠ app2 tools

**The agent:**
- ✅ KNOWS which app it's working for (`context.app_id`)
- ✅ LOADS only that app's data (`context.blueprint_path`)
- ✅ USES only that app's tools (`context.ui_tools[0]`)
- ✅ SAVES results to the right folder (`context.logs_path`)

---

**Last Updated:** 2026-03-26  
**Platform:** Apex AI Testing Platform  
**Version:** 2.0.0 (Multi-App Isolation)
