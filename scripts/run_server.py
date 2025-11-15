#!/usr/bin/env python3
"""
YouTube Repurposer API Server Runner

Development server runner for the YouTube Repurposer API.
This script starts the FastAPI application using uvicorn with development settings.
"""

import uvicorn
from app.core.config.settings import settings


def main():
    """Run the development server with appropriate settings."""
    print("🚀 Starting YouTube Repurposer API Development Server...")
    print(f"📍 Server will run at: http://{settings.host}:{settings.port}")
    print(f"📚 API Documentation: http://{settings.host}:{settings.port}/docs")
    print(f"🔍 Interactive API Explorer: http://{settings.host}:{settings.port}/redoc")
    print("-" * 60)
    
    try:
        uvicorn.run(
            "app.main:app",
            host=settings.host,
            port=settings.port,
            reload=settings.debug,
            log_level=settings.log_level.lower(),
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())