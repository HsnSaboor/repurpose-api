import sqlite3

DB_FILE = "yt_repurposer.db"

def inspect_videos_table_schema():
    """Connects to the SQLite database and prints the schema of the 'videos' table."""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        print(f"Inspecting schema for table 'videos' in database '{DB_FILE}':")
        cursor.execute("PRAGMA table_info(videos);")
        rows = cursor.fetchall()
        if rows:
            print("Columns:")
            for row in rows:
                # row format: (cid, name, type, notnull, dflt_value, pk)
                print(f"  - Name: {row[1]}, Type: {row[2]}, NotNull: {row[3]}, Default: {row[4]}, PK: {row[5]}")
        else:
            print("Table 'videos' not found or has no columns.")
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    inspect_videos_table_schema()