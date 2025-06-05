"""
Livro schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from .base import BaseResponse

class LivroBase(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=255, description="Título do livro")
    isbn: Optional[str] = Field(None, max_length=20, description="ISBN do livro")
    numero_paginas: Optional[int] = Field(None, gt=0, description="Número de páginas")
    editora: Optional[str] = Field(None, max_length=255, description="Editora")
    data_publicacao: Optional[date] = Field(None, description="Data de publicação")

class LivroCreate(LivroBase):
    """Schema for creating a new book"""
    id_livro: int = Field(..., description="ID que referencia a tabela Titulo")

class LivroUpdate(BaseModel):
    """Schema for updating book data"""
    titulo: Optional[str] = Field(None, min_length=1, max_length=255)
    isbn: Optional[str] = Field(None, max_length=20)
    numero_paginas: Optional[int] = Field(None, gt=0)
    editora: Optional[str] = Field(None, max_length=255)
    data_publicacao: Optional[date] = None

class LivroResponse(LivroBase):
    """Schema for book response"""
    id_livro: int
    
    class Config:
        from_attributes = True

class LivroListResponse(BaseResponse):
    """Schema for book list response"""
    data: list[LivroResponse]
    total: int
