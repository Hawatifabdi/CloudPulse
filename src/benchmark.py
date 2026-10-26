
from pathlib import Path
import time
import duckdb

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "raw" / "access_logs.csv"
PARQUET = ROOT / "data" / "processed" / "access_logs.parquet"

con = duckdb.connect()

queries = {
    "CSV": f"""
        SELECT status_code, COUNT(*) AS requests
        FROM read_csv_auto('{CSV.as_posix()}')
        GROUP BY status_code
    """,
    "Parquet": f"""
        SELECT status_code, COUNT(*) AS requests
        FROM read_parquet('{PARQUET.as_posix()}')
        GROUP BY status_code
    """,
}

for name, sql in queries.items():
    # Warm up the query engine, then measure repeated executions.
    con.execute(sql)
    timings = []
    for _ in range(5):
        start = time.perf_counter()
        result = con.execute(sql).df()
        timings.append(time.perf_counter() - start)

    print(f"{name}: median query time = {sorted(timings)[len(timings)//2]:.6f}s")
    print(result.to_string(index=False))

print(f"\nCSV size: {CSV.stat().st_size:,} bytes")
print(f"Parquet size: {PARQUET.stat().st_size:,} bytes")
con.close()
