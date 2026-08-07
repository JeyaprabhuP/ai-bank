from services import data_loader as dl


class CustomerService:
    @staticmethod
    def list_customers(limit: int = 50):
        return dl.load_customers()[:limit]

    @staticmethod
    def get_customer(customer_id: str):
        customers = dl.load_customers()
        return next((c for c in customers if c["customer_id"] == customer_id), None)

    @staticmethod
    def get_accounts_for_customer(customer_id: str):
        accounts = dl.load_accounts()
        return [a for a in accounts if a["customer_id"] == customer_id]
