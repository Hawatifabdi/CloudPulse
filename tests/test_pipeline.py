from pathlib import Path
import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PARQUET = ROOT / "data" / "processed" / "access_logs.parquet"


def test_processed_file_exists():
    assert PARQUET.exists()


def test_processed_data_has_required_columns():
    df = pd.read_parquet(PARQUET)
    required = {
        "timestamp", "server_id", "method", "path",
        "status_code", "response_time_ms", "bytes_sent",
        "status_class", "is_error", "is_slow"
    }
    assert required.issubset(df.columns)


def test_processed_data_has_valid_values():
    df = pd.read_parquet(PARQUET)
    assert df["timestamp"].notna().all()
    assert df["status_code"].between(100, 599).all()
    assert (df["response_time_ms"] >= 0).all()
    assert (df["bytes_sent"] >= 0).all()


def test_duckdb_can_query_processed_data():
    con = duckdb.connect()
    count = con.execute(
        "SELECT COUNT(*) FROM read_parquet(?)",
        [str(PARQUET)]
    ).fetchone()[0]
    con.close()
    assert count > 0
