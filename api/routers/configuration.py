"""
Configuration and Content Style Router
"""

from fastapi import APIRouter, HTTPException
from api.config import CONTENT_STYLE_PRESETS
from repurpose import DEFAULT_FIELD_LIMITS, CURRENT_FIELD_LIMITS


router = APIRouter(prefix="", tags=["configuration"])


@router.get("/content-styles/presets/")
async def get_style_presets():
    """Get all available content style presets"""
    return {
        "presets": {
            key: {
                "name": preset.name,
                "description": preset.description,
                "target_audience": preset.target_audience,
                "language": preset.language,
                "tone": preset.tone
            } for key, preset in CONTENT_STYLE_PRESETS.items()
        }
    }


@router.get("/content-styles/presets/{preset_name}")
async def get_style_preset(preset_name: str):
    """Get details of a specific content style preset including content configuration"""
    if preset_name not in CONTENT_STYLE_PRESETS:
        raise HTTPException(status_code=404, detail=f"Style preset '{preset_name}' not found")
    
    preset = CONTENT_STYLE_PRESETS[preset_name]
    return {
        "name": preset.name,
        "description": preset.description,
        "target_audience": preset.target_audience,
        "call_to_action": preset.call_to_action,
        "content_goal": preset.content_goal,
        "language": preset.language,
        "tone": preset.tone,
        "additional_instructions": preset.additional_instructions,
        "content_config": preset.content_config.model_dump()
    }


@router.get("/content-config/default")
async def get_default_content_config():
    """Get the default content generation configuration including field limits"""
    return {
        "description": "Default configuration for content generation",
        "field_limits": DEFAULT_FIELD_LIMITS,
        "min_ideas": 6,
        "max_ideas": 8,
        "content_pieces_per_idea": 1,
        "note": "These are the default settings. You can override them in custom_style.content_config when processing videos/documents."
    }


@router.get("/content-config/current")
async def get_current_content_config():
    """Get the currently active content generation configuration"""
    return {
        "description": "Currently active configuration for content generation",
        "field_limits": CURRENT_FIELD_LIMITS,
        "note": "This shows the active configuration. To use custom limits, pass them in the content_config parameter when processing."
    }
