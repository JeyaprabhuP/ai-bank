from services import data_loader as dl


class TransactionService:
    @staticmethod
    def list_transactions(customer_id: str = None, limit: int = 100):
        txns = dl.load_transactions()
        if customer_id:
            txns = [t for t in txns if t["customer_id"] == customer_id]
        txns = sorted(txns, key=lambda t: t["timestamp"], reverse=True)
        return txns[:limit]

    @staticmethod
    def get_transaction(transaction_id: str):
        txns = dl.load_transactions()
        return next((t for t in txns if t["transaction_id"] == transaction_id), None)
