from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.schemas.schemas import Livro, LivroCreate, LivroUpdate
from app.services.livro_service import livro_service

router = APIRouter()

@router.post("/", response_model=Livro, status_code=201)
def create_livro(livro: LivroCreate):
    return livro_service.create_livro(livro)

@router.get("/{id_livro}", response_model=Livro)
def get_livro(id_livro: int):
    livro = livro_service.get_livro(id_livro)
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return livro

@router.get("/", response_model=List[Livro])
def get_livros(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros")
):
    return livro_service.get_livros(skip=skip, limit=limit)

@router.get("/search/", response_model=List[Livro])
def search_livros(q: str = Query(..., min_length=1, description="Termo de busca")):
    return livro_service.search_livros(q)

@router.put("/{id_livro}", response_model=Livro)
def update_livro(id_livro: int, livro: LivroUpdate):
    updated_livro = livro_service.update_livro(id_livro, livro)
    if not updated_livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return updated_livro

@router.delete("/{id_livro}")
def delete_livro(id_livro: int):
    if not livro_service.delete_livro(id_livro):
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return {"message": "Livro excluído com sucesso"}
