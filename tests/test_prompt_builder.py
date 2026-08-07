from prompt_builder import build_prompt_messages
def test_build_prompt_messages():
    top_records = [
        {"source": "faq", "index": 0, "record": {"id":"faq_1", "question":"q","answer":"a"}, "score": 0.9, "snippet":"a snippet"}
    ]
    history = [{"role":"user","content":"hello"}]
    msgs = build_prompt_messages("What's the fee?", top_records, history)
    # expect system + kb + chat history + user
    assert any(m["role"] == "system" for m in msgs)
    assert any("Relevant historical knowledge" in m["content"] for m in msgs if m["role"] == "system")
    assert any(m["role"] == "user" and "What's the fee?" in m["content"] for m in msgs)
