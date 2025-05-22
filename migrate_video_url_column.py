import sqlite3
import os

DATABASE_FILE = 'yt_repurposer.db'

def migrate_schema():
    """
    Migrates the 'videos' table schema in the SQLite database.
    Renames the 'url' column to 'youtube_video_id'.
    """
    db_path = os.path.join(os.getcwd(), DATABASE_FILE)
    if not os.path.exists(db_path):
        print(f"Error: Database file '{DATABASE_FILE}' not found in the current directory.")
        print(f"Expected at: {db_path}")
        return

    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("Starting schema migration for 'videos' table...")

        # Begin transaction
        cursor.execute("BEGIN TRANSACTION;")
        print("  Transaction started.")

        # 1. Rename the existing videos table to videos_old
        cursor.execute("ALTER TABLE videos RENAME TO videos_old;")
        print("  Renamed 'videos' to 'videos_old'.")

        # 2. Create a new videos table with the corrected schema
        create_table_sql = """
        CREATE TABLE videos (
            id INTEGER PRIMARY KEY NOT NULL,
            video_id VARCHAR NOT NULL,
            youtube_video_id VARCHAR NOT NULL,
            title VARCHAR,
            original_transcript TEXT,
            processed_at DATETIME,
            status VARCHAR
        );
        """
        cursor.execute(create_table_sql)
        print("  Created new 'videos' table with 'youtube_video_id' column.")

        # 3. Copy data from videos_old to the new videos table
        copy_data_sql = """
        INSERT INTO videos (id, video_id, youtube_video_id, title, original_transcript, processed_at, status)
        SELECT id, video_id, url, title, original_transcript, processed_at, status
        FROM videos_old;
        """
        cursor.execute(copy_data_sql)
        print(f"  Copied {cursor.rowcount} rows from 'videos_old' to new 'videos' table.")

        # 4. Drop the videos_old table
        cursor.execute("DROP TABLE videos_old;")
        print("  Dropped 'videos_old' table.")

        # Commit transaction
        conn.commit()
        print("  Transaction committed.")

        print("\nSuccessfully migrated 'videos' table: renamed 'url' to 'youtube_video_id'.")

    except sqlite3.Error as e:
        if conn:
            conn.rollback()
            print(f"  Transaction rolled back due to error.")
        print(f"\nAn error occurred during migration: {e}")
        print("  No changes were made to the database.")
    except Exception as ex:
        if conn:
            conn.rollback()
            print(f"  Transaction rolled back due to an unexpected error.")
        print(f"\nAn unexpected error occurred: {ex}")
        print("  No changes were made to the database.")
    finally:
        if conn:
            conn.close()
            print("  Database connection closed.")

if __name__ == '__main__':
    migrate_schema()