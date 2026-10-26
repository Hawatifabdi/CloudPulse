SELECT
    path,
    COUNT(*) AS total_requests,
    SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) AS error_count,
    ROUND(
        100.0 * SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END)
        / COUNT(*),
        2
    ) AS error_percentage,
    SUM(CASE WHEN status_code >= 500 THEN 1 ELSE 0 END) AS server_errors
FROM cloudpulse.access_logs
GROUP BY path
HAVING SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) > 0
ORDER BY error_percentage DESC, error_count DESC
LIMIT 10;
