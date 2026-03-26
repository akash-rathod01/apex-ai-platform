# 🚀 Apex AI Testing Platform

**Enterprise-grade, Multi-Agent AI-Powered Test Automation Platform**

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Node.js](https://img.shields.io/badge/Node.js-22+-green.svg)](https://nodejs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Overview

Apex AI is a **blueprint-first, deterministic test automation platform** powered by multiple specialized AI agents. It combines:

- 🎯 **Blueprint-first architecture** - YAML/JSON as source of truth
- 🤖 **Multi-agent system** - QA, Performance, Security, DevOps, Docs agents
- ✅ **Deterministic validation** - NO AI in pass/fail decisions
- 🏢 **Multi-application isolation** - Each app has isolated resources
- 🔌 **Plugin-based** - Runtime-loaded tools (Playwright, k6, ZAP, etc.)
- 🧠 **Test Intelligence** - Flakiness detection, risk scoring, auto-healing
- 🌐 **Provider-agnostic LLM** - Local (Ollama) or remote (OpenAI, Anthropic)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Web Dashboard (Next.js)                   │
└─────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Multi-Agent Orchestration                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │QA Agent  │  │Perf Agent│  │Sec Agent │  │DevOps    │  ...  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Core Engines                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │Blueprint     │  │Validation    │  │Test          │         │
│  │Engine        │  │Engine        │  │Intelligence  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Runtime Executors                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │Playwright│  │Selenium  │  │k6        │  │ZAP       │  ...  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✨ Key Features

### 🎯 Blueprint-First Testing
- Tests defined in YAML/JSON blueprints
- Generated on-demand, never stored
- Versioned and validated

### 🤖 Multi-Agent System
- **QA Agent** - UI/API test generation and execution
- **Performance Agent** - Load testing with k6/JMeter/Locust
- **Security Agent** - Vulnerability scanning with ZAP/Nmap
- **DevOps Agent** - CI/CD integration and pipeline management
- **Docs Agent** - Report generation and documentation

### ✅ Deterministic Validation
- **NO AI** in pass/fail decisions
- Rule-based validation against:
  - Blueprints (expected outcomes)
  - Contracts (API schemas)
  - Baselines (historical passing state)
  - Logs (error detection)
  - Visual diffs (pixel/structural)

### 🏢 Multi-Application Isolation
Each application has **completely isolated resources**:
```
apps/
├── app1/
│   ├── blueprints/      # Test definitions
│   ├── snapshots/       # UI/API/performance baselines
│   ├── logs/            # Execution logs
│   ├── config.yaml      # Tool configuration
│   └── rules.yaml       # Validation rules
├── app2/
│   └── ...
└── app3/
    └── ...

core/memory/
├── app1_memory.db       # Isolated database per app
├── app2_memory.db
└── app3_memory.db
```

### 🧠 Test Intelligence Brain
- **Flakiness Detection** - Identify unstable tests
- **Risk Scoring** - Prioritize critical test failures
- **Auto-Healing** - Suggest locator fixes automatically
- **Performance Baselines** - Track regression over time

---

## 📦 Installation

### Prerequisites
- **Python 3.10+** (Installed: 3.13.4)
- **Node.js 18+** (Installed: 22.14.0)
- **Git** (Installed: 2.34.1)

### Quick Start

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/apex-ai-platform.git
cd apex-ai-platform

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install

# Install UI dependencies
cd ui/web
npm install
cd ../..

# Run verification
python verify_complete_setup.py
```

### Development Setup

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\Activate.ps1

# Install all dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Initialize databases
python test_database.py

# Start web dashboard
cd ui/web
npm run dev
```

---

## 🚀 Usage

### 1. Create a Blueprint

```yaml
# apps/app1/blueprints/login_test.yaml
version: "1.0"
blueprint_id: "LOGIN_001"
type: "ui"
metadata:
  name: "User Login Test"
  app_id: "app1"
  priority: "high"

steps:
  - action: navigate
    target: "https://app.example.com/login"
  
  - action: fill
    selector: "#email"
    value: "user@example.com"
  
  - action: fill
    selector: "#password"
    value: "secure_password"
  
  - action: click
    selector: "#login-button"

expected:
  url: "/dashboard"
  status_code: 200
  elements_present:
    - "#welcome-message"
    - "#user-menu"
  response_time_max: 2000
```

### 2. Run Tests

```python
from core.agents.qa import QAAgent
from core.blueprints import load_blueprint

# Load blueprint
blueprint = load_blueprint("apps/app1/blueprints/login_test.yaml")

# Create QA agent with app context
qa_agent = QAAgent(
    app_id="app1",
    tools=["playwright"]
)

# Execute test
result = qa_agent.execute_test(blueprint)

print(f"Status: {result.status}")
print(f"Confidence: {result.confidence}")
print(f"Reasoning:\n{result.reasoning}")
```

### 3. View Results

```bash
# Start web dashboard
cd ui/web
npm run dev

# Open http://localhost:3000
# View test results, baselines, flakiness metrics
```

---

## 🛠️ Configuration

### Environment Variables

Create `.env` file in project root:

```bash
# LLM Configuration
LLM_PROVIDER=ollama              # ollama, openai, anthropic
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b

# OpenAI (optional)
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4

# Anthropic (optional)
ANTHROPIC_API_KEY=your_key_here
ANTHROPIC_MODEL=claude-3-sonnet

# Platform Configuration
LOG_LEVEL=INFO
MAX_PARALLEL_AGENTS=5
ENABLE_AUTO_HEALING=true
```

### Per-App Configuration

```yaml
# apps/app1/config.yaml
app_id: app1
name: "My React SPA"

tools:
  ui_tools: ["playwright"]
  api_tools: ["requests", "httpx"]
  perf_tools: ["k6"]
  security_tools: ["zap"]

llm:
  model: "qwen2.5:3b"
  temperature: 0.7

execution:
  max_retries: 3
  timeout_ms: 30000
  headless: true
```

---

## 📁 Project Structure

```
apex-ai-platform/
├── apps/                      # Per-app isolation
│   ├── app1/
│   │   ├── blueprints/        # Test blueprints
│   │   ├── snapshots/         # Baselines (UI, API, perf)
│   │   ├── logs/              # Execution logs
│   │   ├── config.yaml        # App configuration
│   │   └── rules.yaml         # Validation rules
│   └── app2/
├── core/                      # Core engines
│   ├── agents/                # Multi-agent system
│   │   ├── qa/
│   │   ├── performance/
│   │   ├── security/
│   │   ├── devops/
│   │   └── docs/
│   ├── blueprints/            # Blueprint engine
│   ├── validation/            # Validation engine
│   ├── llm/                   # LLM adapter
│   ├── intelligence/          # Test intelligence brain
│   ├── memory/                # Database manager
│   └── utils/
├── plugins/                   # Runtime-loaded plugins
│   ├── qa/                    # Playwright, Selenium
│   ├── api/                   # Requests, HTTPx
│   ├── performance/           # k6, JMeter, Locust
│   └── security/              # ZAP, Nmap, Nikto
├── runtime/                   # Test execution
│   ├── runner-api/            # REST API
│   ├── runner-agents/         # Agent orchestration
│   ├── runner-executors/      # Playwright/Selenium runners
│   └── sandbox/               # Isolated execution
├── ui/                        # Web dashboard
│   └── web/                   # Next.js app
├── cicd/                      # CI/CD integrations
│   ├── github/
│   ├── jenkins/
│   ├── gitlab/
│   └── azure/
├── environments/              # Environment configs
│   ├── dev/
│   ├── qa/
│   └── prod-safe/
├── observability/             # Metrics/logs/traces
├── .gitignore
├── README.md
├── requirements.txt
├── SETUP_COMPLETE.md
└── verify_complete_setup.py
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/core/validation/

# Run with coverage
pytest --cov=core --cov-report=html

# Test database setup
python test_database.py

# Verify installation
python verify_complete_setup.py
```

---

## 📚 Documentation

- [Setup Guide](SETUP_COMPLETE.md) - Installation and configuration
- [Multi-App Isolation](MULTI_APP_ISOLATION.md) - Multi-tenant architecture
- [CI/CD Integration](MULTI_APP_EXTENSION.md) - Pipeline setup and scalability
- [Blueprint Engine](core/blueprints/COPILOT_BLUEPRINT_ENGINE.md) - Blueprint documentation
- [Validation Engine](core/validation/COPILOT_VALIDATION_ENGINE.md) - Validation rules
- [Agent System](core/agents/AGENTS_README.md) - Agent architecture

---

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

---

## 🙏 Acknowledgments

- Built with [Playwright](https://playwright.dev/) for UI automation
- Powered by [FastAPI](https://fastapi.tiangolo.com/) for API layer
- UI built with [Next.js](https://nextjs.org/) and [TailwindCSS](https://tailwindcss.com/)
- LLM integration via [Ollama](https://ollama.com/)

---

## 📞 Support

- 📧 Email: support@apex-ai platform.dev
- 💬 Discord: [Join our community](https://discord.gg/apex-ai)
- 📖 Docs: [docs.apex-ai-platform.dev](https://docs.apex-ai-platform.dev)
- 🐛 Issues: [GitHub Issues](https://github.com/YOUR_USERNAME/apex-ai-platform/issues)

---

**Built with ❤️ by the Apex AI Team**
