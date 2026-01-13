"""
Brain Knowledge Base Router
Handles Brain source management, search, and content generation
"""

import os
import json
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from core.database import SessionLocal, BrainSource, BrainSession
from core.services.brain_service import BrainService, get_brain_service
from core.services.brain_content_generator import BrainContentGenerator
from core.services.content_service import ContentGenerator
from core.services.url_service import URLExtractor, URLExtractionError

from api.models import (
    BrainSourceCreate,
    BrainSourceUpdate,
    BrainSourceResponse,
    BrainSourceListResponse,
    URLSourceCreate,
    URLExtractOptions,
    VisionGenerateRequest,
    VisionGenerateResponse,
    MatchedSource,
    AutoGenerateSingleRequest,
    AutoGenerateMultipleRequest,
    AutoGenerateAutoRequest,
    AutoGenerateResponse,
    HybridGenerateRequest,
    HybridGenerateResponse,
    BrainSearchRequest,
    BrainSearchResult,
    BrainSearchResponse,
    BrainSessionResponse,
)

router = APIRouter(prefix="/brain", tags=["brain"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_content_generator():
    """Get a ContentGenerator instance"""
    api_key = os.environ.get("GEMINI_API_KEY", "")
    return ContentGenerator(api_key=api_key)


def source_to_response(source: BrainSource) -> BrainSourceResponse:
    """Convert BrainSource model to response model"""
    return BrainSourceResponse(
        source_id=source.source_id,
        title=source.title,
        content=source.content,
        source_type=source.source_type,
        summary=source.summary,
        topics=json.loads(source.topics) if source.topics else None,
        tags=json.loads(source.tags) if source.tags else None,
        source_metadata=json.loads(source.source_metadata) if source.source_metadata else None,
        use_count=source.use_count or 0,
        last_used_at=source.last_used_at.isoformat() if source.last_used_at else None,
        created_at=source.created_at.isoformat(),
        updated_at=source.updated_at.isoformat(),
        has_embedding=source.embedding is not None,
    )


# =============================================================================
# Source CRUD Endpoints
# =============================================================================

@router.get("/sources", response_model=BrainSourceListResponse)
async def list_sources(
    source_type: Optional[str] = Query(None, description="Filter by source type"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    topic: Optional[str] = Query(None, description="Filter by topic"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """List Brain sources with optional filtering and pagination"""
    brain_service = BrainService(db)
    
    source_types = [source_type] if source_type else None
    tags = [tag] if tag else None
    topics = [topic] if topic else None
    
    offset = (page - 1) * page_size
    sources, total = brain_service.get_sources(
        source_types=source_types,
        tags=tags,
        topics=topics,
        limit=page_size,
        offset=offset,
    )
    
    return BrainSourceListResponse(
        sources=[source_to_response(s) for s in sources],
        total=total,
        page=page,
        page_size=page_size,
        has_more=(offset + len(sources)) < total,
    )


@router.get("/sources/{source_id}", response_model=BrainSourceResponse)
async def get_source(
    source_id: str,
    db: Session = Depends(get_db),
):
    """Get a specific Brain source by ID"""
    brain_service = BrainService(db)
    source = brain_service.get_source(source_id)
    
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    return source_to_response(source)


@router.post("/sources", response_model=BrainSourceResponse, status_code=201)
async def create_source(
    request: BrainSourceCreate,
    db: Session = Depends(get_db),
):
    """Create a new Brain source"""
    brain_service = BrainService(db)
    content_generator = get_content_generator()
    
    source = brain_service.create_source(
        title=request.title,
        content=request.content,
        source_type=request.source_type,
        summary=request.summary,
        topics=request.topics,
        tags=request.tags,
        source_metadata=request.source_metadata,
    )
    
    # Index the source (extract topics, summary if not provided)
    if not request.summary or not request.topics:
        source = brain_service.index_source(source, content_generator)
    
    return source_to_response(source)


@router.post("/sources/url", response_model=BrainSourceResponse, status_code=201)
async def create_source_from_url(
    request: URLSourceCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new Brain source from a URL.
    
    Fetches the URL, extracts main content as Markdown, and indexes it.
    YouTube URLs are blocked - use video processing instead.
    """
    brain_service = BrainService(db)
    content_generator = get_content_generator()
    
    # Extract content from URL
    try:
        options = request.extract_options or URLExtractOptions()
        extracted = URLExtractor.extract_from_url(
            url=request.url,
            include_tables=options.include_tables,
            include_links=options.include_links,
            include_images=options.include_images,
        )
    except URLExtractionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract URL content: {e}")
    
    # Use provided title or extracted title
    title = request.title or extracted["title"] or request.url
    
    # Build metadata
    source_metadata = {
        "original_url": extracted["original_url"],
        "author": extracted.get("author"),
        "date": extracted.get("date"),
        "description": extracted.get("description"),
        "sitename": extracted.get("sitename"),
    }
    # Remove None values
    source_metadata = {k: v for k, v in source_metadata.items() if v is not None}
    
    # Create the source
    source = brain_service.create_source(
        title=title,
        content=extracted["content"],
        source_type="url",
        tags=request.tags,
        source_metadata=source_metadata,
    )
    
    # Index the source (extract topics, summary)
    source = brain_service.index_source(source, content_generator)
    
    return source_to_response(source)


@router.patch("/sources/{source_id}", response_model=BrainSourceResponse)
async def update_source(
    source_id: str,
    request: BrainSourceUpdate,
    db: Session = Depends(get_db),
):
    """Update a Brain source"""
    brain_service = BrainService(db)
    
    source = brain_service.update_source(
        source_id=source_id,
        title=request.title,
        content=request.content,
        summary=request.summary,
        topics=request.topics,
        tags=request.tags,
        source_metadata=request.source_metadata,
    )
    
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    return source_to_response(source)


@router.delete("/sources/{source_id}", status_code=204)
async def delete_source(
    source_id: str,
    db: Session = Depends(get_db),
):
    """Delete a Brain source"""
    brain_service = BrainService(db)
    
    if not brain_service.delete_source(source_id):
        raise HTTPException(status_code=404, detail="Source not found")


# =============================================================================
# Search Endpoint
# =============================================================================

@router.post("/search", response_model=BrainSearchResponse)
async def search_sources(
    request: BrainSearchRequest,
    db: Session = Depends(get_db),
):
    """Search Brain sources using semantic matching"""
    brain_service = BrainService(db)
    
    results = brain_service.search_sources(
        query=request.query,
        source_types=request.source_types,
        tags=request.tags,
        topics=request.topics,
        limit=request.limit,
        min_score=request.min_score,
    )
    
    search_results = [
        BrainSearchResult(
            source_id=r["source"].source_id,
            title=r["source"].title,
            source_type=r["source"].source_type,
            relevance_score=r["score"],
            snippet=r["snippet"],
            topics=json.loads(r["source"].topics) if r["source"].topics else [],
            tags=json.loads(r["source"].tags) if r["source"].tags else [],
        )
        for r in results
    ]
    
    return BrainSearchResponse(
        results=search_results,
        total_results=len(search_results),
        query=request.query,
    )


# =============================================================================
# Generation Endpoints
# =============================================================================

@router.post("/generate/vision", response_model=VisionGenerateResponse)
async def generate_from_vision(
    request: VisionGenerateRequest,
    db: Session = Depends(get_db),
):
    """Generate content based on user's vision/idea"""
    brain_service = BrainService(db)
    content_generator = get_content_generator()
    brain_generator = BrainContentGenerator(brain_service, content_generator)
    
    try:
        result = brain_generator.generate_from_vision(
            user_vision=request.user_vision,
            content_types=request.content_types,
            style_preset=request.style_preset,
            custom_style=request.custom_style.model_dump() if request.custom_style else None,
            max_sources=request.max_sources,
            min_match_score=request.min_match_score,
        )
        
        matched_sources = [
            MatchedSource(
                source_id=s["source_id"],
                title=s["title"],
                source_type=s["source_type"],
                match_score=s["match_score"],
                matched_topics=s.get("matched_topics", []),
                snippet=s.get("snippet", ""),
            )
            for s in result["matched_sources"]
        ]
        
        return VisionGenerateResponse(
            session_id=result["session_id"],
            matched_sources=matched_sources,
            generated_content=result["generated_content"],
            total_matches=result["total_matches"],
            status=result["status"],
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/single", response_model=AutoGenerateResponse)
async def generate_from_single_source(
    request: AutoGenerateSingleRequest,
    db: Session = Depends(get_db),
):
    """Generate content from a single source"""
    brain_service = BrainService(db)
    content_generator = get_content_generator()
    brain_generator = BrainContentGenerator(brain_service, content_generator)
    
    try:
        result = brain_generator.generate_from_single_source(
            source_id=request.source_id,
            content_types=request.content_types,
            style_preset=request.style_preset,
            custom_style=request.custom_style.model_dump() if request.custom_style else None,
        )
        
        return AutoGenerateResponse(
            session_id=result["session_id"],
            sources_used=result["sources_used"],
            generated_content=result["generated_content"],
            content_count=result["content_count"],
            status=result["status"],
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/multiple", response_model=AutoGenerateResponse)
async def generate_from_multiple_sources(
    request: AutoGenerateMultipleRequest,
    db: Session = Depends(get_db),
):
    """Generate content from multiple selected sources"""
    brain_service = BrainService(db)
    content_generator = get_content_generator()
    brain_generator = BrainContentGenerator(brain_service, content_generator)
    
    try:
        result = brain_generator.generate_from_multiple_sources(
            source_ids=request.source_ids,
            content_count=request.content_count,
            content_types=request.content_types,
            style_preset=request.style_preset,
            custom_style=request.custom_style.model_dump() if request.custom_style else None,
        )
        
        return AutoGenerateResponse(
            session_id=result["session_id"],
            sources_used=result["sources_used"],
            generated_content=result["generated_content"],
            content_count=result["content_count"],
            status=result["status"],
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/auto", response_model=AutoGenerateResponse)
async def generate_auto(
    request: AutoGenerateAutoRequest,
    db: Session = Depends(get_db),
):
    """Auto-select sources and generate content"""
    brain_service = BrainService(db)
    content_generator = get_content_generator()
    brain_generator = BrainContentGenerator(brain_service, content_generator)
    
    try:
        result = brain_generator.generate_auto(
            content_count=request.content_count,
            content_types=request.content_types,
            source_types=request.source_types,
            tags=request.tags,
            topics=request.topics,
            style_preset=request.style_preset,
            custom_style=request.custom_style.model_dump() if request.custom_style else None,
        )
        
        return AutoGenerateResponse(
            session_id=result["session_id"],
            sources_used=result["sources_used"],
            generated_content=result["generated_content"],
            content_count=result["content_count"],
            status=result["status"],
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/hybrid", response_model=HybridGenerateResponse)
async def generate_hybrid(
    request: HybridGenerateRequest,
    db: Session = Depends(get_db),
):
    """Generate using user-selected + AI-discovered sources"""
    brain_service = BrainService(db)
    content_generator = get_content_generator()
    brain_generator = BrainContentGenerator(brain_service, content_generator)
    
    try:
        result = brain_generator.generate_hybrid(
            selected_source_ids=request.selected_source_ids,
            ai_augment_hint=request.ai_augment_hint,
            ai_augment_strategy=request.ai_augment_strategy,
            ai_augment_count=request.ai_augment_count,
            content_count=request.content_count,
            content_types=request.content_types,
            style_preset=request.style_preset,
            custom_style=request.custom_style.model_dump() if request.custom_style else None,
        )
        
        return HybridGenerateResponse(
            session_id=result["session_id"],
            user_sources=result["user_sources"],
            ai_discovered_sources=result["ai_discovered_sources"],
            combined_sources_count=result["combined_sources_count"],
            generated_content=result["generated_content"],
            content_count=result["content_count"],
            status=result["status"],
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Session Endpoints
# =============================================================================

@router.get("/sessions/{session_id}", response_model=BrainSessionResponse)
async def get_session(
    session_id: str,
    db: Session = Depends(get_db),
):
    """Get details of a generation session"""
    brain_service = BrainService(db)
    session = brain_service.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return BrainSessionResponse(
        session_id=session.session_id,
        mode=session.mode,
        status=session.status,
        user_vision=session.user_vision,
        selected_source_ids=json.loads(session.selected_source_ids) if session.selected_source_ids else None,
        matched_source_ids=json.loads(session.matched_source_ids) if session.matched_source_ids else None,
        ai_discovered_source_ids=json.loads(session.ai_discovered_source_ids) if session.ai_discovered_source_ids else None,
        generated_count=session.generated_count,
        created_at=session.created_at.isoformat(),
        completed_at=session.completed_at.isoformat() if session.completed_at else None,
        error_message=session.error_message,
    )
