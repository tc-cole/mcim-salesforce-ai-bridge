from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
from dotenv import load_dotenv
from src.models.schemas import MatchRequest, MatchResponse, HealthResponse, WelcomeResponse, ErrorResponse
from src.ai.mockservice import MockService
from src.exceptions import (
    SalesforceAIBridgeException,
    ProcessingError,
)

load_dotenv()

app = FastAPI(
    title="Salesforce AI Bridge",
    description="A bridge application between Salesforce and external AI systems",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize mock AI service
ai_service = MockService()

# Custom exception handlers
@app.exception_handler(SalesforceAIBridgeException)
async def custom_exception_handler(request: Request, exc: SalesforceAIBridgeException):
    """Handle custom application exceptions with appropriate HTTP status codes."""
    logger.error(f"Application error: {exc.message}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.__class__.__name__,
            message=exc.message,
            details=str(exc)
        ).model_dump()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {str(exc)}")
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred",
            details=str(exc)
        ).model_dump()
    )

@app.get("/", response_model=WelcomeResponse)
async def root():
    """Root endpoint returning a welcome message."""
    return WelcomeResponse(message="Salesforce AI Bridge is running")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Basic health check - could be extended to check dependencies
        return HealthResponse(status="healthy")
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.post("/match", response_model=MatchResponse)
async def match_asset(request: MatchRequest):
    """
    Process asset data and return matching information.
    
    Args:
        request: MatchRequest containing asset information
        
    Returns:
        MatchResponse with processing results
        
    Raises:
        ValidationError: For invalid input data
        ProcessingError: For processing failures
        AIServiceError: For AI service issues
        CacheError: For cache operation failures
    """
    try:
        # Process the request through the mock AI service
        logger.info(f"Processing asset match request for manufacturer: {request.manufacturer_name}")
        
        ai_response = ai_service.process_asset_data(request.model_dump())
        
        # Use the create_match_response method
        response = ai_response.create_match_response(request.model_dump())
        
        logger.info(f"Successfully processed asset match request")
        return response

    except SalesforceAIBridgeException:
        # Re-raise custom exceptions to be handled by custom handler
        raise
    except Exception as e:
        # Convert unexpected exceptions to ProcessingError
        logger.error(f"Unexpected error in match_asset: {str(e)}")
        raise ProcessingError(f"Failed to process asset data: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))