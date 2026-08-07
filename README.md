# AI Assistant POC (local mock data)

This project demonstrates a modular design to enrich LLM prompts using locally stored historical data (no vectors, no embeddings).

Key components:
- knowledge_loader.py: Loads and caches JSON files from `mock_data/`.
- knowledge_search.py: Lightweight keyword + fuzzy matching and ranking.
- prompt_builder.py: Constructs system + KB + chat history + user question for the LLM.
- openai_client.py: Thin wrapper to call OpenAI; easy to mock in tests.
- chat_service.py: Orchestrates the whole workflow and maintains conversation memory.

Design goals:
- No vector DB, no embeddings, no RAG — simple POC search using token overlap + fuzzy matching.
- Load data once at startup and cache it.
- Keep architecture modular for easy future swap to vector search or RAG.

Usage:
1. Populate `mock_data/` with JSON files (examples are included).
2. Set `OPENAI_API_KEY` env var or pass an OpenAIClient with a real key.
3. Run `python main.py` or integrate ChatService into your application.

Testing:
- Run `pytest` to execute unit tests.

Migration notes (future):
- Replace KnowledgeSearch with a vector-based search adapter implementing the same interface (`search(query, top_n, source_filter) -> list`).
- Keep prompt building unchanged; only the search module needs swapping.
- Add embeddings: compute embeddings during load and store them; adapt SearchAdapter to use a vector index.

Security & safety:
- System prompt instructs the model to prefer historical knowledge and avoid fabrications.
- Conversation memory is in-memory; for production, persist or securely store it as needed.
