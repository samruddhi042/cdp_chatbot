from pipeline.config import get_llm_response
import re

STANDARDIZATION_PROMPT = """
You are standardizing CDP terminology. Given an entity/action phrase, 
return its MOST COMMON canonical form used in {platform} documentation.
Examples:
  - "setup source" → "set up source"
  - "user profle" → "user profile" 
  - "track event" → "track event"

Return ONLY the standardized phrase (no explanations).

Input: {phrase}
"""

def standardize_term(term: str, platform: str) -> str:
    """Converts a term to its canonical form."""
    prompt = STANDARDIZATION_PROMPT.format(platform=platform, phrase=term)
    try:
        response = get_llm_response(prompt)
        # Remove quotes/punctuation, lowercase for matching
        return re.sub(r"[^\w\s]", "", response).lower().strip()
    except Exception:
        # Fallback: basic rule-based normalization
        return term.lower().replace("setup", "set up").replace("userid", "user id").strip()

def standardize_extractions(extractions: list, platform: str) -> list:
    """Applies standardization to all entities/actions in extraction results."""
    standardized = []
    for item in extractions:
        new_item = item.copy()
        # Standardize entity/action/subject/object fields
        for key in ["entity", "action", "subject", "object"]:
            if key in new_item and isinstance(new_item[key], str):
                new_item[key] = standardize_term(new_item[key], platform)
        standardized.append(new_item)
    return standardized