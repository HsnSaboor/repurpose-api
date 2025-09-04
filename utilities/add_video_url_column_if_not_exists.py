import sqlite3

DATABASE_NAME = "yt_repurposer.db"

def column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

def add_video_url_column():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        if not column_exists(cursor, "videos", "video_url"):
            print("Adding 'video_url' column to 'videos' table...")
            cursor.execute("ALTER TABLE videos ADD COLUMN video_url TEXT")
            conn.commit()
            print("'video_url' column added successfully.")
        else:
            print("'video_url' column already exists in 'videos' table.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    add_video_url_column()