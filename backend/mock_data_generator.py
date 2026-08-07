"""
Generates mock JSON/CSV data for the Banking AI Platform.
Run once: python mock_data_generator.py
Regenerate any time to reset the demo data.
"""
import json
import random
import csv
import os
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()
random.seed(42)
Faker.seed(42)

BASE = os.path.join(os.path.dirname(__file__), "mock_data")
os.makedirs(BASE, exist_ok=True)

N_CUSTOMERS = 100
N_TRANSACTIONS = 1000
N_FRAUD_ALERTS = 100

COUNTRIES = ["USA", "Mexico", "UK", "Nigeria", "Russia", "India", "Germany", "Brazil", "China", "France"]
DEVICE_TYPES = ["known", "new"]
MERCHANT_CATEGORIES = ["groceries", "electronics", "travel", "dining", "utilities", "entertainment", "atm_withdrawal", "online_retail", "gas_station", "wire_transfer"]


def gen_customers():
    customers = []
    for i in range(1, N_CUSTOMERS + 1):
        customers.append({
            "customer_id": f"CUST{i:04d}",
            "name": fake.name(),
            "email": fake.email(),
            "phone": fake.phone_number(),
            "address": fake.address().replace("\n", ", "),
            "account_opened": fake.date_between(start_date="-8y", end_date="-1y").isoformat(),
            "risk_profile": random.choice(["low", "medium", "high"]),
            "failed_login_attempts": random.choice([0, 0, 0, 1, 2, 5]),
            "home_country": random.choice(COUNTRIES[:3]),
        })
    with open(os.path.join(BASE, "customers.json"), "w") as f:
        json.dump(customers, f, indent=2)
    return customers


def gen_accounts(customers):
    accounts = []
    for c in customers:
        for _ in range(random.choice([1, 1, 2])):
            accounts.append({
                "account_id": fake.iban(),
                "customer_id": c["customer_id"],
                "account_type": random.choice(["checking", "savings", "credit_card"]),
                "balance": round(random.uniform(100, 85000), 2),
                "currency": "USD",
                "status": "active",
            })
    with open(os.path.join(BASE, "accounts.json"), "w") as f:
        json.dump(accounts, f, indent=2)
    return accounts


def gen_transactions(customers, accounts):
    rows = []
    for i in range(1, N_TRANSACTIONS + 1):
        acct = random.choice(accounts)
        cust = next(c for c in customers if c["customer_id"] == acct["customer_id"])
        is_foreign = random.random() < 0.12
        location = random.choice(COUNTRIES) if is_foreign else cust["home_country"]
        ts = datetime.now() - timedelta(days=random.randint(0, 90), hours=random.randint(0, 23))
        rows.append({
            "transaction_id": f"TXN{i:05d}",
            "account_id": acct["account_id"],
            "customer_id": cust["customer_id"],
            "amount": round(random.uniform(5, 9500), 2),
            "currency": "USD",
            "merchant_category": random.choice(MERCHANT_CATEGORIES),
            "location": location,
            "is_foreign": is_foreign,
            "device": random.choice(DEVICE_TYPES),
            "timestamp": ts.isoformat(),
        })
    with open(os.path.join(BASE, "transactions.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return rows


def compute_risk_score(txn, customer):
    score = 0
    if txn["amount"] > 5000:
        score += 30
    elif txn["amount"] > 1500:
        score += 15
    if txn["is_foreign"]:
        score += 25
    if txn["device"] == "new":
        score += 20
    score += min(customer["failed_login_attempts"] * 5, 20)
    if txn["merchant_category"] in ("wire_transfer", "atm_withdrawal"):
        score += 10
    score += random.randint(0, 10)
    return min(score, 100)


def priority_for(score):
    if score >= 90:
        return "Critical"
    if score >= 70:
        return "High"
    if score >= 40:
        return "Medium"
    return "Low"


def action_for(priority):
    return {
        "Critical": "Freeze Card",
        "High": "Verify with Customer",
        "Medium": "Monitor Account",
        "Low": "No Action Required",
    }[priority]


def gen_fraud_alerts(customers, transactions):
    alerts = []
    sample_txns = random.sample(transactions, min(N_FRAUD_ALERTS, len(transactions)))
    for i, txn in enumerate(sample_txns, start=1):
        cust = next(c for c in customers if c["customer_id"] == txn["customer_id"])
        score = compute_risk_score(txn, cust)
        priority = priority_for(score)
        alerts.append({
            "alert_id": f"ALERT{i:04d}",
            "transaction_id": txn["transaction_id"],
            "customer_id": cust["customer_id"],
            "customer_name": cust["name"],
            "risk_score": score,
            "priority": priority,
            "recommended_action": action_for(priority),
            "status": random.choice(["open", "open", "investigating", "resolved"]),
            "created_at": txn["timestamp"],
            "factors": {
                "amount": txn["amount"],
                "location": txn["location"],
                "is_foreign": txn["is_foreign"],
                "new_device": txn["device"] == "new",
                "failed_login_attempts": cust["failed_login_attempts"],
            },
        })
    with open(os.path.join(BASE, "fraud_alerts.json"), "w") as f:
        json.dump(alerts, f, indent=2)
    return alerts


def gen_tickets(customers):
    statuses = ["open", "in_progress", "resolved", "resolved", "closed"]
    tickets = []
    for i in range(1, 41):
        cust = random.choice(customers)
        tickets.append({
            "ticket_id": f"TICKET{i:04d}",
            "customer_id": cust["customer_id"],
            "subject": random.choice([
                "Suspicious transaction reported",
                "Card used in another country",
                "Unable to log in",
                "Dispute a charge",
                "Request account statement",
            ]),
            "status": random.choice(statuses),
            "priority": random.choice(["Low", "Medium", "High", "Critical"]),
            "created_at": fake.date_time_between(start_date="-60d", end_date="now").isoformat(),
            "assigned_agent": random.choice(["Customer Support Agent", "Fraud Detection Agent", "Compliance Agent", "Supervisor Agent"]),
        })
    with open(os.path.join(BASE, "tickets.json"), "w") as f:
        json.dump(tickets, f, indent=2)
    return tickets


def gen_faq():
    faq = [
        {"question": "How do I report a suspicious transaction?", "answer": "You can report it directly in this chat, or call the number on the back of your card."},
        {"question": "How long does a dispute take to resolve?", "answer": "Most disputes are resolved within 5-10 business days."},
        {"question": "How do I freeze my card?", "answer": "Say 'freeze my card' in chat or use the Settings page, and our Fraud Agent will action it immediately."},
        {"question": "What do I do if I travel abroad?", "answer": "Notify us in advance via chat so foreign transactions aren't flagged unnecessarily."},
        {"question": "How is my fraud risk score calculated?", "answer": "It factors in transaction amount, location, device recognition, and recent login activity."},
    ]
    with open(os.path.join(BASE, "faq.json"), "w") as f:
        json.dump(faq, f, indent=2)


def gen_compliance_rules():
    rules = [
        {"rule_id": "REG-CTR-1", "description": "Transactions over $10,000 must be reported (Currency Transaction Report)."},
        {"rule_id": "REG-KYC-2", "description": "Customer identity must be verified before high-risk actions are taken."},
        {"rule_id": "REG-AML-3", "description": "Repeated foreign transactions within 24h must be escalated for AML review."},
        {"rule_id": "REG-PCI-4", "description": "Card data must never be exposed in plaintext in logs or responses."},
    ]
    with open(os.path.join(BASE, "compliance_rules.json"), "w") as f:
        json.dump(rules, f, indent=2)


def gen_products():
    products = [
        {"product_id": "PRD1", "name": "Everyday Checking", "type": "checking", "apy": 0.01},
        {"product_id": "PRD2", "name": "High-Yield Savings", "type": "savings", "apy": 0.045},
        {"product_id": "PRD3", "name": "Platinum Rewards Credit Card", "type": "credit_card", "apy": 0.219},
        {"product_id": "PRD4", "name": "Secure Travel Card", "type": "credit_card", "apy": 0.189},
    ]
    with open(os.path.join(BASE, "products.json"), "w") as f:
        json.dump(products, f, indent=2)


if __name__ == "__main__":
    customers = gen_customers()
    accounts = gen_accounts(customers)
    transactions = gen_transactions(customers, accounts)
    gen_fraud_alerts(customers, transactions)
    gen_tickets(customers)
    gen_faq()
    gen_compliance_rules()
    gen_products()
    print(f"Generated mock data in {BASE}:")
    for fname in sorted(os.listdir(BASE)):
        print(f"  - {fname}")
