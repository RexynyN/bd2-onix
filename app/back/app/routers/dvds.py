from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.schemas.dvd import DVDCreate, DVDUpdate, DVDResponse, DVDWithAuthors
from app.services.dvd_service import DVDService
from app.schemas.schemas import DVD

router = APIRouter()
dvd_service = DVDService()

@router.post("/", response_model=DVDResponse, status_code=201)
async def create_dvd(dvd: DVDCreate):
    """Criar um novo DVD"""
    try:
        return await dvd_service.create_dvd(dvd)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{dvd_id}", response_model=DVDResponse)
async def get_dvd(dvd_id: int):
    """Buscar DVD por ID"""
    dvd = await dvd_service.get_dvd_by_id(dvd_id)
    if not dvd:
        raise HTTPException(status_code=404, detail="DVD não encontrado")
    return dvd

@router.get("/", response_model=List[DVDResponse])
async def list_dvds(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """Listar DVDs com paginação"""
    return await dvd_service.get_dvds(skip=skip, limit=limit)

@router.put("/{dvd_id}", response_model=DVDResponse)
async def update_dvd(dvd_id: int, dvd: DVDUpdate):
    """Atualizar DVD"""
    try:
        updated_dvd = await dvd_service.update_dvd(dvd_id, dvd)
        if not updated_dvd:
            raise HTTPException(status_code=404, detail="DVD não encontrado")
        return updated_dvd
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{dvd_id}")
async def delete_dvd(dvd_id: int):
    """Excluir DVD"""
    try:
        deleted = await dvd_service.delete_dvd(dvd_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="DVD não encontrado")
        return {"message": "DVD excluído com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/", response_model=List[DVDResponse])
async def search_dvds(q: str = Query(..., min_length=1)):
    """Buscar DVDs por título, ISAN ou distribuidora"""
    return await dvd_service.search_dvds(q)

@router.get("/{dvd_id}/autores", response_model=DVDWithAuthors)
async def get_dvd_with_authors(dvd_id: int):
    """Buscar DVD com seus autores/diretores"""
    dvd = await dvd_service.get_dvd_with_authors(dvd_id)
    if not dvd:
        raise HTTPException(status_code=404, detail="DVD não encontrado")
    return dvd

@router.get("/pesquisar/dvds", response_model=List[DVD])
async def search_dvds(
    title: Optional[str] = Query(None, description="Título do item a ser pesquisado")
):
    """Buscar itens do estoque a partir do ID do estoque ou da biblioteca"""
    if not title:
        raise HTTPException(status_code=400, detail="Título é obrigatório para busca")
    return await dvd_service.search_dvds(title)