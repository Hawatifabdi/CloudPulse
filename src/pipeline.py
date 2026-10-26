
from pathlib import Path
import json
import time

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "access_logs.csv"
PROCESSED = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"

PROCESSED.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)

PARQUET = PROCESSED / "access_logs.parquet"
DB = ROOT / "cloudpulse.duckdb"

REQUIRED = [
    "timestamp", "server_id", "method", "path", "status_code",
    "response_time_ms", "bytes_sent", "user_agent", "ip_address",
    "referrer",
]


def main():
    if not RAW.exists():
        raise FileNotFoundError(f"Missing source file: {RAW}")

    df = pd.read_csv(RAW)
    missing = set(REQUIRED) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    source_rows = len(df)

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    for col in ["server_id", "status_code", "response_time_ms", "bytes_sent"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["method"] = df["method"].astype("string").str.strip().str.upper()
    df["path"] = df["path"].astype("string").str.strip()

    # Keep records with valid timestamps, status codes and measurements.
    valid = (
        df["timestamp"].notna()
        & df["status_code"].between(100, 599)
        & df["response_time_ms"].ge(0)
        & df["bytes_sent"].ge(0)
        & df["method"].notna()
        & df["path"].notna()
    )
    invalid_rows = int((~valid).sum())
    df = df.loc[valid].copy()

    # Remove exact duplicate records.
    before_dedup = len(df)
    df = df.drop_duplicates()
    duplicate_rows = before_dedup - len(df)

    df["date"] = df["timestamp"].dt.date.astype(str)
    df["hour"] = df["timestamp"].dt.hour
    df["status_class"] = (df["status_code"] // 100).astype(str) + "xx"
    df["is_error"] = df["status_code"].ge(400)
    df["is_slow"] = df["response_time_ms"].ge(1000)

    # Write the cleaned data as compressed Parquet.
    df.to_parquet(PARQUET, index=False, compression="snappy")

    con = duckdb.connect(str(DB))
    con.execute("CREATE OR REPLACE TABLE access_logs AS SELECT * FROM read_parquet(?)", [str(PARQUET)])

    summary = {
        "source_file": RAW.name,
        "source_rows": source_rows,
        "clean_rows": len(df),
        "invalid_rows_removed": invalid_rows,
        "duplicate_rows_removed": duplicate_rows,
        "parquet_bytes": PARQUET.stat().st_size,
        "csv_bytes": RAW.stat().st_size,
        "processed_at_utc": pd.Timestamp.now(tz="UTC").isoformat(),
    }

    (REPORTS / "data_quality.json").write_text(json.dumps(summary, indent=2))

    print("\n=== CloudPulse Pipeline ===")
    print(json.dumps(summary, indent=2))
    print("\n=== HTTP Status Summary ===")
    print(con.execute("""
        SELECT status_code, COUNT(*) AS requests
        FROM access_logs
        GROUP BY status_code
        ORDER BY requests DESC
    """).df().to_string(index=False))

    con.close()


if __name__ == "__main__":
    main()
