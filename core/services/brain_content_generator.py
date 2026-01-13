"""Brain Content Generation Service

Provides content generation using Brain knowledge base sources.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from core.database import BrainSource, BrainSession
from core.services.brain_service import BrainService
from core.services.content_service import ContentGenerator


logger = logging.getLogger(__name__)


class BrainContentGenerator:
    """Generates content using Brain knowledge base"""
    
    def __init__(
        self,
        brain_service: BrainService,
        content_generator: ContentGenerator,
    ):
        self.brain_service = brain_service
        self.content_generator = content_generator
    
    # =========================================================================
    # Vision-Based Generation
    # =========================================================================
    
    def generate_from_vision(
        self,
        user_vision: str,
        content_types: List[str],
        style_preset: Optional[str] = None,
        custom_style: Optional[Dict[str, Any]] = None,
        max_sources: int = 5,
        min_match_score: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Generate content based on user's vision/idea.
        
        1. Search Brain for sources matching the vision
        2. Combine vision with matched sources
        3. Generate content pieces
        """
        # Create session
        session = self.brain_service.create_session(
            mode="vision",
            user_vision=user_vision,
            content_types=content_types,
            style_preset=style_preset,
        )
        
        try:
            # Find matching sources
            matched_results = self.brain_service.get_relevant_sources(
                user_vision=user_vision,
                max_sources=max_sources,
                min_score=min_match_score,
            )
            
            if not matched_results:
                # No matches found - generate purely from vision
                matched_sources = []
                matched_source_ids = []
                source_context = "No existing sources matched. Generate based on the idea alone."
            else:
                matched_sources = [
                    {
                        "source_id": r["source"]["source_id"],
                        "title": r["source"].title,
                        "source_type": r["source"].source_type,
                        "match_score": r["score"],
                        "snippet": r["snippet"],
                        "matched_topics": json.loads(r["source"].topics) if r["source"].topics else [],
                    }
                    for r in matched_results
                ]
                matched_source_ids = [s["source_id"] for s in matched_sources]
                
                # Build context from sources
                source_context = self._build_source_context(matched_results)
                
                # Increment use counts
                for source_id in matched_source_ids:
                    self.brain_service.increment_use_count(source_id)
            
            # Generate content
            generated_content = self._generate_content_pieces(
                user_vision=user_vision,
                source_context=source_context,
                content_types=content_types,
                style_preset=style_preset,
                custom_style=custom_style,
            )
            
            # Update session
            self.brain_service.update_session_status(
                session.session_id,
                status="completed",
                matched_source_ids=matched_source_ids,
                generated_content=generated_content,
            )
            
            return {
                "session_id": session.session_id,
                "matched_sources": matched_sources,
                "generated_content": generated_content,
                "total_matches": len(matched_sources),
                "status": "completed",
            }
            
        except Exception as e:
            logger.error(f"Vision generation failed: {e}")
            self.brain_service.update_session_status(
                session.session_id,
                status="failed",
                error_message=str(e),
            )
            raise
    
    # =========================================================================
    # Full AI Mode - Single Source
    # =========================================================================
    
    def generate_from_single_source(
        self,
        source_id: str,
        content_types: List[str],
        style_preset: Optional[str] = None,
        custom_style: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate content from a single source"""
        session = self.brain_service.create_session(
            mode="full_ai_single",
            selected_source_ids=[source_id],
            content_types=content_types,
            style_preset=style_preset,
        )
        
        try:
            source = self.brain_service.get_source(source_id)
            if not source:
                raise ValueError(f"Source not found: {source_id}")
            
            source_context = f"""
Source: {source.title}
Type: {source.source_type}
Content:
{source.content[:4000]}
"""
            
            generated_content = self._generate_content_pieces(
                user_vision=f"Create engaging content based on this source about: {source.title}",
                source_context=source_context,
                content_types=content_types,
                style_preset=style_preset,
                custom_style=custom_style,
            )
            
            self.brain_service.increment_use_count(source_id)
            
            self.brain_service.update_session_status(
                session.session_id,
                status="completed",
                generated_content=generated_content,
            )
            
            return {
                "session_id": session.session_id,
                "sources_used": [{"source_id": source_id, "title": source.title}],
                "generated_content": generated_content,
                "content_count": len(generated_content),
                "status": "completed",
            }
            
        except Exception as e:
            logger.error(f"Single source generation failed: {e}")
            self.brain_service.update_session_status(
                session.session_id,
                status="failed",
                error_message=str(e),
            )
            raise
    
    # =========================================================================
    # Full AI Mode - Multiple Sources
    # =========================================================================
    
    def generate_from_multiple_sources(
        self,
        source_ids: List[str],
        content_count: int,
        content_types: List[str],
        style_preset: Optional[str] = None,
        custom_style: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate content from multiple selected sources"""
        session = self.brain_service.create_session(
            mode="full_ai_multiple",
            selected_source_ids=source_ids,
            requested_count=content_count,
            content_types=content_types,
            style_preset=style_preset,
        )
        
        try:
            sources = []
            for source_id in source_ids:
                source = self.brain_service.get_source(source_id)
                if source:
                    sources.append(source)
            
            if not sources:
                raise ValueError("No valid sources found")
            
            source_context = self._build_source_context_from_sources(sources)
            
            generated_content = self._generate_multiple_content_pieces(
                source_context=source_context,
                content_count=content_count,
                content_types=content_types,
                style_preset=style_preset,
                custom_style=custom_style,
            )
            
            for source_id in source_ids:
                self.brain_service.increment_use_count(source_id)
            
            self.brain_service.update_session_status(
                session.session_id,
                status="completed",
                generated_content=generated_content,
            )
            
            return {
                "session_id": session.session_id,
                "sources_used": [{"source_id": s.source_id, "title": s.title} for s in sources],
                "generated_content": generated_content,
                "content_count": len(generated_content),
                "status": "completed",
            }
            
        except Exception as e:
            logger.error(f"Multiple sources generation failed: {e}")
            self.brain_service.update_session_status(
                session.session_id,
                status="failed",
                error_message=str(e),
            )
            raise
    
    # =========================================================================
    # Full AI Mode - Auto Selection
    # =========================================================================
    
    def generate_auto(
        self,
        content_count: int,
        content_types: List[str],
        source_types: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        topics: Optional[List[str]] = None,
        style_preset: Optional[str] = None,
        custom_style: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Auto-select sources and generate content"""
        session = self.brain_service.create_session(
            mode="full_ai_auto",
            requested_count=content_count,
            content_types=content_types,
            style_preset=style_preset,
        )
        
        try:
            # Get sources with filters
            sources, total = self.brain_service.get_sources(
                source_types=source_types,
                tags=tags,
                topics=topics,
                limit=content_count * 2,  # Get more than needed
            )
            
            if not sources:
                raise ValueError("No sources found matching criteria")
            
            # Select diverse sources
            selected_sources = sources[:min(len(sources), content_count)]
            
            source_context = self._build_source_context_from_sources(selected_sources)
            
            generated_content = self._generate_multiple_content_pieces(
                source_context=source_context,
                content_count=content_count,
                content_types=content_types,
                style_preset=style_preset,
                custom_style=custom_style,
            )
            
            for source in selected_sources:
                self.brain_service.increment_use_count(source.source_id)
            
            self.brain_service.update_session_status(
                session.session_id,
                status="completed",
                matched_source_ids=[s.source_id for s in selected_sources],
                generated_content=generated_content,
            )
            
            return {
                "session_id": session.session_id,
                "sources_used": [{"source_id": s.source_id, "title": s.title} for s in selected_sources],
                "generated_content": generated_content,
                "content_count": len(generated_content),
                "status": "completed",
            }
            
        except Exception as e:
            logger.error(f"Auto generation failed: {e}")
            self.brain_service.update_session_status(
                session.session_id,
                status="failed",
                error_message=str(e),
            )
            raise
    
    # =========================================================================
    # Hybrid Mode
    # =========================================================================
    
    def generate_hybrid(
        self,
        selected_source_ids: List[str],
        ai_augment_hint: Optional[str],
        ai_augment_strategy: str,
        ai_augment_count: int,
        content_count: int,
        content_types: List[str],
        style_preset: Optional[str] = None,
        custom_style: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Hybrid generation: user-selected + AI-discovered sources.
        
        Strategies:
        - augment: Find sources that expand on selected topics
        - fill: Find sources that fill gaps in the selected content
        - support: Find sources that support/validate selected content
        """
        session = self.brain_service.create_session(
            mode="hybrid",
            selected_source_ids=selected_source_ids,
            requested_count=content_count,
            content_types=content_types,
            style_preset=style_preset,
        )
        
        try:
            # Get user-selected sources
            user_sources = []
            for source_id in selected_source_ids:
                source = self.brain_service.get_source(source_id)
                if source:
                    user_sources.append(source)
            
            if not user_sources:
                raise ValueError("No valid user-selected sources found")
            
            # AI-discover additional sources
            ai_sources = []
            if ai_augment_count > 0:
                ai_sources = self._discover_additional_sources(
                    user_sources=user_sources,
                    hint=ai_augment_hint,
                    strategy=ai_augment_strategy,
                    count=ai_augment_count,
                )
            
            # Combine sources
            all_sources = user_sources + ai_sources
            source_context = self._build_source_context_from_sources(all_sources)
            
            generated_content = self._generate_multiple_content_pieces(
                source_context=source_context,
                content_count=content_count,
                content_types=content_types,
                style_preset=style_preset,
                custom_style=custom_style,
            )
            
            # Increment use counts
            for source in all_sources:
                self.brain_service.increment_use_count(source.source_id)
            
            self.brain_service.update_session_status(
                session.session_id,
                status="completed",
                matched_source_ids=[s.source_id for s in user_sources],
                ai_discovered_source_ids=[s.source_id for s in ai_sources],
                generated_content=generated_content,
            )
            
            return {
                "session_id": session.session_id,
                "user_sources": [{"source_id": s.source_id, "title": s.title} for s in user_sources],
                "ai_discovered_sources": [{"source_id": s.source_id, "title": s.title} for s in ai_sources],
                "combined_sources_count": len(all_sources),
                "generated_content": generated_content,
                "content_count": len(generated_content),
                "status": "completed",
            }
            
        except Exception as e:
            logger.error(f"Hybrid generation failed: {e}")
            self.brain_service.update_session_status(
                session.session_id,
                status="failed",
                error_message=str(e),
            )
            raise
    
    # =========================================================================
    # Helper Methods
    # =========================================================================
    
    def _build_source_context(self, matched_results: List[Dict[str, Any]]) -> str:
        """Build context string from matched results"""
        context_parts = []
        for i, result in enumerate(matched_results, 1):
            source = result["source"]
            context_parts.append(f"""
Source {i}: {source.title}
Relevance: {result['score']:.0%}
Type: {source.source_type}
Snippet: {result['snippet']}
""")
        return "\n".join(context_parts)
    
    def _build_source_context_from_sources(self, sources: List[BrainSource]) -> str:
        """Build context string from source objects"""
        context_parts = []
        for i, source in enumerate(sources, 1):
            summary = source.summary or source.content[:500]
            context_parts.append(f"""
Source {i}: {source.title}
Type: {source.source_type}
Summary: {summary}
""")
        return "\n".join(context_parts)
    
    def _discover_additional_sources(
        self,
        user_sources: List[BrainSource],
        hint: Optional[str],
        strategy: str,
        count: int,
    ) -> List[BrainSource]:
        """Discover additional sources based on strategy"""
        # Build search query based on user sources and hint
        topics = []
        for source in user_sources:
            if source.topics:
                topics.extend(json.loads(source.topics))
        
        query = hint if hint else " ".join(topics[:5])
        
        if not query:
            return []
        
        # Search for related sources
        results = self.brain_service.search_sources(
            query=query,
            limit=count * 2,
            min_score=0.3,
        )
        
        # Exclude already selected sources
        user_source_ids = {s.source_id for s in user_sources}
        discovered = [
            r["source"] for r in results
            if r["source"].source_id not in user_source_ids
        ]
        
        return discovered[:count]
    
    def _generate_content_pieces(
        self,
        user_vision: str,
        source_context: str,
        content_types: List[str],
        style_preset: Optional[str] = None,
        custom_style: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Generate content pieces using the LLM"""
        style_instructions = self._get_style_instructions(style_preset, custom_style)
        
        system_prompt = f"""You are a social media content creator. Generate engaging content for the following platforms: {', '.join(content_types)}.

{style_instructions}

Use the provided source material as factual foundation for your content.
Make the content engaging, valuable, and platform-appropriate.

Return JSON with:
{{
  "content_pieces": [
    {{
      "content_id": "c1",
      "content_type": "reel|tweet|image_carousel",
      "title": "...",
      "content": {{...platform-specific fields...}}
    }}
  ]
}}
"""
        
        user_prompt = f"""
User's Idea/Vision:
{user_vision}

Source Material:
{source_context}

Generate one content piece for each requested type: {', '.join(content_types)}
"""
        
        result = self.content_generator.generate_content(system_prompt, user_prompt)
        
        if result and "content_pieces" in result:
            return result["content_pieces"]
        
        return []
    
    def _generate_multiple_content_pieces(
        self,
        source_context: str,
        content_count: int,
        content_types: List[str],
        style_preset: Optional[str] = None,
        custom_style: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Generate multiple content pieces"""
        style_instructions = self._get_style_instructions(style_preset, custom_style)
        
        system_prompt = f"""You are a social media content creator. Generate {content_count} engaging content pieces.

{style_instructions}

Content types to generate: {', '.join(content_types)}
Distribute content evenly across types.

Use the provided source material as factual foundation.

Return JSON with:
{{
  "content_pieces": [
    {{
      "content_id": "c1",
      "content_type": "reel|tweet|image_carousel",
      "title": "...",
      "content": {{...platform-specific fields...}}
    }}
  ]
}}
"""
        
        user_prompt = f"""
Source Material:
{source_context}

Generate exactly {content_count} content pieces.
"""
        
        result = self.content_generator.generate_content(system_prompt, user_prompt)
        
        if result and "content_pieces" in result:
            return result["content_pieces"]
        
        return []
    
    def _get_style_instructions(
        self,
        style_preset: Optional[str],
        custom_style: Optional[Dict[str, Any]],
    ) -> str:
        """Get style instructions from preset or custom style"""
        if custom_style:
            return f"""
Target Audience: {custom_style.get('target_audience', 'General')}
Tone: {custom_style.get('tone', 'Professional')}
Goal: {custom_style.get('content_goal', 'Engagement')}
Call to Action: {custom_style.get('call_to_action', 'None')}
Additional: {custom_style.get('additional_instructions', '')}
"""
        
        if style_preset:
            return f"Use the '{style_preset}' style preset for content generation."
        
        return "Use a professional, engaging tone appropriate for social media."
