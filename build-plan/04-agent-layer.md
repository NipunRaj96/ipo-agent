# Phase 4: Agent layer

The LLM extracts and explains. It does not predict.

- Search: DDGS (no key). Page reading: Crawl4AI or Jina Reader. SearXNG skipped, too heavy for this use.
- Reads RHP/DRHP and recent news, returns structured JSON red flags (litigation, promoter pledge, use of proceeds, auditor remarks, valuation vs peers). These become model features.
- Writes a plain-language explanation next to the model's probability.
- LLM: free tier (Gemini, Groq) or local Ollama. Only ~5-10 IPOs are open at a time, so limits are fine.
