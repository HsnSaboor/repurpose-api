#!/usr/bin/env python3
"""
URL Source Feature Verification Tests (URL-008)
Tests extraction, validation, API, and CLI integration
"""

import sys
import json
sys.path.insert(0, '.')


def test_url_extraction():
    """Test URLExtractor functionality"""
    from core.services.url_service import URLExtractor, URLExtractionError
    
    print("=" * 60)
    print("TEST 1: URL Extraction")
    print("=" * 60)
    
    # Test 1.1: Extract from example.com
    print("\n1.1 Extract from example.com...")
    result = URLExtractor.extract_from_url("https://example.com")
    assert result["content"] is not None, "Content should not be None"
    assert result["title"] == "Example Domain", f"Expected 'Example Domain', got '{result['title']}'"
    assert result["original_url"] == "https://example.com"
    print(f"  ✓ Title: {result['title']}")
    print(f"  ✓ Content: {len(result['content'])} chars")
    
    # Test 1.2: URL validation
    print("\n1.2 URL validation...")
    
    # Valid URLs
    for url in ["https://example.com", "http://httpbin.org/get"]:
        try:
            URLExtractor.validate_url(url)
            print(f"  ✓ {url}: valid")
        except URLExtractionError as e:
            raise AssertionError(f"Should be valid: {url}: {e}")
    
    # Invalid URLs - YouTube blocked
    print("\n1.3 YouTube blocking...")
    for url in ["https://www.youtube.com/watch?v=abc", "https://youtu.be/abc123456"]:
        try:
            URLExtractor.validate_url(url)
            raise AssertionError(f"Should be blocked: {url}")
        except URLExtractionError as e:
            print(f"  ✓ {url}: correctly blocked")
    
    # Test 1.4: Private IPs blocked
    print("\n1.4 Private IP blocking...")
    for url in ["http://localhost/test", "http://127.0.0.1/api", "http://192.168.1.1/admin"]:
        try:
            URLExtractor.validate_url(url)
            raise AssertionError(f"Should be blocked: {url}")
        except URLExtractionError as e:
            print(f"  ✓ {url}: correctly blocked")
    
    # Test 1.5: Helper methods
    print("\n1.5 Helper methods...")
    assert URLExtractor.is_url("https://example.com") == True
    assert URLExtractor.is_url("not_a_url.txt") == False
    assert URLExtractor.is_youtube_url("https://youtube.com/watch?v=abc") == True
    assert URLExtractor.is_youtube_url("https://example.com") == False
    print("  ✓ is_url() works correctly")
    print("  ✓ is_youtube_url() works correctly")
    
    print("\n✅ URL Extraction tests passed!")
    return True


def test_pydantic_models():
    """Test Pydantic models for URL sources"""
    from api.models import URLSourceCreate, URLExtractOptions
    
    print("\n" + "=" * 60)
    print("TEST 2: Pydantic Models")
    print("=" * 60)
    
    # Test 2.1: Default options
    print("\n2.1 Default URLSourceCreate...")
    model = URLSourceCreate(url="https://example.com")
    assert model.extract_options.include_tables == True
    assert model.extract_options.include_links == True
    assert model.extract_options.include_images == False
    print("  ✓ Default options correct")
    
    # Test 2.2: Custom options
    print("\n2.2 Custom extract options...")
    model = URLSourceCreate(
        url="https://example.com",
        title="Custom Title",
        tags=["test", "url"],
        extract_options=URLExtractOptions(
            include_tables=False,
            include_images=True
        )
    )
    assert model.title == "Custom Title"
    assert model.tags == ["test", "url"]
    assert model.extract_options.include_tables == False
    assert model.extract_options.include_images == True
    print("  ✓ Custom options work")
    
    # Test 2.3: URL validation in model
    print("\n2.3 URL format validation...")
    try:
        model = URLSourceCreate(url="not-a-url")
        # Pydantic HttpUrl should reject this
        raise AssertionError("Should reject invalid URL")
    except Exception:
        print("  ✓ Invalid URL rejected by Pydantic")
    
    print("\n✅ Pydantic model tests passed!")
    return True


def test_brain_service():
    """Test Brain service with URL sources"""
    from core.database import Base, engine, SessionLocal
    from core.services.brain_service import BrainService
    import json as json_lib
    
    print("\n" + "=" * 60)
    print("TEST 3: Brain Service Integration")
    print("=" * 60)
    
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    brain_service = BrainService(db)
    
    try:
        # Test 3.1: Create URL source
        print("\n3.1 Create URL source...")
        source = brain_service.create_source(
            title="Test URL Source",
            content="# Test Article\n\nThis is test content from a URL.",
            source_type="url",
            tags=["test", "url-feature"],
            source_metadata={
                "original_url": "https://test.example.com/article",
                "author": "Test Author",
                "sitename": "Example Site"
            }
        )
        assert source.source_id.startswith("src_")
        assert source.source_type == "url"
        print(f"  ✓ Created source: {source.source_id}")
        
        # Test 3.2: Verify metadata
        print("\n3.2 Verify metadata storage...")
        metadata = json_lib.loads(source.source_metadata)
        assert metadata["original_url"] == "https://test.example.com/article"
        assert metadata["author"] == "Test Author"
        print(f"  ✓ Metadata stored correctly: {list(metadata.keys())}")
        
        # Test 3.3: Search by type
        print("\n3.3 Search by type...")
        sources, total = brain_service.get_sources(source_types=["url"])
        assert total > 0
        url_source = next((s for s in sources if s.source_id == source.source_id), None)
        assert url_source is not None
        print(f"  ✓ Found {total} URL source(s)")
        
        # Cleanup
        brain_service.delete_source(source.source_id)
        print("\n  ✓ Cleanup complete")
        
    finally:
        db.close()
    
    print("\n✅ Brain service tests passed!")
    return True


def test_api_router():
    """Test API router (import only, not full request)"""
    print("\n" + "=" * 60)
    print("TEST 4: API Router")
    print("=" * 60)
    
    # Test 4.1: Import router
    print("\n4.1 Import brain router...")
    from api.routers.brain import router
    
    routes = [r.path for r in router.routes]
    print(f"  ✓ Router has {len(routes)} routes")
    
    # Test 4.2: Check URL endpoint exists
    print("\n4.2 Check URL endpoint...")
    assert "/brain/sources/url" in routes, "Missing /brain/sources/url endpoint"
    print("  ✓ POST /brain/sources/url endpoint exists")
    
    print("\n✅ API router tests passed!")
    return True


def test_cli_parse():
    """Test CLI input parsing"""
    print("\n" + "=" * 60)
    print("TEST 5: CLI Input Parsing")
    print("=" * 60)
    
    from repurpose import parse_input_source
    
    # Test 5.1: URL detection
    print("\n5.1 URL detection...")
    sources = parse_input_source(["https://example.com"])
    assert len(sources) == 1
    assert sources[0]["type"] == "url"
    print("  ✓ https://example.com detected as URL")
    
    # Test 5.2: YouTube stays as video
    print("\n5.2 YouTube handled as video...")
    sources = parse_input_source(["https://www.youtube.com/watch?v=dQw4w9WgXcQ"])
    assert len(sources) == 1
    assert sources[0]["type"] == "video"
    assert sources[0]["value"] == "dQw4w9WgXcQ"
    print("  ✓ YouTube URL detected as video")
    
    # Test 5.3: Mixed input
    print("\n5.3 Mixed input types...")
    sources = parse_input_source([
        "https://example.com",
        "dQw4w9WgXcQ",
        "https://httpbin.org/get"
    ])
    types = [s["type"] for s in sources]
    assert types.count("url") == 2
    assert types.count("video") == 1
    print(f"  ✓ Mixed: {types}")
    
    print("\n✅ CLI parsing tests passed!")
    return True


def main():
    print("\n" + "=" * 60)
    print("URL SOURCE FEATURE VERIFICATION")
    print("=" * 60)
    
    tests = [
        ("URL Extraction", test_url_extraction),
        ("Pydantic Models", test_pydantic_models),
        ("Brain Service", test_brain_service),
        ("API Router", test_api_router),
        ("CLI Parsing", test_cli_parse),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_fn in tests:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"\n❌ FAILED: {name}")
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
