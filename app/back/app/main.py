from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api import usuarios, emprestimos, estoque, livros
from app.routers import revistas, dvds, artigos, biblioteca, autor
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar instância da aplicação FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(
    usuarios.router, 
    prefix=f"{settings.API_V1_STR}/usuarios", 
    tags=["Usuários"]
)

app.include_router(
    emprestimos.router, 
    prefix=f"{settings.API_V1_STR}/emprestimos", 
    tags=["Empréstimos"]
)

app.include_router(
    estoque.router, 
    prefix=f"{settings.API_V1_STR}/estoque", 
    tags=["Estoque"]
)



# Incluir os roteadores no main
app.include_router(revistas.router, prefix="/api/v1/revistas", tags=["revistas"])
app.include_router(livros.router, prefix="/api/v1/livros", tags=["revistas"])
app.include_router(dvds.router, prefix="/api/v1/dvds", tags=["dvds"])
app.include_router(artigos.router, prefix="/api/v1/artigos", tags=["artigos"])
app.include_router(biblioteca.router, prefix="/api/v1/bibliotecas", tags=["bibliotecas"])
app.include_router(autor.router, prefix="/api/v1/autores", tags=["autores"])

# Rota raiz
@app.get("/")
def read_root():
    return {
        "message": "Sistema de Gerenciamento de Biblioteca",
        "version": settings.VERSION,
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

# Rota de health check
@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "API funcionando corretamente"}

# Handler global para exceções
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Erro interno: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor"}
    )

# Evento de inicialização
@app.on_event("startup")
async def startup_event():
    logger.info(f"Iniciando {settings.PROJECT_NAME}")
    logger.info(f"Versão: {settings.VERSION}")

# Evento de finalização
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Finalizando aplicação")
    from app.database.connection import db
    db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
