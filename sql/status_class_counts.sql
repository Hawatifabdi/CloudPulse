SELECT
    status_class,
    COUNT(*) AS request_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM cloudpulse.access_logs
GROUP BY status_class
ORDER BY status_class;
