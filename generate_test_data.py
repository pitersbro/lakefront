"""
Generate synthetic Parquet datasets for testing lop.
Simulates schema drift between two versions of an orders table.

Usage:
    python generate_test_data.py
"""
import random
from datetime import datetime, timedelta
from pathlib import Path

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError:
    print("pip install pyarrow")
    raise

random.seed(42)
OUT = Path("test_data/sales")
OUT.mkdir(parents=True, exist_ok=True)


def fake_orders(n: int, include_fraud: bool = False, null_amount_rate: float = 0.04):
    statuses = ["completed", "pending", "cancelled", "refunded"]
    if include_fraud:
        statuses.append("pending_review")  # simulate new value drift

    order_ids = list(range(10_000_001, 10_000_001 + n))
    customer_ids = [random.randint(1, 50_000) for _ in range(n)]
    statuses_col = [random.choice(statuses) for _ in range(n)]
    base = datetime(2024, 1, 1)
    created_at = [base + timedelta(seconds=random.randint(0, 86400 * 365)) for _ in range(n)]
    amounts = [
        None if random.random() < null_amount_rate else round(random.uniform(5, 2000), 2)
        for _ in range(n)
    ]
    discounts = [None if random.random() < 0.45 else round(random.uniform(0, 0.5), 3) for _ in range(n)]

    schema_fields = [
        pa.field("order_id", pa.int64()),
        pa.field("customer_id", pa.int64()),
        pa.field("status", pa.string()),
        pa.field("created_at", pa.timestamp("us")),
        pa.field("amount_usd", pa.float64()),
        pa.field("discount_pct", pa.float64()),
    ]

    arrays = [
        pa.array(order_ids, type=pa.int64()),
        pa.array(customer_ids, type=pa.int64()),
        pa.array(statuses_col, type=pa.string()),
        pa.array(created_at, type=pa.timestamp("us")),
        pa.array(amounts, type=pa.float64()),
        pa.array(discounts, type=pa.float64()),
    ]

    if include_fraud:
        schema_fields.append(pa.field("is_fraud", pa.bool_()))
        arrays.append(pa.array([random.random() < 0.02 for _ in range(n)], type=pa.bool_()))

    schema = pa.schema(schema_fields)
    return pa.table({f.name: arr for f, arr in zip(schema_fields, arrays)}, schema=schema)


print("Generating test_data/sales/orders_2024.parquet (100k rows)…")
t1 = fake_orders(100_000, include_fraud=False, null_amount_rate=0.04)
pq.write_table(t1, OUT / "orders_2024.parquet", compression="snappy")

print("Generating test_data/sales/orders_2025.parquet (120k rows, with drift)…")
t2 = fake_orders(120_000, include_fraud=True, null_amount_rate=0.12)
pq.write_table(t2, OUT / "orders_2025.parquet", compression="snappy")

print("Generating test_data/sales/customers.parquet (50k rows)…")
n = 50_000
customers = pa.table({
    "customer_id": pa.array(range(1, n + 1), type=pa.int64()),
    "country": pa.array([random.choice(["PL", "DE", "US", "FR", "GB"]) for _ in range(n)]),
    "signup_date": pa.array(
        [datetime(2020, 1, 1) + timedelta(days=random.randint(0, 1500)) for _ in range(n)],
        type=pa.timestamp("us")
    ),
    "ltv_usd": pa.array([round(random.uniform(0, 10000), 2) for _ in range(n)], type=pa.float64()),
    "is_active": pa.array([random.random() > 0.2 for _ in range(n)], type=pa.bool_()),
})
pq.write_table(customers, OUT / "customers.parquet", compression="snappy")

print("Done. Run: lop explore test_data/")
