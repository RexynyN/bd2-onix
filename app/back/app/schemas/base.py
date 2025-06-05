"""
Base schemas for the application
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from enum import Enum

class MidiaTipo(str, Enum):
    livro = "livro"
    revista = "revista"
    dvd = "dvd"
    artigo = "artigo"

class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = True
    message: str = "Operation completed successfully"

class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=10, ge=1, le=100, description="Items per page")
