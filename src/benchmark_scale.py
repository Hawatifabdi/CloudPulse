from pathlib import Path
import time
import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "processed" / "synthetic_logs.csv"
PARQUET = ROOT / "data" / "processed" / "synthetic_logs.parquet"

# Convert the synthetic CSV to Parquet once.
con = duckdb.connect()
con.execute(
    "COPY (SELECT * FROM read_csv_auto(?)) TO ? (FORMAT PARQUET, COMPRESSION ZSTD)",
    [str(CSV), str(PARQUET)]
)

queries = {
    "CSV": "SELECT status_code, COUNT(*) AS requests "
           "FROM read_csv_auto(?) GROUP BY status_code",
    "Parquet": "SELECT status_code, COUNT(*) AS requests "
               "FROM read_parquet(?) GROUP BY status_code",
}

print(f"Rows: {len(pd.read_csv(CSV, usecols=['status_code'])):,}")
print()

results = {}
for name, sql in queries.items():
    path = str(CSV if name == "CSV" else PARQUET)

    # Warm-up, then five timed runs.
    con.execute(sql, [path]).fetchall()
    timings = []

    for _ in range(5):
        start = time.perf_counter()
        result = con.execute(sql, [path]).fetchall()
        timings.append(time.perf_counter() - start)

    median = sorted(timings)[len(timings) // 2]
    results[name] = median
    print(f"{name}: median query time = {median * 1000:.3f} ms")
    print(f"Status counts: {sorted(result)}")
    print()

csv_size = CSV.stat().st_size
parquet_size = PARQUET.stat().st_size

print(f"CSV size:     {csv_size:,} bytes")
print(f"Parquet size: {parquet_size:,} bytes")
print(f"Space saved:  {(1 - parquet_size / csv_size) * 100:.1f}%")

if results["Parquet"] > 0:
    print(f"Speed ratio:  {results['CSV'] / results['Parquet']:.2f}x")

con.close()
