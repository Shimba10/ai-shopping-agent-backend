# Example instruction you send to an LLM to extract structured intent.
INTENT_EXTRACTION_PROMPT = """
You are an intent extraction assistant. Convert the user query into a JSON object with keys:
- intent: one of ["search", "compare", "detail", "explain"]
- budget_max_inr: integer or null
- brands: list of brand names or empty list
- features: list of requested features (e.g. "camera", "oIS", "compact", "fast charging")
- models: list of model strings if the user references exact models
- raw_query: original text

Return only valid JSON.
User query: {user_query}
"""
