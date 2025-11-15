"""
Transcript Caching Functions
"""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging


def get_cache_key(video_id: str, language_code: str, transcript_type: str) -> str:
    """Generate a unique cache key for transcript data"""
    return f"{video_id}_{language_code}_{transcript_type}"


def get_cached_transcript(video_id: str, language_code: str, transcript_type: str, db_session: Optional[Session] = None) -> Optional[str]:
    """Retrieve cached transcript data"""
    if not db_session:
        return None
    
    try:
        from core.database import TranscriptCache
        
        cache_entry = db_session.query(TranscriptCache).filter(
            TranscriptCache.video_id == video_id,
            TranscriptCache.language_code == language_code,
            TranscriptCache.transcript_type == transcript_type
        ).first()
        
        if cache_entry:
            # Check if cache is still valid (7 days)
            cache_age = datetime.utcnow() - cache_entry.cached_at
            if cache_age < timedelta(days=7):
                logging.info(f"Cache hit for {video_id} ({language_code}, {transcript_type})")
                return cache_entry.transcript_text
            else:
                # Cache expired, remove it
                db_session.delete(cache_entry)
                db_session.commit()
                logging.info(f"Cache expired and removed for {video_id}")
        
        return None
        
    except Exception as e:
        logging.error(f"Error retrieving cached transcript: {e}")
        return None


def cache_transcript(video_id: str, language_code: str, transcript_type: str, transcript_text: str, 
                    is_translated: bool = False, source_language: Optional[str] = None, 
                    db_session: Optional[Session] = None) -> bool:
    """Cache transcript data for future use"""
    if not db_session:
        return False
    
    try:
        from core.database import TranscriptCache
        
        # Check if entry already exists
        existing_entry = db_session.query(TranscriptCache).filter(
            TranscriptCache.video_id == video_id,
            TranscriptCache.language_code == language_code,
            TranscriptCache.transcript_type == transcript_type
        ).first()
        
        if existing_entry:
            # Update existing entry
            existing_entry.transcript_text = transcript_text
            existing_entry.is_translated = is_translated
            existing_entry.source_language = source_language
            existing_entry.cached_at = datetime.utcnow()
        else:
            # Create new cache entry
            cache_entry = TranscriptCache(
                video_id=video_id,
                language_code=language_code,
                transcript_type=transcript_type,
                transcript_text=transcript_text,
                is_translated=is_translated,
                source_language=source_language
            )
            db_session.add(cache_entry)
        
        db_session.commit()
        logging.info(f"Cached transcript for {video_id} ({language_code}, {transcript_type})")
        return True
        
    except Exception as e:
        logging.error(f"Error caching transcript: {e}")
        db_session.rollback()
        return False


def clear_expired_cache(db_session: Optional[Session] = None, days_old: int = 7) -> int:
    """Clear expired cache entries"""
    if not db_session:
        return 0
    
    try:
        from core.database import TranscriptCache
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        expired_entries = db_session.query(TranscriptCache).filter(
            TranscriptCache.cached_at < cutoff_date
        )
        
        count = expired_entries.count()
        expired_entries.delete()
        db_session.commit()
        
        logging.info(f"Cleared {count} expired cache entries")
        return count
        
    except Exception as e:
        logging.error(f"Error clearing expired cache: {e}")
        db_session.rollback()
        return 0


def get_cache_statistics(db_session: Optional[Session] = None) -> Dict[str, Any]:
    """Get statistics about the transcript cache"""
    if not db_session:
        return {"error": "No database session provided"}
    
    try:
        from core.database import TranscriptCache
        
        total_entries = db_session.query(TranscriptCache).count()
        
        # Count by language
        from sqlalchemy import func
        language_counts = db_session.query(
            TranscriptCache.language_code,
            func.count(TranscriptCache.id).label('count')
        ).group_by(TranscriptCache.language_code).all()
        
        # Count by type
        type_counts = db_session.query(
            TranscriptCache.transcript_type,
            func.count(TranscriptCache.id).label('count')
        ).group_by(TranscriptCache.transcript_type).all()
        
        # Count translated vs original
        translated_count = db_session.query(TranscriptCache).filter(
            TranscriptCache.is_translated == True
        ).count()
        
        # Average cache age
        now = datetime.utcnow()
        caches = db_session.query(TranscriptCache).all()
        if caches:
            avg_age_seconds = sum((now - c.cached_at).total_seconds() for c in caches) / len(caches)
            avg_age_hours = avg_age_seconds / 3600
        else:
            avg_age_hours = 0
        
        return {
            "total_entries": total_entries,
            "by_language": {lang: count for lang, count in language_counts},
            "by_type": {t_type: count for t_type, count in type_counts},
            "translated_count": translated_count,
            "original_count": total_entries - translated_count,
            "average_age_hours": round(avg_age_hours, 2)
        }
        
    except Exception as e:
        logging.error(f"Error getting cache statistics: {e}")
        return {"error": str(e)}


def cleanup_cache(db_session: Optional[Session] = None, max_entries: int = 1000) -> Dict[str, int]:
    """Clean up cache to keep only most recent entries"""
    if not db_session:
        return {"error": "No database session"}
    
    try:
        from core.database import TranscriptCache
        
        total_entries = db_session.query(TranscriptCache).count()
        
        if total_entries <= max_entries:
            return {
                "total_entries": total_entries,
                "deleted": 0,
                "remaining": total_entries
            }
        
        # Get entries to keep (most recent)
        entries_to_delete_count = total_entries - max_entries
        
        # Delete oldest entries
        oldest_entries = db_session.query(TranscriptCache).order_by(
            TranscriptCache.cached_at.asc()
        ).limit(entries_to_delete_count).all()
        
        for entry in oldest_entries:
            db_session.delete(entry)
        
        db_session.commit()
        
        return {
            "total_entries": total_entries,
            "deleted": entries_to_delete_count,
            "remaining": max_entries
        }
        
    except Exception as e:
        logging.error(f"Error cleaning up cache: {e}")
        db_session.rollback()
        return {"error": str(e)}
