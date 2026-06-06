# etl_engine.py
import mysql.connector
from config import DB_PARAMS

def run_etl_pipeline():
    conn = mysql.connector.connect(**DB_PARAMS)
    cursor = conn.cursor()
    
    # 1. EXTRACT: Find pending transactions that haven't been calculated yet
    cursor.execute("""
        SELECT transaction_id, amount_local_currency, currency_code, country_code, industry_category
        FROM financial_transactions 
        WHERE is_processed = FALSE;
    """)
    unprocessed_records = cursor.fetchall()
    
    if not unprocessed_records:
        print("Pipeline reporting: Complete. No data requires transformations.")
        conn.close()
        return

    # 2. TRANSFORM: Process carbon impacts normalized to currency & context
    for record in unprocessed_records:
        tx_id, local_amount, currency, country, category = record
        
        # Get matching dollar conversion scaling rate
        cursor.execute("SELECT rate_to_usd FROM exchange_rates WHERE currency_code = %s", (currency,))
        rate_res = cursor.fetchone()
        rate_to_usd = rate_res[0] if rate_res else 1.0
        
        normalized_usd_amount = local_amount * rate_to_usd
        
        # Pull context-aware regional coefficient values
        cursor.execute("""
            SELECT co2_per_usd_spent FROM regional_emission_factors 
            WHERE country_code = %s AND industry_category = %s
        """, (country, category))
        factor_res = cursor.fetchone()
        co2_factor = factor_res[0] if factor_res else 0.35 # Fallback safety default
        
        # Run calculation
        final_co2_mass = normalized_usd_amount * co2_factor
        
        # 3. LOAD: Save each calculated value back down into production records
        cursor.execute("""
            UPDATE financial_transactions 
            SET calculated_co2_kg = %s, is_processed = TRUE 
            WHERE transaction_id = %s;
        """, (final_co2_mass, tx_id))

    conn.commit()
    print(f"ETL Execution Phase: Complete. Normalized {len(unprocessed_records)} logs.")
    
    # Fetch Data back out using our SQL Window Function Analytics View
    print("\n--- FETCHING PIPELINE ANOMALY ANALYSIS ---")
    cursor.execute("SELECT transaction_id, industry_category, calculated_co2_kg, baseline_avg, anomaly_signature FROM user_carbon_anomaly_detection;")
    
    for analysis in cursor.fetchall():
        tx_id, cat, co2, baseline, alert_status = analysis
        print(f"TX ID: {tx_id} | {cat} | Current: {co2:.1f}kg CO2 | 5-Day Historical Baseline: {baseline or 0.0}kg")
        print(f"   Status Evaluation -> {alert_status}\n")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    run_etl_pipeline()