# Test Intelligence & Memory Architecture

## 🧠 Overview

The Apex AI Platform's Test Intelligence Brain provides:
- **Historical analysis** - Learn from past test executions
- **Flakiness detection** - Identify unreliable tests
- **Risk scoring** - Predict test failure probability
- **Auto-healing patterns** - Learn selector changes
- **Performance baselines** - Detect regressions
- **Test selection** - Choose optimal test subset

**Critical:** All intelligence is **per-application** with complete isolation.

---

## 📊 Memory Isolation Architecture

### Memory Database Structure
```
core/memory/
   app1_memory.db           # Application 1 intelligence
   app2_memory.db           # Application 2 intelligence
   app3_memory.db           # Application 3 intelligence
```

**Each database is completely isolated:**
- ✅ No shared tables
- ✅ No cross-references
- ✅ No joins between apps
- ❌ No global memory
- ❌ No shared intelligence

---

## 🎯 What's Stored Per App

### 1. Historical Test Results
```python
{
  "app_id": "app1",
  "blueprint_id": "LOGIN_001",
  "execution_count": 1523,
  "pass_count": 1511,
  "fail_count": 12,
  "average_duration_ms": 2300,
  "last_execution": "2026-03-26T14:30:00Z"
}
```

### 2. Flakiness Scores
```python
{
  "app_id": "app1",
  "blueprint_id": "CHECKOUT_001",
  "flakiness_score": 0.15,    # 15% flaky
  "pattern": "network_timeout",
  "recommended_retries": 2
}
```

### 3. Risk Scores
```python
{
  "app_id": "app1",
  "blueprint_id": "PAYMENT_PROCESS",
  "risk_score": 0.85,          # High probability of failure
  "priority": "critical",
  "impact": "high"
}
```

### 4. Auto-Healing History
```python
{
  "app_id": "app1",
  "blueprint_id": "LOGIN_001",
  "healing_events": [
    {
      "date": "2026-03-20",
      "type": "selector_change",
      "old_value": "#login-btn",
      "new_value": "#btn-login",
      "confidence": 0.95
    }
  ]
}
```

### 5. Performance Baselines
```python
{
  "app_id": "app1",
  "blueprint_id": "API_GET_USER",
  "p50_ms": 150,
  "p95_ms": 450,
  "p99_ms": 800,
  "established_date": "2026-03-01"
}
```

---

## 🔧 Test Intelligence Brain Interface

```python
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

@dataclass
class TestIntelligence:
    """Intelligence data for a test"""
    app_id: str
    blueprint_id: str
    flakiness_score: float      # 0.0 - 1.0
    risk_score: float           # 0.0 - 1.0
    execution_count: int
    failure_count: int
    average_duration_ms: float
    last_failure: Optional[str]
    healing_suggestions: List[dict]

class TestIntelligenceBrain:
    """Per-application test intelligence"""
    
    def __init__(self, context: ProjectContext):
        # Load app-specific memory database
        self.memory = VectorMemory(context.memory_path)
        self.app_id = context.app_id
        self.context = context
    
    def get_intelligence(self, blueprint_id: str) -> TestIntelligence:
        """Get intelligence for a specific test in THIS app"""
        data = self.memory.get(f"{self.app_id}:{blueprint_id}")
        return TestIntelligence(**data) if data else self._default_intelligence(blueprint_id)
    
    def mark_execution(
        self, 
        blueprint_id: str, 
        status: str, 
        duration_ms: float
    ):
        """Record test execution for THIS app"""
        key = f"{self.app_id}:{blueprint_id}:history"
        
        # Load existing history
        history = self.memory.get(key) or {
            "app_id": self.app_id,
            "blueprint_id": blueprint_id,
            "executions": []
        }
        
        # Append new execution
        history["executions"].append({
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "duration_ms": duration_ms
        })
        
        # Calculate updated metrics
        total = len(history["executions"])
        failures = sum(1 for e in history["executions"] if e["status"] == "fail")
        
        # Update intelligence
        self.memory.store(f"{self.app_id}:{blueprint_id}", {
            "app_id": self.app_id,
            "blueprint_id": blueprint_id,
            "execution_count": total,
            "failure_count": failures,
            "flakiness_score": failures / total if total > 0 else 0.0,
            "last_execution": datetime.now().isoformat()
        })
    
    def get_flaky_tests(self, threshold: float = 0.1) -> List[str]:
        """Get tests with flakiness above threshold for THIS app"""
        results = self.memory.query(
            field="flakiness_score",
            condition=">=",
            value=threshold,
            filter_app_id=self.app_id  # Only this app!
        )
        return [r["blueprint_id"] for r in results]
    
    def get_high_risk_tests(self, threshold: float = 0.7) -> List[str]:
        """Get high-risk tests for THIS app"""
        results = self.memory.query(
            field="risk_score",
            condition=">=",
            value=threshold,
            filter_app_id=self.app_id  # Only this app!
        )
        return [r["blueprint_id"] for r in results]
    
    def suggest_test_subset(
        self,
        max_tests: int,
        prioritize: str = "coverage"  # or "risk" or "flakiness"
    ) -> List[str]:
        """Suggest optimal test subset for THIS app"""
        # Load all test intelligence for this app
        all_tests = self.memory.query(filter_app_id=self.app_id)
        
        if prioritize == "risk":
            # Sort by risk score (high to low)
            sorted_tests = sorted(
                all_tests, 
                key=lambda t: t["risk_score"], 
                reverse=True
            )
        elif prioritize == "flakiness":
            # Sort by flakiness (low to high - prefer stable)
            sorted_tests = sorted(
                all_tests, 
                key=lambda t: t["flakiness_score"]
            )
        else:  # coverage
            # TODO: Implement coverage-based selection
            sorted_tests = all_tests
        
        return [t["blueprint_id"] for t in sorted_tests[:max_tests]]
    
    def learn_healing_pattern(
        self,
        blueprint_id: str,
        old_selector: str,
        new_selector: str,
        confidence: float
    ):
        """Store auto-healing pattern for THIS app"""
        key = f"{self.app_id}:{blueprint_id}:healing"
        
        healing_data = self.memory.get(key) or {
            "app_id": self.app_id,
            "blueprint_id": blueprint_id,
            "patterns": []
        }
        
        healing_data["patterns"].append({
            "timestamp": datetime.now().isoformat(),
            "old_selector": old_selector,
            "new_selector": new_selector,
            "confidence": confidence
        })
        
        self.memory.store(key, healing_data)
    
    def update_baseline(
        self,
        blueprint_id: str,
        metric_name: str,
        value: float
    ):
        """Update performance baseline for THIS app"""
        key = f"{self.app_id}:{blueprint_id}:baseline"
        
        baseline = self.memory.get(key) or {
            "app_id": self.app_id,
            "blueprint_id": blueprint_id,
            "metrics": {}
        }
        
        baseline["metrics"][metric_name] = {
            "value": value,
            "updated_at": datetime.now().isoformat()
        }
        
        self.memory.store(key, baseline)
```

---

## 🔄 Usage in Agents

### QA Agent with Intelligence
```python
class QAAgent(BaseAgent):
    def execute_test(
        self, 
        blueprint: Blueprint, 
        context: ProjectContext
    ) -> TestResult:
        # Initialize intelligence brain for THIS app
        intelligence = TestIntelligenceBrain(context)
        
        # Check if test is flaky
        intel = intelligence.get_intelligence(blueprint.id)
        
        if intel.flakiness_score > 0.1:
            logger.warning(
                f"Test {blueprint.id} is flaky ({intel.flakiness_score:.2%})"
            )
            max_retries = 3  # Retry flaky tests
        else:
            max_retries = 1
        
        # Execute test with retries
        for attempt in range(max_retries):
            start = time.time()
            result = self._execute(blueprint, context)
            duration = (time.time() - start) * 1000
            
            # Record execution
            intelligence.mark_execution(
                blueprint.id,
                result.status,
                duration
            )
            
            if result.status == "pass":
                break
        
        return result
```

### Performance Agent with Baselines
```python
class PerformanceAgent(BaseAgent):
    def execute_load_test(
        self,
        blueprint: Blueprint,
        context: ProjectContext
    ) -> PerformanceResult:
        # Initialize intelligence for THIS app
        intelligence = TestIntelligenceBrain(context)
        
        # Get baseline
        intel = intelligence.get_intelligence(blueprint.id)
        baseline_p95 = intel.performance_baseline.get("p95_ms", 0)
        
        # Execute load test
        metrics = self._execute_load_test(blueprint, context)
        
        # Detect regression
        if baseline_p95 > 0:
            if metrics.p95_ms > baseline_p95 * 1.2:  # 20% slower
                logger.error(
                    f"Performance regression detected: "
                    f"{metrics.p95_ms}ms vs baseline {baseline_p95}ms"
                )
        
        # Update baseline if improved
        if metrics.p95_ms < baseline_p95 or baseline_p95 == 0:
            intelligence.update_baseline(
                blueprint.id,
                "p95_ms",
                metrics.p95_ms
            )
        
        return metrics
```

---

## 🎯 Benefits of Per-App Intelligence

### 1. Accurate Insights
- App1's flaky tests don't affect app2's metrics
- Risk scores are app-specific
- Each app learns independently

### 2. Optimized Test Selection
- Select tests based on app-specific risk
- Prioritize unstable tests for app1
- Skip flaky tests for app2 (if stable)

### 3. Targeted Auto-Healing
- Learn selector changes per app
- App1's healing patterns don't apply to app2
- No false positives from cross-app contamination

### 4. Performance Baselines
- Each app has its own performance profile
- Fast app vs slow app - different baselines
- Accurate regression detection per app

---

## ✅ Memory Code Generation Rules

**ALWAYS:**
- Use `context.memory_path` to load memory
- Filter by `app_id` in all queries
- Store `app_id` with all intelligence data
- Scope intelligence brain to `ProjectContext`

**NEVER:**
- Use global memory path (`/core/memory/shared.db`)
- Query across apps
- Mix intelligence from multiple apps
- Share flakiness/risk data between apps

---

**Last Updated:** 2026-03-26  
**Platform:** Apex AI Testing Platform  
**Version:** 2.0.0 (Per-App Intelligence)
