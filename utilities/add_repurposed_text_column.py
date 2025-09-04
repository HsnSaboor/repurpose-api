import sqlite3
import os

DATABASE_FILE = "yt_repurposer.db"

def add_repurposed_text_column():
    """Adds the repurposed_text column to the videos table."""
    db_path = os.path.join(os.getcwd(), DATABASE_FILE)
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("ALTER TABLE videos ADD COLUMN repurposed_text TEXT;")
        conn.commit()
        print("Successfully added 'repurposed_text' column to 'videos' table.")
    except sqlite3.Error as e:
        print(f"Error adding 'repurposed_text' column: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    add_repurposed_text_column()