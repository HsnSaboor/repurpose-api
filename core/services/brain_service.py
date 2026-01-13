"""Brain Knowledge Base Service

Provides operations for managing Brain sources and generating content
using the knowledge base.
"""

import json
import uuid
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from core.database import BrainSource, BrainSession, Video, SessionLocal


logger = logging.getLogger(__name__)


class BrainService:
    """Service for Brain knowledge base operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # =========================================================================
    # Source CRUD Operations
    # =========================================================================
    
    def create_source(
        self,
        title: str,
        content: str,
        source_type: str,
        summary: Optional[str] = None,
        topics: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        source_metadata: Optional[Dict[str, Any]] = None,
    ) -> BrainSource:
        """Create a new Brain source"""
        source_id = f"src_{uuid.uuid4().hex[:12]}"
        
        source = BrainSource(
            source_id=source_id,
            source_type=source_type,
            title=title,
            content=content,
            summary=summary,
            topics=json.dumps(topics) if topics else None,
            tags=json.dumps(tags) if tags else None,
            source_metadata=json.dumps(source_metadata) if source_metadata else None,
            use_count=0,
        )
        
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        
        logger.info(f"Created Brain source: {source_id}")
        return source
    
    def get_source(self, source_id: str) -> Optional[BrainSource]:
        """Get a source by ID"""
        return self.db.query(BrainSource).filter(
            BrainSource.source_id == source_id
        ).first()
    
    def get_sources(
        self,
        source_types: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        topics: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[BrainSource], int]:
        """Get sources with optional filters, returns (sources, total_count)"""
        query = self.db.query(BrainSource)
        
        if source_types:
            query = query.filter(BrainSource.source_type.in_(source_types))
        
        if tags:
            tag_conditions = []
            for tag in tags:
                tag_conditions.append(BrainSource.tags.contains(f'"{tag}"'))
            query = query.filter(or_(*tag_conditions))
        
        if topics:
            topic_conditions = []
            for topic in topics:
                topic_conditions.append(BrainSource.topics.contains(f'"{topic}"'))
            query = query.filter(or_(*topic_conditions))
        
        total = query.count()
        sources = query.order_by(BrainSource.updated_at.desc()).offset(offset).limit(limit).all()
        
        return sources, total
    
    def update_source(
        self,
        source_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        summary: Optional[str] = None,
        topics: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        source_metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[BrainSource]:
        """Update a Brain source"""
        source = self.get_source(source_id)
        if not source:
            return None
        
        if title is not None:
            source.title = title
        if content is not None:
            source.content = content
        if summary is not None:
            source.summary = summary
        if topics is not None:
            source.topics = json.dumps(topics)
        if tags is not None:
            source.tags = json.dumps(tags)
        if source_metadata is not None:
            source.source_metadata = json.dumps(source_metadata)
        
        source.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(source)
        
        logger.info(f"Updated Brain source: {source_id}")
        return source
    
    def delete_source(self, source_id: str) -> bool:
        """Delete a Brain source"""
        source = self.get_source(source_id)
        if not source:
            return False
        
        self.db.delete(source)
        self.db.commit()
        
        logger.info(f"Deleted Brain source: {source_id}")
        return True
    
    def increment_use_count(self, source_id: str) -> None:
        """Increment the use count for a source"""
        source = self.get_source(source_id)
        if source:
            source.use_count += 1
            source.last_used_at = datetime.now(timezone.utc)
            self.db.commit()
    
    # =========================================================================
    # Source Indexing
    # =========================================================================
    
    def index_source(
        self,
        source: BrainSource,
        content_generator: Any = None,
    ) -> BrainSource:
        """
        Index a source: extract topics, generate summary, create embedding.
        
        Args:
            source: The source to index
            content_generator: Optional ContentGenerator for LLM calls
        """
        if content_generator:
            # Extract topics and summary using LLM
            extracted = self._extract_topics_and_summary(
                source.content,
                source.title,
                content_generator
            )
            
            if extracted:
                source.topics = json.dumps(extracted.get("topics", []))
                source.summary = extracted.get("summary", "")
        
        # TODO: Generate embedding when vector store is implemented
        # source.embedding = self._generate_embedding(source.content)
        
        source.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(source)
        
        logger.info(f"Indexed Brain source: {source.source_id}")
        return source
    
    def _extract_topics_and_summary(
        self,
        content: str,
        title: str,
        content_generator: Any,
    ) -> Optional[Dict[str, Any]]:
        """Extract topics and generate summary using LLM"""
        system_prompt = """You are a content analyzer. Extract key topics and generate a concise summary.
        
Return a JSON object with:
- "topics": array of 3-7 topic keywords/phrases
- "summary": concise summary (200-500 characters)

Focus on themes, concepts, and key ideas that would help match this content with user needs."""
        
        user_prompt = f"""Analyze this content:

Title: {title}

Content:
{content[:4000]}  # Limit content length

Extract topics and summary."""
        
        return content_generator.generate_content(system_prompt, user_prompt)
    
    # =========================================================================
    # Search Operations
    # =========================================================================
    
    def search_sources(
        self,
        query: str,
        source_types: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        topics: Optional[List[str]] = None,
        limit: int = 10,
        min_score: float = 0.3,
    ) -> List[Dict[str, Any]]:
        """
        Search sources using keyword matching.
        
        TODO: Implement semantic search with embeddings when vector store is ready.
        """
        sources, _ = self.get_sources(
            source_types=source_types,
            tags=tags,
            topics=topics,
            limit=limit * 3,  # Get more to filter by relevance
        )
        
        results = []
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        for source in sources:
            score = self._calculate_relevance_score(source, query_lower, query_words)
            
            if score >= min_score:
                results.append({
                    "source": source,
                    "score": score,
                    "snippet": self._get_relevant_snippet(source.content, query_lower),
                })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
    
    def _calculate_relevance_score(
        self,
        source: BrainSource,
        query_lower: str,
        query_words: set,
    ) -> float:
        """Calculate relevance score for a source based on query matching"""
        score = 0.0
        
        # Title match (high weight)
        title_lower = source.title.lower()
        if query_lower in title_lower:
            score += 0.4
        else:
            title_words = set(title_lower.split())
            word_overlap = len(query_words & title_words) / max(len(query_words), 1)
            score += 0.3 * word_overlap
        
        # Content match
        content_lower = source.content.lower()
        if query_lower in content_lower:
            score += 0.3
        else:
            # Count word occurrences
            content_words = set(content_lower.split())
            word_overlap = len(query_words & content_words) / max(len(query_words), 1)
            score += 0.2 * word_overlap
        
        # Topic match
        if source.topics:
            topics = json.loads(source.topics)
            topics_lower = [t.lower() for t in topics]
            for topic in topics_lower:
                if any(w in topic for w in query_words):
                    score += 0.1
                    break
        
        # Tag match
        if source.tags:
            tags = json.loads(source.tags)
            tags_lower = [t.lower() for t in tags]
            for tag in tags_lower:
                if any(w in tag for w in query_words):
                    score += 0.1
                    break
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _get_relevant_snippet(self, content: str, query: str, snippet_length: int = 200) -> str:
        """Extract a relevant snippet from content"""
        content_lower = content.lower()
        query_pos = content_lower.find(query)
        
        if query_pos == -1:
            # Query not found, return beginning of content
            return content[:snippet_length] + "..." if len(content) > snippet_length else content
        
        # Center snippet around query
        start = max(0, query_pos - snippet_length // 2)
        end = min(len(content), start + snippet_length)
        
        snippet = content[start:end]
        
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."
        
        return snippet
    
    # =========================================================================
    # Vision-Based Matching
    # =========================================================================
    
    def get_relevant_sources(
        self,
        user_vision: str,
        max_sources: int = 5,
        min_score: float = 0.5,
        source_types: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Find sources relevant to user's vision/idea.
        Uses keyword matching for now, will use semantic similarity later.
        """
        return self.search_sources(
            query=user_vision,
            source_types=source_types,
            limit=max_sources,
            min_score=min_score,
        )
    
    # =========================================================================
    # Session Management
    # =========================================================================
    
    def create_session(
        self,
        mode: str,
        user_vision: Optional[str] = None,
        selected_source_ids: Optional[List[str]] = None,
        requested_count: Optional[int] = None,
        style_preset: Optional[str] = None,
        content_types: Optional[List[str]] = None,
    ) -> BrainSession:
        """Create a new generation session"""
        session_id = f"sess_{uuid.uuid4().hex[:12]}"
        
        session = BrainSession(
            session_id=session_id,
            mode=mode,
            user_vision=user_vision,
            selected_source_ids=json.dumps(selected_source_ids) if selected_source_ids else None,
            requested_count=requested_count,
            style_preset=style_preset,
            content_types=json.dumps(content_types) if content_types else None,
            status="pending",
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        logger.info(f"Created Brain session: {session_id} (mode: {mode})")
        return session
    
    def update_session_status(
        self,
        session_id: str,
        status: str,
        matched_source_ids: Optional[List[str]] = None,
        ai_discovered_source_ids: Optional[List[str]] = None,
        generated_content: Optional[List[Dict[str, Any]]] = None,
        error_message: Optional[str] = None,
    ) -> Optional[BrainSession]:
        """Update session status and results"""
        session = self.db.query(BrainSession).filter(
            BrainSession.session_id == session_id
        ).first()
        
        if not session:
            return None
        
        session.status = status
        
        if matched_source_ids is not None:
            session.matched_source_ids = json.dumps(matched_source_ids)
        if ai_discovered_source_ids is not None:
            session.ai_discovered_source_ids = json.dumps(ai_discovered_source_ids)
        if generated_content is not None:
            session.generated_content = json.dumps(generated_content)
            session.generated_count = len(generated_content)
        if error_message is not None:
            session.error_message = error_message
        
        if status in ("completed", "failed"):
            session.completed_at = datetime.now(timezone.utc)
        
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    def get_session(self, session_id: str) -> Optional[BrainSession]:
        """Get a session by ID"""
        return self.db.query(BrainSession).filter(
            BrainSession.session_id == session_id
        ).first()
    
    # =========================================================================
    # Video Auto-Indexing
    # =========================================================================
    
    def index_video_as_source(
        self,
        video: Video,
        content_generator: Any = None,
    ) -> BrainSource:
        """
        Create a Brain source from a processed video.
        Called automatically after video processing.
        """
        source = self.create_source(
            title=video.title or f"Video {video.youtube_video_id}",
            content=video.transcript or "",
            source_type="youtube",
            source_metadata={
                "video_id": video.youtube_video_id,
                "video_url": video.video_url,
            },
        )
        
        # Index the source (extract topics, summary)
        if content_generator:
            source = self.index_source(source, content_generator)
        
        # Update video to mark as indexed
        video.is_indexed = True
        video.indexed_at = datetime.now(timezone.utc)
        video.source_type = "youtube"
        
        if source.topics:
            video.topics = source.topics
        if source.summary:
            video.summary = source.summary
        
        self.db.commit()
        
        logger.info(f"Indexed video {video.youtube_video_id} as Brain source {source.source_id}")
        return source


def get_brain_service(db: Session = None) -> BrainService:
    """Get a BrainService instance"""
    if db is None:
        db = SessionLocal()
    return BrainService(db)
