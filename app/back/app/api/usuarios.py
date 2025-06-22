from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.schemas.schemas import Usuario, UsuarioCreate, UsuarioUpdate
from app.services.usuario_service import usuario_service

router = APIRouter()

@router.post("/", response_model=Usuario, status_code=201)
def create_usuario(usuario: UsuarioCreate):
    """Criar um novo usuário"""
    return usuario_service.create_usuario(usuario)

@router.get("/{id_usuario}", response_model=Usuario)
def get_usuario(id_usuario: int):
    """Buscar usuário por ID"""
    usuario = usuario_service.get_usuario(id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario

@router.get("/", response_model=List[Usuario])
def get_usuarios(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros")
):
    """Listar usuários com paginação"""
    return usuario_service.get_usuarios(skip=skip, limit=limit)

@router.put("/{id_usuario}", response_model=Usuario)
def update_usuario(id_usuario: int, usuario: UsuarioUpdate):
    """Atualizar dados do usuário"""
    updated_usuario = usuario_service.update_usuario(id_usuario, usuario)
    if not updated_usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return updated_usuario

@router.delete("/{id_usuario}")
def delete_usuario(id_usuario: int):
    """Excluir usuário"""
    if not usuario_service.delete_usuario(id_usuario):
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"message": "Usuário excluído com sucesso"}

@router.get("/emprestimos/ativos", response_model=List[Usuario])
def get_usuarios_com_emprestimos_ativos(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros")
):
    """Listar usuários com empréstimos em andamento"""
    return usuario_service.get_usuarios_com_emprestimos_em_andamento(skip, limit)

@router.get("/pesquisar/usuarios", response_model=List[Usuario])
def search_usuarios(
    name: Optional[str] = Query(None, description="Título do item a ser pesquisado")
):

    """Buscar itens do estoque a partir do ID do estoque ou da biblioteca"""
    if not name:
        raise HTTPException(status_code=400, detail="Título é obrigatório para busca")
    return usuario_service.search_usuarios(name)