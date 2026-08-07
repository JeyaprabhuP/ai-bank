"""
main.py - simple demonstration script

Run this to see an end-to-end example using the included mock_data.
"""
import logging
from chat_service import ChatService
from openai_client import OpenAIClient

logging.basicConfig(level=logging.INFO)

def demo():
    # Provide a mock OpenAI client or set OPENAI_API_KEY in env to make real calls.
    client = OpenAIClient(api_key=None, model="gpt-4")  # Use None for offline/mock testing
    cs = ChatService("mock_data", openai_client=client)
    session = "demo-session-1"
    q = "What is the fee for international transfers?"
    out = cs.handle_user_query(session, q, top_n=3, source_filter=["policies", "faq"])
    print("Assistant response:")
    print(out["assistant"])
    print("Used historical records:")
    for r in out["used_records"]:
        print(r)

if __name__ == "__main__":
    demo()
