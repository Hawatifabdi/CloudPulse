from pathlib import Path
import argparse
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "raw" / "access_logs.csv"
OUTPUT = ROOT / "data" / "processed" / "synthetic_logs.csv"

parser = argparse.ArgumentParser()
parser.add_argument("--rows", type=int, default=100_000)
args = parser.parse_args()

if args.rows < 1:
    raise SystemExit("--rows must be at least 1")

rng = np.random.default_rng(42)
source = pd.read_csv(SOURCE)

# Sample existing rows, then vary fields to create a repeatable test workload.
indices = rng.integers(0, len(source), size=args.rows)
df = source.iloc[indices].reset_index(drop=True).copy()

df["timestamp"] = (
    pd.Timestamp("2026-01-01")
    + pd.to_timedelta(
        rng.integers(0, 30 * 24 * 60 * 60, size=args.rows),
        unit="s"
    )
)
df["server_id"] = rng.choice(
    ["web-01", "web-02", "web-03", "api-01"],
    size=args.rows
)
df["response_time_ms"] = rng.integers(5, 3001, size=args.rows)
df["bytes_sent"] = rng.integers(100, 500_001, size=args.rows)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT, index=False)

print(f"Generated {len(df):,} synthetic log records")
print(f"Output: {OUTPUT}")
print(f"File size: {OUTPUT.stat().st_size:,} bytes")
print("Note: synthetic test data, not real production traffic.")
