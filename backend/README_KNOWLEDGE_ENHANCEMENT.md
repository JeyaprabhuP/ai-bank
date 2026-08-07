# Historical Knowledge Enhancement

Adds locally-trained-data awareness to the chat assistant **without** a
vector database, embeddings, or RAG — as specified. Every user query now
considers both the local `mock_data/*.json` files and the live
conversation history before hitting OpenAI (or Gemini, or whichever
provider `agents/llm_provider.py` returns).

## Where it lives

```
knowledge/
  knowledge_loader.py   # loads + caches mock_data/*.json at startup
  knowledge_search.py   # keyword + fuzzy relevance search, no embeddings
  prompt_builder.py     # assembles system + user prompt
  chat_service.py       # orchestrates: search -> build prompt -> call LLM
mock_data/
  customers.json, accounts.json, transactions.json, chat_history.json,
  policies.json, faq.json, knowledge_base.json   # example data
tests/
  test_knowledge_loader.py, test_knowledge_search.py,
  test_prompt_builder.py, test_chat_service.py   # 22 tests, all passing
agents/
  customer_agent.py     # patched: falls back to the knowledge layer
```

## Workflow

```
User Question
    -> knowledge_search.search()      keyword + fuzzy match over cached JSON
    -> prompt_builder.build_prompt()  system prompt + top matches + history + question
    -> agents.llm_provider.generate() same LLMProvider you already use (OpenAI/Gemini/mock)
    -> ChatResponse                   reply + which records were used + confidence
```

### 1. `knowledge_loader.py`
On first import, scans `mock_data/*.json`. Each file becomes a "collection"
named after the filename. Each record is normalized into a `Record`
(`source`, `collection`, `id`, flattened `text`, original `data`) and
cached in memory (`load_knowledge_base()` / `get_knowledge_base()` /
`reload_knowledge_base()`). Handles both top-level-list files
(`[...]`) and dict-wrapped files (`{"policies": [...]}`).

### 2. `knowledge_search.py`
No embeddings. Tokenizes the query, scores records by keyword overlap
weighted by a cheap IDF term (rare words like "overdraft" count more
than "account"), and adds a small `difflib`-based fuzzy bonus so typos
and near-misses ("overdaft" → "overdraft") still match. Returns ranked
`SearchResult`s with a `score` (0–1) and `matched_terms`, and supports
filtering by `collections=["policies", "faq"]`.

### 3. `prompt_builder.py`
Builds the exact system prompt from the spec ("treat historical
knowledge as primary source of truth... never fabricate...") plus a
user prompt containing the top matches, trimmed conversation history,
and the question.

### 4. `chat_service.py`
The single entry point: `answer(user_question, history=None,
collections=None, top_k=5)` → `ChatResponse(reply, grounded,
used_records, top_confidence, collections_searched)`. `grounded=True`
means at least one historical record was used, so you can log/display a
confidence badge in the UI. On LLM failure, falls back to a plain-text
answer built directly from the best-matching record instead of crashing.

## Integration with `agents/customer_agent.py`

Rather than replacing your existing structured lookups (accounts,
transactions, FAQ), the knowledge layer is wired in as a **fallback**:

- `policy inquiry` intent: still tries `FAQService.search()` first; if
  that returns nothing, falls back to `knowledge_search` over
  `["policies", "faq"]`.
- Every other intent that previously returned `"No extra account
  context was needed."` (loan inquiry, complaint registration,
  greetings, etc.) now checks the knowledge base first via the new
  `_knowledge_fallback()` helper.
- The import is wrapped in `try/except ImportError`, and every call
  into it is wrapped in `try/except Exception` — if `knowledge/` isn't
  present or a lookup fails, the agent behaves exactly as it did
  before. Nothing about the existing flow can break.

This is a diff against the `customer_agent.py` you shared — merge it in
alongside the `knowledge/` and `mock_data/` folders in this deliverable.

## Running it

```bash
pip install python-dotenv   # already a dependency of llm_provider.py
python3 -m unittest discover -s tests -v   # 22 tests, all passing

# quick manual check with the mock provider (no API key needed):
LLM_BACKEND=mock python3 -c "
from knowledge import chat_service
r = chat_service.answer('What is the overdraft fee policy?')
print(r.grounded, r.top_confidence, r.reply)
"
```

`MOCK_DATA_DIR` env var overrides the default `mock_data/` location if
you want to point at a different directory.

## Future migration to embeddings / a vector DB

The whole point of the `Record` / `SearchResult` dataclasses is that
nothing above them needs to change when you swap the retrieval
mechanism:

1. In `knowledge_loader.py`, keep `load_knowledge_base()` exactly as
   is — it already gives you the full text of every record.
2. In `knowledge_search.py`, replace the body of `search()`: embed
   `record.text` for every record once (cache the vectors keyed by
   `source` + `id`), embed the incoming query, and run a similarity
   query against FAISS/Pinecone/Chroma instead of the keyword/IDF
   scoring loop. Keep returning `SearchResult(record, score,
   matched_terms)` — `matched_terms` can just be `[]` for a vector
   search.
3. `prompt_builder.py` and `chat_service.py` need **zero changes**,
   since they only consume `SearchResult` objects.
4. For incremental data (new transactions, new FAQ entries), add an
   `upsert()` path to the vector index and call it wherever
   `mock_data/*.json` currently gets written to.

## Notes / assumptions

- I only had the `agents/` folder from your repo (no `services/` or
  the real `mock_data/`), so the sample JSON files here are
  illustrative — schema-compatible with what `customer_agent.py`
  already expects (`customer_id`, `account_id`, etc.) but you should
  swap in your real data.
- `knowledge_search` treats every JSON field as flat searchable text,
  so it works with your existing `mock_data/` files as-is, whatever
  their exact shape — no need to write a per-file parser.
