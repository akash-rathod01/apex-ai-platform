# Copilot Instructions — DevOps Agent

## ✅ Purpose
Handles **CI integrations, environment orchestration, configuration validation**, not deployments.

---

## ✅ Responsibilities

### Core Functions
- **Integrate with CI/CD platforms** (GitHub Actions, Jenkins, GitLab, Azure DevOps)
- **Trigger appropriate testing flows** based on events
- **Validate environment health** before test execution
- **Validate infrastructure configuration** (Terraform plan checks, not apply)
- **Manage test runner clusters** (Kubernetes, Docker)
- **Produce CI annotations + PR comments** with test results
- **Coordinate multi-environment testing** (dev, qa, staging)

### Key Activities
- CI/CD webhook handling
- Environment provisioning for tests
- Configuration validation
- Test result reporting
- PR/commit status updates
- Build artifact validation
- Container orchestration for test runners

---

## ✅ What NOT to do

### ❌ FORBIDDEN Actions
- ❌ Do NOT deploy applications to production
- ❌ Do NOT destroy infrastructure
- ❌ Do NOT edit customer infrastructure directly
- ❌ Do NOT apply Terraform changes (only validate/plan)
- ❌ Do NOT make pass/fail decisions (validation engine decides)
- ❌ Do NOT store deployment scripts
- ❌ Do NOT execute kubectl delete or destructive commands
- ❌ Do NOT hardcode CI/CD configurations

---

## ✅ What Copilot Should Generate

### Modular Components
```python
# ✅ GOOD: CI integration adapters
class CIAdapter:
    def handle_webhook(self, event: WebhookEvent) -> TestTrigger:
        """Process CI webhook and trigger appropriate tests"""
        pass
    
    def post_status(self, commit: str, status: TestStatus) -> None:
        """Post test status to CI platform"""
        pass
    
    def create_pr_comment(self, results: TestResults) -> str:
        """Generate PR comment with test results"""
        pass
```

### Generate These Types of Code
- ✅ CI platform adapters (GitHub, GitLab, Jenkins, Azure DevOps)
- ✅ Environment health checkers
- ✅ PR comment builders
- ✅ Secrets loader wrappers
- ✅ Safe environment config validators
- ✅ Container orchestration helpers
- ✅ Test runner provisioners
- ✅ Build artifact validators
- ✅ Webhook handlers

---

## ✅ What Copilot Should NOT Generate

### ❌ AVOID These Patterns
```python
# ❌ BAD: Deployment operations
def deploy_to_production():
    kubectl.apply("deployment.yaml")  # DON'T
    terraform.apply()  # DON'T
    
# ❌ BAD: Destructive operations
def cleanup_environment():
    kubectl.delete("namespace", "prod")  # DON'T
    terraform.destroy()  # DON'T

# ❌ BAD: Hardcoded credentials
GITHUB_TOKEN = "ghp_xxxx"  # DON'T
AWS_KEY = "AKIA..."  # DON'T
```

---

## ✅ Tools Used

### Plugin-Based Tool Access
```python
# ✅ CORRECT: Load via plugin system
github_cli = self.plugins.load("github-cli")
jenkins = self.plugins.load("jenkins-client")
terraform = self.plugins.load("terraform")
kubectl = self.plugins.load("kubectl")
docker = self.plugins.load("docker")

# ❌ INCORRECT: Direct execution
import subprocess
subprocess.run(["kubectl", "apply", "-f", "deploy.yaml"])  # DON'T
```

### Primary Tools
- **GitHub CLI** (via plugin) - GitHub integration
- **Jenkins Client** (via plugin) - Jenkins integration
- **GitLab API** (via plugin) - GitLab integration
- **Terraform** (via plugin) - Infrastructure validation only (plan, not apply)
- **Kubectl** (via plugin) - Kubernetes test environment management
- **Docker** (via plugin) - Container management for test runners
- **Azure CLI** (via plugin) - Azure DevOps integration

---

## ✅ Blueprint-First Architecture

### Reading DevOps Blueprints
```yaml
# devops_pr_validation.blueprint.yaml
blueprint_id: "devops_pr_001"
type: devops
ci_platform: github_actions

triggers:
  - event: pull_request
    branches: [main, develop]
    actions: [opened, synchronize, reopened]

environment_requirements:
  - name: test_database
    type: postgres
    version: "14"
  - name: redis_cache
    type: redis
    version: "7"

test_flows:
  - name: unit_tests
    agent: qa
    environment: ephemeral
  - name: integration_tests
    agent: qa
    environment: shared_qa
  - name: security_scan
    agent: security
    environment: shared_qa

pr_comment_template: |
  ## Test Results
  {{test_summary}}
  
  ### Details
  {{detailed_results}}
  
  {{security_findings}}

health_checks:
  - endpoint: "${BASE_URL}/health"
    expected_status: 200
    timeout: 5
  - endpoint: "${BASE_URL}/ready"
    expected_status: 200
    timeout: 10
```

### Blueprint-Driven Execution
```python
# ✅ CORRECT: Blueprint-driven CI integration
blueprint = self.blueprint_loader.load("devops_pr_001")

# Handle webhook event
webhook_event = self.parse_webhook(request)

# Check if event matches blueprint triggers
if self.matches_trigger(webhook_event, blueprint.triggers):
    # Validate environment health
    health_status = self.check_environment_health(
        blueprint.health_checks
    )
    
    if not health_status.healthy:
        self.post_status(webhook_event.commit, "PENDING")
        self.provision_environment(blueprint.environment_requirements)
    
    # Trigger test flows via runtime
    results = []
    for flow in blueprint.test_flows:
        result = self.runtime.invoke_agent(
            agent=flow.agent,
            context={
                "blueprint_id": flow.name,
                "environment": flow.environment,
                "commit": webhook_event.commit
            }
        )
        results.append(result)
    
    # Post results to PR
    comment = self.generate_comment(results, blueprint.pr_comment_template)
    github = self.plugins.load("github-cli")
    github.create_comment(webhook_event.pr_number, comment)
    
    # Update commit status
    self.post_status(
        webhook_event.commit,
        "SUCCESS" if all(r.passed for r in results) else "FAILURE"
    )
```

---

## ✅ CI Platform Integration

### GitHub Actions Integration
```python
class GitHubActionsAdapter:
    def handle_webhook(self, event: dict) -> WebhookEvent:
        """Process GitHub webhook"""
        return WebhookEvent(
            platform="github",
            event_type=event["action"],
            pr_number=event["pull_request"]["number"],
            commit=event["pull_request"]["head"]["sha"],
            branch=event["pull_request"]["head"]["ref"],
            author=event["pull_request"]["user"]["login"]
        )
    
    def post_status(self, commit: str, status: str, context: str = "apex-tests"):
        """Post commit status"""
        github = self.plugins.load("github-cli")
        
        github.create_status(
            commit=commit,
            state=status.lower(),  # pending, success, failure
            context=context,
            description=f"Apex AI Platform: {status}",
            target_url=self.get_results_url(commit)
        )
    
    def create_pr_comment(self, pr_number: int, comment: str):
        """Create PR comment with results"""
        github = self.plugins.load("github-cli")
        github.create_comment(pr_number, comment)
```

### Jenkins Integration
```python
class JenkinsAdapter:
    def trigger_job(self, job_name: str, parameters: dict):
        """Trigger Jenkins job"""
        jenkins = self.plugins.load("jenkins-client")
        
        build_number = jenkins.trigger_build(
            job_name=job_name,
            parameters=parameters
        )
        
        return build_number
    
    def get_build_status(self, job_name: str, build_number: int):
        """Get build status"""
        jenkins = self.plugins.load("jenkins-client")
        return jenkins.get_build_info(job_name, build_number)
```

---

## ✅ Environment Health Validation

### Health Check Implementation
```python
class EnvironmentHealthChecker:
    def check_health(self, health_checks: List[HealthCheck]) -> HealthStatus:
        """Validate environment is ready for testing"""
        
        results = []
        
        for check in health_checks:
            try:
                response = requests.get(
                    check.endpoint,
                    timeout=check.timeout
                )
                
                passed = response.status_code == check.expected_status
                
                results.append(HealthCheckResult(
                    endpoint=check.endpoint,
                    passed=passed,
                    status_code=response.status_code,
                    response_time=response.elapsed.total_seconds()
                ))
            except Exception as e:
                results.append(HealthCheckResult(
                    endpoint=check.endpoint,
                    passed=False,
                    error=str(e)
                ))
        
        return HealthStatus(
            healthy=all(r.passed for r in results),
            checks=results
        )
```

---

## ✅ Configuration Validation

### Terraform Plan Validation (No Apply!)
```python
class TerraformValidator:
    def validate_configuration(self, config_path: str) -> ValidationResult:
        """Validate Terraform configuration - NO APPLY!"""
        terraform = self.plugins.load("terraform")
        
        # ✅ SAFE: Init and validate
        terraform.init(config_path)
        validation = terraform.validate(config_path)
        
        if not validation.valid:
            return ValidationResult(
                valid=False,
                errors=validation.errors
            )
        
        # ✅ SAFE: Plan only (no apply)
        plan = terraform.plan(config_path)
        
        return ValidationResult(
            valid=True,
            plan_summary=plan.summary,
            changes=plan.changes
        )
    
    def apply_configuration(self, config_path: str):
        """❌ FORBIDDEN - Do not implement"""
        raise NotImplementedError(
            "Terraform apply is forbidden. "
            "This agent only validates configurations."
        )
```

---

## ✅ PR Comment Generation

### Generate Formatted Test Results
```python
class PRCommentGenerator:
    def generate_comment(
        self,
        test_results: List[TestResult],
        template: str
    ) -> str:
        """Generate formatted PR comment"""
        
        # Aggregate results
        total = len(test_results)
        passed = sum(1 for r in test_results if r.status == "PASS")
        failed = sum(1 for r in test_results if r.status == "FAIL")
        
        # Generate summary
        summary = f"✅ {passed} passed, ❌ {failed} failed ({total} total)"
        
        # Generate details table
        details = "| Test | Status | Duration | Details |\n"
        details += "|------|--------|----------|----------|\n"
        
        for result in test_results:
            emoji = "✅" if result.status == "PASS" else "❌"
            details += f"| {result.name} | {emoji} {result.status} | {result.duration}s | [View]({result.url}) |\n"
        
        # Find security findings
        security_findings = ""
        security_results = [r for r in test_results if r.agent == "security"]
        if security_results:
            for sr in security_results:
                if sr.vulnerabilities:
                    security_findings += "### 🔒 Security Findings\n\n"
                    for vuln in sr.vulnerabilities:
                        security_findings += f"- **{vuln.severity}**: {vuln.type} in {vuln.location}\n"
        
        # Render template
        comment = template.format(
            test_summary=summary,
            detailed_results=details,
            security_findings=security_findings
        )
        
        return comment
```

---

## ✅ Container Orchestration for Test Runners

### Kubernetes-Based Test Runner Management
```python
class TestRunnerOrchestrator:
    def provision_test_environment(
        self,
        requirements: List[EnvironmentRequirement]
    ) -> Environment:
        """Provision ephemeral test environment"""
        kubectl = self.plugins.load("kubectl")
        
        namespace = f"test-{uuid.uuid4().hex[:8]}"
        
        # Create namespace
        kubectl.create_namespace(namespace)
        
        # Deploy required services
        for req in requirements:
            if req.type == "postgres":
                kubectl.apply(
                    namespace=namespace,
                    manifest=self._generate_postgres_manifest(req)
                )
            elif req.type == "redis":
                kubectl.apply(
                    namespace=namespace,
                    manifest=self._generate_redis_manifest(req)
                )
        
        # Wait for readiness
        kubectl.wait_for_ready(namespace, timeout=120)
        
        return Environment(
            namespace=namespace,
            services=requirements,
            cleanup_callback=lambda: kubectl.delete_namespace(namespace)
        )
```

---

## ✅ Secrets Management

### Safe Secrets Loading
```python
class SecretsLoader:
    def load_secrets(self, blueprint: Blueprint) -> dict:
        """Load secrets from secure storage"""
        
        secrets = {}
        
        for secret_ref in blueprint.required_secrets:
            # Load from environment-specific secret store
            if self.platform == "github":
                github = self.plugins.load("github-cli")
                value = github.get_secret(secret_ref)
            elif self.platform == "jenkins":
                jenkins = self.plugins.load("jenkins-client")
                value = jenkins.get_credential(secret_ref)
            
            secrets[secret_ref] = value
        
        return secrets
    
    def _never_log_secrets(self, data: dict) -> dict:
        """Redact secrets from logs"""
        redacted = data.copy()
        secret_keys = ["password", "token", "key", "secret", "credential"]
        
        for key in redacted:
            if any(sk in key.lower() for sk in secret_keys):
                redacted[key] = "***REDACTED***"
        
        return redacted
```

---

## ✅ Code Generation Examples

### ✅ GOOD: Modular, Safe
```python
class DevOpsAgent(BaseAgent):
    def __init__(self, runtime, llm_adapter, plugin_loader):
        super().__init__(runtime, llm_adapter, plugin_loader)
        self.github_adapter = GitHubActionsAdapter(plugin_loader)
        self.health_checker = EnvironmentHealthChecker()
        self.orchestrator = TestRunnerOrchestrator(plugin_loader)
    
    def handle_pr_event(self, webhook_event: dict) -> None:
        # Load blueprint
        blueprint = self.blueprint_loader.load_for_event(webhook_event)
        
        # Parse event
        event = self.github_adapter.handle_webhook(webhook_event)
        
        # Post pending status
        self.github_adapter.post_status(event.commit, "PENDING")
        
        # Check environment health
        health = self.health_checker.check_health(blueprint.health_checks)
        
        if not health.healthy:
            # Provision fresh environment
            env = self.orchestrator.provision_test_environment(
                blueprint.environment_requirements
            )
        
        # Trigger tests via runtime
        test_results = []
        for flow in blueprint.test_flows:
            result = self.runtime.invoke_agent(
                agent=flow.agent,
                context={
                    "blueprint_id": flow.name,
                    "commit": event.commit,
                    "pr_number": event.pr_number
                }
            )
            test_results.append(result)
        
        # Generate and post PR comment
        comment = self.generate_pr_comment(test_results, blueprint)
        self.github_adapter.create_pr_comment(event.pr_number, comment)
        
        # Update status
        final_status = "SUCCESS" if all(r.passed for r in test_results) else "FAILURE"
        self.github_adapter.post_status(event.commit, final_status)
```

---

## ✅ File Structure

```
core/agents/devops/
├── __init__.py
├── agent.py                     # Main DevOps agent
├── COPILOT_DEVOPS.md           # This file
├── config.py
├── adapters/
│   ├── github_adapter.py       # GitHub Actions integration
│   ├── jenkins_adapter.py      # Jenkins integration
│   ├── gitlab_adapter.py       # GitLab integration
│   └── azure_devops_adapter.py # Azure DevOps integration
├── orchestration/
│   ├── k8s_orchestrator.py     # Kubernetes test environment
│   └── docker_orchestrator.py  # Docker test environment
├── validators/
│   ├── health_checker.py       # Environment health validation
│   └── config_validator.py     # Terraform/config validation
├── utils/
│   ├── pr_comment_generator.py
│   └── secrets_loader.py
└── tests/
    └── test_devops_agent.py
```

---

## ✅ Checklist for DevOps Agent Code

- [ ] Extends `BaseAgent` class
- [ ] Loads DevOps blueprints
- [ ] Integrates with CI platforms safely
- [ ] Validates environment health
- [ ] Uses plugin loader for tools
- [ ] NO deployment or destructive operations
- [ ] Terraform plan only (no apply)
- [ ] Generates PR comments
- [ ] Posts commit statuses
- [ ] Manages test environments
- [ ] Handles secrets securely
- [ ] Communicates via runtime
- [ ] Is modular (< 500 lines per file)

---

## 🎯 Remember

> **Validate, don't deploy.**  
> **Provision test environments, don't touch production.**  
> **Terraform plan, never apply.**

---

*Last updated: 2026-03-26*
