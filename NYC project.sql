-- =====================================================
-- 1.TABLE CREATION
-- =====================================================
CREATE TABLE housing_violations (
    violation_id BIGINT PRIMARY KEY,
    borough VARCHAR(50),
    postcode VARCHAR(10),
    class VARCHAR(10),
    inspection_date VARCHAR(20),   
    current_status VARCHAR(100)
);


CREATE TABLE service_requests_311 (
    unique_key BIGINT PRIMARY KEY,
    created_date VARCHAR(30),
    complaint_type VARCHAR(100),
    descriptor TEXT,
    incident_zip VARCHAR(10),
    status VARCHAR(50),
    resolution TEXT,
    borough VARCHAR(50),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6)
);

CREATE TABLE population_forecast (
    borough VARCHAR(100),
    population_2020 INTEGER,
    population_2030 INTEGER,
    population_2040 INTEGER
);

-- =====================================================
-- 2️.DATA VALIDATION & PREVIEW
-- =====================================================

SELECT COUNT(*) AS total_rows FROM housing_violations;
SELECT COUNT(*) AS total_rows FROM service_requests_311;
SELECT COUNT(*) AS total_rows FROM population_forecast;

SELECT * FROM housing_violations LIMIT 5;
SELECT * FROM service_requests_311 LIMIT 5;
SELECT * FROM population_forecast LIMIT 5;


-- =====================================================
-- 3️.DATA CLEANING & STANDARDIZATION
-- =====================================================

UPDATE housing_violations
SET borough = UPPER(TRIM(borough));

UPDATE service_requests_311
SET borough = UPPER(TRIM(borough));

UPDATE population_forecast
SET borough = UPPER(TRIM(borough));

UPDATE housing_violations
SET borough = 'MANHATTAN'
WHERE borough LIKE 'MN%';


-- =====================================================
-- 4️.ANALYTICAL VIEW CREATION
-- =====================================================
CREATE VIEW nyc_housing_summary AS
SELECT 
    h.borough,
    COUNT(DISTINCT h.violation_id) AS total_violations,
    COUNT(DISTINCT s.unique_key) AS total_complaints,
    p.population_2020,
    ROUND(COUNT(DISTINCT s.unique_key)::NUMERIC / p.population_2020 * 100000, 2) AS complaints_per_100k
FROM housing_violations h
JOIN service_requests_311 s
    ON h.borough = s.borough
JOIN population_forecast p
    ON h.borough = p.borough
GROUP BY h.borough, p.population_2020;


-- =====================================================
-- 5️.SQL ANALYSIS & INSIGHTS
-- =====================================================
SELECT borough, COUNT(*) AS total_violations
FROM housing_violations
GROUP BY borough
ORDER BY total_violations DESC;


SELECT complaint_type, COUNT(*) AS total_complaints
FROM service_requests_311
GROUP BY complaint_type
ORDER BY total_complaints DESC
LIMIT 5;


SELECT 
    p.borough,
    COUNT(DISTINCT s.unique_key) AS total_complaints,
    p.population_2020,
    ROUND(COUNT(DISTINCT s.unique_key)::NUMERIC / p.population_2020 * 100000, 2) AS complaints_per_100k
FROM service_requests_311 s
JOIN population_forecast p
    ON s.borough = p.borough
GROUP BY p.borough, p.population_2020
ORDER BY complaints_per_100k DESC;

SELECT 
    incident_zip,
    COUNT(*) AS total_complaints
FROM service_requests_311
WHERE incident_zip IS NOT NULL
GROUP BY incident_zip
ORDER BY total_complaints DESC
LIMIT 10;

SELECT 
    current_status,
    COUNT(*) AS total_cases
FROM housing_violations
WHERE current_status IS NOT NULL
GROUP BY current_status
ORDER BY total_cases DESC;








