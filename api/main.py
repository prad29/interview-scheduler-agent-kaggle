from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from api.routes import candidate_routes, job_routes, interview_routes
from config import config
from utils.logger import setup_logger

# Setup logging
logger = setup_logger("API", "api.log")

app = FastAPI(
    title="Intelligent Recruitment System API",
    description="API for AI-powered recruitment and talent matching",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    candidate_routes.router, 
    prefix="/api/candidates", 
    tags=["candidates"]
)
app.include_router(
    job_routes.router, 
    prefix="/api/jobs", 
    tags=["jobs"]
)
app.include_router(
    interview_routes.router, 
    prefix="/api/interviews", 
    tags=["interviews"]
)

# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "An internal server error occurred",
            "detail": str(exc) if config.DEBUG else None
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail
        }
    )

# Root endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Intelligent Recruitment System API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Intelligent Recruitment System",
        "version": "1.0.0"
    }

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("Starting Intelligent Recruitment System API")
    logger.info(f"Debug mode: {config.DEBUG}")

@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("Shutting down Intelligent Recruitment System API")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=config.APP_HOST,
        port=config.APP_PORT,
        reload=config.DEBUG
    )