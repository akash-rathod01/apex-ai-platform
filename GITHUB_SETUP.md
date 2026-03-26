# GitHub Repository Setup Guide

## 🚀 Quick Start

### 1. Check Git Status

```powershell
git status
```

You should see all new files ready to be committed.

### 2. Stage All Files

```powershell
git add .
```

### 3. Create Initial Commit

```powershell
git commit -m "Initial commit: Apex AI Platform setup

- Core Python dependencies installed (FastAPI, Playwright, pytest)
- Next.js web UI with TailwindCSS and ShadCN UI
- SQLite database manager with per-app isolation
- Multi-agent architecture documentation
- Blueprint and validation engine specifications
- Multi-application isolation architecture
- CI/CD integration guides
- Complete setup verification scripts"
```

---

## 🌐 Create GitHub Repository

### Option 1: Using GitHub CLI (Recommended)

```powershell
# Install GitHub CLI (if not already installed)
winget install GitHub.cli

# Login to GitHub
gh auth login

# Create new repository
gh repo create apex-ai-platform --public --description "Enterprise-grade, Multi-Agent AI-Powered Test Automation Platform"

# Set remote and push
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/apex-ai-platform.git
git push -u origin main
```

### Option 2: Using GitHub Web Interface

1. **Go to GitHub.com** and sign in

2. **Create New Repository:**
   - Click the `+` icon → "New repository"
   - Repository name: `apex-ai-platform`
   - Description: `Enterprise-grade, Multi-Agent AI-Powered Test Automation Platform`
   - Visibility: Public (or Private)
   - **DO NOT** initialize with README (we already have one)
   - Click "Create repository"

3. **Push Your Local Repository:**

```powershell
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/apex-ai-platform.git
git push -u origin main
```

---

## 📋 Repository Settings (Recommended)

### 1. Add Repository Topics

Go to repository → Settings → About → Add topics:
```
test-automation
python
playwright
multi-agent-system
ai-testing
nextjs
fastapi
test-intelligence
ci-cd
enterprise
```

### 2. Enable Discussions

Settings → Features → Check "Discussions"

### 3. Set Up Branch Protection

Settings → Branches → Add rule for `main`:
- ✅ Require pull request reviews before merging
- ✅ Require status checks to pass (after setting up CI/CD)
- ✅ Require branches to be up to date

### 4. Add GitHub Actions Secrets

Settings → Secrets and variables → Actions → New repository secret:
```
OPENAI_API_KEY (if using OpenAI)
ANTHROPIC_API_KEY (if using Anthropic)
SLACK_WEBHOOK_URL (for notifications)
```

---

## 🔄 Regular Git Workflow

### Daily Development

```powershell
# Pull latest changes
git pull origin main

# Create feature branch
git checkout -b feature/add-qa-agent

# Make changes, then:
git add .
git commit -m "feat: implement QA agent with Playwright integration"

# Push to GitHub
git push origin feature/add-qa-agent

# Create Pull Request on GitHub
# After review and approval, merge to main
```

### Commit Message Conventions

Use conventional commits:
```
feat: Add new feature
fix: Bug fix
docs: Documentation changes
test: Add or update tests
refactor: Code refactoring
perf: Performance improvements
ci: CI/CD changes
chore: Maintenance tasks
```

Examples:
```powershell
git commit -m "feat(agents): add QA agent with Playwright support"
git commit -m "fix(validation): resolve baseline comparison bug"
git commit -m "docs: update multi-app isolation guide"
git commit -m "test: add unit tests for validation engine"
```

---

## 📁 Files That Should NOT Be in Git

Already configured in `.gitignore`:

- ✅ `core/memory/*.db` - Per-app databases (LARGE)
- ✅ `apps/*/snapshots/**/*.png` - Screenshot baselines (LARGE)
- ✅ `apps/*/logs/**/*.log` - Execution logs (LARGE)
- ✅ `.env` - Environment variables (SECRETS)
- ✅ `node_modules/` - Node dependencies
- ✅ `__pycache__/` - Python cache
- ✅ `.next/` - Next.js build artifacts

Keep these in Git:
- ✅ `.env.example` - Template for environment variables
- ✅ `requirements.txt` - Python dependencies list
- ✅ `package.json` - Node dependencies list
- ✅ Documentation files (`*.md`)
- ✅ Configuration templates

---

## 🏷️ Tagging Releases

```powershell
# Create version tag
git tag -a v1.0.0 -m "Release v1.0.0: Initial platform launch"

# Push tags to GitHub
git push origin --tags
```

---

## 🌿 Branching Strategy

```
main (production-ready)
  ↑
  └─ develop (integration branch)
      ↑
      ├─ feature/qa-agent
      ├─ feature/perf-agent
      ├─ feature/security-agent
      └─ bugfix/validation-engine
```

### Create Develop Branch

```powershell
git checkout -b develop
git push -u origin develop
```

---

## 📊 View Repository Stats

```powershell
# View commit history
git log --oneline --graph --all

# View file changes
git diff

# View file history
git log --follow core/validation/engine.py

# View contributors
git shortlog -sn
```

---

## 🆘 Common Issues

### Issue: "Remote origin already exists"

```powershell
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/apex-ai-platform.git
```

### Issue: "Failed to push - rejected"

```powershell
git pull origin main --rebase
git push origin main
```

### Issue: "Accidentally committed .env file"

```powershell
# Remove from Git but keep local file
git rm --cached .env

# Commit the removal
git commit -m "chore: remove .env from version control"

# Push
git push origin main
```

---

## ✅ Verification Checklist

After pushing to GitHub, verify:

- [ ] Repository is visible on GitHub
- [ ] README.md is displaying correctly
- [ ] All necessary files are present
- [ ] `.gitignore` is working (no large files/secrets)
- [ ] GitHub Actions can be set up (optional)
- [ ] Repository topics are added
- [ ] License file is included (if open source)

---

## 🎉 Your Repository is Ready!

Repository URL will be:
```
https://github.com/YOUR_USERNAME/apex-ai-platform
```

Share it with:
- ✅ Team members (for collaboration)
- ✅ Community (if open source)
- ✅ CI/CD systems (for automation)
- ✅ Documentation sites (for integration)
