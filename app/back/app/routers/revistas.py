from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.schemas.revista import RevistaCreate, RevistaUpdate, RevistaResponse, RevistaWithAuthors
from app.services.revista_service import RevistaService
from app.schemas.schemas import Revista

router = APIRouter()
revista_service = RevistaService()

@router.post("/", response_model=RevistaResponse, status_code=201)
async def create_revista(revista: RevistaCreate):
    """Criar uma nova revista"""
    try:
        return await revista_service.create_revista(revista)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{revista_id}", response_model=RevistaResponse)
async def get_revista(revista_id: int):
    """Buscar revista por ID"""
    revista = await revista_service.get_revista_by_id(revista_id)
    if not revista:
        raise HTTPException(status_code=404, detail="Revista não encontrada")
    return revista

@router.get("/", response_model=List[RevistaResponse])
async def list_revistas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """Listar revistas com paginação"""
    return await revista_service.get_revistas(skip=skip, limit=limit)

@router.put("/{revista_id}", response_model=RevistaResponse)
async def update_revista(revista_id: int, revista: RevistaUpdate):
    """Atualizar revista"""
    try:
        updated_revista = await revista_service.update_revista(revista_id, revista)
        if not updated_revista:
            raise HTTPException(status_code=404, detail="Revista não encontrada")
        return updated_revista
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{revista_id}")
async def delete_revista(revista_id: int):
    """Excluir revista"""
    try:
        deleted = await revista_service.delete_revista(revista_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Revista não encontrada")
        return {"message": "Revista excluída com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/", response_model=List[RevistaResponse])
async def search_revistas(q: str = Query(..., min_length=1)):
    """Buscar revistas por título, ISSN ou editora"""
    return await revista_service.search_revistas(q)

@router.get("/{revista_id}/autores", response_model=RevistaWithAuthors)
async def get_revista_with_authors(revista_id: int):
    """Buscar revista com seus autores"""
    revista = await revista_service.get_revista_with_authors(revista_id)
    if not revista:
        raise HTTPException(status_code=404, detail="Revista não encontrada")
    return revista


@router.get("/pesquisar/revistas", response_model=List[Revista])
async def search_revistas(
    title: Optional[str] = Query(None, description="Título do item a ser pesquisado")
):
    """Buscar itens do estoque a partir do ID do estoque ou da biblioteca"""
    if not title:
        raise HTTPException(status_code=400, detail="Título é obrigatório para busca")
    return await revista_service.search_revistas(title)