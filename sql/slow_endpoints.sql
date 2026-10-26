SELECT
    path,
    COUNT(*) AS request_count,
    ROUND(AVG(response_time_ms), 2) AS avg_response_ms,
    MAX(response_time_ms) AS max_response_ms,
    SUM(CASE WHEN is_slow THEN 1 ELSE 0 END) AS slow_requests
FROM cloudpulse.access_logs
GROUP BY path
ORDER BY avg_response_ms DESC
LIMIT 10;
