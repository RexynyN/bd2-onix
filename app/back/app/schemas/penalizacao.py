"""
Penalizacao schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from .base import BaseResponse

class PenalizacaoBase(BaseModel):
    descricao: Optional[str] = Field(None, description="Descrição da penalização")
    final_penalizacao: Optional[date] = Field(None, description="Data final da penalização")
    id_usuario: Optional[int] = Field(None, description="ID do usuário")
    id_emprestimo: Optional[int] = Field(None, description="ID do empréstimo")

class PenalizacaoCreate(PenalizacaoBase):
    """Schema for creating a new penalty"""
    pass

class PenalizacaoUpdate(BaseModel):
    """Schema for updating penalty data"""
    descricao: Optional[str] = None
    final_penalizacao: Optional[date] = None
    id_usuario: Optional[int] = None
    id_emprestimo: Optional[int] = None

class PenalizacaoResponse(PenalizacaoBase):
    """Schema for penalty response"""
    id_penalizacao: int
    
    class Config:
        from_attributes = True

class PenalizacaoListResponse(BaseResponse):
    """Schema for penalty list response"""
    data: list[PenalizacaoResponse]
    total: int

class PenalizacaoDetalhada(BaseModel):
    """Schema for detailed penalty information"""
    id_penalizacao: int
    descricao: Optional[str]
    final_penalizacao: Optional[date]
    usuario_info: dict
    emprestimo_info: Optional[dict]
    ativa: bool
