#!/usr/bin/env python3
"""
Simple server starter for the YouTube Repurposer API
"""

import uvicorn

if __name__ == "__main__":
    print("🚀 Starting YouTube Repurposer API Server...")
    print("📍 Server running at: http://127.0.0.1:8002")
    print("📚 API Documentation: http://127.0.0.1:8002/docs")
    print("-" * 50)
    
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8002,
        reload=True,
        log_level="info"
    )