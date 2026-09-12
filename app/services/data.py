import csv
from pathlib import Path
DATA = Path(__file__).resolve().parents[2] / "data"

def load_rows(name):
    with open(DATA / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def customer(customer_id):
    return next((r for r in load_rows("customers.csv") if r["customer_id"] == customer_id), None)

def order_for_customer(customer_id):
    rows = [r for r in load_rows("orders.csv") if r["customer_id"] == customer_id]
    return rows[0] if rows else None

def shipment_for_order(order_id):
    return next((r for r in load_rows("shipments.csv") if r["order_id"] == order_id), None)

def tickets_for_customer(customer_id):
    return [r for r in load_rows("tickets.csv") if r["customer_id"] == customer_id]

def policies():
    return load_rows("policies.csv")
