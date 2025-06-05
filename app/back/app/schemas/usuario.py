"""
Usuario schemas for request/response validation
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from .base import BaseResponse

class UsuarioBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=255, description="Nome do usuário")
    email: Optional[EmailStr] = Field(None, description="Email do usuário")
    endereco: Optional[str] = Field(None, max_length=500, description="Endereço do usuário")
    telefone: Optional[str] = Field(None, max_length=20, description="Telefone do usuário")

class UsuarioCreate(UsuarioBase):
    """Schema for creating a new user"""
    pass

class UsuarioUpdate(BaseModel):
    """Schema for updating user data"""
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    endereco: Optional[str] = Field(None, max_length=500)
    telefone: Optional[str] = Field(None, max_length=20)

class UsuarioResponse(UsuarioBase):
    """Schema for user response"""
    id_usuario: int
    
    class Config:
        from_attributes = True

class UsuarioListResponse(BaseResponse):
    """Schema for user list response"""
    data: list[UsuarioResponse]
    total: int
