import pytest
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
BASE_URL = "http://localhost:8002"  # Update if different
API_KEY = os.getenv("GEMINI_API_KEY")

# Sample test video ID
TEST_VIDEO_ID = "dQw4w9WgXcQ"

@pytest.fixture
def headers():
    return {"Authorization": f"Bearer {API_KEY}"}

def test_transcript_endpoint(headers):
    response = requests.get(f"{BASE_URL}/transcript/{TEST_VIDEO_ID}", headers=headers)
    assert response.status_code == 200
    assert "text" in response.json()

def test_content_ideas_endpoint(headers):
    response = requests.post(
        f"{BASE_URL}/content-ideas/",
        json={"video_id": TEST_VIDEO_ID},
        headers=headers
    )
    assert response.status_code == 200
    assert "ideas" in response.json()

def test_generate_content_endpoint(headers):
    response = requests.post(
        f"{BASE_URL}/generate-content/",
        json={
            "video_id": TEST_VIDEO_ID,
            "content_type": "reel",
            "transcript_snippet": "Sample transcript snippet"
        },
        headers=headers
    )
    assert response.status_code == 200
    assert "content" in response.json()

def test_carousel_endpoint(headers):
    response = requests.post(
        f"{BASE_URL}/carousel/",
        json={"video_id": TEST_VIDEO_ID},
        headers=headers
    )
    assert response.status_code == 200
    assert "carousel" in response.json()

def test_tweet_endpoint(headers):
    response = requests.post(
        f"{BASE_URL}/tweet/",
        json={"video_id": TEST_VIDEO_ID},
        headers=headers
    )
    assert response.status_code == 200
    assert "tweet" in response.json()