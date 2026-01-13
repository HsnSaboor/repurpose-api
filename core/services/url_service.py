"""URL Content Extraction Service

Extracts main content from web URLs as clean Markdown using trafilatura.
"""

import logging
import re
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from trafilatura import fetch_url, extract, extract_metadata

logger = logging.getLogger(__name__)


class URLExtractionError(Exception):
    """Raised when URL extraction fails"""
    pass


class URLExtractor:
    """Extract main content from web URLs as Markdown"""
    
    # URLs that should not be processed (use dedicated handlers instead)
    BLOCKED_DOMAINS = [
        "youtube.com",
        "youtu.be",
        "www.youtube.com",
        "m.youtube.com",
    ]
    
    # Private/local IP patterns
    PRIVATE_PATTERNS = [
        r"^localhost",
        r"^127\.",
        r"^10\.",
        r"^172\.(1[6-9]|2[0-9]|3[0-1])\.",
        r"^192\.168\.",
        r"^0\.0\.0\.0",
        r"^\[::1\]",
    ]
    
    @classmethod
    def validate_url(cls, url: str) -> None:
        """
        Validate URL is safe to fetch.
        
        Raises:
            URLExtractionError: If URL is invalid or blocked
        """
        if not url or not url.strip():
            raise URLExtractionError("URL cannot be empty")
        
        # Parse URL
        try:
            parsed = urlparse(url)
        except Exception as e:
            raise URLExtractionError(f"Invalid URL format: {e}")
        
        # Must have scheme
        if parsed.scheme not in ("http", "https"):
            raise URLExtractionError(f"Invalid URL scheme: {parsed.scheme}. Must be http or https")
        
        # Must have host
        if not parsed.netloc:
            raise URLExtractionError("URL must have a host")
        
        host = parsed.netloc.lower()
        
        # Remove port if present
        if ":" in host:
            host = host.split(":")[0]
        
        # Check blocked domains (YouTube should use video processing)
        for blocked in cls.BLOCKED_DOMAINS:
            if host == blocked or host.endswith("." + blocked):
                raise URLExtractionError(
                    f"YouTube URLs should be processed as videos, not URLs. "
                    f"Use: python repurpose.py \"{url}\""
                )
        
        # Check private/local IPs
        for pattern in cls.PRIVATE_PATTERNS:
            if re.match(pattern, host):
                raise URLExtractionError(f"Cannot fetch private/local URLs: {host}")
    
    @classmethod
    def extract_from_url(
        cls,
        url: str,
        include_tables: bool = True,
        include_links: bool = True,
        include_images: bool = False,
    ) -> Dict[str, Any]:
        """
        Fetch URL and extract main content as Markdown.
        
        Args:
            url: The URL to fetch and extract
            include_tables: Include tables in output
            include_links: Preserve hyperlinks
            include_images: Include image references
            
        Returns:
            Dict with keys: content, title, author, date, description, sitename, original_url
            
        Raises:
            URLExtractionError: If fetch or extraction fails
        """
        # Validate URL first
        cls.validate_url(url)
        
        logger.info(f"Fetching URL: {url}")
        
        # Fetch the HTML
        try:
            downloaded = fetch_url(url)
        except Exception as e:
            logger.error(f"Failed to fetch URL {url}: {e}")
            raise URLExtractionError(f"Failed to fetch URL: {e}")
        
        if not downloaded:
            raise URLExtractionError(f"Failed to fetch URL: No content returned from {url}")
        
        # Extract main content as Markdown
        try:
            content = extract(
                downloaded,
                output_format="markdown",
                include_tables=include_tables,
                include_links=include_links,
                include_images=include_images,
                include_comments=False,
                favor_recall=True,  # Get more content rather than less
            )
        except Exception as e:
            logger.error(f"Failed to extract content from {url}: {e}")
            raise URLExtractionError(f"Failed to extract content: {e}")
        
        if not content or len(content.strip()) < 50:
            raise URLExtractionError(
                f"No meaningful content extracted from {url}. "
                "The page may be JavaScript-rendered, behind a paywall, or mostly images."
            )
        
        # Extract metadata
        metadata = None
        try:
            metadata = extract_metadata(downloaded)
        except Exception as e:
            logger.warning(f"Failed to extract metadata from {url}: {e}")
        
        result = {
            "content": content,
            "title": metadata.title if metadata and metadata.title else None,
            "author": metadata.author if metadata and metadata.author else None,
            "date": metadata.date if metadata and metadata.date else None,
            "description": metadata.description if metadata and metadata.description else None,
            "sitename": metadata.sitename if metadata and metadata.sitename else None,
            "original_url": url,
        }
        
        logger.info(
            f"Extracted {len(content)} chars from {url} "
            f"(title: {result['title'] or 'N/A'})"
        )
        
        return result
    
    @classmethod
    def is_url(cls, text: str) -> bool:
        """Check if text looks like a URL (not a file path)"""
        if not text:
            return False
        
        text = text.strip()
        
        # Must start with http:// or https://
        if text.startswith(("http://", "https://")):
            try:
                parsed = urlparse(text)
                return bool(parsed.netloc)
            except Exception:
                return False
        
        return False
    
    @classmethod
    def is_youtube_url(cls, url: str) -> bool:
        """Check if URL is a YouTube URL"""
        if not url:
            return False
        
        try:
            parsed = urlparse(url)
            host = parsed.netloc.lower()
            
            # Remove port if present
            if ":" in host:
                host = host.split(":")[0]
            
            for yt_domain in cls.BLOCKED_DOMAINS:
                if host == yt_domain or host.endswith("." + yt_domain):
                    return True
            
            return False
        except Exception:
            return False
