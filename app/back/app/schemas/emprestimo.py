"""
Emprestimo schemas for request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date
from .base import BaseResponse

class EmprestimoBase(BaseModel):
    data_emprestimo: date = Field(..., description="Data do empréstimo")
    data_devolucao_prevista: Optional[date] = Field(None, description="Data prevista para devolução")
    data_devolucao: Optional[date] = Field(None, description="Data real da devolução")
    id_estoque: int = Field(..., description="ID do item do estoque")
    id_usuario: int = Field(..., description="ID do usuário")

    @validator('data_devolucao_prevista')
    def validate_data_devolucao_prevista(cls, v, values):
        if v and 'data_emprestimo' in values and v < values['data_emprestimo']:
            raise ValueError('Data de devolução prevista deve ser posterior à data do empréstimo')
        return v

    @validator('data_devolucao')
    def validate_data_devolucao(cls, v, values):
        if v and 'data_emprestimo' in values and v < values['data_emprestimo']:
            raise ValueError('Data de devolução deve ser posterior à data do empréstimo')
        return v

class EmprestimoCreate(EmprestimoBase):
    """Schema for creating a new loan"""
    pass

class EmprestimoUpdate(BaseModel):
    """Schema for updating loan data"""
    data_emprestimo: Optional[date] = None
    data_devolucao_prevista: Optional[date] = None
    data_devolucao: Optional[date] = None
    id_estoque: Optional[int] = None
    id_usuario: Optional[int] = None

class EmprestimoResponse(EmprestimoBase):
    """Schema for loan response"""
    id_emprestimo: int
    
    class Config:
        from_attributes = True

class EmprestimoListResponse(BaseResponse):
    """Schema for loan list response"""
    data: list[EmprestimoResponse]
    total: int

class EmprestimoDetalhado(BaseModel):
    """Schema for detailed loan information"""
    id_emprestimo: int
    data_emprestimo: date
    data_devolucao_prevista: Optional[date]
    data_devolucao: Optional[date]
    usuario_info: dict
    item_info: dict
    status: str  # 'ativo', 'devolvido', 'atrasado'

class DevolucaoRequest(BaseModel):
    """Schema for returning a loan"""
    data_devolucao: date = Field(..., description="Data da devolução")
