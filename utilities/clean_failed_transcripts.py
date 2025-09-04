#!/usr/bin/env python3
"""
Clean up database records with failed transcripts
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.database import Video, init_db

def clean_failed_transcripts():
    """Remove records with 'Transcript unavailable' so they can be re-fetched"""
    
    # Initialize database
    init_db()
    
    # Create session
    DATABASE_URL = "sqlite:///./yt_repurposer.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    try:
        # Find records with failed transcripts
        failed_records = db.query(Video).filter(
            Video.transcript == "Transcript unavailable"
        ).all()
        
        print(f"Found {len(failed_records)} records with failed transcripts:")
        
        for record in failed_records:
            print(f"  - ID: {record.id}, Video ID: {record.youtube_video_id}, Title: {record.title}")
        
        if failed_records:
            response = input(f"\\nDelete these {len(failed_records)} records? (y/N): ")
            if response.lower() == 'y':
                for record in failed_records:
                    db.delete(record)
                db.commit()
                print(f"✅ Deleted {len(failed_records)} records.")
            else:
                print("❌ No records deleted.")
        else:
            print("✅ No failed transcript records found.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clean_failed_transcripts()