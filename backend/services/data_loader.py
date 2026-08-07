"""
Central data-loading layer. Every service reads through here.
Swap these functions for real DB/API calls later without changing
route or agent code (see CustomerService/FraudService/etc.).
"""
import json
import csv
import os
from functools import lru_cache

BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mock_data")


def _load_json(filename):
    path = os.path.join(BASE, filename)
    with open(path, "r") as f:
        return json.load(f)


def _load_csv(filename):
    path = os.path.join(BASE, filename)
    with open(path, "r", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def load_customers():
    return _load_json("customers.json")


def load_accounts():
    return _load_json("accounts.json")


def load_transactions():
    rows = _load_csv("transactions.csv")
    for r in rows:
        r["amount"] = float(r["amount"])
        r["is_foreign"] = r["is_foreign"] in ("True", "true", "1")
    return rows


def load_fraud_alerts():
    return _load_json("fraud_alerts.json")


def load_tickets():
    return _load_json("tickets.json")


def load_faq():
    return _load_json("faq.json")


def load_compliance_rules():
    return _load_json("compliance_rules.json")


def load_products():
    return _load_json("products.json")


def save_fraud_alerts(alerts):
    path = os.path.join(BASE, "fraud_alerts.json")
    with open(path, "w") as f:
        json.dump(alerts, f, indent=2)


def save_tickets(tickets):
    path = os.path.join(BASE, "tickets.json")
    with open(path, "w") as f:
        json.dump(tickets, f, indent=2)
