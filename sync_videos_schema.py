import sqlite3
import importlib.util
from pathlib import Path
import logging
import sys

# --- Configuration ---
DB_PATH = "yt_repurposer.db"
# Assumes database.py is in the same directory as this script,
# or in a location findable by Python's import mechanism relative to CWD.
# If running from project root, and database.py is also in root, this is fine.
MODEL_FILE_PATH = "database.py"
MODEL_CLASS_NAME = "Video"
TABLE_NAME = "videos"

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_sqlalchemy_type_to_sqlite_type(col_type_obj, col_name):
    """Maps SQLAlchemy column types to simplified SQLite types."""
    try:
        # Dynamically import SQLAlchemy types to avoid hard dependency if module not found initially
        from sqlalchemy.sql import sqltypes
        from sqlalchemy import Integer, String, Text, DateTime, Boolean, Float, Numeric, Enum
    except ImportError:
        logging.error("SQLAlchemy is not installed or not found in PYTHONPATH. This script requires SQLAlchemy to inspect model types.")
        logging.error("Please install SQLAlchemy in your environment (e.g., 'pip install SQLAlchemy') and try again.")
        raise # Propagate error to stop script

    if isinstance(col_type_obj, (sqltypes.Integer, Integer)):
        return "INTEGER"
    elif isinstance(col_type_obj, (sqltypes.String, String)):
        return "VARCHAR"
    elif isinstance(col_type_obj, (sqltypes.Text, Text)):
        return "TEXT"
    elif isinstance(col_type_obj, (sqltypes.DateTime, DateTime)):
        return "DATETIME"
    elif isinstance(col_type_obj, (sqltypes.Boolean, Boolean)):
        return "BOOLEAN"
    elif isinstance(col_type_obj, (sqltypes.Float, Float, sqltypes.Numeric, Numeric)):
        return "REAL"
    elif isinstance(col_type_obj, Enum):
        logging.info(f"  SQLAlchemy Enum type for column '{col_name}' will be mapped to TEXT.")
        return "TEXT"
    else:
        logging.warning(f"  Unhandled SQLAlchemy type '{type(col_type_obj).__name__}' for column '{col_name}'. Defaulting to TEXT.")
        return "TEXT"

def get_expected_schema_from_model():
    """Loads database.py, inspects the Video model, and returns its schema."""
    expected_schema = {}
    logging.info(f"Attempting to load model '{MODEL_CLASS_NAME}' from '{MODEL_FILE_PATH}'...")

    model_file_abs_path = Path(MODEL_FILE_PATH).resolve()
    if not model_file_abs_path.exists():
        logging.error(f"Model file '{model_file_abs_path}' not found. Cannot proceed.")
        return {}
        
    model_dir = str(model_file_abs_path.parent)
    original_sys_path = list(sys.path)
    if model_dir not in sys.path:
        sys.path.insert(0, model_dir)

    try:
        spec = importlib.util.spec_from_file_location("db_model_module", str(model_file_abs_path))
        if spec is None or spec.loader is None:
            logging.error(f"Could not create spec for module at '{model_file_abs_path}'.")
            return {}
        
        db_module = importlib.util.module_from_spec(spec)
        sys.modules['db_model_module'] = db_module # Add to sys.modules before execution
        
        spec.loader.exec_module(db_module)

        VideoModel = getattr(db_module, MODEL_CLASS_NAME, None)
        if VideoModel is None:
            logging.error(f"Class '{MODEL_CLASS_NAME}' not found in '{MODEL_FILE_PATH}'. Available: {dir(db_module)}")
            return {}

        if not hasattr(VideoModel, "__table__") or not hasattr(VideoModel.__table__, "columns"):
            logging.error(f"'{MODEL_CLASS_NAME}' does not appear to be a valid SQLAlchemy model with a __table__ attribute.")
            return {}

        logging.info(f"Successfully loaded model '{MODEL_CLASS_NAME}'. Inspecting columns...")
        for column in VideoModel.__table__.columns:
            col_name = column.name
            sqlite_type = get_sqlalchemy_type_to_sqlite_type(column.type, col_name)
            expected_schema[col_name] = sqlite_type
            logging.info(f"  Model column: {col_name} (SQLAlchemy type: {type(column.type).__name__}) -> SQLite type: {sqlite_type}")
        
    except ImportError as e:
        logging.error(f"ImportError while loading model or its dependencies (e.g., SQLAlchemy): {e}")
        logging.error("Ensure SQLAlchemy and other dependencies of database.py are installed and accessible.")
        return {}
    except Exception as e:
        logging.error(f"Error inspecting model from '{MODEL_FILE_PATH}': {e}", exc_info=True)
        return {}
    finally:
        sys.path = original_sys_path # Restore original sys.path
        if 'db_model_module' in sys.modules:
            del sys.modules['db_model_module']


    if not expected_schema:
        logging.error(f"Could not derive schema from model '{MODEL_CLASS_NAME}'.")
    return expected_schema

def get_current_db_schema(conn):
    """Connects to the DB and returns the current schema of the videos table."""
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{TABLE_NAME}';")
        if not cursor.fetchone():
            logging.warning(f"Table '{TABLE_NAME}' does not exist in the database '{DB_PATH}'.")
            return None 

        cursor.execute(f"PRAGMA table_info('{TABLE_NAME}');")
        current_schema = {row[1]: str(row[2]).upper() for row in cursor.fetchall()}
        logging.info(f"Current DB schema for '{TABLE_NAME}': {current_schema}")
        return current_schema
    except sqlite3.Error as e:
        logging.error(f"SQLite error getting table info for '{TABLE_NAME}': {e}")
        raise

def sync_schema():
    """Main function to synchronize the database schema with the model."""
    logging.info(f"Starting schema synchronization for table '{TABLE_NAME}' in database '{DB_PATH}'.")
    logging.warning(f"IMPORTANT: Please ensure you have backed up '{DB_PATH}' before running this script.")

    expected_schema = get_expected_schema_from_model()
    if not expected_schema:
        logging.error("Failed to get expected schema from model. Aborting synchronization.")
        return

    if not Path(DB_PATH).exists():
        logging.error(f"Database file '{DB_PATH}' not found. Aborting.")
        return

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        conn.execute("BEGIN TRANSACTION;")

        current_schema_db = get_current_db_schema(conn)
        if current_schema_db is None:
            logging.error(f"Table '{TABLE_NAME}' does not exist. This script synchronizes an existing table. Please create it first.")
            conn.execute("ROLLBACK;")
            return
        
        model_has_created_at = "created_at" in expected_schema
        db_has_created_at = "created_at" in current_schema_db
        db_has_processed_at = "processed_at" in current_schema_db
        needs_rename_migration = model_has_created_at and not db_has_created_at and db_has_processed_at

        if needs_rename_migration:
            logging.info("Performing rename migration: 'processed_at' (DB) -> 'created_at' (Model).")
            temp_table_name = f"{TABLE_NAME}_temp_sync_migration"
            
            try:
                cursor.execute(f"ALTER TABLE \"{TABLE_NAME}\" RENAME TO \"{temp_table_name}\";")
                logging.info(f"  Renamed '{TABLE_NAME}' to '{temp_table_name}'.")

                column_defs = []
                for name, type_ in expected_schema.items():
                    pk_def = ""
                    if name == "id" and expected_schema.get("id") == "INTEGER": # Basic PK assumption
                         pk_def = " PRIMARY KEY"
                    column_defs.append(f"\"{name}\" {type_}{pk_def}")
                
                create_table_sql = f"CREATE TABLE \"{TABLE_NAME}\" ({', '.join(column_defs)});"
                logging.info(f"  Executing: {create_table_sql}")
                cursor.execute(create_table_sql)
                logging.info(f"  Created new '{TABLE_NAME}' table with expected schema.")

                cursor.execute(f"PRAGMA table_info(\"{temp_table_name}\");")
                temp_table_columns_info = {row[1]: row for row in cursor.fetchall()}
                
                model_column_names_ordered = list(expected_schema.keys())
                select_expressions = []
                for model_col_name in model_column_names_ordered:
                    if model_col_name == "created_at" and "processed_at" in temp_table_columns_info:
                        select_expressions.append("processed_at")
                    elif model_col_name in temp_table_columns_info:
                        select_expressions.append(model_col_name)
                    else:
                        select_expressions.append("NULL") # For new columns not in old table
                
                insert_cols_str = ', '.join([f'"{c}"' for c in model_column_names_ordered])
                select_cols_str = ', '.join([f'"{c}"' if c != "NULL" else "NULL" for c in select_expressions])
                insert_sql = f"INSERT INTO \"{TABLE_NAME}\" ({insert_cols_str}) SELECT {select_cols_str} FROM \"{temp_table_name}\";"
                logging.info(f"  Executing data migration: {insert_sql}")
                cursor.execute(insert_sql)
                
                cursor.execute(f"DROP TABLE \"{temp_table_name}\";")
                logging.info(f"  Dropped temporary table '{temp_table_name}'.")
                logging.info("Rename migration for 'created_at' completed.")
                current_schema_db = get_current_db_schema(conn) # Refresh schema
            except Exception as e_mig:
                logging.error(f"Error during rename migration: {e_mig}", exc_info=True)
                logging.error("Rolling back transaction due to migration error.")
                conn.execute("ROLLBACK;") # Rollback on migration error
                return 

        # Add other missing columns
        for col_name, col_type in expected_schema.items():
            if col_name not in current_schema_db:
                add_sql = f"ALTER TABLE \"{TABLE_NAME}\" ADD COLUMN \"{col_name}\" {col_type};"
                try:
                    logging.info(f"Adding column '{col_name} {col_type}' to '{TABLE_NAME}'. Executing: {add_sql}")
                    cursor.execute(add_sql)
                    logging.info(f"  Successfully added column '{col_name}'.")
                except sqlite3.Error as e_add:
                    # Check if column now exists (e.g. if rename created it)
                    # This specific check might be redundant if current_schema_db was refreshed after migration
                    logging.error(f"  Failed to add column '{col_name}': {e_add}.")
                    # Re-check current schema to see if it was added by rename or other means
                    check_schema_again = get_current_db_schema(conn)
                    if check_schema_again and col_name in check_schema_again:
                         logging.info(f"  Column '{col_name}' appears to exist now. Continuing.")
                    else:
                         raise # Re-raise if it's a genuine persistent error
            else:
                logging.info(f"Column '{col_name}' already exists in '{TABLE_NAME}'. DB type: {current_schema_db[col_name]}, Model expects: {col_type}.")
                if current_schema_db[col_name].upper() != col_type.upper():
                    logging.warning(f"  Type mismatch for column '{col_name}'. DB: {current_schema_db[col_name]}, Model: {col_type}. SQLite has limited type alteration support.")
        
        db_only_columns = set(current_schema_db.keys()) - set(expected_schema.keys())
        if db_only_columns:
            logging.info(f"Columns in DB table '{TABLE_NAME}' but not in model '{MODEL_CLASS_NAME}': {', '.join(db_only_columns)}. These were not modified.")

        conn.execute("COMMIT;")
        logging.info("Schema synchronization process finished successfully.")

    except sqlite3.Error as e:
        logging.error(f"SQLite error during synchronization: {e}", exc_info=True)
        if conn:
            try: conn.execute("ROLLBACK;") 
            except sqlite3.Error: logging.error("Failed to rollback transaction.")
    except ImportError: 
        logging.error("Synchronization aborted due to missing SQLAlchemy (ImportError).")
        # No conn.rollback() needed as transaction wouldn't have started or error handled before.
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
        if conn:
            try: conn.execute("ROLLBACK;")
            except sqlite3.Error: logging.error("Failed to rollback transaction on unexpected error.")
    finally:
        if conn:
            conn.close()
            logging.info("Database connection closed.")

if __name__ == "__main__":
    sync_schema()