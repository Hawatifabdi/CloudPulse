# CloudPulse

CloudPulse is a Python-based web server log analytics and observability project. It processes HTTP access logs, analyzes traffic and error patterns, identifies slow endpoints, and benchmarks CSV against compressed Parquet storage.

## Features

- Data cleaning and validation using Pandas
- Analytical SQL queries using DuckDB
- Compressed Parquet storage
- Interactive dashboard built with Streamlit and Plotly
- Automated data-quality tests using pytest
- CSV versus Parquet performance benchmarks
- Synthetic workload generation for scaling experiments

## Technology Stack

- **Language:** Python
- **Data processing:** Pandas
- **Analytics:** DuckDB
- **Storage:** CSV, Apache Parquet, PyArrow
- **Dashboard:** Streamlit, Plotly
- **Testing:** pytest

## Architecture

1. Load HTTP access logs from a CSV file.
2. Validate fields, convert data types, remove duplicate records, and derive analytical fields.
3. Store cleaned records in Parquet format.
4. Query the processed data using DuckDB.
5. Analyze traffic patterns, HTTP errors, and endpoint response times.
6. Display metrics through the Streamlit dashboard.
7. Benchmark query latency and storage size across data formats.

## Performance Results

The following results were measured locally using 100,000 synthetic log records.

| Metric | CSV | Parquet |
|---|---:|---:|
| File size | 14.39 MB | 1.42 MB |
| Median query time | 58.209 ms | 2.134 ms |

For the tested HTTP status-code aggregation, Parquet used approximately **90.1% less storage**, and the query ran approximately **27.27 times faster** than the CSV version.

Both formats returned identical HTTP status-code counts.

These results apply to the specific query, dataset, and local environment tested. Performance improvements will vary depending on the workload and configuration.

## Data

The access-log dataset contains fields such as:

- Timestamp
- Server identifier
- HTTP method
- Request path
- HTTP status code
- Response time
- Bytes sent
- User agent
- IP address
- Referrer

The larger benchmark dataset is synthetically generated test data, not real production traffic.

Raw and generated datasets are excluded from version control. Check the original dataset's redistribution terms before sharing it.

## Getting Started

### Prerequisites

- Python 3
- Git (optional, for version control)

### 1. Clone the repository

If you have published the project on GitHub:

```bash
git clone <your-repository-url>
cd cloudpulse
```

Alternatively, navigate to your existing local project directory.

### 2. Create and activate a virtual environment

On Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install pandas duckdb pyarrow streamlit plotly pytest
```

### 4. Prepare the input data

Place the source CSV file at:

```text
data/raw/access_logs.csv
```

The file must contain the columns expected by `src/pipeline.py`.

### 5. Process the logs

```bash
python src/pipeline.py
```

This runs the data-processing pipeline and generates the processed data and associated local outputs.

### 6. Run the analytics

```bash
python src/analytics.py
```

### 7. Launch the dashboard

```bash
streamlit run src/app.py
```

Open the local URL printed in the terminal by Streamlit.

### 8. Run automated tests

```bash
python -m pytest -v
```

The current test suite checks that the processed Parquet file exists, required columns are present, values are valid, and DuckDB can query the processed data.

### 9. Reproduce the benchmarks

Run the small-dataset benchmark:

```bash
python src/benchmark.py
```

Generate a larger synthetic dataset:

```bash
python src/generate_data.py --rows 100000
```

Benchmark the larger dataset:

```bash
python src/benchmark_scale.py
```

The benchmark scripts report query timing and storage-size comparisons for the tested data formats.

## Project Structure

```text
cloudpulse/
├── data/
│   ├── raw/
│   └── processed/
├── reports/
├── src/
│   ├── analytics.py
│   ├── app.py
│   ├── benchmark.py
│   ├── benchmark_scale.py
│   ├── generate_data.py
│   └── pipeline.py
├── tests/
│   └── test_pipeline.py
├── .gitignore
└── README.md
```

Generated datasets, local database files, and reports may be created when running the pipeline and benchmarks. They are excluded from version control by the project's `.gitignore` configuration.

## Testing

The current test suite contains four checks covering:

- Processed Parquet file existence
- Required columns
- Valid data values
- Successful DuckDB queries

Run the tests with:

```bash
python -m pytest -v
```

## AWS Analytics

CloudPulse extends the local analytics workflow to AWS:

- **Amazon S3:** Stores the processed Parquet access logs.
- **Amazon Athena:** Runs serverless SQL queries against the Parquet data.
- **Local dashboard:** Streamlit and Plotly provide interactive visualizations without requiring a cloud-hosted dashboard.

The Athena database is `cloudpulse`, and the external table is `cloudpulse.access_logs`. SQL scripts for creating the database and table, analysing HTTP status codes, measuring latency, identifying slow endpoints, and examining endpoint errors are available in `sql/`.

### Cloud Validation

The local DuckDB results were compared with Athena results for the same 5,000-request dataset.

- Total requests: 5,000 in both systems.
- Total errors: 707 in both systems.
- Client errors (4xx): 597.
- Server errors (5xx): 110.
- Maximum response time: 7,510 ms in both systems.

Latency percentiles differed slightly because DuckDB's `quantile_cont` and Athena's `approx_percentile` use different calculation methods. See `reports/aws_validation.md` for the comparison.

The dataset is synthetic, so these findings validate the workflow rather than describe real production traffic.

### AWS Cost and Access Notes

- Athena query results are written to the S3 location configured for the query.
- Keep S3 Block Public Access enabled.
- Avoid uploading credentials, secrets, or unnecessary datasets to version control.
- Athena and S3 usage may incur charges. Review the AWS billing dashboard and remove only project resources you no longer need.

## Future Work

Potential extensions include:

- Adding more comprehensive data-quality checks
- Improving dashboard filtering and observability metrics
- Testing additional query patterns and larger synthetic datasets

## Disclaimer

CloudPulse is an educational portfolio project. The synthetic benchmark results are specific to the tested workload and local environment and do not represent production performance guarantees.
