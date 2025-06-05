"""
Main FastAPI application
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.db.database import db_manager

# Import routers
from app.routers import (
    usuario, biblioteca, emprestimo, media, 
    estoque, autor, penalizacao
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting up...")
    try:
        db_manager.create_pool()
        logger.info("Database connection pool created")
    except Exception as e:
        logger.error(f"Failed to create database connection pool: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    db_manager.close_pool()
    logger.info("Database connection pool closed")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(usuario.router, prefix=settings.API_V1_PREFIX)
app.include_router(biblioteca.router, prefix=settings.API_V1_PREFIX)
app.include_router(emprestimo.router, prefix=settings.API_V1_PREFIX)
app.include_router(media.router, prefix=settings.API_V1_PREFIX)
app.include_router(estoque.router, prefix=settings.API_V1_PREFIX)
app.include_router(autor.router, prefix=settings.API_V1_PREFIX)
app.include_router(penalizacao.router, prefix=settings.API_V1_PREFIX)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Bem-vindo ao {settings.PROJECT_NAME}!",
        "version": settings.VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        
        return {
            "status": "healthy",
            "database": "connected",
            "version": settings.VERSION
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.get(f"{settings.API_V1_PREFIX}/info")
async def api_info():
    """API information endpoint"""
    return {
        "api_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": settings.DESCRIPTION,
        "endpoints": {
            "usuarios": f"{settings.API_V1_PREFIX}/usuarios",
            "bibliotecas": f"{settings.API_V1_PREFIX}/bibliotecas",
            "emprestimos": f"{settings.API_V1_PREFIX}/emprestimos",
            "midias": f"{settings.API_V1_PREFIX}/midias",
            "estoque": f"{settings.API_V1_PREFIX}/estoque",
            "autores": f"{settings.API_V1_PREFIX}/autores",
            "penalizacoes": f"{settings.API_V1_PREFIX}/penalizacoes"
        }
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
