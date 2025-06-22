from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.schemas.schemas import Estoque, EstoqueCreate, EstoqueUpdate, DisponibilidadeItem, TituloSearch
from app.services.estoque_service import estoque_service

router = APIRouter()

@router.post("/", response_model=Estoque, status_code=201)
def create_estoque(estoque: EstoqueCreate):
    """Adicionar item ao estoque"""
    return estoque_service.create_estoque(estoque)

@router.get("/{id_estoque}", response_model=Estoque)
def get_estoque(id_estoque: int):
    """Buscar item do estoque por ID"""
    estoque = estoque_service.get_estoque(id_estoque)
    if not estoque:
        raise HTTPException(status_code=404, detail="Item do estoque não encontrado")
    return estoque

@router.get("/", response_model=List[Estoque])
def get_estoques(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros")
):
    """Listar itens do estoque com paginação"""
    return estoque_service.get_estoques(skip=skip, limit=limit)

@router.get("/biblioteca/{id_biblioteca}", response_model=List[Estoque])
def get_estoque_por_biblioteca(
    id_biblioteca: int,
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros")
):
    """Listar estoque de uma biblioteca específica"""
    return estoque_service.get_estoque_por_biblioteca(id_biblioteca, skip, limit)

@router.get("/disponibilidade/{id_titulo}", response_model=DisponibilidadeItem)
def get_disponibilidade_item(id_titulo: int):
    """Verificar disponibilidade de um título"""
    disponibilidade = estoque_service.get_disponibilidade_item(id_titulo)
    if not disponibilidade:
        raise HTTPException(status_code=404, detail="Título não encontrado")
    return disponibilidade

@router.put("/{id_estoque}", response_model=Estoque)
def update_estoque(id_estoque: int, estoque: EstoqueUpdate):
    """Atualizar item do estoque"""
    updated_estoque = estoque_service.update_estoque(id_estoque, estoque)
    if not updated_estoque:
        raise HTTPException(status_code=404, detail="Item do estoque não encontrado")
    return updated_estoque

@router.delete("/{id_estoque}")
def delete_estoque(id_estoque: int):
    """Remover item do estoque"""
    if not estoque_service.delete_estoque(id_estoque):
        raise HTTPException(status_code=404, detail="Item do estoque não encontrado")
    return {"message": "Item removido do estoque com sucesso"}


@router.get("/pesquisar/titulo", response_model=List[TituloSearch])
def search_from_title(
    title: Optional[str] = Query(None, description="Título do item a ser pesquisado")
):
    """Buscar itens do estoque a partir do título"""
    if not title:
        raise HTTPException(status_code=400, detail="Título é obrigatório para busca")
    return estoque_service.search_from_title(title)


@router.get("/pesquisar/estoque", response_model=List[Estoque])
def search_from_estoque(
    title: Optional[str] = Query(None, description="Título do item a ser pesquisado")
):
    """Buscar itens do estoque a partir do ID do estoque ou da biblioteca"""
    if not title:
        raise HTTPException(status_code=400, detail="Título é obrigatório para busca")
    return estoque_service.search_from_estoque(title)