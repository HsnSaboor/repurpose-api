#!/usr/bin/env python3
"""
Database reader to get content piece IDs for editing
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.database import Video, init_db
import json

def get_content_pieces_from_db(video_id: str):
    """Read content pieces from database for a specific video"""
    
    # Initialize database
    init_db()
    
    # Create session
    DATABASE_URL = "sqlite:///./yt_repurposer.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    try:
        # Find the video
        db_video = db.query(Video).filter(Video.youtube_video_id == video_id).first()
        
        if not db_video:
            print(f"❌ Video with ID '{video_id}' not found in database.")
            return []
        
        if not db_video.repurposed_text:
            print(f"❌ No content pieces found for video '{video_id}'.")
            return []
        
        print(f"✅ Found video: {db_video.title}")
        print(f"📊 Database ID: {db_video.id}")
        print(f"🎬 YouTube ID: {db_video.youtube_video_id}")
        print("-" * 80)
        
        # Parse the stored content pieces
        try:
            # Extract content pieces from repurposed_text
            content_pieces_section = db_video.repurposed_text.split("Content Pieces:")[-1].strip()
            content_pieces_json_parts = content_pieces_section.split("\\n\\n---\\n\\n")
            
            content_pieces = []
            
            for i, piece_json in enumerate(content_pieces_json_parts, 1):
                if piece_json.strip():
                    try:
                        piece_data = json.loads(piece_json.strip())
                        content_pieces.append(piece_data)
                        
                        content_id = piece_data.get('content_id', 'Unknown')
                        content_type = piece_data.get('content_type', 'Unknown')
                        title = piece_data.get('title', 'No title')
                        
                        print(f"{i}. ID: {content_id}")
                        print(f"   Type: {content_type}")
                        print(f"   Title: {title}")
                        
                        if content_type == 'reel':
                            caption = piece_data.get('caption', '')
                            print(f"   Caption ({len(caption)} chars): {caption[:100]}...")
                        elif content_type == 'tweet':
                            tweet_text = piece_data.get('tweet_text', '')
                            print(f"   Tweet ({len(tweet_text)} chars): {tweet_text}")
                        elif content_type == 'image_carousel':
                            caption = piece_data.get('caption', '')
                            slides = piece_data.get('slides', [])
                            print(f"   Caption ({len(caption)} chars): {caption[:100]}...")
                            print(f"   Slides: {len(slides)}")
                        
                        print("-" * 40)
                        
                    except json.JSONDecodeError as e:
                        print(f"❌ Failed to parse piece {i}: {e}")
                        continue
            
            return content_pieces
            
        except Exception as e:
            print(f"❌ Failed to parse content pieces: {e}")
            return []
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return []
    finally:
        db.close()

if __name__ == "__main__":
    video_id = "7Un6mV2YQ54"
    print(f"🔍 Reading content pieces for video: {video_id}")
    print("=" * 80)
    
    content_pieces = get_content_pieces_from_db(video_id)
    
    if content_pieces:
        print(f"\\n📋 Summary: Found {len(content_pieces)} content pieces")
        print("\\n🎯 To edit piece #7 (Sourdough Discard tweet), use:")
        if len(content_pieces) >= 7:
            piece_7 = content_pieces[6]  # 0-indexed
            content_id = piece_7.get('content_id')
            print(f"   Content ID: {content_id}")
            print(f"   Content Type: {piece_7.get('content_type')}")
            print(f"   Title: {piece_7.get('title')}")
        else:
            print(f"   ❌ Piece #7 not found (only {len(content_pieces)} pieces available)")
    else:
        print("\\n❌ No content pieces found.")