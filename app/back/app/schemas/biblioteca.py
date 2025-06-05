"""
Biblioteca schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from .base import BaseResponse

class BibliotecaBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=255, description="Nome da biblioteca")
    endereco: Optional[str] = Field(None, max_length=500, description="Endereço da biblioteca")

class BibliotecaCreate(BibliotecaBase):
    """Schema for creating a new library"""
    pass

class BibliotecaUpdate(BaseModel):
    """Schema for updating library data"""
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    endereco: Optional[str] = Field(None, max_length=500)

class BibliotecaResponse(BibliotecaBase):
    """Schema for library response"""
    id_biblioteca: int
    
    class Config:
        from_attributes = True

class BibliotecaListResponse(BaseResponse):
    """Schema for library list response"""
    data: list[BibliotecaResponse]
    total: int
