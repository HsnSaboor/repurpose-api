#!/usr/bin/env python
"""Quick test of content generation"""

from repurpose import generate_content_ideas, generate_specific_content_pieces
from core.content.models import ContentIdea

# Simple test text
test_text = """
This is a comprehensive guide about artificial intelligence and machine learning.
AI is revolutionizing industries across the world. Machine learning algorithms
can process vast amounts of data and identify patterns. Deep learning neural
networks are particularly powerful for image recognition and natural language
processing. The future of AI looks very promising with applications in healthcare,
finance, and transportation.
""" * 5

print("Testing content generation...")
print(f"Text length: {len(test_text)} chars")
print()

print("1. Generating ideas...")
try:
    ideas = generate_content_ideas(test_text)
    if ideas:
        print(f"   ✅ Generated {len(ideas)} ideas")
        # Convert to ContentIdea objects
        idea_objects = [ContentIdea(**idea) for idea in ideas]
        
        print("\n2. Generating content pieces...")
        try:
            content = generate_specific_content_pieces(
                idea_objects,
                test_text,
                "https://youtube.com/watch?v=test123"
            )
            
            if content and hasattr(content, 'pieces'):
                print(f"   ✅ Generated {len(content.pieces)} content pieces")
                for piece in content.pieces:
                    print(f"      - {piece.content_type}: {piece.title[:50]}")
            else:
                print("   ❌ No content pieces generated")
        except Exception as e:
            print(f"   ❌ Error generating pieces: {e}")
    else:
        print("   ❌ No ideas generated")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\nDone!")
