#!/usr/bin/env python3
"""LLM Integration Tools.

Tools for interacting with various LLM providers including local (Ollama)
and cloud-based services (OpenAI, Anthropic, OpenRouter).
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class LLMConfig(BaseModel):
    """Configuration for LLM tools."""
    
    provider: str = Field(default="ollama", description="LLM provider")
    model: str = Field(default="qwen2.5-coder", description="Model name")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Temperature")
    max_tokens: int = Field(default=2000, gt=0, description="Max tokens to generate")
    api_key: Optional[str] = Field(default=None, description="API key for cloud providers")
    base_url: Optional[str] = Field(default="http://localhost:11434", description="Base URL")


class LLMCompletionTool:
    """Generate text completions using LLMs."""
    
    name: str = "llm_completion"
    description: str = "Generate text completions using local or cloud LLMs"
    
    def __init__(self, config: Optional[LLMConfig] = None) -> None:
        """Initialize LLM completion tool."""
        self.config = config or LLMConfig()
        logger.info(f"Initialized LLM tool with provider: {self.config.provider}")
    
    def execute(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute completion request.
        
        Args:
            prompt: The prompt text
            **kwargs: Additional parameters (system_prompt, temperature, etc.)
        
        Returns:
            Completion result with text and metadata
        """
        try:
            if self.config.provider == "ollama":
                return self._ollama_completion(prompt, **kwargs)
            elif self.config.provider == "openai":
                return self._openai_completion(prompt, **kwargs)
            elif self.config.provider == "anthropic":
                return self._anthropic_completion(prompt, **kwargs)
            elif self.config.provider == "openrouter":
                return self._openrouter_completion(prompt, **kwargs)
            else:
                raise ValueError(f"Unsupported provider: {self.config.provider}")
        except Exception as e:
            logger.error(f"LLM completion failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "text": ""
            }
    
    def _ollama_completion(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """Generate completion using Ollama."""
        try:
            import requests
            
            url = f"{self.config.base_url}/api/generate"
            payload = {
                "model": self.config.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", self.config.temperature),
                    "num_predict": kwargs.get("max_tokens", self.config.max_tokens)
                }
            }
            
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            return {
                "status": "success",
                "text": result.get("response", ""),
                "model": self.config.model,
                "provider": "ollama",
                "tokens": result.get("eval_count", 0)
            }
        except Exception as e:
            logger.error(f"Ollama completion failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "text": ""
            }
    
    def _openai_completion(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """Generate completion using OpenAI API."""
        try:
            import openai
            
            if not self.config.api_key:
                raise ValueError("OpenAI API key not configured")
            
            client = openai.OpenAI(api_key=self.config.api_key)
            
            response = client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": kwargs.get("system_prompt", "You are a helpful assistant.")},
                    {"role": "user", "content": prompt}
                ],
                temperature=kwargs.get("temperature", self.config.temperature),
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens)
            )
            
            return {
                "status": "success",
                "text": response.choices[0].message.content,
                "model": self.config.model,
                "provider": "openai",
                "tokens": response.usage.total_tokens
            }
        except Exception as e:
            logger.error(f"OpenAI completion failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "text": ""
            }
    
    def _anthropic_completion(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """Generate completion using Anthropic API."""
        return {
            "status": "error",
            "error": "Anthropic integration not yet implemented",
            "text": ""
        }
    
    def _openrouter_completion(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """Generate completion using OpenRouter API."""
        try:
            import requests
            
            if not self.config.api_key:
                raise ValueError("OpenRouter API key not configured")
            
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.config.model,
                "messages": [
                    {"role": "system", "content": kwargs.get("system_prompt", "You are a helpful assistant.")},
                    {"role": "user", "content": prompt}
                ],
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens)
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            return {
                "status": "success",
                "text": result["choices"][0]["message"]["content"],
                "model": self.config.model,
                "provider": "openrouter",
                "tokens": result.get("usage", {}).get("total_tokens", 0)
            }
        except Exception as e:
            logger.error(f"OpenRouter completion failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "text": ""
            }


class LLMEmbeddingTool:
    """Generate embeddings using LLMs."""
    
    name: str = "llm_embedding"
    description: str = "Generate text embeddings for semantic search"
    
    def __init__(self, config: Optional[LLMConfig] = None) -> None:
        """Initialize embedding tool."""
        self.config = config or LLMConfig(model="nomic-embed-text")
    
    def execute(self, text: str, **kwargs: Any) -> Dict[str, Any]:
        """Generate embedding.
        
        Args:
            text: Text to embed
            **kwargs: Additional parameters
        
        Returns:
            Embedding result with vector and metadata
        """
        try:
            if self.config.provider == "ollama":
                return self._ollama_embedding(text)
            else:
                raise ValueError(f"Embeddings not supported for provider: {self.config.provider}")
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "embedding": []
            }
    
    def _ollama_embedding(self, text: str) -> Dict[str, Any]:
        """Generate embedding using Ollama."""
        try:
            import requests
            
            url = f"{self.config.base_url}/api/embeddings"
            payload = {
                "model": self.config.model,
                "prompt": text
            }
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            return {
                "status": "success",
                "embedding": result.get("embedding", []),
                "model": self.config.model,
                "dimensions": len(result.get("embedding", []))
            }
        except Exception as e:
            logger.error(f"Ollama embedding failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "embedding": []
            }


def llm_completion_tool(config: Optional[Dict[str, Any]] = None) -> LLMCompletionTool:
    """Factory function for LLM completion tool."""
    cfg = LLMConfig(**config) if config else LLMConfig()
    return LLMCompletionTool(cfg)


def llm_embedding_tool(config: Optional[Dict[str, Any]] = None) -> LLMEmbeddingTool:
    """Factory function for LLM embedding tool."""
    cfg = LLMConfig(**config) if config else LLMConfig(model="nomic-embed-text")
    return LLMEmbeddingTool(cfg)


__all__ = [
    "LLMConfig",
    "LLMCompletionTool",
    "LLMEmbeddingTool",
    "llm_completion_tool",
    "llm_embedding_tool",
]
