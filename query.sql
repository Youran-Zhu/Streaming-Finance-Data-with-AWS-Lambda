WITH T1 AS 
    (SELECT name,
         high,
         ts,
         SUBSTRING(ts,
         12,
         2) AS hour_of_day
    FROM finance_data_p3), T2 AS 
    (SELECT T1.name AS company_name,
         MAX(T1.high) AS high_price_hour,
         T1.hour_of_day AS hour_of_day
    FROM T1
    GROUP BY  T1.name, T1.hour_of_day)
SELECT T2.company_name,
         T2.high_price_hour,
         T2.hour_of_day,
         T1.ts
FROM T1, T2
WHERE T1.name = T2.company_name
        AND T1.high = T2.high_price_hour
        AND T1.hour_of_day = T2.hour_of_day
ORDER BY  T2.company_name, T2.hour_of_day 
