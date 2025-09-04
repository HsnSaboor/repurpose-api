#!/usr/bin/env python3
"""
Database migration script to add enhanced transcript metadata columns
"""
import sqlite3
import os
from pathlib import Path

def migrate_database():
    """Add new transcript metadata columns to existing database"""
    
    # Database path
    db_path = Path(__file__).parent.parent / "yt_repurposer.db"
    
    if not db_path.exists():
        print(f"Database not found at {db_path}. Creating new database will include all columns.")
        return
    
    print(f"Migrating database at {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # List of new columns to add
        new_columns = [
            ("transcript_language", "VARCHAR(10)"),
            ("transcript_type", "VARCHAR(20)"),
            ("is_translated", "BOOLEAN DEFAULT 0"),
            ("source_language", "VARCHAR(10)"),
            ("translation_confidence", "REAL"),
            ("transcript_priority", "VARCHAR(20)"),
            ("processing_notes", "TEXT")
        ]
        
        # Check which columns already exist
        cursor.execute("PRAGMA table_info(videos)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        print(f"Existing columns: {existing_columns}")
        
        # Add missing columns
        for column_name, column_type in new_columns:
            if column_name not in existing_columns:
                try:
                    sql = f"ALTER TABLE videos ADD COLUMN {column_name} {column_type}"
                    cursor.execute(sql)
                    print(f"✓ Added column: {column_name}")
                except sqlite3.Error as e:
                    print(f"✗ Failed to add column {column_name}: {e}")
        
        # Create transcript_cache table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transcript_cache (
                id INTEGER PRIMARY KEY,
                video_id VARCHAR(50) NOT NULL,
                language_code VARCHAR(10) NOT NULL,
                transcript_type VARCHAR(20) NOT NULL,
                transcript_text TEXT NOT NULL,
                is_translated BOOLEAN DEFAULT 0,
                source_language VARCHAR(10),
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transcript_cache_video_id 
            ON transcript_cache(video_id)
        """)
        
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_transcript_cache_unique 
            ON transcript_cache(video_id, language_code, transcript_type)
        """)
        
        print("✓ Created transcript_cache table and indexes")
        
        conn.commit()
        print("✓ Database migration completed successfully!")
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()