from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import date
from app.schemas.schemas import Emprestimo, EmprestimoCreate, EmprestimoCompleto, RelatorioEmprestimos
from app.services.emprestimo_service import emprestimo_service

router = APIRouter()

@router.post("/", response_model=Emprestimo, status_code=201)
def create_emprestimo(emprestimo: EmprestimoCreate):
    """Criar um novo empréstimo"""
    return emprestimo_service.create_emprestimo(emprestimo)

@router.get("/{id_emprestimo}", response_model=Emprestimo)
def get_emprestimo(id_emprestimo: int):
    """Buscar empréstimo por ID"""
    emprestimo = emprestimo_service.get_emprestimo(id_emprestimo)
    if not emprestimo:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado")
    return emprestimo

@router.get("/", response_model=List[Emprestimo])
def get_emprestimos(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros")
):
    """Listar empréstimos com paginação"""
    return emprestimo_service.get_emprestimos(skip=skip, limit=limit)

@router.patch("/{id_emprestimo}/devolver", response_model=Emprestimo)
def devolver_item(
    id_emprestimo: int, 
    data_devolucao: date = Query(None, description="Data da devolução (opcional, usa data atual se não informada)")
):
    """Registrar devolução de item emprestado"""
    return emprestimo_service.devolver_item(id_emprestimo, data_devolucao)

@router.get("/em-andamento/", response_model=List[EmprestimoCompleto])
def get_emprestimos_em_andamento(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros")
):
    """Listar empréstimos em andamento com informações completas"""
    return emprestimo_service.get_emprestimos_em_andamento(skip, limit)

@router.get("/vencidos/", response_model=List[EmprestimoCompleto])
def get_emprestimos_vencidos(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros")
):
    """Listar empréstimos vencidos"""
    return emprestimo_service.get_emprestimos_vencidos(skip, limit)

@router.get("/relatorio/", response_model=RelatorioEmprestimos)
def get_relatorio_emprestimos():
    """Obter relatório resumido de empréstimos"""
    return emprestimo_service.get_relatorio_emprestimos()

@router.get("/pesquisar/emprestimos", response_model=List[Emprestimo])
def search_emprestimos(
    query: Optional[str] = Query(None, description="Título do item a ser pesquisado")
):

    """Buscar itens do estoque a partir do ID do estoque ou da biblioteca"""
    if not query:
        raise HTTPException(status_code=400, detail="Título é obrigatório para busca")
    return emprestimo_service.search_emprestimos(query)