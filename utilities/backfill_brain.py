#!/usr/bin/env python3
"""
Utility script to backfill existing videos into Brain knowledge base.

Usage:
    python utilities/backfill_brain.py [--limit N] [--dry-run]
"""

import sys
import os
import argparse
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal, Video
from core.services.brain_service import BrainService
from core.services.content_service import ContentGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def backfill_videos(limit: int = None, dry_run: bool = False, with_topics: bool = True):
    """
    Backfill existing videos into Brain knowledge base.
    
    Args:
        limit: Maximum number of videos to process (None = all)
        dry_run: If True, only report what would be done
        with_topics: If True, extract topics/summary using LLM (requires GEMINI_API_KEY)
    """
    db = SessionLocal()
    brain_service = BrainService(db)
    
    # Get content generator if extracting topics
    content_generator = None
    if with_topics:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if api_key:
            content_generator = ContentGenerator(api_key=api_key)
            logger.info("Topic extraction enabled (GEMINI_API_KEY found)")
        else:
            logger.warning("GEMINI_API_KEY not set - skipping topic extraction")
    
    try:
        # Get videos that are not indexed
        query = db.query(Video).filter(
            Video.is_indexed == False,
            Video.transcript.isnot(None),
            Video.transcript != "",
            Video.transcript != "Transcript unavailable",
        )
        
        total_unindexed = query.count()
        logger.info(f"Found {total_unindexed} videos not indexed in Brain")
        
        if limit:
            query = query.limit(limit)
        
        videos = query.all()
        
        if dry_run:
            logger.info(f"[DRY RUN] Would index {len(videos)} videos:")
            for video in videos[:10]:
                logger.info(f"  - {video.youtube_video_id}: {video.title}")
            if len(videos) > 10:
                logger.info(f"  ... and {len(videos) - 10} more")
            return
        
        indexed_count = 0
        failed_count = 0
        
        for i, video in enumerate(videos, 1):
            try:
                logger.info(f"[{i}/{len(videos)}] Indexing {video.youtube_video_id}: {video.title}")
                
                source = brain_service.index_video_as_source(
                    video,
                    content_generator=content_generator
                )
                
                logger.info(f"  Created source: {source.source_id}")
                indexed_count += 1
                
            except Exception as e:
                logger.error(f"  Failed: {e}")
                failed_count += 1
        
        logger.info("="*50)
        logger.info(f"Backfill complete:")
        logger.info(f"  - Indexed: {indexed_count}")
        logger.info(f"  - Failed: {failed_count}")
        logger.info(f"  - Total remaining: {total_unindexed - indexed_count}")
        
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Backfill videos to Brain knowledge base")
    parser.add_argument("--limit", type=int, default=None, help="Max videos to process")
    parser.add_argument("--dry-run", action="store_true", help="Report only, don't index")
    parser.add_argument("--no-topics", action="store_true", help="Skip topic extraction")
    
    args = parser.parse_args()
    
    backfill_videos(
        limit=args.limit,
        dry_run=args.dry_run,
        with_topics=not args.no_topics,
    )


if __name__ == "__main__":
    main()
