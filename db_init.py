# db_init.py
import mysql.connector
from config import DB_PARAMS

def initialize_system():
    # 1. Create a temporary connection parameters dictionary without the database name
    # This prevents the "Unknown database" error by connecting to the server first
    temp_params = DB_PARAMS.copy()
    if "database" in temp_params:
        del temp_params["database"]
        
    print("Connecting to MySQL Server...")
    conn = mysql.connector.connect(**temp_params)
    cursor = conn.cursor()
    
    # 2. Safely create the database environment if it does not exist
    print("Creating database 'carbon_enterprise' if it doesn't exist...")
    cursor.execute("CREATE DATABASE IF NOT EXISTS carbon_enterprise;")
    cursor.execute("USE carbon_enterprise;")
    
    # 3. Read and split the schema.sql file
    print("Reading schema.sql configuration script...")
    with open('schema.sql', 'r') as f:
        schema_sql = f.read()
        
    sql_commands = schema_sql.split(';')
    
    print("Building database structures and Analytics View...")
    for command in sql_commands:
        if command.strip():
            cursor.execute(command)
            
    print("Database structures complete.")
    
    # 4. Seed Mock User
    cursor.execute("""
        INSERT IGNORE INTO users (username, email, home_country_code) 
        VALUES ('eco_warrior', 'player@earth.com', 'USA');
    """)
    
    # 5. Seed Global Exchange Rates
    exchange_data = [('USD', 1.0), ('EUR', 1.08), ('INR', 0.012)]
    for curr, rate in exchange_data:
        cursor.execute("""
            INSERT INTO exchange_rates (currency_code, rate_to_usd) 
            VALUES (%s, %s) ON DUPLICATE KEY UPDATE rate_to_usd = VALUES(rate_to_usd);
        """, (curr, rate))

    # 6. Seed Regional Industry Carbon Intensities
    factors = [
        ('USA', 'Energy', 0.55),
        ('USA', 'Transportation', 0.82),
        ('FRA', 'Energy', 0.09),         
        ('FRA', 'Transportation', 0.70),
        ('IND', 'Energy', 0.78),         
        ('IND', 'Transportation', 0.88)
    ]
    for country, industry, co2_val in factors:
        cursor.execute("""
            INSERT IGNORE INTO regional_emission_factors (country_code, industry_category, co2_per_usd_spent) 
            VALUES (%s, %s, %s);
        """, (country, industry, co2_val))

    # 7. Seed Raw, Unprocessed Transactions for testing
    mock_txs = [
        (1, '2026-06-01 10:00:00', 'Duke Energy', 'Energy', 120.00, 'USD', 'USA'),
        (1, '2026-06-02 11:30:00', 'EDF Nuclear', 'Energy', 110.00, 'EUR', 'FRA'),
        (1, '2026-06-03 14:15:00', 'Adani Power', 'Energy', 8000.00, 'INR', 'IND'),
        (1, '2026-06-04 09:00:00', 'Private Jet Charter', 'Transportation', 5000.00, 'USD', 'USA')
    ]
    for tx in mock_txs:
        cursor.execute("""
            INSERT INTO financial_transactions 
            (user_id, transaction_date, merchant_name, industry_category, amount_local_currency, currency_code, country_code)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, tx)

    conn.commit()
    cursor.close()
    conn.close()
    print("Database seeding phase completely successful!")

if __name__ == "__main__":
    initialize_system()