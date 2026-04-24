import logging

from langchain_anthropic import ChatAnthropic
from langchain_ollama import OllamaLLM

from app.core.config import settings

logger = logging.getLogger(__name__)

_llm_instance = None


def get_llm():
    """Factory function to get LLM instance based on provider setting."""
    global _llm_instance
    if _llm_instance is not None:
        return _llm_instance

    provider = settings.llm_provider.lower()

    if provider == "anthropic":
        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in .env")
        _llm_instance = ChatAnthropic(
            model=settings.claude_model,
            api_key=settings.anthropic_api_key,
            temperature=0.7,
        )
        logger.info(f"Initialized Anthropic LLM: {settings.claude_model}")

    elif provider == "ollama":
        _llm_instance = OllamaLLM(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=0.7,
        )
        logger.info(
            f"Initialized Ollama LLM: {settings.ollama_model} at {settings.ollama_base_url}"
        )

    else:
        raise ValueError(f"Unknown LLM provider: {provider}")

    return _llm_instance


def test_llm():
    """Test LLM connection by sending a simple prompt."""
    try:
        llm = get_llm()
        response = llm.invoke("Say hello in one sentence")
        logger.info(f"LLM test successful: {response}")
        return response
    except Exception as e:
        logger.error(f"LLM test failed: {e}")
        raise
