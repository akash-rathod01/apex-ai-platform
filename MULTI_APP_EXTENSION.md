# Multi-Application Extension Guide

## 🔄 CI/CD Integration Is Application-Aware

The platform's CI/CD integration ensures **test execution isolation** at the pipeline level.

### CI/CD Structure

```
cicd/
   github/
      app1.yaml              # App1 GitHub Actions workflow
      app2.yaml              # App2 GitHub Actions workflow
      app3.yaml              # App3 GitHub Actions workflow
   
   jenkins/
      app1.groovy            # App1 Jenkins pipeline
      app2.groovy            # App2 Jenkins pipeline
   
   gitlab/
      app1.gitlab-ci.yml     # App1 GitLab CI
      app2.gitlab-ci.yml     # App2 GitLab CI
   
   azure/
      app1-pipeline.yaml     # App1 Azure DevOps pipeline
      app2-pipeline.yaml     # App2 Azure DevOps pipeline
```

### Why Per-App CI/CD Matters

**1. App1 tests ONLY run for App1 code changes**
```yaml
# cicd/github/app1.yaml
name: App1 Tests

on:
  pull_request:
    paths:
      - 'apps/app1/**'              # Only app1 changes
      - 'core/**'                   # Or core framework changes
  push:
    branches:
      - main
    paths:
      - 'apps/app1/**'

jobs:
  test-app1:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      
      - name: Run App1 Tests
        run: |
          python main.py \
            --app-id app1 \
            --blueprints apps/app1/blueprints/ \
            --env dev
```

**2. App2 tests ONLY run for App2 PRs**
```yaml
# cicd/github/app2.yaml
name: App2 Tests

on:
  pull_request:
    paths:
      - 'apps/app2/**'              # Only app2 changes
      - 'core/**'
  push:
    branches:
      - main
    paths:
      - 'apps/app2/**'

jobs:
  test-app2:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      
      - name: Run App2 Tests
        run: |
          python main.py \
            --app-id app2 \
            --blueprints apps/app2/blueprints/ \
            --env dev
```

**3. App3 tests ONLY run for App3 builds**
```yaml
# cicd/github/app3.yaml
name: App3 Tests

on:
  pull_request:
    paths:
      - 'apps/app3/**'
      - 'core/**'

jobs:
  test-app3:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      
      - name: Run App3 Tests
        run: |
          python main.py \
            --app-id app3 \
            --blueprints apps/app3/blueprints/ \
            --env dev \
            --report-format markdown
```

### Multi-Branch Pipeline Pattern (Jenkins)

```groovy
// cicd/jenkins/app1.groovy
pipeline {
    agent any
    
    when {
        anyOf {
            changeset "apps/app1/**"
            changeset "core/**"
        }
    }
    
    environment {
        APP_ID = 'app1'
        BLUEPRINTS_PATH = 'apps/app1/blueprints/'
        SNAPSHOTS_PATH = 'apps/app1/snapshots/'
    }
    
    stages {
        stage('Test App1') {
            steps {
                sh '''
                    python main.py \
                        --app-id ${APP_ID} \
                        --blueprints ${BLUEPRINTS_PATH} \
                        --env ${BRANCH_NAME}
                '''
            }
        }
        
        stage('Generate Report') {
            steps {
                sh '''
                    python main.py \
                        --app-id ${APP_ID} \
                        --action report \
                        --output apps/app1/reports/
                '''
            }
        }
    }
}
```

### GitLab Multi-Project Pattern

```yaml
# cicd/gitlab/app1.gitlab-ci.yml
variables:
  APP_ID: "app1"
  BLUEPRINTS_PATH: "apps/app1/blueprints/"

workflow:
  rules:
    - changes:
        - apps/app1/**
        - core/**

stages:
  - test
  - report

test-app1:
  stage: test
  script:
    - python main.py --app-id $APP_ID --blueprints $BLUEPRINTS_PATH --env dev
  only:
    changes:
      - apps/app1/**
      - core/**

report-app1:
  stage: report
  script:
    - python main.py --app-id $APP_ID --action report
  artifacts:
    paths:
      - apps/app1/reports/
```

### Benefits of Application-Aware CI/CD

**1. Efficient Pipeline Execution:**
- App1 PR doesn't trigger App2 tests
- No wasted compute resources
- Faster feedback loops

**2. Clear Failure Attribution:**
- App1 pipeline failure = App1 issue
- App2 pipeline failure = App2 issue
- No confusion about which app broke

**3. Independent Deployment:**
- Deploy App1 without affecting App2
- Rollback App1 without touching App2
- Scale pipelines per app

**4. Team Autonomy:**
- App1 team owns app1.yaml
- App2 team owns app2.yaml
- No merge conflicts between teams

### Parallel Execution

```yaml
# cicd/github/monorepo-tests.yaml (Optional: Run all apps in parallel)
name: All Apps Tests

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  # Detect which apps changed
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      app1: ${{ steps.changes.outputs.app1 }}
      app2: ${{ steps.changes.outputs.app2 }}
      app3: ${{ steps.changes.outputs.app3 }}
    steps:
      - uses: actions/checkout@v3
      - uses: dorny/paths-filter@v2
        id: changes
        with:
          filters: |
            app1:
              - 'apps/app1/**'
            app2:
              - 'apps/app2/**'
            app3:
              - 'apps/app3/**'
  
  # Run app1 tests (if changed)
  test-app1:
    needs: detect-changes
    if: needs.detect-changes.outputs.app1 == 'true'
    runs-on: ubuntu-latest
    steps:
      - run: python main.py --app-id app1 --env dev
  
  # Run app2 tests (if changed)
  test-app2:
    needs: detect-changes
    if: needs.detect-changes.outputs.app2 == 'true'
    runs-on: ubuntu-latest
    steps:
      - run: python main.py --app-id app2 --env dev
  
  # Run app3 tests (if changed)
  test-app3:
    needs: detect-changes
    if: needs.detect-changes.outputs.app3 == 'true'
    runs-on: ubuntu-latest
    steps:
      - run: python main.py --app-id app3 --env dev
```

---

## 🤖 Agents Never Mix Information

Multi-agent execution is **completely isolated per application**.

### Agent Execution Flow Per App

```
┌─────────────────────────────────────────────────────────┐
│                      App1 Execution                      │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  QA Agent         →  Only sees apps/app1/                │
│                     Only loads app1 blueprints           │
│                     Only uses app1 UI tools              │
│                                                           │
│  Security Agent   →  Only scans apps/app1/               │
│                     Only loads app1 security tools       │
│                     Only reports app1 vulnerabilities    │
│                                                           │
│  Performance Agent→  Only tests apps/app1/               │
│                     Only loads app1 perf tools           │
│                     Only compares app1 baselines         │
│                                                           │
│  Docs Agent       →  Only documents app1 tests           │
│                     Only reads app1 logs                 │
│                     Only generates app1 reports          │
│                                                           │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                      App2 Execution                      │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  QA Agent         →  Only sees apps/app2/                │
│  Security Agent   →  Only scans apps/app2/               │
│  Performance Agent→  Only tests apps/app2/               │
│  Docs Agent       →  Only documents app2 tests           │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### Agent Isolation Examples

#### Example 1: QA Agent for App1
```python
# App1 execution
context_app1 = ProjectContext(
    app_id="app1",
    blueprint_path=Path("apps/app1/blueprints"),
    ui_tools=["playwright"],
    # ...
)

qa_agent = QAAgent()
result = qa_agent.execute_ui_test(
    blueprint=blueprint_app1,
    context=context_app1
)

# QA Agent:
# ✅ Loads blueprints ONLY from apps/app1/blueprints/
# ✅ Uses Playwright (app1's tool)
# ✅ Saves logs ONLY to apps/app1/logs/
# ✅ Compares ONLY against apps/app1/snapshots/
# ❌ Never touches apps/app2/ or apps/app3/
```

#### Example 2: Security Agent for App2
```python
# App2 execution
context_app2 = ProjectContext(
    app_id="app2",
    blueprint_path=Path("apps/app2/blueprints"),
    security_tools=["zap", "nmap"],
    # ...
)

security_agent = SecurityAgent()
result = security_agent.scan_vulnerabilities(
    blueprint=blueprint_app2,
    context=context_app2
)

# Security Agent:
# ✅ Scans ONLY app2's endpoints (from apps/app2/blueprints/)
# ✅ Uses ZAP + Nmap (app2's tools)
# ✅ Reports ONLY to apps/app2/logs/security.log
# ❌ Never scans app1 or app3
```

#### Example 3: Performance Agent for App3
```python
# App3 execution
context_app3 = ProjectContext(
    app_id="app3",
    blueprint_path=Path("apps/app3/blueprints"),
    perf_tools=["k6", "locust"],
    # ...
)

perf_agent = PerformanceAgent()
result = perf_agent.run_load_test(
    blueprint=blueprint_app3,
    context=context_app3
)

# Performance Agent:
# ✅ Loads k6 + Locust (app3's tools)
# ✅ Tests ONLY app3's API endpoints
# ✅ Compares ONLY against apps/app3/snapshots/performance/
# ✅ Uses app3's memory database for baselines
# ❌ Never touches app1 or app2 performance data
```

#### Example 4: DevOps Agent for App1
```python
# App1 CI/CD integration
context_app1 = ProjectContext(
    app_id="app1",
    # ...
)

devops_agent = DevOpsAgent()
devops_agent.trigger_ci_pipeline(
    app_id="app1",
    context=context_app1,
    pipeline_file="cicd/github/app1.yaml"
)

# DevOps Agent:
# ✅ Triggers ONLY app1.yaml pipeline
# ✅ Posts comments ONLY on app1-related PRs
# ✅ Deploys ONLY app1 artifacts
# ❌ Never triggers app2 or app3 pipelines
```

### Multi-Agent Orchestration (Per App)

```python
class TestOrchestrator:
    """Orchestrate multi-agent execution per app"""
    
    def execute_full_test_suite(
        self,
        context: ProjectContext
    ) -> TestSuiteResult:
        """Run all agents for THIS app only"""
        
        results = {}
        
        # 1. QA Agent (UI + API tests)
        qa_agent = QAAgent()
        results["qa"] = qa_agent.execute_tests(context)
        
        # 2. Performance Agent (Load tests)
        perf_agent = PerformanceAgent()
        results["performance"] = perf_agent.execute_tests(context)
        
        # 3. Security Agent (Vulnerability scans)
        security_agent = SecurityAgent()
        results["security"] = security_agent.execute_scans(context)
        
        # 4. Docs Agent (Generate reports)
        docs_agent = DocsAgent()
        results["report"] = docs_agent.generate_report(
            context,
            test_results=results
        )
        
        return TestSuiteResult(
            app_id=context.app_id,  # Always includes app_id!
            agent_results=results
        )

# ✅ CORRECT: Each app gets isolated orchestration
orchestrator = TestOrchestrator()

# App1 execution (completely isolated)
suite_result_app1 = orchestrator.execute_full_test_suite(context_app1)

# App2 execution (completely isolated)
suite_result_app2 = orchestrator.execute_full_test_suite(context_app2)

# No cross-contamination!
```

### Agent Isolation Guarantees

**1. Storage Isolation:**
- QA Agent writes to `apps/{app_id}/logs/qa.log`
- Security Agent writes to `apps/{app_id}/logs/security.log`
- Performance Agent writes to `apps/{app_id}/logs/performance.log`
- Docs Agent writes to `apps/{app_id}/reports/`

**2. Tool Isolation:**
- App1 QA Agent uses Playwright
- App2 QA Agent uses Selenium
- No conflicts, no shared state

**3. Memory Isolation:**
- App1 agents use `core/memory/app1_memory.db`
- App2 agents use `core/memory/app2_memory.db`
- No shared test intelligence

**4. Configuration Isolation:**
- App1 agents read `apps/app1/config.yaml`
- App2 agents read `apps/app2/config.yaml`
- Independent tool configurations

---

## 📈 This Architecture Scales to ANY Number of Applications

The multi-application isolation pattern is designed to **scale from 2-3 apps to 50+ apps** without architectural changes.

### Scalability Progression

#### Phase 1: Initial Setup (2-3 Apps)
```
apps/
   app1/  (E-commerce)
   app2/  (Banking API)
   app3/  (Admin Dashboard)

core/memory/
   app1_memory.db
   app2_memory.db
   app3_memory.db
```

**Status:**
- ✅ 3 isolated tenants
- ✅ Independent tool configs
- ✅ Separate CI/CD pipelines
- ✅ Total isolation achieved

#### Phase 2: Growth (5-10 Apps)
```
apps/
   app1/  (E-commerce)
   app2/  (Banking API)
   app3/  (Admin Dashboard)
   app4/  (Mobile API)
   app5/  (Reporting Service)
   app6/  (Notification Service)
   app7/  (Payment Gateway)
   app8/  (User Management)
   app9/  (Analytics Dashboard)
   app10/ (Partner Portal)
```

**Status:**
- ✅ 10 isolated tenants
- ✅ No architectural changes needed
- ✅ Each app still has own blueprints, memory, logs, snapshots
- ✅ CI/CD still isolated (10 separate pipeline files)
- ✅ No performance degradation (blueprints are small, tests generated on-demand)

#### Phase 3: Enterprise Scale (50+ Apps)
```
apps/
   app1/ ... app50/ (Monorepo with 50 microservices)
   
   # Or organized by domain:
   ecommerce/
      app1/ (Frontend)
      app2/ (Cart Service)
      app3/ (Product Catalog)
   
   banking/
      app4/ (Transfers)
      app5/ (Accounts)
      app6/ (Loans)
   
   admin/
      app7/ (User Management)
      app8/ (Reporting)
```

**Status:**
- ✅ 50+ isolated tenants
- ✅ STILL no architectural changes
- ✅ Each app maintains isolation
- ✅ CI/CD scales linearly (50 pipeline files)
- ✅ Parallel execution (GitHub Actions matrix strategy)

### Why This Architecture Never Collapses

**1. Blueprints Are Small**
```yaml
# Each blueprint: ~50-200 lines
id: LOGIN_001
name: Login Flow Test
app_id: app1
version: 2.1.0
steps:
  - action: navigate
    url: "{{BASE_URL}}/login"
  # ... 10-20 steps total
```
- No script storage (tests generated on-demand)
- Blueprints don't grow over time
- Each app has 50-500 blueprints (~10-100 KB per app)

**2. Scripts Are Generated On-Demand**
```python
# NO permanent script storage
test_script = llm_adapter.generate_test(blueprint, context)
executor.execute(test_script)
# Script discarded after execution!
```
- No script sprawl
- No repository bloat
- Always fresh, always clean

**3. Execution Is Isolated**
- App1 tests run in isolation
- App2 tests run in isolation
- No shared runtime state between apps

**4. Memory Is Isolated**
```
core/memory/
   app1_memory.db   (5 MB)
   app2_memory.db   (8 MB)
   ...
   app50_memory.db  (6 MB)
   # Total: ~300 MB for 50 apps
```
- Each database stays small (~5-10 MB per app)
- No cross-app joins
- Scales linearly

**5. Plugins Are App-Bound**
```python
# App1 uses Playwright
context_app1.ui_tools = ["playwright"]

# App2 uses Selenium
context_app2.ui_tools = ["selenium"]

# No conflicts, each app loads own tools
```

**6. Agents Run Per-App Context**
```python
# Each agent invocation includes context
qa_agent.execute_test(blueprint, context_app1)  # App1
qa_agent.execute_test(blueprint, context_app27) # App27
```
- No global agent state
- Scales to any number of apps

**7. Environment Configs Are Separate**
```
environments/
   dev/
      app1.yaml ... app50.yaml
   qa/
      app1.yaml ... app50.yaml
```
- Each app manages own environments
- No merge conflicts

### Scalability Benchmarks

| Apps | Blueprints | Memory DBs | CI/CD Files | Total Disk | Scalability |
|------|------------|------------|-------------|------------|-------------|
| 3    | ~900       | 3 x 5 MB   | 3           | ~50 MB     | ✅ Easy     |
| 10   | ~3,000     | 10 x 6 MB  | 10          | ~150 MB    | ✅ Easy     |
| 50   | ~15,000    | 50 x 7 MB  | 50          | ~500 MB    | ✅ Easy     |
| 100  | ~30,000    | 100 x 8 MB | 100         | ~1 GB      | ✅ Easy     |

**Key Insight:** Linear scaling with NO architectural changes.

---

## ➕ Adding New Applications Is Trivial

Adding a new application requires **minimal setup** and **zero changes to existing apps**.

### Step 1: Create App Directory Structure

```bash
# Add new app4
mkdir -p apps/app4/{blueprints,snapshots,logs,metadata}
mkdir -p apps/app4/snapshots/{ui,api,performance}
```

Result:
```
apps/
   app4/
      blueprints/           # Empty, ready for blueprints
      snapshots/
         ui/                # Empty, ready for UI baselines
         api/               # Empty, ready for API baselines
         performance/       # Empty, ready for perf baselines
      logs/                 # Empty, ready for execution logs
      metadata/             # Empty, ready for metadata
```

### Step 2: Create App Configuration

```yaml
# apps/app4/config.yaml
app:
  id: app4
  name: "Customer Portal"
  version: "1.0.0"

tools:
  ui_tools:
    - cypress              # App4 uses Cypress
  api_tools:
    - rest-assured
  perf_tools:
    - artillery
  security_tools:
    - burp

llm:
  model: "llama-3.1"       # App4 uses Llama 3.1

execution:
  parallel: true
  max_workers: 4
```

### Step 3: Add Plugin Entry (Optional)

```json
// plugins/app4.json
{
  "app_id": "app4",
  "plugins": [
    {
      "name": "cypress",
      "type": "ui",
      "version": "13.0.0",
      "enabled": true
    },
    {
      "name": "rest-assured",
      "type": "api",
      "version": "5.3.0",
      "enabled": true
    }
  ]
}
```

### Step 4: Add Validation Rules (Optional)

```yaml
# apps/app4/rules.yaml
rules:
  performance:
    page_load_max_ms: 2000
    api_response_max_ms: 500
  
  visual:
    pixel_diff_threshold: 0.03    # 3% tolerance
    structural_diff: relaxed
  
  api:
    required_headers:
      - Content-Type
      - Authorization
    schema_validation: strict
```

### Step 5: Add Environment Configs

```yaml
# environments/dev/app4.yaml
environment:
  name: dev
  app_id: app4
  api:
    base_url: https://customer-portal-dev.com
    endpoints:
      login: /auth/login
      dashboard: /dashboard
  authentication:
    type: oauth2
    client_id: "app4-dev-client"
```

### Step 6: Add CI/CD Pipeline

```yaml
# cicd/github/app4.yaml
name: App4 Tests

on:
  pull_request:
    paths:
      - 'apps/app4/**'
      - 'core/**'

jobs:
  test-app4:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run App4 Tests
        run: python main.py --app-id app4 --env dev
```

### Step 7: Done! ✅

**That's it.** App4 is now:
- ✅ Fully isolated from App1, App2, App3
- ✅ Has its own blueprints, memory, logs, snapshots
- ✅ Has its own CI/CD pipeline
- ✅ Uses its own tools (Cypress, Rest-Assured, Artillery, Burp)
- ✅ Has its own validation rules
- ✅ Has its own environment configs
- ✅ Can scale independently

### What DOESN'T Change When Adding App4

❌ **App1, App2, App3 are unaffected**
- No changes to their blueprints
- No changes to their configs
- No changes to their pipelines
- No changes to their memory databases

❌ **Core framework is unaffected**
- No code changes needed
- No new dependencies
- No architectural refactoring

❌ **Agents are unaffected**
- QAAgent, PerfAgent, SecurityAgent, DocsAgent work identically
- Just pass `context_app4` instead of `context_app1`

### Adding Apps at Scale

```bash
# Add 10 new apps at once
for i in {11..20}; do
    mkdir -p apps/app$i/{blueprints,snapshots,logs,metadata}
    cp apps/app1/config.yaml apps/app$i/config.yaml
    sed -i "s/app1/app$i/g" apps/app$i/config.yaml
    cp cicd/github/app1.yaml cicd/github/app$i.yaml
    sed -i "s/app1/app$i/g" cicd/github/app$i.yaml
done
```

**Result:** 10 new isolated apps in seconds.

---

**Last Updated:** 2026-03-26  
**Platform:** Apex AI Testing Platform  
**Document:** Multi-Application CI/CD, Agent Isolation & Scalability
