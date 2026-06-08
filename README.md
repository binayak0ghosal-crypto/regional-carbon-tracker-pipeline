Régional-carbon-tracker-pipeline
A context-aware financial ETL carbon tracking pipeline built with Python and MySQL

Context-Aware Regional Carbon Footprint Pipeline

This is a production-ready ETL (Extract, Transform, Load) data pipeline made with Python and MySQL. The system automatically takes in financial transactions, normalizes multi-currency expenses, applies carbon-intensity factors based on regional energy grids, and uses SQL Window Functions to flag environmental anomalies in real-time.

Tech Stack & Skills Highlight
*   Programming Language: Python 3.12+
*   Database Management: MySQL (Workbench)
*   Python Drivers: mysql-connector-python
*   SQL Concepts: Common Table Expressions (CTEs), Window Functions (AVG() OVER), Relational Database Normalization, View Creation.
*   Design: ETL Pipeline Design, Data Normalization.

Key Features

1.  Context-Aware Regional Carbon Math
    The pipeline understands that spending money in different countries has different environmental implications. For example, $100 in electricity consumed within a country with a clean nuclear grid like France, generates a vastly lower CO2 amount compared to $100 in electricity consumed from a coal-heavy grid.

2.  Multi-Currency Normalization
    The system relies on a dynamic table of world currency exchange rates to swiftly convert local currencies like EUR or INR, into a baseline USD before applying carbon calculations.

3.  Automated Anomaly Detection (SQL Window Functions)
    Instead of static thresholds, the system relies on a custom SQL View, which is derived using a window function. This function calculates a user's 5-day historical rolling baseline and sorts transactions by:
    *   Normal Variance: Transactions which stay within the usual historic trend.
    *   Elevated Emission Event: transactions that exceed the rolling average by more than 1.5x.
    *   Critical Anomaly: A massive deviation in emissions that goes above 2.5x the normal footprint of the user (i.e.,private travel)

Project Architecture
*   config.py: Contains database connection information centrally.
*   schema.sql: Contains core relational schemas and the definition of the analytics View.
*   db_init.py: Connects to server, creates database schema, and adds mock transaction data.
*   etl_engine.py: Main script, responsible for extracting untreated rows, applying carbon math, updating database and retrieving anomaly tracking analysis.


git clone https://github.com/binayak0ghosal-crypto/regional-carbon-tracker-pipeline.git
cd regional-carbon-tracker-pipeline

