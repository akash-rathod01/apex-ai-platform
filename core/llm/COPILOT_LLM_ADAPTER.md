# Copilot Instructions — LLM Adapter Layer (APEX AI Platform)

## ✅ Purpose
The LLM Adapter Layer provides a **unified, provider-agnostic interface** for all AI/LLM interactions in the Apex AI Platform.

This layer ensures the system remains:
- ✅ **Model-agnostic** - Switch providers/models seamlessly
- ✅ **Scalable** - Handle varying load with model routing
- ✅ **Upgradable** - Add new models without code changes
- ✅ **Laptop-friendly** - Support local quantized models
- ✅ **Enterprise-secure** - Centralized model access control
- ✅ **Cost-optimized** - Route to cost-effective models

This layer enables:
- **Provider Independence** - OpenAI, Anthropic, Azure, local models (Nemotron, Qwen, Llama, DeepSeek)
- **Model Routing** - Choose best model per task (complexity, latency, availability)
- **Safe Prompts** - Sanitized, templated prompts
- **Inference Caching** - Reduce redundant LLM calls
- **On-demand Loading** - Load/unload models dynamically
- **Complete Abstraction** - Agents never call models directly

---

## ✅ Core Principles

### 1. Provider-Agnostic
All agents must call LLMs through the adapter, NEVER directly.

```python
# ✅ CORRECT: Via adapter
response = self.llm_adapter.generate(
    prompt="Generate test steps",
    provider="openai",
    model="gpt-4"
)

# ❌ INCORRECT: Direct call
import openai
response = openai.ChatCompletion.create(...)  # DON'T!
```

### 2. Deterministic Where Possible
Use low temperature (0.0-0.3) for code/test generation.
Use higher temperature (0.5-0.8) for creative/exploratory tasks.

### 3. Never Use LLMs for Pass/Fail
LLMs assist generation and analysis, NEVER validation.

```python
# ❌ WRONG: LLM decides pass/fail
result = llm.generate("Did this test pass? {evidence}")
if "yes" in result.lower():
    return "PASS"  # DON'T DO THIS!

# ✅ CORRECT: LLM generates test, validation engine decides
test = llm.generate("Generate test from {blueprint}")
evidence = execute_test(test)
result = validation_engine.validate(evidence, blueprint)  # Deterministic
```

---

## ✅ LLM Adapter Architecture

### Adapter Interface
```python
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

@dataclass
class LLMResponse:
    """Standardized LLM response"""
    content: str
    model: str
    provider: str
    tokens_used: int
    cost: float
    latency_ms: float
    raw_response: dict
    
@dataclass
class LLMRequest:
    """Standardized LLM request"""
    prompt: str
    system_prompt: Optional[str] = None
    temperature: float = 0.3
    max_tokens: int = 2000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: Optional[List[str]] = None
    response_format: Optional[str] = None  # "json", "text"

class BaseLLMProvider(ABC):
    """Base class for LLM providers"""
    
    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate completion"""
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """Validate provider configuration"""
        pass
    
    @abstractmethod
    def get_cost_per_token(self, model: str) -> Dict[str, float]:
        """Get pricing info"""
        pass
```

### LLM Adapter Implementation
```python
class LLMAdapter:
    """Unified LLM interface for all agents"""
    
    def __init__(self):
        self.providers = self._load_providers()
        self.prompt_manager = PromptManager()
        self.cache = LLMCache()
        self.rate_limiter = RateLimiter()
        self.metrics = LLMMetrics()
    
    def generate(
        self,
        prompt: str,
        provider: str = "openai",
        model: str = "gpt-4",
        temperature: float = 0.3,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None,
        use_cache: bool = True,
        retry_on_failure: bool = True,
        **kwargs
    ) -> LLMResponse:
        """Generate completion with unified interface"""
        
        # Create request
        request = LLMRequest(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # Check cache
        if use_cache:
            cached = self.cache.get(request)
            if cached:
                self.metrics.record_cache_hit(provider, model)
                return cached
        
        # Rate limiting
        self.rate_limiter.wait_if_needed(provider)
        
        # Get provider
        llm_provider = self.providers.get(provider)
        if not llm_provider:
            raise ProviderNotFoundError(f"Provider {provider} not found")
        
        # Execute with retry
        try:
            response = self._execute_with_retry(
                llm_provider,
                request,
                retry_on_failure
            )
            
            # Cache response
            if use_cache:
                self.cache.set(request, response)
            
            # Record metrics
            self.metrics.record_call(
                provider=provider,
                model=model,
                tokens=response.tokens_used,
                cost=response.cost,
                latency=response.latency_ms
            )
            
            return response
        
        except Exception as e:
            self.metrics.record_error(provider, model, str(e))
            raise
    
    def _execute_with_retry(
        self,
        provider: BaseLLMProvider,
        request: LLMRequest,
        retry: bool,
        max_retries: int = 3
    ) -> LLMResponse:
        """Execute with exponential backoff retry"""
        
        last_exception = None
        
        for attempt in range(max_retries if retry else 1):
            try:
                return provider.generate(request)
            
            except RateLimitError as e:
                # Wait and retry on rate limit
                wait_time = 2 ** attempt
                time.sleep(wait_time)
                last_exception = e
                continue
            
            except (APIError, TimeoutError) as e:
                # Retry on transient errors
                if attempt < max_retries - 1:
                    last_exception = e
                    continue
                else:
                    raise
            
            except Exception as e:
                # Don't retry on other errors
                raise
        
        raise last_exception
    
    def generate_with_fallback(
        self,
        prompt: str,
        providers: List[str],
        **kwargs
    ) -> LLMResponse:
        """Try multiple providers in order until success"""
        
        last_exception = None
        
        for provider in providers:
            try:
                return self.generate(
                    prompt=prompt,
                    provider=provider,
                    **kwargs
                )
            except Exception as e:
                last_exception = e
                continue
        
        raise AllProvidersFailed(
            f"All providers failed: {last_exception}"
        )
    
    def generate_batch(
        self,
        prompts: List[str],
        provider: str = "openai",
        **kwargs
    ) -> List[LLMResponse]:
        """Generate multiple completions efficiently"""
        
        # Check if provider supports batching
        llm_provider = self.providers[provider]
        
        if hasattr(llm_provider, 'generate_batch'):
            # Use provider's batch API
            requests = [
                LLMRequest(prompt=p, **kwargs)
                for p in prompts
            ]
            return llm_provider.generate_batch(requests)
        else:
            # Sequential fallback
            return [
                self.generate(prompt=p, provider=provider, **kwargs)
                for p in prompts
            ]
    
    def estimate_cost(
        self,
        prompt: str,
        provider: str,
        model: str
    ) -> float:
        """Estimate cost before making call"""
        
        # Estimate tokens
        estimated_tokens = len(prompt.split()) * 1.3  # Rough estimate
        
        # Get pricing
        llm_provider = self.providers[provider]
        pricing = llm_provider.get_cost_per_token(model)
        
        cost = (estimated_tokens * pricing['input']) + \
               (estimated_tokens * 0.5 * pricing['output'])  # Assume 50% output
        
        return cost
```

---

## ✅ Provider Implementations

### OpenAI Provider
```python
class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider"""
    
    def __init__(self, config: dict):
        self.api_key = config.get('api_key') or os.getenv('OPENAI_API_KEY')
        self.organization = config.get('organization')
        self.base_url = config.get('base_url', 'https://api.openai.com/v1')
        
        import openai
        self.client = openai.OpenAI(
            api_key=self.api_key,
            organization=self.organization
        )
    
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate completion via OpenAI"""
        
        start_time = time.time()
        
        messages = []
        if request.system_prompt:
            messages.append({
                "role": "system",
                "content": request.system_prompt
            })
        messages.append({
            "role": "user",
            "content": request.prompt
        })
        
        response = self.client.chat.completions.create(
            model=request.model or "gpt-4",
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_p=request.top_p,
            frequency_penalty=request.frequency_penalty,
            presence_penalty=request.presence_penalty,
            stop=request.stop_sequences,
            response_format={"type": request.response_format} if request.response_format else None
        )
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Calculate cost
        tokens_used = response.usage.total_tokens
        pricing = self.get_cost_per_token(request.model or "gpt-4")
        cost = (response.usage.prompt_tokens * pricing['input']) + \
               (response.usage.completion_tokens * pricing['output'])
        
        return LLMResponse(
            content=response.choices[0].message.content,
            model=response.model,
            provider="openai",
            tokens_used=tokens_used,
            cost=cost,
            latency_ms=latency_ms,
            raw_response=response.model_dump()
        )
    
    def validate_config(self) -> bool:
        """Validate OpenAI configuration"""
        if not self.api_key:
            raise ConfigurationError("OpenAI API key not found")
        return True
    
    def get_cost_per_token(self, model: str) -> Dict[str, float]:
        """Get OpenAI pricing per 1K tokens"""
        pricing = {
            "gpt-4": {"input": 0.03 / 1000, "output": 0.06 / 1000},
            "gpt-4-turbo": {"input": 0.01 / 1000, "output": 0.03 / 1000},
            "gpt-3.5-turbo": {"input": 0.0015 / 1000, "output": 0.002 / 1000},
        }
        return pricing.get(model, pricing["gpt-4"])
```

### Anthropic Provider
```python
class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude API provider"""
    
    def __init__(self, config: dict):
        self.api_key = config.get('api_key') or os.getenv('ANTHROPIC_API_KEY')
        
        import anthropic
        self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate completion via Anthropic"""
        
        start_time = time.time()
        
        response = self.client.messages.create(
            model=request.model or "claude-3-sonnet-20240229",
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            system=request.system_prompt,
            messages=[{
                "role": "user",
                "content": request.prompt
            }]
        )
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Calculate cost
        tokens_used = response.usage.input_tokens + response.usage.output_tokens
        pricing = self.get_cost_per_token(request.model or "claude-3-sonnet-20240229")
        cost = (response.usage.input_tokens * pricing['input']) + \
               (response.usage.output_tokens * pricing['output'])
        
        return LLMResponse(
            content=response.content[0].text,
            model=response.model,
            provider="anthropic",
            tokens_used=tokens_used,
            cost=cost,
            latency_ms=latency_ms,
            raw_response=response.model_dump()
        )
    
    def get_cost_per_token(self, model: str) -> Dict[str, float]:
        """Get Anthropic pricing per 1M tokens"""
        pricing = {
            "claude-3-opus-20240229": {"input": 15 / 1_000_000, "output": 75 / 1_000_000},
            "claude-3-sonnet-20240229": {"input": 3 / 1_000_000, "output": 15 / 1_000_000},
            "claude-3-haiku-20240307": {"input": 0.25 / 1_000_000, "output": 1.25 / 1_000_000},
        }
        return pricing.get(model, pricing["claude-3-sonnet-20240229"])
```

### Azure OpenAI Provider
```python
class AzureOpenAIProvider(BaseLLMProvider):
    """Azure OpenAI Service provider"""
    
    def __init__(self, config: dict):
        self.api_key = config.get('api_key') or os.getenv('AZURE_OPENAI_API_KEY')
        self.endpoint = config.get('endpoint') or os.getenv('AZURE_OPENAI_ENDPOINT')
        self.api_version = config.get('api_version', '2024-02-15-preview')
        
        from openai import AzureOpenAI
        self.client = AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.endpoint
        )
    
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate completion via Azure OpenAI"""
        # Similar to OpenAI provider
        # Uses deployment name instead of model
        pass
```

---

## ✅ Prompt Management

### Centralized Prompt Templates
```python
class PromptManager:
    """Manage reusable prompt templates"""
    
    def __init__(self, templates_dir: str = "core/llm/prompts"):
        self.templates_dir = templates_dir
        self.templates = self._load_templates()
    
    def get_template(self, name: str) -> str:
        """Get prompt template by name"""
        if name not in self.templates:
            raise TemplateNotFoundError(f"Template {name} not found")
        return self.templates[name]
    
    def render(self, template_name: str, **variables) -> str:
        """Render template with variables"""
        template = self.get_template(template_name)
        
        # Use Jinja2 for rendering
        from jinja2 import Template
        return Template(template).render(**variables)
    
    def _load_templates(self) -> Dict[str, str]:
        """Load all prompt templates"""
        templates = {}
        
        for file in os.listdir(self.templates_dir):
            if file.endswith('.prompt'):
                name = file[:-7]  # Remove .prompt extension
                with open(os.path.join(self.templates_dir, file)) as f:
                    templates[name] = f.read()
        
        return templates

# Example prompt template file: core/llm/prompts/generate_test.prompt
"""
Generate a Playwright test script from the following blueprint:

Blueprint ID: {{blueprint.id}}
Blueprint Type: {{blueprint.type}}

Flow Steps:
{% for step in blueprint.flow %}
{{loop.index}}. {{step.step}}: {{step.target if step.target else ''}}
{% endfor %}

Expected Outcomes:
- URL: {{blueprint.expected.url}}
- Elements Present: {{blueprint.expected.elements_present | join(', ')}}

Generate a well-structured, modern Playwright test that:
1. Follows best practices
2. Includes proper waits
3. Has meaningful assertions
4. Uses page object patterns where appropriate

Output only the test code, no explanations.
"""
```

---

## ✅ LLM Response Caching

### Intelligent Caching
```python
class LLMCache:
    """Cache LLM responses to reduce costs"""
    
    def __init__(self, cache_dir: str = ".llm_cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def get(self, request: LLMRequest) -> Optional[LLMResponse]:
        """Get cached response"""
        cache_key = self._generate_key(request)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if os.path.exists(cache_file):
            with open(cache_file) as f:
                data = json.load(f)
                return LLMResponse(**data)
        
        return None
    
    def set(self, request: LLMRequest, response: LLMResponse):
        """Cache response"""
        cache_key = self._generate_key(request)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        with open(cache_file, 'w') as f:
            json.dump(response.__dict__, f)
    
    def _generate_key(self, request: LLMRequest) -> str:
        """Generate cache key from request"""
        import hashlib
        
        # Hash prompt + key parameters
        key_string = f"{request.prompt}|{request.temperature}|{request.max_tokens}"
        return hashlib.sha256(key_string.encode()).hexdigest()
```

---

## ✅ Rate Limiting

### Provider Rate Limiting
```python
class RateLimiter:
    """Rate limit LLM API calls"""
    
    def __init__(self):
        self.limits = {
            "openai": {"calls_per_minute": 500, "tokens_per_minute": 150000},
            "anthropic": {"calls_per_minute": 50, "tokens_per_minute": 100000},
        }
        self.usage = defaultdict(lambda: {"calls": [], "tokens": []})
    
    def wait_if_needed(self, provider: str):
        """Wait if rate limit would be exceeded"""
        
        if provider not in self.limits:
            return
        
        now = time.time()
        minute_ago = now - 60
        
        # Clean old entries
        self.usage[provider]["calls"] = [
            t for t in self.usage[provider]["calls"] if t > minute_ago
        ]
        
        # Check if we'd exceed limit
        calls_in_last_minute = len(self.usage[provider]["calls"])
        limit = self.limits[provider]["calls_per_minute"]
        
        if calls_in_last_minute >= limit:
            # Wait until oldest call expires
            oldest_call = min(self.usage[provider]["calls"])
            wait_time = 60 - (now - oldest_call)
            time.sleep(wait_time)
        
        # Record this call
        self.usage[provider]["calls"].append(now)
```

---

## ✅ LLM Metrics & Observability

### Track All LLM Calls
```python
class LLMMetrics:
    """Track LLM usage metrics"""
    
    def __init__(self):
        self.metrics = {
            "total_calls": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "by_provider": defaultdict(lambda: {
                "calls": 0,
                "tokens": 0,
                "cost": 0.0,
                "errors": 0
            })
        }
    
    def record_call(
        self,
        provider: str,
        model: str,
        tokens: int,
        cost: float,
        latency: float
    ):
        """Record successful LLM call"""
        
        self.metrics["total_calls"] += 1
        self.metrics["total_tokens"] += tokens
        self.metrics["total_cost"] += cost
        
        self.metrics["by_provider"][provider]["calls"] += 1
        self.metrics["by_provider"][provider]["tokens"] += tokens
        self.metrics["by_provider"][provider]["cost"] += cost
        
        # Send to observability system
        self._emit_metric({
            "metric": "llm_call",
            "provider": provider,
            "model": model,
            "tokens": tokens,
            "cost": cost,
            "latency_ms": latency
        })
    
    def record_error(self, provider: str, model: str, error: str):
        """Record failed LLM call"""
        self.metrics["by_provider"][provider]["errors"] += 1
        
        self._emit_metric({
            "metric": "llm_error",
            "provider": provider,
            "model": model,
            "error": error
        })
    
    def record_cache_hit(self, provider: str, model: str):
        """Record cache hit"""
        self._emit_metric({
            "metric": "llm_cache_hit",
            "provider": provider,
            "model": model
        })
    
    def get_summary(self) -> dict:
        """Get metrics summary"""
        return {
            "total_calls": self.metrics["total_calls"],
            "total_tokens": self.metrics["total_tokens"],
            "total_cost": round(self.metrics["total_cost"], 4),
            "by_provider": dict(self.metrics["by_provider"])
        }
```

---

## ✅ Supported Models

### Local Models (Preferred for Privacy & Cost)
- **Nemotron** (NVIDIA) - Code generation, reasoning
- **Qwen 2.5** - General purpose, fast inference
- **Llama 3.1** - High quality, widely supported
- **DeepSeek** - Code-focused, efficient

### Remote Models (Optional)
- **OpenAI** (GPT-4, GPT-3.5) - High quality, fast
- **Anthropic** (Claude 3.5, Claude 3) - Long context, reasoning
- **Azure OpenAI** - Enterprise compliance

### Custom Models
- Fine-tuned models for domain-specific tasks
- Organization-specific models

---

## ✅ What Copilot MUST Generate

### Core Components
- ✅ **Base adapter class** (interface)
- ✅ **Per-model adapters:**
  - `llama_adapter.py`
  - `qwen_adapter.py`
  - `nemotron_adapter.py`
  - `deepseek_adapter.py`
  - `openai_adapter.py`
  - `anthropic_adapter.py`
  - `azure_adapter.py`

### Routing & Management
- ✅ **Routing logic based on:**
  - Task type (code gen, reasoning, summarization)
  - Complexity (simple vs complex)
  - Latency requirements (real-time vs batch)
  - Model availability (local vs remote)
  - Cost constraints (prefer local when possible)

### Supporting Infrastructure
- ✅ **Prompt templates** (modular, testable)
- ✅ **Output validators** (schema validation)
- ✅ **Retry logic** (exponential backoff)
- ✅ **Inference caching** (reduce redundant calls)
- ✅ **Safe input sanitization** (prevent injection)
- ✅ **Model loading/unloading** (memory management)
- ✅ **Metrics tracking** (usage, cost, latency)

---

## ✅ What Copilot MUST NOT Generate

### ❌ FORBIDDEN Patterns

#### ❌ NO Direct LLM Calls in Agents
```python
# ❌ BAD: Agent bypasses adapter
import openai
response = openai.ChatCompletion.create(...)

# ❌ BAD: Direct model import
from transformers import AutoModel
model = AutoModel.from_pretrained("llama-3.1")
```

#### ❌ NO Hardcoded Model Names in Business Logic
```python
# ❌ BAD: Hardcoded model
def generate_test(blueprint):
    response = llm.call(model="gpt-4", ...)  # Inflexible!

# ✅ GOOD: Model routing
def generate_test(blueprint):
    response = llm_adapter.generate(
        task_type="test_generation",  # Adapter picks model
        complexity="medium"
    )
```

#### ❌ NO Mixed Responsibilities
```python
# ❌ BAD: LLM adapter doing validation
class LLMAdapter:
    def generate_and_validate(self, prompt):
        result = self.llm.generate(prompt)
        if result.passes_tests:  # WRONG! Validation Engine does this
            return "PASS"
```

#### ❌ NO Non-Deterministic Pass/Fail Checks
```python
# ❌ BAD: LLM decides pass/fail
result = llm.ask("Did this test pass? {evidence}")
if "yes" in result.lower():
    return "PASS"  # FORBIDDEN!
```

#### ❌ NO Very Large Prompts
```python
# ❌ BAD: Massive context
prompt = f"Analyze this 50,000 line codebase: {entire_codebase}"

# ✅ GOOD: Focused, chunked prompts
prompt = f"Analyze this function: {function_code[:500]}"
```

---

## ✅ Critical Architectural Rules

### Rule 1: All LLM Calls MUST Go Through This Layer
```python
# ✅ CORRECT: Via adapter
response = self.llm_adapter.generate(
    prompt="Generate test steps",
    task_type="test_generation"
)

# ❌ WRONG: Direct call
import openai
response = openai.ChatCompletion.create(...)  # FORBIDDEN!
```

### Rule 2: Agents Never Call AI Directly
```python
# ✅ CORRECT: Agent uses adapter
class QAAgent:
    def __init__(self, llm_adapter):
        self.llm_adapter = llm_adapter  # Injected dependency
    
    def generate_test(self, blueprint):
        return self.llm_adapter.generate(...)

# ❌ WRONG: Agent imports LLM library
class QAAgent:
    def generate_test(self, blueprint):
        from anthropic import Anthropic
        client = Anthropic()  # FORBIDDEN!
```

### Rule 3: Prompts Must Be Templated, Not Inline Strings
```python
# ✅ CORRECT: Template-based
response = llm_adapter.generate(
    template="generate_ui_test",
    context={"blueprint": blueprint.to_dict()}
)

# ❌ WRONG: Inline prompt
response = llm_adapter.generate(
    prompt=f"Generate a test for {blueprint}"  # Not maintainable!
)
```

### Rule 4: LLM Responses Must Be Validated Before Use
```python
# ✅ CORRECT: Validated output
response = llm_adapter.generate(...)
validated = output_validator.validate(
    response.content,
    expected_schema={"type": "object", "required": ["steps"]}
)
if validated.is_valid:
    use_response(validated.data)

# ❌ WRONG: Direct use
response = llm_adapter.generate(...)
use_response(response.content)  # Could be malformed!
```

### Rule 5: Fail Gracefully → Fallback to Local Model
```python
# ✅ CORRECT: Fallback strategy
try:
    response = llm_adapter.generate(
        task_type="test_generation",
        preferred_provider="openai"  # Try remote first
    )
except ProviderUnavailable:
    response = llm_adapter.generate(
        task_type="test_generation",
        preferred_provider="local-llama"  # Fallback to local
    )
```

### Rule 6: Keep Inference Cost Low → Prefer Local Models
```python
# ✅ CORRECT: Cost-conscious routing
routing_config = {
    "simple_tasks": "local-qwen",      # Fast, cheap
    "medium_tasks": "local-llama",     # Good quality
    "complex_tasks": "local-nemotron", # Best local
    "critical_tasks": "openai-gpt4"   # Remote fallback
}
```

---

## ✅ Typical LLM Use Cases (ALLOWED)

### Generation Tasks
- ✅ **Test plan generation** from blueprints
- ✅ **Blueprint expansion** (add missing details)
- ✅ **Locator healing suggestions** (auto-fix selectors)
- ✅ **Error explanation** (interpret stack traces)
- ✅ **Flow reasoning** (understand user journeys)
- ✅ **Documentation summaries** (generate reports)
- ✅ **Code generation** (Playwright, k6, etc.)
- ✅ **Prompt construction** (dynamic context)

---

## ❌ Forbidden LLM Use Cases (NOT ALLOWED)

### Validation Tasks (Use Validation Engine Instead)
- ❌ **Pass/fail decisions** → Validation Engine decides
- ❌ **Vulnerability confirmation** → Security Agent validates deterministically
- ❌ **Performance result interpretation** → Performance Agent uses SLA thresholds
- ❌ **Contract validation** → Schema validators handle this

### Mutation Tasks (Blueprints Are Stable)
- ❌ **Direct mutation of blueprints** → Use versioned blueprint updates
- ❌ **Rewriting test logic** → Generate new, don't mutate existing

---

## ✅ Checklist for LLM Adapter Code

- [ ] All LLM calls go through adapter (no direct imports)
- [ ] Supports local models (Nemotron, Qwen, Llama, DeepSeek)
- [ ] Supports remote models (OpenAI, Anthropic, Azure)
- [ ] Implements intelligent routing based on task type
- [ ] Uses prompt templates (no inline strings)
- [ ] Validates output before returning
- [ ] Implements retry logic with exponential backoff
- [ ] Has rate limiting per provider
- [ ] Caches responses to reduce cost
- [ ] Tracks costs, tokens, and latency metrics
- [ ] Handles failures gracefully (fallback models)
- [ ] Supports on-demand model loading/unloading
- [ ] Sanitizes inputs (prevent injection attacks)
- [ ] Never makes pass/fail decisions
- [ ] Is modular (< 500 lines per file)
- [ ] Has fallback mechanisms
- [ ] Validates configurations
- [ ] Never uses LLM for validation
- [ ] Is modular (< 500 lines per file)

---

## 🎯 Remember

> **LLMs generate, NEVER validate.**  
> **All LLM calls through adapter, NEVER direct.**  
> **Prefer local models, fallback to remote.**  
> **Template prompts, validate outputs.**  
> **Route intelligently, cache aggressively.**  
> **Fail gracefully, track everything.**

---

## 📚 Related Documentation

- [Main Platform Instructions](../../.apex_copilot_instructions.md)
- [Blueprint Engine](../blueprints/COPILOT_BLUEPRINT_ENGINE.md)
- [Validation Engine](../validation/COPILOT_VALIDATION_ENGINE.md)
- [Agent Instructions](../agents/AGENTS_README.md)

---

*Last updated: 2026-03-26*
