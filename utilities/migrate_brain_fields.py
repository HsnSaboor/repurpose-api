#!/usr/bin/env python3
"""Migration script to add Brain indexing fields to videos table"""

import sqlite3
import os

DATABASE_PATH = "./yt_repurposer.db"

def migrate_videos_table():
    """Add Brain indexing columns to videos table if they don't exist"""
    
    if not os.path.exists(DATABASE_PATH):
        print("Database does not exist. Will be created by init_db().")
        return True
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Get existing columns
    cursor.execute("PRAGMA table_info(videos)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    
    # New columns to add
    new_columns = [
        ("is_indexed", "BOOLEAN DEFAULT 0"),
        ("indexed_at", "DATETIME"),
        ("source_type", "VARCHAR(20)"),
        ("tags", "TEXT"),
        ("topics", "TEXT"),
        ("summary", "TEXT"),
        ("embedding_id", "VARCHAR(100)"),
    ]
    
    added = []
    for col_name, col_type in new_columns:
        if col_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE videos ADD COLUMN {col_name} {col_type}")
                added.append(col_name)
                print(f"✓ Added column: {col_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print(f"  Column {col_name} already exists")
                else:
                    raise
        else:
            print(f"  Column {col_name} already exists")
    
    # Create indexes if they don't exist
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_videos_is_indexed ON videos(is_indexed)")
        print("✓ Created index: idx_videos_is_indexed")
    except sqlite3.OperationalError:
        print("  Index idx_videos_is_indexed already exists")
    
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_videos_source_type ON videos(source_type)")
        print("✓ Created index: idx_videos_source_type")
    except sqlite3.OperationalError:
        print("  Index idx_videos_source_type already exists")
    
    conn.commit()
    conn.close()
    
    if added:
        print(f"\nMigration complete: Added {len(added)} columns")
    else:
        print("\nNo migration needed: All columns exist")
    
    return True


if __name__ == "__main__":
    print("Running videos table migration for Brain indexing fields...")
    print("="*50)
    migrate_videos_table()
    print("="*50)
