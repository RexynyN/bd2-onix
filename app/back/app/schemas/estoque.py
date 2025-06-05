"""
Estoque schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from .base import BaseResponse

class EstoqueBase(BaseModel):
    condicao: Optional[str] = Field(None, max_length=100, description="Condição do item")
    id_titulo: int = Field(..., description="ID do título")
    id_biblioteca: int = Field(..., description="ID da biblioteca")

class EstoqueCreate(EstoqueBase):
    """Schema for creating a new stock item"""
    pass

class EstoqueUpdate(BaseModel):
    """Schema for updating stock data"""
    condicao: Optional[str] = Field(None, max_length=100)
    id_titulo: Optional[int] = None
    id_biblioteca: Optional[int] = None

class EstoqueResponse(EstoqueBase):
    """Schema for stock response"""
    id_estoque: int
    
    class Config:
        from_attributes = True

class EstoqueListResponse(BaseResponse):
    """Schema for stock list response"""
    data: list[EstoqueResponse]
    total: int

class EstoqueDetalhado(BaseModel):
    """Schema for detailed stock information with title and library details"""
    id_estoque: int
    condicao: Optional[str]
    titulo_info: dict
    biblioteca_info: dict
    disponivel: bool
