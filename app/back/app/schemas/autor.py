"""
Autor schemas for request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date
from .base import BaseResponse

class AutorBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=255, description="Nome do autor")
    data_nascimento: Optional[date] = Field(None, description="Data de nascimento")
    data_falecimento: Optional[date] = Field(None, description="Data de falecimento")

    @validator('data_falecimento')
    def validate_data_falecimento(cls, v, values):
        if v and 'data_nascimento' in values and values['data_nascimento'] and v < values['data_nascimento']:
            raise ValueError('Data de falecimento deve ser posterior à data de nascimento')
        return v

class AutorCreate(AutorBase):
    """Schema for creating a new author"""
    pass

class AutorUpdate(BaseModel):
    """Schema for updating author data"""
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    data_nascimento: Optional[date] = None
    data_falecimento: Optional[date] = None

class AutorResponse(AutorBase):
    """Schema for author response"""
    id_autor: int
    
    class Config:
        from_attributes = True

class AutorListResponse(BaseResponse):
    """Schema for author list response"""
    data: list[AutorResponse]
    total: int

# Autorias schemas
class AutoriasBase(BaseModel):
    id_autor: int = Field(..., description="ID do autor")
    id_titulo: int = Field(..., description="ID do título")

class AutoriasCreate(AutoriasBase):
    """Schema for creating a new authorship"""
    pass

class AutoriasResponse(AutoriasBase):
    """Schema for authorship response"""
    id_autorias: int
    
    class Config:
        from_attributes = True

class AutoriasListResponse(BaseResponse):
    """Schema for authorship list response"""
    data: list[AutoriasResponse]
    total: int
