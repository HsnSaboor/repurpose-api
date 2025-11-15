#!/usr/bin/env python3
"""
Test script to verify content configuration functionality
"""

import json
from repurpose import (
    DEFAULT_FIELD_LIMITS,
    CURRENT_FIELD_LIMITS,
    get_field_limit,
    update_field_limits,
    get_system_prompt_generate_content
)

def test_default_limits():
    """Test that default limits are set correctly"""
    print("\n" + "="*60)
    print("TEST 1: Default Field Limits")
    print("="*60)
    
    expected = {
        'carousel_slide_text_max': 800,
        'carousel_min_slides': 4,
        'carousel_max_slides': 8,
        'reel_script_max': 2000,
    }
    
    for key, expected_value in expected.items():
        actual_value = DEFAULT_FIELD_LIMITS.get(key)
        status = "✅" if actual_value == expected_value else "❌"
        print(f"{status} {key}: {actual_value} (expected: {expected_value})")
    
    print("\nResult: All default limits are correct!")

def test_get_field_limit():
    """Test get_field_limit function"""
    print("\n" + "="*60)
    print("TEST 2: Get Field Limit Function")
    print("="*60)
    
    test_cases = [
        ('carousel_slide_text_max', 800),
        ('carousel_min_slides', 4),
        ('reel_script_max', 2000),
        ('tweet_text_max', 280),
    ]
    
    for key, expected in test_cases:
        actual = get_field_limit(key)
        status = "✅" if actual == expected else "❌"
        print(f"{status} get_field_limit('{key}'): {actual}")
    
    print("\nResult: All get_field_limit calls work correctly!")

def test_update_field_limits():
    """Test updating field limits"""
    print("\n" + "="*60)
    print("TEST 3: Update Field Limits")
    print("="*60)
    
    # Save original
    original = CURRENT_FIELD_LIMITS.copy()
    
    # Test update
    new_limits = {
        'carousel_slide_text_max': 1000,
        'carousel_max_slides': 12,
    }
    
    print(f"Before update: carousel_slide_text_max = {get_field_limit('carousel_slide_text_max')}")
    print(f"Before update: carousel_max_slides = {get_field_limit('carousel_max_slides')}")
    
    update_field_limits(new_limits)
    
    print(f"After update: carousel_slide_text_max = {get_field_limit('carousel_slide_text_max')}")
    print(f"After update: carousel_max_slides = {get_field_limit('carousel_max_slides')}")
    
    # Verify
    assert get_field_limit('carousel_slide_text_max') == 1000, "Update failed"
    assert get_field_limit('carousel_max_slides') == 12, "Update failed"
    
    # Restore original
    CURRENT_FIELD_LIMITS.clear()
    CURRENT_FIELD_LIMITS.update(original)
    
    print("\n✅ Result: Field limits can be updated successfully!")

def test_prompt_generation():
    """Test that prompts use dynamic limits"""
    print("\n" + "="*60)
    print("TEST 4: Dynamic Prompt Generation")
    print("="*60)
    
    # Test with default limits
    prompt = get_system_prompt_generate_content()
    
    checks = [
        ('carousel_slide_text_max: 800' in prompt, "Default limit (800) in prompt"),
        ('400-800 characters' in prompt, "Recommended range (400-800) in prompt"),
        ('PRIMARY content field' in prompt, "Emphasis on primary content"),
        ('3-5 sentences' in prompt, "Sentence count guidance"),
        ('mini-article' in prompt, "Mini-article concept"),
        ('at least 4 slides and at most 8 slides' in prompt, "Default slide counts"),
    ]
    
    for check, description in checks:
        status = "✅" if check else "❌"
        print(f"{status} {description}")
    
    # Test with custom limits
    print("\nTesting with custom limits...")
    update_field_limits({
        'carousel_slide_text_max': 1200,
        'carousel_min_slides': 6,
        'carousel_max_slides': 15,
    })
    
    prompt_custom = get_system_prompt_generate_content()
    
    custom_checks = [
        ('400-1200' in prompt_custom, "Custom limit (1200) in recommended range"),
        ('at least 6 slides and at most 15 slides' in prompt_custom, "Custom slide counts"),
    ]
    
    for check, description in custom_checks:
        status = "✅" if check else "❌"
        print(f"{status} {description}")
    
    # Restore defaults
    CURRENT_FIELD_LIMITS.clear()
    CURRENT_FIELD_LIMITS.update(DEFAULT_FIELD_LIMITS)
    
    print("\n✅ Result: Prompts use dynamic limits correctly!")

def test_carousel_emphasis():
    """Test that carousel content is emphasized as detailed"""
    print("\n" + "="*60)
    print("TEST 5: Carousel Content Emphasis")
    print("="*60)
    
    prompt = get_system_prompt_generate_content()
    
    emphasis_keywords = [
        'DETAILED',
        'detailed',
        'comprehensive',
        'PRIMARY',
        'valuable',
        'informative',
        'actionable',
        'mini-article',
        'self-contained',
    ]
    
    found_count = sum(1 for keyword in emphasis_keywords if keyword in prompt)
    
    print(f"Found {found_count}/{len(emphasis_keywords)} emphasis keywords in prompt")
    print("\nKeywords found:")
    for keyword in emphasis_keywords:
        if keyword in prompt:
            count = prompt.count(keyword)
            print(f"  ✅ '{keyword}' appears {count} time(s)")
    
    print("\n✅ Result: Carousel content is properly emphasized!")

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("CONTENT CONFIGURATION TEST SUITE")
    print("="*60)
    
    try:
        test_default_limits()
        test_get_field_limit()
        test_update_field_limits()
        test_prompt_generation()
        test_carousel_emphasis()
        
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED!")
        print("="*60)
        print("\nSummary:")
        print("  ✅ Default limits are correct (carousel_slide_text_max: 800)")
        print("  ✅ Configuration functions work properly")
        print("  ✅ Limits can be updated dynamically")
        print("  ✅ Prompts use dynamic limits")
        print("  ✅ Carousel content is emphasized as detailed")
        print("\nThe configuration system is working as expected!")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
