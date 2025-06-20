"""
Usuario API routes
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from app.schemas.usuario import (
    UsuarioCreate, UsuarioUpdate, UsuarioResponse, 
    UsuarioListResponse
)
from app.schemas.base import BaseResponse, PaginationParams
from app.services.usuario_service import usuario_service

router = APIRouter()

@router.post("/", response_model=UsuarioResponse, status_code=201)
async def create_usuario(usuario: UsuarioCreate):
    """Create a new user"""
    try:
        # Check if email already exists
        if usuario.email and usuario_service.get_by_email(usuario.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        
        user_data = usuario.dict(exclude_unset=True)
        user_id = usuario_service.create(user_data)
        
        if not user_id:
            raise HTTPException(status_code=500, detail="Failed to create user")
        
        created_user = usuario_service.get_by_id(user_id)
        return UsuarioResponse(**created_user)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=UsuarioListResponse)
async def list_usuarios(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    search: str = Query(None, description="Search by name or email")
):
    """Get list of users with optional search"""
    try:
        if search:
            users, total = usuario_service.search_users(search, page, size)
        else:
            users, total = usuario_service.get_all(page, size)
        
        return UsuarioListResponse(
            data=[UsuarioResponse(**user) for user in users],
            total=total,
            message=f"Found {total} users"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{user_id}", response_model=UsuarioResponse)
async def get_usuario(user_id: int):
    """Get user by ID"""
    user = usuario_service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UsuarioResponse(**user)

@router.put("/{user_id}", response_model=UsuarioResponse)
async def update_usuario(user_id: int, usuario: UsuarioUpdate):
    """Update user"""
    if not usuario_service.exists(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        # Check email uniqueness if updating email
        if usuario.email:
            existing_user = usuario_service.get_by_email(usuario.email)
            if existing_user and existing_user['id_usuario'] != user_id:
                raise HTTPException(status_code=400, detail="Email already registered")
        
        user_data = usuario.dict(exclude_unset=True, exclude_none=True)
        if not user_data:
            raise HTTPException(status_code=400, detail="No data provided for update")
        
        success = usuario_service.update(user_id, user_data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update user")
        
        updated_user = usuario_service.get_by_id(user_id)
        return UsuarioResponse(**updated_user)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{user_id}", response_model=BaseResponse)
async def delete_usuario(user_id: int):
    """Delete user"""
    if not usuario_service.exists(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        success = usuario_service.delete(user_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete user")
        
        return BaseResponse(message="User deleted successfully")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{user_id}/emprestimos")
async def get_user_loans(user_id: int):
    """Get all loans for a specific user"""
    if not usuario_service.exists(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        loans = usuario_service.get_user_loans(user_id)
        return {
            "success": True,
            "data": loans,
            "total": len(loans),
            "message": f"Found {len(loans)} loans for user"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{user_id}/penalizacoes")
async def get_user_penalties(user_id: int):
    """Get all penalties for a specific user"""
    if not usuario_service.exists(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        penalties = usuario_service.get_user_penalties(user_id)
        return {
            "success": True,
            "data": penalties,
            "total": len(penalties),
            "message": f"Found {len(penalties)} penalties for user"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
