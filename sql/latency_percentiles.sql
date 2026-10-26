SELECT
    COUNT(*) AS total_requests,
    ROUND(approx_percentile(response_time_ms, 0.50), 2) AS p50_ms,
    ROUND(approx_percentile(response_time_ms, 0.95), 2) AS p95_ms,
    ROUND(approx_percentile(response_time_ms, 0.99), 2) AS p99_ms,
    MAX(response_time_ms) AS max_ms
FROM cloudpulse.access_logs;
