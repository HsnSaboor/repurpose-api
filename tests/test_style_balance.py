"""
Test if content styles are too aggressive and overpower video content
"""

import sys
sys.path.insert(0, '/home/saboor/code/repurpose-api')

from core.content.prompts import get_system_prompt_generate_ideas, get_system_prompt_generate_content
from api.config import get_content_style_prompt

print("=" * 70)
print("🧪 TESTING CONTENT STYLE vs VIDEO CONTENT BALANCE")
print("=" * 70)
print()

# Test different scenarios
test_cases = [
    {
        "name": "Default (Roman Urdu - E-commerce)",
        "style_preset": None,
        "custom_style": None
    },
    {
        "name": "Professional Business",
        "style_preset": "professional_business",
        "custom_style": None
    },
    {
        "name": "Educational Content",
        "style_preset": "educational_content",
        "custom_style": None
    }
]

def analyze_prompt_balance(prompt_text, style_info):
    """Analyze if prompt gives too much weight to style vs content"""
    
    # Count style-related instructions
    style_keywords = [
        'style', 'tone', 'audience', 'call to action', 'language',
        'must follow', 'strictly', 'critical', 'mandatory'
    ]
    
    # Count content-related instructions
    content_keywords = [
        'transcript', 'video', 'idea', 'relevant', 'inspired',
        'analyze', 'extract', 'based on'
    ]
    
    style_count = sum(prompt_text.lower().count(kw) for kw in style_keywords)
    content_count = sum(prompt_text.lower().count(kw) for kw in content_keywords)
    
    # Check for overly strict language
    strict_phrases = [
        'MUST be', 'MUST follow', 'CRITICAL', 'strictly follow',
        'MANDATORY', 'absolute', 'REQUIRED'
    ]
    strict_count = sum(prompt_text.count(phrase) for phrase in strict_phrases)
    
    total_length = len(prompt_text)
    
    return {
        'style_mentions': style_count,
        'content_mentions': content_count,
        'strict_instructions': strict_count,
        'total_length': total_length,
        'style_to_content_ratio': style_count / max(content_count, 1)
    }

print("ANALYZING IDEA GENERATION PROMPT")
print("-" * 70)
print()

for i, test in enumerate(test_cases, 1):
    print(f"[{i}] {test['name']}")
    print("-" * 70)
    
    style_prompt = get_content_style_prompt(
        style_preset=test['style_preset'],
        custom_style=test['custom_style']
    )
    
    ideas_prompt = get_system_prompt_generate_ideas(content_style=style_prompt)
    
    analysis = analyze_prompt_balance(ideas_prompt, style_prompt)
    
    print(f"  Total prompt length: {analysis['total_length']} chars")
    print(f"  Style mentions: {analysis['style_mentions']}")
    print(f"  Content mentions: {analysis['content_mentions']}")
    print(f"  Strict instructions: {analysis['strict_instructions']}")
    print(f"  Style-to-Content ratio: {analysis['style_to_content_ratio']:.2f}")
    
    # Check balance
    if analysis['style_to_content_ratio'] > 2.0:
        print(f"  ⚠️  WARNING: Style may overpower content (ratio > 2.0)")
    elif analysis['style_to_content_ratio'] > 1.5:
        print(f"  ⚡ CAUTION: Style emphasis is high (ratio > 1.5)")
    else:
        print(f"  ✅ BALANCED: Good balance between style and content")
    
    print()

print()
print("=" * 70)
print("ANALYZING CONTENT GENERATION PROMPT")
print("=" * 70)
print()

for i, test in enumerate(test_cases, 1):
    print(f"[{i}] {test['name']}")
    print("-" * 70)
    
    style_prompt = get_content_style_prompt(
        style_preset=test['style_preset'],
        custom_style=test['custom_style']
    )
    
    content_prompt = get_system_prompt_generate_content(content_style=style_prompt)
    
    analysis = analyze_prompt_balance(content_prompt, style_prompt)
    
    print(f"  Total prompt length: {analysis['total_length']} chars")
    print(f"  Style mentions: {analysis['style_mentions']}")
    print(f"  Content mentions: {analysis['content_mentions']}")
    print(f"  Strict instructions: {analysis['strict_instructions']}")
    print(f"  Style-to-Content ratio: {analysis['style_to_content_ratio']:.2f}")
    
    # Check balance
    if analysis['style_to_content_ratio'] > 2.0:
        print(f"  ⚠️  WARNING: Style may overpower content (ratio > 2.0)")
    elif analysis['style_to_content_ratio'] > 1.5:
        print(f"  ⚡ CAUTION: Style emphasis is high (ratio > 1.5)")
    else:
        print(f"  ✅ BALANCED: Good balance between style and content")
    
    print()

print()
print("=" * 70)
print("📊 ANALYSIS SUMMARY")
print("=" * 70)
print()
print("KEY FINDINGS:")
print()

# Check actual style prompt content
default_style = get_content_style_prompt()
print("1. Style Prompt Length Analysis:")
print(f"   Default style prompt: {len(default_style)} chars")
print()

# Extract key phrases from prompts
ideas_prompt_sample = get_system_prompt_generate_ideas("{CONTENT_STYLE}")
content_prompt_sample = get_system_prompt_generate_content("{CONTENT_STYLE}")

print("2. Instruction Balance in Ideas Prompt:")
if "must strictly follow" in ideas_prompt_sample.lower():
    print("   ⚠️  Contains 'must strictly follow' - may be too strict")
else:
    print("   ✅ No overly strict language detected")
print()

print("3. Instruction Balance in Content Prompt:")
if content_prompt_sample.count("MUST") > 5:
    print(f"   ⚠️  High use of 'MUST' ({content_prompt_sample.count('MUST')} times)")
else:
    print("   ✅ Reasonable use of directive language")
print()

print("4. Content Prioritization:")
if "transcript" in ideas_prompt_sample and "video" in ideas_prompt_sample:
    print("   ✅ Transcript/video analysis is mentioned")
else:
    print("   ⚠️  Limited mention of source content")
print()

print("RECOMMENDATIONS:")
print("-" * 70)
print("""
For better balance between style and content:

1. Reduce repetitive style enforcement in prompts
2. Add more emphasis on extracting key insights from video
3. Make style more of a 'guide' than a 'strict requirement'
4. Allow content to naturally flow from video while maintaining style
5. Consider using softer language: 'should' instead of 'MUST'

Current Status:
- Style enforcement appears moderate to high
- Content focus is present but could be emphasized more
- Consider testing with actual videos to see output balance
""")

