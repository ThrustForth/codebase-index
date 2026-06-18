# ~/projects/codebase-index/config.py

# ============================================================================
# MODEL CONFIGURATION
# Change models here to update them throughout the entire codebase
# ============================================================================

# ============================================================================
# Per-Agent Psychoanalytic Models
# ============================================================================

ID_MODEL = "ollama/mistral:7b"        # Impulsive, creative bug-finding
SUPERCERO_MODEL = "ollama/llama3.2:1b" # Perfectionist, quality demands
EGO_MODEL = "ollama/qwen2.5:7b"       # Rational mediator

# Default psychoanalytic model (backwards compatibility)
PSYCHO_MODEL = ID_MODEL

# ============================================================================
# Code Puppy Default Model
# ============================================================================

CODEPUPPY_MODEL = "ollama/llama3.2:1b"

# ============================================================================
# Embedding Model for LanceDB
# ============================================================================

EMBED_MODEL = "ollama/nomic-embed-text"

# ============================================================================
# OpenRouter Configuration (fallback for complex tasks)
# ============================================================================

# OpenRouter model slug
# Options:
#   - "openrouter/auto"           = OpenRouter chooses best model
#   - "anthropic/claude-sonnet-4.5" = Specific Claude model
#   - "openai/gpt-5"              = Specific OpenAI model
#   - "mistralai/mistral-large"   = Specific Mistral model
OPENROUTER_MODEL = "openrouter/auto"

# OpenRouter API key (from environment variable for security)
# Set in your shell: export OPENROUTER_API_KEY="your_key_here"
OPENROUTER_API_KEY_ENV = "OPENROUTER_API_KEY"

# OpenRouter base URL
OPENROUTER_BASE_URL = "https://api.openrouter.ai/v1"

# ============================================================================
# Ollama Configuration
# ============================================================================

OLLAMA_BASE_URL = "http://localhost:11434"

# ============================================================================
# Agent Temperatures
# ============================================================================

ID_TEMPERATURE = 0.8
SUPERCERO_TEMPERATURE = 0.3
EGO_TEMPERATURE = 0.5

# ============================================================================
# Helper: Get model for a specific agent
# ============================================================================

def get_psycho_model(agent_name: str) -> str:
    """Get the model for a specific psychoanalytic agent."""
    models = {
        "id": ID_MODEL,
        "superego": SUPERCERO_MODEL,
        "ego": EGO_MODEL,
    }
    return models.get(agent_name, PSYCHO_MODEL)
