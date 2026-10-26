SELECT status_code, COUNT(*) AS request_count
FROM cloudpulse.access_logs
GROUP BY status_code
ORDER BY request_count DESC;
