import time
from fastapi import FastAPI, HTTPException
from app.utils.logger import setup_logging, get_logger
from app.schema.models import (
    AnalyzeRequest, TopicRequest, AnalyzeResponse, TopicResponse,
    HealthResponse
)
from app.service.analysis import analyze_text, analyze_topic
from app.core.config import get_settings

setup_logging()
logger = get_logger(__name__)

def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description="AI Gap Finder - Microservice for scientific research gap analysis"
    )

    @app.post("/analyze", response_model=AnalyzeResponse)
    async def analyze(request: AnalyzeRequest):
        start_time = time.time()
        try:
            result = await analyze_text(request)
            processing_time = round(time.time() - start_time, 2)
            result['processing_time'] = processing_time
            return result
        except Exception as e:
            logger.error(f"Error during /analyze: {str(e)}")
            raise HTTPException(status_code=500, detail="An error occurred during analysis.")

    @app.post("/topic", response_model=TopicResponse)
    async def analyze_topic_route(request: TopicRequest):
        start_time = time.time()
        try:
            result = await analyze_topic(request)
            processing_time = round(time.time() - start_time, 2)
            result['processing_time'] = processing_time
            return result
        except Exception as e:
            logger.error(f"Error during /topic: {str(e)}")
            raise HTTPException(status_code=500, detail="An error occurred during topic analysis.")

    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        return HealthResponse(status="healthy", version=settings.version, timestamp=str(time.time()))

    return app
