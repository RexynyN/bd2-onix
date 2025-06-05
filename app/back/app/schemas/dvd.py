"""
DVD schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from .base import BaseResponse

class DVDBase(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=255, description="Título do DVD")
    isan: Optional[str] = Field(None, max_length=30, description="ISAN do DVD")
    duracao: Optional[int] = Field(None, gt=0, description="Duração em minutos")
    distribuidora: Optional[str] = Field(None, max_length=255, description="Distribuidora")
    data_lancamento: Optional[date] = Field(None, description="Data de lançamento")

class DVDCreate(DVDBase):
    """Schema for creating a new DVD"""
    id_dvd: int = Field(..., description="ID que referencia a tabela Titulo")

class DVDUpdate(BaseModel):
    """Schema for updating DVD data"""
    titulo: Optional[str] = Field(None, min_length=1, max_length=255)
    isan: Optional[str] = Field(None, max_length=30)
    duracao: Optional[int] = Field(None, gt=0)
    distribuidora: Optional[str] = Field(None, max_length=255)
    data_lancamento: Optional[date] = None

class DVDResponse(DVDBase):
    """Schema for DVD response"""
    id_dvd: int
    
    class Config:
        from_attributes = True

class DVDListResponse(BaseResponse):
    """Schema for DVD list response"""
    data: list[DVDResponse]
    total: int
