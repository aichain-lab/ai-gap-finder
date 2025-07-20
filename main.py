#!/usr/bin/env python3
"""
AI Gap Finder Microservice
Main entry point for the FastAPI application
"""

import uvicorn
from app.core.config import get_settings
from app.api.app import create_app

def main():
    """Main entry point"""
    settings = get_settings()
    app = create_app()
    
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

if __name__ == "__main__":
    main()
