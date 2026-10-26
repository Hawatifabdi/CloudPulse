# CloudPulse: Local and AWS Validation

## Objective
Validate AWS Athena analytics against local DuckDB analytics
using the same 5,000-request access-log dataset.

## Results

| Metric | DuckDB | Athena |
|---|---:|---:|
| Total requests | 5,000 | 5,000 |
| Total errors | 707 | 707 |
| 4xx errors | 597 | 597 |
| 5xx errors | 110 | 110 |
| p50 latency | 90 ms | 91 ms |
| p95 latency | 627.1 ms | 626 ms |
| p99 latency | 1,459.04 ms | 1,474 ms |
| Maximum latency | 7,510 ms | 7,510 ms |

## Findings
- Request and error counts matched exactly.
- Maximum response time matched exactly.
- Latency percentile estimates differed slightly because
  DuckDB quantile_cont and Athena approx_percentile use
  different percentile calculation methods.

## Architecture
- Local processing and analytics: Python, Pandas, DuckDB.
- Columnar data format: Apache Parquet.
- Cloud storage: Amazon S3.
- Cloud SQL analytics: Amazon Athena.

## Dataset limitation
The access logs are synthetic. Findings demonstrate the
analytics workflow and are not production incident evidence.
