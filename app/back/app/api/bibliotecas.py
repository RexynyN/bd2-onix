from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.schemas.schemas import Biblioteca, BibliotecaCreate, BibliotecaUpdate
from app.services.biblioteca_service import biblioteca_service

router = APIRouter()

@router.post("/", response_model=Biblioteca, status_code=201)
def create_biblioteca(biblioteca: BibliotecaCreate):

    return biblioteca_service.create_biblioteca(biblioteca)

@router.get("/{id_biblioteca}", response_model=Biblioteca)
def get_biblioteca(id_biblioteca: int):

    biblioteca = biblioteca_service.get_biblioteca(id_biblioteca)
    if not biblioteca:
        raise HTTPException(status_code=404, detail="Biblioteca não encontrada")
    return biblioteca

@router.get("/", response_model=List[Biblioteca])
def get_bibliotecas(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros")
):
    return biblioteca_service.get_bibliotecas(skip=skip, limit=limit)

@router.put("/{id_biblioteca}", response_model=Biblioteca)
def update_biblioteca(id_biblioteca: int, biblioteca: BibliotecaUpdate):
    updated_biblioteca = biblioteca_service.update_biblioteca(id_biblioteca, biblioteca)
    if not updated_biblioteca:
        raise HTTPException(status_code=404, detail="Biblioteca não encontrada")
    return updated_biblioteca

@router.delete("/{id_biblioteca}")
def delete_biblioteca(id_biblioteca: int):
    if not biblioteca_service.delete_biblioteca(id_biblioteca):
        raise HTTPException(status_code=404, detail="Biblioteca não encontrada")
    return {"message": "Biblioteca excluída com sucesso"}
