# Copilot Instructions — Performance Agent

## ✅ Purpose
Responsible for **load, stress, endurance, and scalability testing** using plugins (JMeter/k6/Locust).

---

## ✅ Responsibilities

### Core Functions
- **Generate performance test plans dynamically** from Blueprints (never hardcode)
- **Select appropriate load model** based on test objectives
- **Interpret performance SLAs** and baseline metrics
- **Compare test runs** with historical baselines
- **Detect performance regressions** automatically
- **Analyze resource utilization** (CPU, memory, network, disk)

### Load Testing Models
```python
class LoadModel(Enum):
    SMOKE = "smoke_load"          # Minimal load verification
    AVERAGE = "average_load"      # Expected normal traffic
    STRESS = "stress_load"        # Beyond normal capacity
    SPIKE = "spike_load"          # Sudden traffic increase
    ENDURANCE = "endurance_load"  # Sustained load over time
    SCALABILITY = "scalability"   # Incremental load increase
```

---

## ✅ What NOT to do

### ❌ FORBIDDEN Actions
- ❌ No embedding of JMeter XML inside code
- ❌ No permanent test scripts storage
- ❌ No tool-specific logic hardcoded
- ❌ No making pass/fail decisions (validation engine decides)
- ❌ No running tests without blueprint context
- ❌ No direct LLM calls (use adapter)
- ❌ No hardcoded SLA thresholds
- ❌ No executing performance tests in production (unless explicitly configured)

---

## ✅ What Copilot Should Generate

### Modular Components
```python
# ✅ GOOD: Performance plan generators
class PerformanceTestPlanner:
    def create_load_plan(self, blueprint: Blueprint) -> LoadPlan:
        """Generate load test plan from blueprint"""
        pass
    
    def select_load_model(self, objectives: List[str]) -> LoadModel:
        """Choose appropriate load model"""
        pass
    
    def calculate_load_parameters(self, sla: SLA, model: LoadModel) -> LoadParams:
        """Calculate VUs, duration, ramp-up from SLA"""
        pass
```

### Generate These Types of Code
- ✅ Performance-plan JSON structures
- ✅ Helpers to invoke plugins (k6, JMeter, Locust)
- ✅ Metrics parsers and aggregators
- ✅ Baseline comparison logic
- ✅ Trend analysis logic
- ✅ Resource utilization monitors
- ✅ SLA validators
- ✅ Regression detectors
- ✅ Report generators

---

## ✅ What Copilot Should NOT Generate

### ❌ AVOID These Patterns
```python
# ❌ BAD: Hardcoded JMeter XML
jmeter_xml = """
<jmeterTestPlan version="1.2">
  <hashTree>
    <!-- 500 lines of XML -->
  </hashTree>
</jmeterTestPlan>
"""  # DON'T DO THIS

# ❌ BAD: Hardcoded thresholds
if response_time > 2000:  # Hardcoded threshold
    return "FAIL"

# ❌ BAD: Permanent script storage
with open("load_test.js", "w") as f:
    f.write(k6_script)  # Don't store
```

---

## ✅ Tools Used

### Plugin-Based Tool Access
```python
# ✅ CORRECT: Load via plugin system
k6 = self.plugins.load("k6", version="0.48.0")
jmeter = self.plugins.load("jmeter", version="5.6")
locust = self.plugins.load("locust", version="2.15.0")
prometheus = self.plugins.load("prometheus")

# ❌ INCORRECT: Direct execution
import subprocess
subprocess.run(["k6", "run", "script.js"])  # DON'T
```

### Primary Tools
- **k6** (via plugin) - Modern load testing, JavaScript-based
- **JMeter** (via plugin) - Enterprise-grade, Java-based
- **Locust** (via plugin) - Python-based, distributed testing
- **Prometheus** (via plugin) - Metrics collection
- **Grafana** (via plugin) - Metrics visualization

---

## ✅ Blueprint-First Architecture

### Reading Performance Blueprints
```yaml
# performance_checkout.blueprint.yaml
blueprint_id: "perf_checkout_001"
type: performance
load_model: stress
target:
  endpoint: "${BASE_URL}/api/checkout"
  method: POST
sla:
  response_time_p95: 500  # ms
  response_time_p99: 1000
  error_rate_max: 0.01    # 1%
  throughput_min: 1000    # req/sec
load_profile:
  virtual_users: 500
  duration: 300           # seconds
  ramp_up: 60             # seconds
scenarios:
  - name: "standard_checkout"
    weight: 80
    steps:
      - request: POST /api/cart/add
      - request: POST /api/checkout
  - name: "guest_checkout"
    weight: 20
    steps:
      - request: POST /api/checkout/guest
```

### Blueprint-Driven Execution
```python
# ✅ CORRECT: Blueprint-driven
blueprint = self.blueprint_loader.load("perf_checkout_001")
load_plan = self.planner.create_load_plan(blueprint)
test_script = self.generator.generate_from_plan(load_plan)

# Execute via plugin
k6_plugin = self.plugins.load("k6")
metrics = k6_plugin.execute(test_script)

# Validate against SLA
result = self.validation_engine.validate(
    metrics=metrics,
    sla=blueprint.sla,
    baseline=historical_baseline
)
```

---

## ✅ Performance Metrics Collection

### Comprehensive Metrics
```python
@dataclass
class PerformanceMetrics:
    # Response Time Metrics
    response_time_avg: float
    response_time_min: float
    response_time_max: float
    response_time_p50: float  # Median
    response_time_p95: float
    response_time_p99: float
    
    # Throughput Metrics
    requests_per_second: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    
    # Error Metrics
    error_rate: float
    error_types: Dict[str, int]
    
    # Resource Metrics
    cpu_usage_avg: float
    memory_usage_avg: float
    network_io: float
    
    # Timing Breakdown
    dns_lookup_time: float
    tcp_connect_time: float
    tls_handshake_time: float
    time_to_first_byte: float
    content_transfer_time: float
```

---

## ✅ Load Model Selection

### Choose Model Based on Objectives
```python
class PerformanceAgent(BaseAgent):
    def select_load_model(self, blueprint: Blueprint) -> LoadModel:
        """Select appropriate load model from blueprint objectives"""
        
        objectives = blueprint.objectives
        
        if "verify_basic_function" in objectives:
            return LoadModel.SMOKE
        
        elif "find_breaking_point" in objectives:
            return LoadModel.STRESS
        
        elif "simulate_traffic_spike" in objectives:
            return LoadModel.SPIKE
        
        elif "test_stability_over_time" in objectives:
            return LoadModel.ENDURANCE
        
        elif "determine_capacity" in objectives:
            return LoadModel.SCALABILITY
        
        else:
            return LoadModel.AVERAGE
    
    def calculate_load_params(self, sla: SLA, model: LoadModel) -> LoadParams:
        """Calculate VUs, duration, ramp-up based on model"""
        
        if model == LoadModel.SMOKE:
            return LoadParams(vus=1, duration=60, ramp_up=10)
        
        elif model == LoadModel.STRESS:
            # Exceed expected capacity
            expected_rps = sla.throughput_min
            return LoadParams(
                vus=int(expected_rps * 1.5),
                duration=600,
                ramp_up=120
            )
        
        elif model == LoadModel.SPIKE:
            return LoadParams(
                vus=1000,
                duration=300,
                ramp_up=10  # Fast ramp-up for spike
            )
        
        elif model == LoadModel.ENDURANCE:
            return LoadParams(
                vus=sla.throughput_min,
                duration=3600,  # 1 hour
                ramp_up=300
            )
```

---

## ✅ Baseline Comparison & Regression Detection

### Detect Performance Regressions
```python
class RegressionDetector:
    def detect_regression(
        self,
        current_metrics: PerformanceMetrics,
        baseline: PerformanceMetrics,
        threshold: float = 0.10  # 10% degradation
    ) -> RegressionReport:
        """Detect performance regressions"""
        
        regressions = []
        
        # Check response time regression
        if current_metrics.response_time_p95 > baseline.response_time_p95 * (1 + threshold):
            regressions.append(Regression(
                metric="response_time_p95",
                baseline=baseline.response_time_p95,
                current=current_metrics.response_time_p95,
                degradation_percent=(
                    (current_metrics.response_time_p95 / baseline.response_time_p95 - 1) * 100
                )
            ))
        
        # Check throughput regression
        if current_metrics.requests_per_second < baseline.requests_per_second * (1 - threshold):
            regressions.append(Regression(
                metric="requests_per_second",
                baseline=baseline.requests_per_second,
                current=current_metrics.requests_per_second,
                degradation_percent=(
                    (1 - current_metrics.requests_per_second / baseline.requests_per_second) * 100
                )
            ))
        
        # Check error rate increase
        if current_metrics.error_rate > baseline.error_rate * (1 + threshold):
            regressions.append(Regression(
                metric="error_rate",
                baseline=baseline.error_rate,
                current=current_metrics.error_rate,
                degradation_percent=(
                    (current_metrics.error_rate / baseline.error_rate - 1) * 100
                )
            ))
        
        return RegressionReport(
            has_regression=len(regressions) > 0,
            regressions=regressions,
            severity=self._calculate_severity(regressions)
        )
```

---

## ✅ SLA Validation

### Validate Against SLA
```python
class SLAValidator:
    def validate_sla(
        self,
        metrics: PerformanceMetrics,
        sla: SLA
    ) -> SLAValidationResult:
        """Validate metrics against SLA (deterministic)"""
        
        violations = []
        
        # Response time SLA
        if metrics.response_time_p95 > sla.response_time_p95:
            violations.append(SLAViolation(
                metric="response_time_p95",
                expected=sla.response_time_p95,
                actual=metrics.response_time_p95,
                severity="HIGH"
            ))
        
        # Error rate SLA
        if metrics.error_rate > sla.error_rate_max:
            violations.append(SLAViolation(
                metric="error_rate",
                expected=sla.error_rate_max,
                actual=metrics.error_rate,
                severity="CRITICAL"
            ))
        
        # Throughput SLA
        if metrics.requests_per_second < sla.throughput_min:
            violations.append(SLAViolation(
                metric="throughput",
                expected=sla.throughput_min,
                actual=metrics.requests_per_second,
                severity="HIGH"
            ))
        
        return SLAValidationResult(
            passed=len(violations) == 0,
            violations=violations
        )
```

---

## ✅ LLM Integration

### Correct LLM Usage
```python
# ✅ Use LLM for test generation, not validation
class PerformanceTestGenerator:
    def generate_load_scenarios(self, blueprint: Blueprint) -> List[Scenario]:
        """Use LLM to generate realistic load scenarios"""
        
        prompt = f"""
        Generate realistic load test scenarios for:
        Endpoint: {blueprint.target.endpoint}
        Expected users: {blueprint.load_profile.virtual_users}
        Business context: {blueprint.context}
        
        Create varied user behaviors with realistic think times.
        """
        
        # ✅ Use LLM adapter
        scenarios_json = self.llm_adapter.generate(
            prompt=prompt,
            provider="openai",
            temperature=0.4
        )
        
        return self.parse_scenarios(scenarios_json)
```

---

## ✅ Code Generation Examples

### ✅ GOOD: Modular, Blueprint-Driven
```python
class PerformanceAgent(BaseAgent):
    def __init__(self, runtime, llm_adapter, plugin_loader):
        super().__init__(runtime, llm_adapter, plugin_loader)
        self.planner = PerformanceTestPlanner()
        self.generator = TestScriptGenerator(llm_adapter)
        self.detector = RegressionDetector()
    
    def execute_performance_test(self, blueprint_id: str) -> PerformanceResult:
        # Load blueprint
        blueprint = self.blueprint_loader.load(blueprint_id)
        
        # Select load model
        load_model = self.select_load_model(blueprint)
        
        # Create plan
        load_plan = self.planner.create_load_plan(blueprint, load_model)
        
        # Generate test script on-demand
        test_script = self.generator.generate_from_plan(load_plan)
        
        # Execute via plugin
        k6 = self.plugins.load("k6")
        metrics = k6.execute(test_script)
        
        # Get baseline
        baseline = self.get_baseline(blueprint_id)
        
        # Detect regressions
        regression_report = self.detector.detect_regression(metrics, baseline)
        
        # Validate SLA
        sla_result = self.validate_sla(metrics, blueprint.sla)
        
        # Send to validation engine
        return self.validation_engine.validate(
            metrics=metrics,
            sla_result=sla_result,
            regression_report=regression_report,
            blueprint=blueprint
        )
```

### ❌ BAD: Hardcoded, Tool-Specific
```python
# ❌ DON'T DO THIS
def run_load_test():
    # Hardcoded JMeter XML
    jmeter_script = """<?xml version="1.0"?>..."""
    
    # Direct execution
    subprocess.run([
        "jmeter",
        "-n",
        "-t", "test.jmx"
    ])
    
    # Hardcoded threshold
    if avg_response > 2000:
        return "FAIL"  # Wrong!
```

---

## ✅ File Structure

```
core/agents/performance/
├── __init__.py
├── agent.py                    # Main performance agent
├── COPILOT_PERF.md            # This file
├── config.py
├── planners/
│   ├── load_planner.py        # Load test planning
│   └── scenario_planner.py    # Scenario generation
├── generators/
│   ├── k6_generator.py        # k6 script generation
│   ├── jmeter_generator.py    # JMeter plan generation
│   └── locust_generator.py    # Locust file generation
├── analyzers/
│   ├── metrics_analyzer.py    # Metrics analysis
│   ├── regression_detector.py # Regression detection
│   └── trend_analyzer.py      # Trend analysis
├── validators/
│   └── sla_validator.py       # SLA validation
└── tests/
    └── test_perf_agent.py
```

---

## ✅ Checklist for Performance Agent Code

- [ ] Extends `BaseAgent` class
- [ ] Loads performance blueprints
- [ ] Selects appropriate load model
- [ ] Generates test scripts on-demand
- [ ] Uses plugin loader for tools
- [ ] Collects comprehensive metrics
- [ ] Compares against baselines
- [ ] Detects regressions
- [ ] Validates SLA deterministically
- [ ] Uses LLM adapter (not direct calls)
- [ ] Communicates via runtime
- [ ] Supports multiple load testing tools
- [ ] Handles resource monitoring
- [ ] Is modular (< 500 lines per file)

---

## 🎯 Remember

> **Generate load plans from blueprints, never hardcode.**  
> **Metrics are collected, validation engine decides.**  
> **Baseline comparison is deterministic, not AI-based.**

---

*Last updated: 2026-03-26*
