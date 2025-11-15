"""
Content Style Presets and Configuration
"""

from typing import Optional
from api.models import ContentStylePreset, CustomContentStyle


# ============================================================================
# Content Style Presets
# ============================================================================

CONTENT_STYLE_PRESETS = {
    "ecommerce_entrepreneur": ContentStylePreset(
        name="E-commerce Entrepreneur",
        description="For e-commerce entrepreneurs and Shopify store owners",
        target_audience="ecom entrepreneurs, Shopify store owners, and DTC brands looking to launch, improve design, or scale with ads",
        call_to_action="DM us to launch or fix your store, check our portfolio, and follow for ROI-boosting tips",
        content_goal="education, lead_generation, brand_awareness",
        language="Roman Urdu",
        tone="Educational and engaging",
        additional_instructions="CRITICAL LANGUAGE RULE: The output language MUST be Roman Urdu. Roman Urdu means writing Urdu words using the English alphabet. DO NOT use the native Urdu script."
    ),
    "professional_business": ContentStylePreset(
        name="Professional Business",
        description="Professional business content for corporate audiences",
        target_audience="business professionals, entrepreneurs, and corporate decision makers",
        call_to_action="Contact us for consultation, follow for business insights",
        content_goal="thought_leadership, brand_awareness, lead_generation",
        language="English",
        tone="Professional and authoritative",
        additional_instructions="Use industry terminology and maintain a professional tone throughout"
    ),
    "social_media_casual": ContentStylePreset(
        name="Social Media Casual",
        description="Casual, engaging content for social media audiences",
        target_audience="general social media users, millennials, and Gen Z",
        call_to_action="Like, share, and follow for more content",
        content_goal="entertainment, engagement, brand_awareness",
        language="English",
        tone="Casual and fun",
        additional_instructions="Use emojis, trendy language, and keep it conversational"
    ),
    "educational_content": ContentStylePreset(
        name="Educational Content",
        description="Educational and informative content for learners",
        target_audience="students, professionals seeking knowledge, lifelong learners",
        call_to_action="Subscribe for more educational content, share with others",
        content_goal="education, knowledge_sharing, community_building",
        language="English",
        tone="Informative and encouraging",
        additional_instructions="Break down complex topics into digestible pieces, use examples and analogies"
    ),
    "fitness_wellness": ContentStylePreset(
        name="Fitness & Wellness",
        description="Health, fitness, and wellness focused content",
        target_audience="fitness enthusiasts, health-conscious individuals, wellness seekers",
        call_to_action="Follow for daily tips, share your progress, join our community",
        content_goal="motivation, education, community_building",
        language="English",
        tone="Motivational and supportive",
        additional_instructions="Use encouraging language, focus on positive health outcomes, include actionable tips"
    )
}


# ============================================================================
# Helper Functions
# ============================================================================

def get_content_style_prompt(style_preset: Optional[str] = None, custom_style: Optional[CustomContentStyle] = None) -> str:
    """Generate content style prompt based on preset or custom style"""
    if custom_style:
        style_text = f"""
        "Target Audience: {custom_style.target_audience}"
        "Call To Action: {custom_style.call_to_action}"
        "Content Goal: {custom_style.content_goal}"
        "Language: {custom_style.language}"
        "Tone: {custom_style.tone}"
        """
        if custom_style.additional_instructions:
            style_text += f'"Additional Instructions: {custom_style.additional_instructions}"'
    elif style_preset and style_preset in CONTENT_STYLE_PRESETS:
        preset = CONTENT_STYLE_PRESETS[style_preset]
        style_text = f"""
        "Target Audience: {preset.target_audience}"
        "Call To Action: {preset.call_to_action}"
        "Content Goal: {preset.content_goal}"
        "Language: {preset.language}"
        "Tone: {preset.tone}"
        """
        if preset.additional_instructions:
            style_text += f'"Additional Instructions: {preset.additional_instructions}"'
    else:
        # Default style (original ecommerce style)
        style_text = """
        "Target Audience: ecom entrepreneurs, Shopify store owners, and DTC brands looking to launch, improve design, or scale with ads."
        "Call To Action: DM us to launch or fix your store, check our portfolio, and follow for ROI-boosting tips."
        "Content Goal: education, lead_generation, brand_awareness."
        "Language: Roman Urdu"
        "Tone: Educational and engaging"
        "CRITICAL LANGUAGE RULE: The output language MUST be Roman Urdu. Roman Urdu means writing Urdu words using the English alphabet. DO NOT use the native Urdu script."
        """
    
    return style_text
