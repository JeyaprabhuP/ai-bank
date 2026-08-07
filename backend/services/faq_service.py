from services import data_loader as dl


class FAQService:
    @staticmethod
    def search(query: str):
        faq = dl.load_faq()
        query_lower = query.lower()
        matches = [f for f in faq if any(w in f["question"].lower() for w in query_lower.split())]
        return matches or faq[:2]
