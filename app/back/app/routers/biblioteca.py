"""
Biblioteca API routes
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from app.schemas.biblioteca import (
    BibliotecaCreate, BibliotecaUpdate, BibliotecaResponse, 
    BibliotecaListResponse
)
from app.schemas.base import BaseResponse
from app.services.biblioteca_service import biblioteca_service

router = APIRouter()

@router.post("/", response_model=BibliotecaResponse, status_code=201)
async def create_biblioteca(biblioteca: BibliotecaCreate):
    """Create a new library"""
    try:
        library_data = biblioteca.dict(exclude_unset=True)
        library = biblioteca_service.create_biblioteca(library_data)
        
        if not library:
            raise HTTPException(status_code=500, detail="Failed to create library")
        return library
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=BibliotecaListResponse)
async def list_bibliotecas(
    page: int = Query(0, ge=0, description="Page number"),
    size: int = Query(100, ge=1, le=10000, description="Items per page")
):
    """Get list of libraries"""
    try:
        libraries = biblioteca_service.get_bibliotecas(page, size)
        leng = len(libraries)
        return BibliotecaListResponse(
            data=libraries,
            total=leng,
            message=f"Found {leng} libraries"
        )
    except Exception as e:
        print(f"Error listing libraries: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{library_id}", response_model=BibliotecaResponse)
async def get_biblioteca(library_id: int):
    """Get library by ID"""
    library = biblioteca_service.get_biblioteca(library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    return library

@router.put("/{library_id}", response_model=BibliotecaResponse)
async def update_biblioteca(library_id: int, biblioteca: BibliotecaUpdate):
    """Update library"""
    if not biblioteca_service.exists(library_id):
        raise HTTPException(status_code=404, detail="Library not found")
    
    try:
        library_data = biblioteca.dict(exclude_unset=True, exclude_none=True)
        if not library_data:
            raise HTTPException(status_code=400, detail="No data provided for update")
        
        library = biblioteca_service.update_biblioteca(library_id, library_data)
        if not library:
            raise HTTPException(status_code=500, detail="Failed to update library")
        
        return library
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{library_id}", response_model=BaseResponse)
async def delete_biblioteca(library_id: int):
    """Delete library"""
    if not biblioteca_service.exists(library_id):
        raise HTTPException(status_code=404, detail="Library not found")
    
    try:
        success = biblioteca_service.delete_biblioteca(library_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete library")
        
        return BaseResponse(message="Library deleted successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{library_id}/estoque")
async def get_library_stock(
    library_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page")
):
    """Get stock items for a specific library"""
    if not biblioteca_service.exists(library_id):
        raise HTTPException(status_code=404, detail="Library not found")
    
    try:
        stock_items, total = biblioteca_service.get_library_stock(library_id, page, size)
        return {
            "success": True,
            "data": stock_items,
            "total": total,
            "message": f"Found {total} items in library stock"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{library_id}/itens-disponiveis")
async def get_available_items(library_id: int):
    """Get available items for loan in a library"""
    if not biblioteca_service.exists(library_id):
        raise HTTPException(status_code=404, detail="Library not found")
    
    try:
        available_items = biblioteca_service.get_available_items(library_id)
        return {
            "success": True,
            "data": available_items,
            "total": len(available_items),
            "message": f"Found {len(available_items)} available items"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
