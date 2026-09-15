from pipeline.config import get_llm_response
import json
import re

EXTRACTION_PROMPT = """
You are a CDP expert analyzing documentation for {platform}. 
Extract: 
1. **Entities**: Key nouns/objects (e.g., "user profile", "event source", "audience segment")
2. **Actions**: Verbs/procedures (e.g., "set up", "track", "create", "sync")
3. **Relationships**: How entities connect via actions (e.g., "user profile <- identified via -> event")

Return ONLY a valid JSON list of objects with this structure:
[
  {{"entity": "user profile", "type": "object"}},
  {{"action": "set up", "type": "verb"}},
  {{"subject": "user profile", "action": "created by", "object": "identify call"}}
]

Documentation chunk:
{chunk_text}
"""

def extract_from_chunk(chunk_text: str, platform: str) -> list:
    """Uses LLM to extract structured entities/actions/relationships from text."""
    prompt = EXTRACTION_PROMPT.format(
        platform=platform.capitalize(),
        chunk_text=chunk_text[:4000]  # Avoid exceeding context limits
    )
    try:
        response = get_llm_response(prompt)
        # Clean potential markdown/json noise
        cleaned = re.sub(r"^```json|```$", "", response.strip()).strip()
        return json.loads(cleaned)
    except (json.JSONDecodeError, Exception) as e:
        print(f"⚠️ Extraction failed for chunk: {e}")
        return []