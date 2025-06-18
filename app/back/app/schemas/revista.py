from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class RevistaBase(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=255)
    ISSN: Optional[str] = Field(None, max_length=20)
    periodicidade: Optional[str] = Field(None, max_length=100)
    editora: Optional[str] = Field(None, max_length=255)
    data_publicacao: Optional[date] = None

class RevistaCreate(RevistaBase):
    pass

class RevistaUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=1, max_length=255)
    ISSN: Optional[str] = Field(None, max_length=20)
    periodicidade: Optional[str] = Field(None, max_length=100)
    editora: Optional[str] = Field(None, max_length=255)
    data_publicacao: Optional[date] = None

class RevistaResponse(RevistaBase):
    id_revista: int
    
    class Config:
        from_attributes = True

class RevistaWithAuthors(RevistaResponse):
    autores: list[dict] = []
