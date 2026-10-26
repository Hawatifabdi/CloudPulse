from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "cloudpulse.duckdb"

def main():
    if not DB.exists():
        raise SystemExit(
            "Database not found. Run: python src/pipeline.py"
        )

    con = duckdb.connect(str(DB), read_only=True)

    queries = {
        "Hourly traffic": """
            SELECT date_trunc('hour', timestamp) AS hour,
                   COUNT(*) AS requests
            FROM access_logs
            GROUP BY date_trunc('hour', timestamp)
            ORDER BY hour
            LIMIT 10
        """,
        "HTTP errors by server": """
            SELECT server_id,
                   COUNT(*) AS total_requests,
                   COUNT(*) FILTER (WHERE status_code >= 400) AS errors,
                   ROUND(
                       100.0 * COUNT(*) FILTER (WHERE status_code >= 400)
                       / NULLIF(COUNT(*), 0), 2
                   ) AS error_rate_percent
            FROM access_logs
            GROUP BY server_id
            ORDER BY error_rate_percent DESC
        """,
        "Slowest endpoints": """
            SELECT path,
                   COUNT(*) AS requests,
                   ROUND(quantile_cont(response_time_ms, 0.95), 2)
                       AS p95_response_ms
            FROM access_logs
            GROUP BY path
            HAVING COUNT(*) >= 5
            ORDER BY p95_response_ms DESC
            LIMIT 10
        """,
    }

    try:
        for title, sql in queries.items():
            print(f"\n=== {title} ===")
            print(con.execute(sql).df().to_string(index=False))
    finally:
        con.close()

if __name__ == "__main__":
    main()
