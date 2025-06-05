"""
Revista schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from .base import BaseResponse

class RevistaBase(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=255, description="Título da revista")
    issn: Optional[str] = Field(None, max_length=20, description="ISSN da revista")
    periodicidade: Optional[str] = Field(None, max_length=100, description="Periodicidade")
    editora: Optional[str] = Field(None, max_length=255, description="Editora")
    data_publicacao: Optional[date] = Field(None, description="Data de publicação")

class RevistaCreate(RevistaBase):
    """Schema for creating a new magazine"""
    id_revista: int = Field(..., description="ID que referencia a tabela Titulo")

class RevistaUpdate(BaseModel):
    """Schema for updating magazine data"""
    titulo: Optional[str] = Field(None, min_length=1, max_length=255)
    issn: Optional[str] = Field(None, max_length=20)
    periodicidade: Optional[str] = Field(None, max_length=100)
    editora: Optional[str] = Field(None, max_length=255)
    data_publicacao: Optional[date] = None

class RevistaResponse(RevistaBase):
    """Schema for magazine response"""
    id_revista: int
    
    class Config:
        from_attributes = True

class RevistaListResponse(BaseResponse):
    """Schema for magazine list response"""
    data: list[RevistaResponse]
    total: int
