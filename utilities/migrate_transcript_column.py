import sqlite3
import os

DATABASE_FILE = "yt_repurposer.db"

def migrate_column():
    """
    Renames the 'original_transcript' column to 'transcript' in the 'videos' table.
    """
    db_path = os.path.join(os.getcwd(), DATABASE_FILE)
    if not os.path.exists(db_path):
        print(f"Error: Database file '{DATABASE_FILE}' not found in the current directory.")
        return

    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("Starting migration: Renaming 'original_transcript' to 'transcript' in 'videos' table...")

        # 1. Begin a transaction
        cursor.execute("BEGIN TRANSACTION;")
        print("  1. Began transaction.")

        # 2. Rename the existing videos table
        cursor.execute("ALTER TABLE videos RENAME TO videos_old_for_transcript_migration;")
        print("  2. Renamed 'videos' to 'videos_old_for_transcript_migration'.")

        # 3. Create the new videos table with the corrected schema
        create_table_sql = """
        CREATE TABLE videos (
            id INTEGER PRIMARY KEY NOT NULL,
            video_id VARCHAR NOT NULL,
            youtube_video_id VARCHAR NOT NULL,
            title VARCHAR,
            transcript TEXT,
            processed_at DATETIME,
            status VARCHAR
        );
        """
        cursor.execute(create_table_sql)
        print("  3. Created new 'videos' table with 'transcript' column.")

        # 4. Copy data from the old table to the new table
        copy_data_sql = """
        INSERT INTO videos (id, video_id, youtube_video_id, title, transcript, processed_at, status)
        SELECT id, video_id, youtube_video_id, title, original_transcript, processed_at, status
        FROM videos_old_for_transcript_migration;
        """
        cursor.execute(copy_data_sql)
        print(f"  4. Copied {cursor.rowcount} rows from 'videos_old_for_transcript_migration' to new 'videos' table.")

        # 5. Drop the old table
        cursor.execute("DROP TABLE videos_old_for_transcript_migration;")
        print("  5. Dropped 'videos_old_for_transcript_migration' table.")

        # 6. Commit the transaction
        conn.commit()
        print("  6. Committed transaction.")

        print("\nSuccessfully migrated 'videos' table: renamed 'original_transcript' to 'transcript'.")

    except sqlite3.Error as e:
        if conn:
            conn.rollback()
            print(f"\nAn error occurred: {e}")
            print("Transaction rolled back.")
        else:
            print(f"\nAn error occurred before establishing a database connection: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    migrate_column()