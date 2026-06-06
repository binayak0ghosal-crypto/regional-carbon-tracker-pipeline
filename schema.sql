-- schema.sql

-- 1. Table for System Users
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    home_country_code VARCHAR(3) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Table for Exchange Rates
CREATE TABLE IF NOT EXISTS exchange_rates (
    rate_id INT AUTO_INCREMENT PRIMARY KEY,
    currency_code VARCHAR(3) NOT NULL UNIQUE,
    rate_to_usd REAL NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Table for Regional Grid Coefficients
CREATE TABLE IF NOT EXISTS regional_emission_factors (
    factor_id INT AUTO_INCREMENT PRIMARY KEY,
    country_code VARCHAR(3) NOT NULL,
    industry_category VARCHAR(100) NOT NULL,
    co2_per_usd_spent REAL NOT NULL,
    source_api VARCHAR(255),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(country_code, industry_category)
);

-- 4. Table for the Live Financial Transaction Ledger
CREATE TABLE IF NOT EXISTS financial_transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    transaction_date TIMESTAMP NOT NULL,
    merchant_name VARCHAR(255),
    industry_category VARCHAR(100) NOT NULL,
    amount_local_currency REAL NOT NULL,
    currency_code VARCHAR(3),
    country_code VARCHAR(3) NOT NULL,
    calculated_co2_kg REAL,
    is_processed BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (currency_code) REFERENCES exchange_rates(currency_code)
);

-- 5. Creating the Advanced Analytics Moving Average View
CREATE OR REPLACE VIEW user_carbon_anomaly_detection AS
WITH transaction_velocity AS (
    SELECT 
        user_id,
        transaction_id,
        transaction_date,
        industry_category,
        calculated_co2_kg,
        -- Window function calculates the average of the 5 preceding transactions
        AVG(calculated_co2_kg) OVER (
            PARTITION BY user_id 
            ORDER BY transaction_date 
            ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING
        ) AS historical_moving_avg
    FROM financial_transactions
    WHERE is_processed = TRUE
)
SELECT 
    user_id,
    transaction_id,
    transaction_date,
    industry_category,
    calculated_co2_kg,
    ROUND(historical_moving_avg, 2) as baseline_avg,
    CASE 
        WHEN calculated_co2_kg > (historical_moving_avg * 2.5) THEN 'CRITICAL ANOMALY: Footprint Spike Detected!'
        WHEN calculated_co2_kg > (historical_moving_avg * 1.5) THEN 'WARNING: Elevated Emission Event'
        ELSE 'Normal Variance'
    END AS anomaly_signature
FROM transaction_velocity;