"""
LLM Adapter Layer - Unified interface for multiple LLM providers
"""

from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging


@dataclass
class LLMMessage:
    """Single message in conversation"""
    role: str  # system, user, assistant
    content: str
    metadata: Dict[str, Any] = None


@dataclass
class LLMResponse:
    """Response from LLM"""
    content: str
    model: str
    usage: Dict[str, int]  # tokens used
    metadata: Dict[str, Any] = None


class LLMAdapter(ABC):
    """
    Base LLM Adapter
    
    Provides unified interface for:
    - Ollama (local)
    - OpenAI
    - Anthropic
    - Azure OpenAI
    """
    
    def __init__(self, model: str, config: Dict[str, Any] = None):
        self.model = model
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    async def generate(self, messages: List[LLMMessage], 
                      **kwargs) -> LLMResponse:
        """
        Generate response from LLM
        
        Args:
            messages: Conversation history
            **kwargs: Provider-specific parameters
        
        Returns:
            LLMResponse
        """
        pass
    
    @abstractmethod
    async def stream(self, messages: List[LLMMessage], 
                    **kwargs):
        """
        Stream response from LLM
        
        Args:
            messages: Conversation history
            **kwargs: Provider-specific parameters
        
        Yields:
            Response chunks
        """
        pass
    
    def format_messages(self, messages: List[LLMMessage]) -> Any:
        """Format messages for specific provider - override if needed"""
        return [{'role': msg.role, 'content': msg.content} for msg in messages]


class OllamaAdapter(LLMAdapter):
    """
    Ollama LLM Adapter - Local LLM execution
    
    Supports: llama2, codellama, mistral, etc.
    """
    
    def __init__(self, model: str = "llama2", base_url: str = "http://localhost:11434"):
        super().__init__(model)
        self.base_url = base_url
    
    async def generate(self, messages: List[LLMMessage], 
                      temperature: float = 0.7,
                      max_tokens: int = 2000,
                      **kwargs) -> LLMResponse:
        """Generate response using Ollama"""
        import httpx
        
        # Format request
        formatted_messages = self.format_messages(messages)
        
        request_data = {
            'model': self.model,
            'messages': formatted_messages,
            'stream': False,
            'options': {
                'temperature': temperature,
                'num_predict': max_tokens,
                **kwargs
            }
        }
        
        # Make request
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json=request_data
            )
            response.raise_for_status()
            result = response.json()
        
        # Parse response
        return LLMResponse(
            content=result['message']['content'],
            model=self.model,
            usage={
                'prompt_tokens': result.get('prompt_eval_count', 0),
                'completion_tokens': result.get('eval_count', 0),
                'total_tokens': result.get('prompt_eval_count', 0) + result.get('eval_count', 0)
            },
            metadata={
                'total_duration': result.get('total_duration'),
                'load_duration': result.get('load_duration'),
                'eval_duration': result.get('eval_duration')
            }
        )
    
    async def stream(self, messages: List[LLMMessage], 
                    temperature: float = 0.7,
                    max_tokens: int = 2000,
                    **kwargs):
        """Stream response using Ollama"""
        import httpx
        import json
        
        formatted_messages = self.format_messages(messages)
        
        request_data = {
            'model': self.model,
            'messages': formatted_messages,
            'stream': True,
            'options': {
                'temperature': temperature,
                'num_predict': max_tokens,
                **kwargs
            }
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                'POST',
                f"{self.base_url}/api/chat",
                json=request_data
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        chunk = json.loads(line)
                        if 'message' in chunk:
                            yield chunk['message']['content']


class OpenAIAdapter(LLMAdapter):
    """
    OpenAI LLM Adapter
    
    Supports: gpt-4, gpt-3.5-turbo, etc.
    """
    
    def __init__(self, model: str = "gpt-4", api_key: str = None):
        super().__init__(model)
        self.api_key = api_key
    
    async def generate(self, messages: List[LLMMessage], 
                      temperature: float = 0.7,
                      max_tokens: int = 2000,
                      **kwargs) -> LLMResponse:
        """Generate response using OpenAI"""
        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise ImportError(
                "OpenAI package not installed. "
                "Install with: pip install openai"
            )
        
        client = AsyncOpenAI(api_key=self.api_key)
        
        formatted_messages = self.format_messages(messages)
        
        response = await client.chat.completions.create(
            model=self.model,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        return LLMResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage={
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            },
            metadata={
                'finish_reason': response.choices[0].finish_reason,
                'id': response.id
            }
        )
    
    async def stream(self, messages: List[LLMMessage], 
                    temperature: float = 0.7,
                    max_tokens: int = 2000,
                    **kwargs):
        """Stream response using OpenAI"""
        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise ImportError(
                "OpenAI package not installed. "
                "Install with: pip install openai"
            )
        
        client = AsyncOpenAI(api_key=self.api_key)
        
        formatted_messages = self.format_messages(messages)
        
        stream = await client.chat.completions.create(
            model=self.model,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class AnthropicAdapter(LLMAdapter):
    """
    Anthropic LLM Adapter
    
    Supports: claude-3-opus, claude-3-sonnet, etc.
    """
    
    def __init__(self, model: str = "claude-3-sonnet-20240229", api_key: str = None):
        super().__init__(model)
        self.api_key = api_key
    
    async def generate(self, messages: List[LLMMessage], 
                      temperature: float = 0.7,
                      max_tokens: int = 2000,
                      **kwargs) -> LLMResponse:
        """Generate response using Anthropic"""
        try:
            from anthropic import AsyncAnthropic
        except ImportError:
            raise ImportError(
                "Anthropic package not installed. "
                "Install with: pip install anthropic"
            )
        
        client = AsyncAnthropic(api_key=self.api_key)
        
        # Extract system message if present
        system_msg = None
        user_messages = []
        
        for msg in messages:
            if msg.role == 'system':
                system_msg = msg.content
            else:
                user_messages.append({'role': msg.role, 'content': msg.content})
        
        # Create request
        request_args = {
            'model': self.model,
            'messages': user_messages,
            'temperature': temperature,
            'max_tokens': max_tokens,
            **kwargs
        }
        
        if system_msg:
            request_args['system'] = system_msg
        
        response = await client.messages.create(**request_args)
        
        return LLMResponse(
            content=response.content[0].text,
            model=response.model,
            usage={
                'prompt_tokens': response.usage.input_tokens,
                'completion_tokens': response.usage.output_tokens,
                'total_tokens': response.usage.input_tokens + response.usage.output_tokens
            },
            metadata={
                'stop_reason': response.stop_reason,
                'id': response.id
            }
        )
    
    async def stream(self, messages: List[LLMMessage], 
                    temperature: float = 0.7,
                    max_tokens: int = 2000,
                    **kwargs):
        """Stream response using Anthropic"""
        try:
            from anthropic import AsyncAnthropic
        except ImportError:
            raise ImportError(
                "Anthropic package not installed. "
                "Install with: pip install anthropic"
            )
        
        client = AsyncAnthropic(api_key=self.api_key)
        
        # Extract system message
        system_msg = None
        user_messages = []
        
        for msg in messages:
            if msg.role == 'system':
                system_msg = msg.content
            else:
                user_messages.append({'role': msg.role, 'content': msg.content})
        
        request_args = {
            'model': self.model,
            'messages': user_messages,
            'temperature': temperature,
            'max_tokens': max_tokens,
            'stream': True,
            **kwargs
        }
        
        if system_msg:
            request_args['system'] = system_msg
        
        async with client.messages.stream(**request_args) as stream:
            async for text in stream.text_stream:
                yield text


class LLMFactory:
    """
    Factory for creating LLM adapters
    
    Usage:
        adapter = LLMFactory.create('ollama', model='llama2')
        adapter = LLMFactory.create('openai', model='gpt-4', api_key='...')
    """
    
    adapters = {
        'ollama': OllamaAdapter,
        'openai': OpenAIAdapter,
        'anthropic': AnthropicAdapter,
    }
    
    @classmethod
    def create(cls, provider: str, **kwargs) -> LLMAdapter:
        """
        Create LLM adapter
        
        Args:
            provider: Provider name (ollama, openai, anthropic)
            **kwargs: Provider-specific arguments
        
        Returns:
            LLMAdapter instance
        """
        adapter_class = cls.adapters.get(provider.lower())
        
        if not adapter_class:
            raise ValueError(
                f"Unknown provider: {provider}. "
                f"Available: {list(cls.adapters.keys())}"
            )
        
        return adapter_class(**kwargs)
    
    @classmethod
    def register(cls, provider: str, adapter_class: type):
        """Register custom adapter"""
        cls.adapters[provider.lower()] = adapter_class
