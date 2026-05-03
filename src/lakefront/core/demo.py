from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path


def ensure_demo_project() -> None:
    """Create the built-in demo project with sample data if it doesn't already exist."""
    from lakefront import models
    from lakefront.core.config import PROJECTS_DIR, ProjectConfigurationService

    if "demo" in ProjectConfigurationService.list_projects():
        return

    ProjectConfigurationService.create("demo", description="Built-in sample datasets")

    data_dir = PROJECTS_DIR / "demo" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    _write_orders(data_dir / "orders.csv")
    _write_customers(data_dir / "customers.csv")

    for name, path, desc in [
        ("orders", str(data_dir / "orders.csv"), "Sample orders (500 rows)"),
        ("customers", str(data_dir / "customers.csv"), "Sample customers (200 rows)"),
    ]:
        ProjectConfigurationService.add_source(
            "demo", models.DataSource(name=name, path=path, description=desc)
        )


def _write_orders(path: Path) -> None:
    rng = random.Random(42)
    statuses = ["completed", "pending", "cancelled", "refunded"]
    base = datetime(2024, 1, 1)
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["order_id", "customer_id", "status", "created_at", "amount_usd", "discount_pct"]
        )
        for i in range(500):
            writer.writerow([
                10_000_001 + i,
                rng.randint(1, 200),
                rng.choice(statuses),
                (base + timedelta(seconds=rng.randint(0, 86400 * 365))).isoformat(),
                round(rng.uniform(5, 2000), 2) if rng.random() > 0.04 else "",
                round(rng.uniform(0, 0.5), 3) if rng.random() > 0.45 else "",
            ])


def _write_customers(path: Path) -> None:
    rng = random.Random(42)
    countries = ["PL", "DE", "US", "FR", "GB"]
    base = datetime(2020, 1, 1)
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["customer_id", "country", "signup_date", "ltv_usd", "is_active"])
        for i in range(1, 201):
            writer.writerow([
                i,
                rng.choice(countries),
                (base + timedelta(days=rng.randint(0, 1500))).date().isoformat(),
                round(rng.uniform(0, 10000), 2),
                rng.random() > 0.2,
            ])
