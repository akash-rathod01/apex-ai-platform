# Copilot Setup Guide — Apex AI Platform

This guide shows where to place all Copilot instruction files for optimal IDE integration.

---

## 📁 File Structure

```
apex-ai-platform/
│
├── .apex_copilot_instructions.md          # ← Main platform instructions (root)
├── COPILOT_SETUP_GUIDE.md                 # ← This guide
│
├── core/
│   ├── agents/
│   │   ├── AGENTS_README.md               # ← Master agent registry
│   │   ├── qa/
│   │   │   └── COPILOT_QA.md             # ← QA Agent instructions
│   │   ├── performance/
│   │   │   └── COPILOT_PERF.md           # ← Performance Agent instructions
│   │   ├── security/
│   │   │   └── COPILOT_SECURITY.md       # ← Security Agent instructions
│   │   ├── devops/
│   │   │   └── COPILOT_DEVOPS.md         # ← DevOps Agent instructions
│   │   └── docs/
│   │       └── COPILOT_DOCS.md           # ← Documentation Agent instructions
│   │
│   ├── blueprints/
│   │   └── COPILOT_BLUEPRINT_ENGINE.md   # ← Blueprint Engine instructions
│   │
│   ├── llm/
│   │   └── COPILOT_LLM_ADAPTER.md        # ← LLM Adapter Layer instructions
│   │
│   └── validation/
│       └── COPILOT_VALIDATION_ENGINE.md  # ← Validation Engine instructions
│
└── plugins/
    └── README_COPILOT_PLUGINS.md          # ← Plugin ecosystem instructions
```

---

## ✅ Installation Steps

### 1. **Main Platform Instructions** (Root)
Place this file at the root of your workspace so Copilot understands the overall platform architecture:

```
📄 .apex_copilot_instructions.md
   ↳ Platform identity, architectural rules, code generation guidelines
```

**When Copilot reads this:**
- Understands it's a TEST AUTOMATION platform (not CI/CD)
- Applies blueprint-first architecture rules
- Never stores permanent test scripts
- Uses deterministic validation only

---

### 2. **Agent Instructions** (Core Systems)
Place agent-specific instructions in their respective directories:

```
📂 core/agents/
   ├── AGENTS_README.md                   # Master registry (read first)
   ├── qa/COPILOT_QA.md                  # QA-specific rules
   ├── performance/COPILOT_PERF.md       # Performance-specific rules
   ├── security/COPILOT_SECURITY.md      # Security-specific rules
   ├── devops/COPILOT_DEVOPS.md          # DevOps-specific rules
   └── docs/COPILOT_DOCS.md              # Docs-specific rules
```

**When Copilot works in:**
- `core/agents/qa/` → Reads `COPILOT_QA.md` → Generates UI/API tests
- `core/agents/performance/` → Reads `COPILOT_PERF.md` → Generates load tests
- `core/agents/security/` → Reads `COPILOT_SECURITY.md` → Generates security scans

---

### 3. **Core Engine Instructions** (Critical Systems)
Place core system instructions in their respective directories:

```
📂 core/
   ├── blueprints/COPILOT_BLUEPRINT_ENGINE.md   # Blueprint parsing rules
   ├── llm/COPILOT_LLM_ADAPTER.md               # LLM integration rules
   └── validation/COPILOT_VALIDATION_ENGINE.md  # Validation rules
```

**When Copilot works in:**
- `core/blueprints/` → Reads blueprint rules → Generates parsers, validators, queries
- `core/llm/` → Reads LLM rules → Generates provider-agnostic adapters
- `core/validation/` → Reads validation rules → Generates deterministic validators

---

### 4. **Plugin Ecosystem Instructions**
Place plugin instructions at the plugin root:

```
📂 plugins/
   └── README_COPILOT_PLUGINS.md          # Plugin architecture rules
```

**When Copilot works in:**
- `plugins/qa/` → Reads plugin rules → Generates Playwright/Selenium adapters
- `plugins/performance/` → Reads plugin rules → Generates k6/JMeter adapters
- `plugins/security/` → Reads plugin rules → Generates ZAP/Nmap adapters

---

## 🎯 How Copilot Discovers These Files

### Automatic Discovery
Copilot automatically reads instruction files based on:

1. **Root-level files** (`.apex_copilot_instructions.md`) - Always loaded
2. **Current working directory** - Loads `COPILOT_*.md` files in current folder
3. **Parent directories** - Walks up to find relevant instruction files

### Manual References
You can reference instruction files explicitly:

```python
# In your code editor, add comment:
# See: core/agents/qa/COPILOT_QA.md for QA agent patterns

# Copilot will read the file and apply its rules
```

---

## 📋 Quick Verification Checklist

After placing all files, verify:

- [ ] `.apex_copilot_instructions.md` exists at workspace root
- [ ] `core/agents/AGENTS_README.md` exists
- [ ] All 5 agent-specific files exist (`COPILOT_QA.md`, etc.)
- [ ] All 3 core engine files exist (Blueprint, LLM, Validation)
- [ ] Plugin instructions exist (`README_COPILOT_PLUGINS.md`)
- [ ] All files are markdown (`.md`) format
- [ ] All files contain `# Copilot Instructions` header

---

## 🔍 Testing Copilot Integration

### Test 1: Platform Identity
Open any file and ask Copilot:
```
"What type of platform is this?"
```
**Expected:** "This is an AI-powered test automation platform, not a CI/CD system."

### Test 2: Blueprint Rules
In `core/blueprints/loader.py`, ask Copilot:
```
"Generate a blueprint loader function"
```
**Expected:** Generates YAML parser, NOT executable test code

### Test 3: Validation Rules
In `core/validation/api_validator.py`, ask Copilot:
```
"Generate an API response validator"
```
**Expected:** Generates deterministic schema validation, NO LLM calls

### Test 4: Agent Rules
In `core/agents/qa/test_generator.py`, ask Copilot:
```
"Generate a UI test from a blueprint"
```
**Expected:** Generates on-demand test, does NOT save to repository

---

## 🛠️ Troubleshooting

### Problem: Copilot Ignores Instructions
**Solution:**
1. Check file names match exactly (case-sensitive)
2. Ensure files are in correct directories
3. Verify markdown formatting is correct
4. Restart VS Code to reload instruction files

### Problem: Copilot Generates Wrong Code Patterns
**Solution:**
1. Check which instruction file applies to current directory
2. Verify instruction file has clear examples (✅ GOOD vs ❌ BAD)
3. Add more specific rules to relevant instruction file

### Problem: Copilot Uses LLMs for Validation
**Solution:**
1. Check `core/validation/COPILOT_VALIDATION_ENGINE.md` exists
2. Verify "NO AI/LLM in pass/fail decisions" rule is present
3. Add explicit forbid patterns in instruction file

---

## 📚 Instruction File Hierarchy

```
Priority: Root → Core Systems → Agents → Plugins

1. .apex_copilot_instructions.md         (Global rules - highest priority)
2. core/blueprints/COPILOT_*.md          (Core system rules)
3. core/llm/COPILOT_*.md                 (Core system rules)
4. core/validation/COPILOT_*.md          (Core system rules)
5. core/agents/AGENTS_README.md          (Agent-level rules)
6. core/agents/*/COPILOT_*.md            (Agent-specific rules)
7. plugins/README_COPILOT_PLUGINS.md     (Plugin-level rules)
```

**Rule Resolution:**
- More specific files override general files
- Agent-specific rules override global rules
- Core system rules always apply to their respective modules

---

## 🎓 Best Practices

### DO:
- ✅ Keep instruction files under 1,000 lines each
- ✅ Include code examples (GOOD vs BAD patterns)
- ✅ Use clear section headers (## ✅, ## ❌)
- ✅ Reference other instruction files for cross-system rules
- ✅ Update instruction files when architecture changes

### DON'T:
- ❌ Duplicate rules across multiple files
- ❌ Write vague instructions ("be careful", "use best practices")
- ❌ Include implementation code (only examples)
- ❌ Create deeply nested instruction hierarchies
- ❌ Forget to update references when moving files

---

## 🔄 Maintenance Schedule

### Monthly:
- Review generated code quality
- Update examples in instruction files
- Add new patterns discovered during development

### Quarterly:
- Audit all instruction files for consistency
- Remove outdated rules
- Consolidate duplicate instructions

### When Architecture Changes:
- Update all affected instruction files immediately
- Test Copilot with new patterns
- Add transition rules if breaking changes

---

## 🚀 Advanced: Custom Instruction Files

You can create additional instruction files per feature:

```
apps/app1/auth/COPILOT_AUTH.md           # Auth-specific rules
apps/app1/checkout/COPILOT_CHECKOUT.md   # Checkout-specific rules
```

**When to create custom files:**
- Feature has unique business rules
- Domain-specific validation logic
- Special security requirements
- Complex workflows needing guidance

---

## 📧 Support

If Copilot consistently generates incorrect code despite proper instruction files:

1. Check [Main Instructions](.apex_copilot_instructions.md) - Platform identity correct?
2. Check [Agent Instructions](core/agents/AGENTS_README.md) - Agent rules clear?
3. Check [Core Systems](core/) - Engine rules specific enough?
4. Test with explicit prompts: "Following COPILOT_QA.md rules, generate..."

---

**Last updated:** 2026-03-26  
**Platform:** Apex AI Testing Platform  
**Instruction Version:** 1.0.0
