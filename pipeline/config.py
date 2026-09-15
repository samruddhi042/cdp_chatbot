import os
from litellm import completion

# ===== LLM CONFIGURATION (SET THESE) =====
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # Options: ollama, openai, azure, vertexai, etc.
LLM_MODEL = os.getenv("LLM_MODEL", "llama3")        # e.g., "llama3" (Ollama), "gpt-3.5-turbo" (OpenAI)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")  # For Ollama
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")        # Required if using OpenAI/Azure

def get_llm_response(prompt: str, temperature: float = 0.1) -> str:
    """Unified LLM caller compatible with all OpenAI-like APIs via LiteLLM."""
    messages = [{"role": "user", "content": prompt}]
    
    if LLM_PROVIDER == "ollama":
        response = completion(
            model=f"ollama/{LLM_MODEL}",
            messages=messages,
            temperature=temperature,
            api_base=OLLAMA_BASE_URL
        )
    else:  # OpenAI, Azure, etc. (LiteLLM handles auth via env vars)
        response = completion(
            model=LLM_MODEL,
            messages=messages,
            temperature=temperature
        )
    return response.choices[0].message.content.strip()