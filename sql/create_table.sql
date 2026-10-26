CREATE EXTERNAL TABLE IF NOT EXISTS cloudpulse.access_logs (
    `timestamp` TIMESTAMP,
    server_id BIGINT,
    method STRING,
    path STRING,
    status_code BIGINT,
    response_time_ms BIGINT,
    bytes_sent BIGINT,
    user_agent STRING,
    ip_address STRING,
    referrer STRING,
    `date` STRING,
    hour INT,
    status_class STRING,
    is_error BOOLEAN,
    is_slow BOOLEAN
)
STORED AS PARQUET
LOCATION 's3://YOUR_CLOUDPULSE_BUCKET/data/';
