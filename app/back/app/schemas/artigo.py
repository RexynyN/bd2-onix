"""
Artigo schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from .base import BaseResponse

class ArtigoBase(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=255, description="Título do artigo")
    doi: Optional[str] = Field(None, max_length=100, description="DOI do artigo")
    publicadora: Optional[str] = Field(None, max_length=255, description="Publicadora")
    data_publicacao: Optional[date] = Field(None, description="Data de publicação")

class ArtigoCreate(ArtigoBase):
    """Schema for creating a new article"""
    id_artigo: int = Field(..., description="ID que referencia a tabela Titulo")

class ArtigoUpdate(BaseModel):
    """Schema for updating article data"""
    titulo: Optional[str] = Field(None, min_length=1, max_length=255)
    doi: Optional[str] = Field(None, max_length=100)
    publicadora: Optional[str] = Field(None, max_length=255)
    data_publicacao: Optional[date] = None

class ArtigoResponse(ArtigoBase):
    """Schema for article response"""
    id_artigo: int
    
    class Config:
        from_attributes = True

class ArtigoListResponse(BaseResponse):
    """Schema for article list response"""
    data: list[ArtigoResponse]
    total: int
