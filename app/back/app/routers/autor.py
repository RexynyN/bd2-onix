"""
Autor API routes
"""
from fastapi import APIRouter, HTTPException, Query
from app.schemas.autor import (
    AutorCreate, AutorUpdate, AutorResponse, AutorListResponse,
    AutoriasCreate, AutoriasResponse, AutoriasListResponse
)
from app.schemas.base import BaseResponse
from app.services.base_service import BaseService

router = APIRouter(prefix="/autores", tags=["autores"])

# Initialize services
autor_service = BaseService("Autores", "id_autor")
autorias_service = BaseService("Autorias", "id_autorias")

@router.post("/", response_model=AutorResponse, status_code=201)
async def create_autor(autor: AutorCreate):
    """Create a new author"""
    try:
        author_data = autor.dict(exclude_unset=True)
        author_id = autor_service.create(author_data)
        
        if not author_id:
            raise HTTPException(status_code=500, detail="Failed to create author")
        
        created_author = autor_service.get_by_id(author_id)
        return AutorResponse(**created_author)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=AutorListResponse)
async def list_autores(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page")
):
    """Get list of authors"""
    try:
        authors, total = autor_service.get_all(page, size)
        
        return AutorListResponse(
            data=[AutorResponse(**author) for author in authors],
            total=total,
            message=f"Found {total} authors"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{author_id}", response_model=AutorResponse)
async def get_autor(author_id: int):
    """Get author by ID"""
    author = autor_service.get_by_id(author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return AutorResponse(**author)

@router.put("/{author_id}", response_model=AutorResponse)
async def update_autor(author_id: int, autor: AutorUpdate):
    """Update author"""
    if not autor_service.exists(author_id):
        raise HTTPException(status_code=404, detail="Author not found")
    
    try:
        author_data = autor.dict(exclude_unset=True, exclude_none=True)
        if not author_data:
            raise HTTPException(status_code=400, detail="No data provided for update")
        
        success = autor_service.update(author_id, author_data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update author")
        
        updated_author = autor_service.get_by_id(author_id)
        return AutorResponse(**updated_author)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{author_id}", response_model=BaseResponse)
async def delete_autor(author_id: int):
    """Delete author"""
    if not autor_service.exists(author_id):
        raise HTTPException(status_code=404, detail="Author not found")
    
    try:
        success = autor_service.delete(author_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete author")
        
        return BaseResponse(message="Author deleted successfully")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

# Autorias endpoints
@router.post("/autorias", response_model=AutoriasResponse, status_code=201)
async def create_autoria(autoria: AutoriasCreate):
    """Create a new authorship relationship"""
    try:
        authorship_data = autoria.dict(exclude_unset=True)
        authorship_id = autorias_service.create(authorship_data)
        
        if not authorship_id:
            raise HTTPException(status_code=500, detail="Failed to create authorship")
        
        created_authorship = autorias_service.get_by_id(authorship_id)
        return AutoriasResponse(**created_authorship)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/autorias", response_model=AutoriasListResponse)
async def list_autorias(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    id_autor: int = Query(None, description="Filter by author ID"),
    id_titulo: int = Query(None, description="Filter by title ID")
):
    """Get list of authorship relationships"""
    try:
        filters = {}
        if id_autor:
            filters['id_autor'] = id_autor
        if id_titulo:
            filters['id_titulo'] = id_titulo
            
        authorships, total = autorias_service.get_all(page, size, filters)
        
        return AutoriasListResponse(
            data=[AutoriasResponse(**authorship) for authorship in authorships],
            total=total,
            message=f"Found {total} authorship relationships"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
