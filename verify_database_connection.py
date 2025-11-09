import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Database Configuration ---
# Use the provided database URL directly for verification
DATABASE_URL = "postgresql://postgres:dKEIiFYGNmoUPbHghPYdyFzKZzQQnmCO@postgres.railway.internal:5432/railway"

if not DATABASE_URL:
    logger.error("FATAL: DATABASE_URL is not set.")
    exit(1)

# --- Flask App Setup for SQLAlchemy Context ---
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def verify_connection_and_schema():
    """
    Connects to the database, verifies the connection, and checks the schema
    of the 'automated_facial_analysis' table.
    """
    logger.info("Attempting to connect to the database...")
    
    with app.app_context():
        try:
            # 1. Verify Connection
            db.session.execute(text('SELECT 1'))
            logger.info("✅ Database connection successful!")

            # 2. Verify 'automated_facial_analysis' table and columns
            inspector = inspect(db.engine)
            table_name = 'automated_facial_analysis'

            if inspector.has_table(table_name):
                logger.info(f"✅ Table '{table_name}' exists.")
                
                columns = [col['name'] for col in inspector.get_columns(table_name)]
                logger.info(f"Columns found in '{table_name}': {columns}")

                # Check for the critical 'credits_used' column
                if 'credits_used' in columns:
                    logger.info("✅ SUCCESS: The 'credits_used' column exists in the 'automated_facial_analysis' table.")
                    logger.info("This confirms the database schema is correct.")
                else:
                    logger.error(f"❌ FAILURE: The 'credits_used' column is MISSING from the '{table_name}' table.")
                    logger.error("This is the cause of the error. The database schema is outdated.")

            else:
                logger.error(f"❌ FAILURE: The table '{table_name}' does not exist in the database.")
                logger.error("The application cannot run without this table. Please ensure migrations have run.")

        except Exception as e:
            logger.error(f"❌ An unexpected error occurred during verification: {e}")

if __name__ == '__main__':
    logger.info("--- Starting Database Connection and Schema Verification Script ---")
    verify_connection_and_schema()
    logger.info("--- Verification Script Finished ---")
