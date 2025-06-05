"""
Titulo schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from .base import BaseResponse, MidiaTipo

class TituloBase(BaseModel):
    tipo_midia: MidiaTipo = Field(..., description="Tipo de mídia")

class TituloCreate(TituloBase):
    """Schema for creating a new title"""
    pass

class TituloUpdate(BaseModel):
    """Schema for updating title data"""
    tipo_midia: Optional[MidiaTipo] = None

class TituloResponse(TituloBase):
    """Schema for title response"""
    id_titulo: int
    
    class Config:
        from_attributes = True

class TituloListResponse(BaseResponse):
    """Schema for title list response"""
    data: list[TituloResponse]
    total: int
