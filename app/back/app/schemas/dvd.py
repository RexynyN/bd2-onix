from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class DVDBase(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=255)
    ISAN: Optional[str] = Field(None, max_length=30)
    duracao: Optional[int] = Field(None, gt=0)
    distribuidora: Optional[str] = Field(None, max_length=255)
    data_lancamento: Optional[date] = None

class DVDCreate(DVDBase):
    pass

class DVDUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=1, max_length=255)
    ISAN: Optional[str] = Field(None, max_length=30)
    duracao: Optional[int] = Field(None, gt=0)
    distribuidora: Optional[str] = Field(None, max_length=255)
    data_lancamento: Optional[date] = None

class DVDResponse(DVDBase):
    id_dvd: int
    
    class Config:
        from_attributes = True

class DVDWithAuthors(DVDResponse):
    autores: list[dict] = []
