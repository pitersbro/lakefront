# lop — Lakehouse Observability Platform

A terminal-first data quality and schema drift tool for Parquet datasets.
Inspired by lazygit's keyboard-driven UX. Powered by DuckDB.

```
┌─ lop ─────────────────────────────────────────────────────────────────────┐
│  files              │ schema  preview  sql  drift                          │
│  ▾ warehouse/       │ #  column       type       nulls    distinct  drift  │
│    ▾ sales/         │ 1  order_id     INT64      0%       100%      ok     │
│    ◆ orders_2025 ●  │ 2  customer_id  INT64      0%       34.2%     ok     │
│    ◆ returns        │ 3  status       VARCHAR    3%       7         ⚠ vals │
│    ◆ customers      │ 4  created_at   TIMESTAMP  0%       99.8%     ok     │
│  ▸ raw/             │ 5  amount_usd   FLOAT64    12%      88.1%     ⚠ null │
│                     │ 6  is_fraud     BOOLEAN    0%       2         + new  │
│  snapshots          ├─────────────────────────────────────────────────────┤
│  ● today 14:32      │ order_id — stats                                     │
│  ● yesterday        │ rows     48,291,004   nulls   0 (0.00%)              │
│                     │ min      10000001     max     58291004                │
│                     │ dist     ▁▂▃▄▆▇█▇▆▄                                 │
└─ j/k move · 1-4 tabs · s snapshot · d drift · r refresh · q quit ─────────┘
```

## Install

```bash
pip install lop
# or from source:
git clone https://github.com/you/lop
cd lop
pip install -e .
```

## Usage

```bash
# Open TUI in current directory
lop explore .

# Open TUI on a specific path
lop explore ~/data/warehouse/

# Profile a file without TUI (outputs JSON)
lop snapshot orders.parquet

# Show drift vs last snapshot
lop diff orders.parquet
```

## Keybindings

| Key | Action |
|-----|--------|
| `j` / `k` | Move file cursor down / up |
| `h` / `l` | Focus sidebar / content |
| `1` | Schema tab |
| `2` | Preview tab (first 100 rows) |
| `3` | SQL tab (write against `data`) |
| `4` | Drift tab |
| `s` | Take snapshot of current file |
| `d` | Show drift vs last snapshot |
| `r` | Refresh / re-profile |
| `?` | Show keybinding help |
| `q` | Quit |

## SQL Tab

The SQL tab exposes the current file as a view called `data`. You can write any DuckDB SQL:

```sql
SELECT status, COUNT(*), AVG(amount_usd)
FROM data
WHERE created_at > '2024-01-01'
GROUP BY 1
ORDER BY 2 DESC
```

Press `ctrl+r` to run.

## How snapshots work

Snapshots are stored in `~/.lop/meta.db` (a local DuckDB file).
Every time you profile a file (`s` key or `lop snapshot`), a snapshot is saved.
Drift is computed by comparing the latest two snapshots for a given file path.

## S3 support

DuckDB handles S3 natively. Set your credentials via environment variables:

```bash
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_DEFAULT_REGION=us-east-1

lop explore s3://my-bucket/warehouse/
```

## Architecture

```
lop/
├── __main__.py   # CLI entrypoint (typer)
├── engine.py     # DuckDB: profiling, snapshots, drift detection
├── app.py        # Textual app: layout, keybindings, reactive state
└── widgets.py    # Reusable TUI widgets
```

The engine is fully decoupled from the TUI — you can use it as a library:

```python
from lop.engine import Engine

eng = Engine()
profile = eng.profile("orders.parquet")
drift   = eng.drift("orders.parquet")
```
