"""
Media API routes for different types of content
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.schemas.livro import LivroCreate, LivroUpdate, LivroResponse, LivroListResponse
from app.schemas.revista import RevistaCreate, RevistaUpdate, RevistaResponse, RevistaListResponse
from app.schemas.dvd import DVDCreate, DVDUpdate, DVDResponse, DVDListResponse
from app.schemas.artigo import ArtigoCreate, ArtigoUpdate, ArtigoResponse, ArtigoListResponse
from app.schemas.titulo import TituloCreate, TituloResponse
from app.schemas.base import BaseResponse, MidiaTipo
from app.services.media_service import media_service

router = APIRouter(prefix="/midias", tags=["midias"])

# Generic media endpoints
@router.get("/buscar")
async def search_media(
    termo: str = Query(..., description="Search term"),
    tipo: Optional[MidiaTipo] = Query(None, description="Media type filter"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page")
):
    """Search across all media types"""
    try:
        results, total = media_service.search_media(termo, tipo, page, size)
        return {
            "success": True,
            "data": results,
            "total": total,
            "message": f"Found {total} items matching '{termo}'"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{title_id}/detalhes")
async def get_media_details(title_id: int):
    """Get complete media details"""
    details = media_service.get_media_details(title_id)
    if not details:
        raise HTTPException(status_code=404, detail="Media not found")
    return {
        "success": True,
        "data": details,
        "message": "Media details retrieved successfully"
    }

# Livros endpoints
@router.post("/livros", response_model=LivroResponse, status_code=201)
async def create_livro(livro: LivroCreate):
    """Create a new book"""
    try:
        book_data = livro.dict(exclude={'id_livro'})
        title_id = media_service.create_media_with_title('livro', book_data)
        
        if not title_id:
            raise HTTPException(status_code=500, detail="Failed to create book")
        
        details = media_service.get_media_details(title_id)
        return LivroResponse(**details['media_details'])
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/livros/{book_id}", response_model=LivroResponse)
async def get_livro(book_id: int):
    """Get book by ID"""
    book = media_service.livro_service.get_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return LivroResponse(**book)

@router.put("/livros/{book_id}", response_model=LivroResponse)
async def update_livro(book_id: int, livro: LivroUpdate):
    """Update book"""
    if not media_service.livro_service.exists(book_id):
        raise HTTPException(status_code=404, detail="Book not found")
    
    try:
        book_data = livro.dict(exclude_unset=True, exclude_none=True)
        if not book_data:
            raise HTTPException(status_code=400, detail="No data provided for update")
        
        success = media_service.livro_service.update(book_id, book_data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update book")
        
        updated_book = media_service.livro_service.get_by_id(book_id)
        return LivroResponse(**updated_book)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

# Revistas endpoints
@router.post("/revistas", response_model=RevistaResponse, status_code=201)
async def create_revista(revista: RevistaCreate):
    """Create a new magazine"""
    try:
        magazine_data = revista.dict(exclude={'id_revista'})
        title_id = media_service.create_media_with_title('revista', magazine_data)
        
        if not title_id:
            raise HTTPException(status_code=500, detail="Failed to create magazine")
        
        details = media_service.get_media_details(title_id)
        return RevistaResponse(**details['media_details'])
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/revistas/{magazine_id}", response_model=RevistaResponse)
async def get_revista(magazine_id: int):
    """Get magazine by ID"""
    magazine = media_service.revista_service.get_by_id(magazine_id)
    if not magazine:
        raise HTTPException(status_code=404, detail="Magazine not found")
    return RevistaResponse(**magazine)

# DVDs endpoints
@router.post("/dvds", response_model=DVDResponse, status_code=201)
async def create_dvd(dvd: DVDCreate):
    """Create a new DVD"""
    try:
        dvd_data = dvd.dict(exclude={'id_dvd'})
        title_id = media_service.create_media_with_title('dvd', dvd_data)
        
        if not title_id:
            raise HTTPException(status_code=500, detail="Failed to create DVD")
        
        details = media_service.get_media_details(title_id)
        return DVDResponse(**details['media_details'])
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/dvds/{dvd_id}", response_model=DVDResponse)
async def get_dvd(dvd_id: int):
    """Get DVD by ID"""
    dvd = media_service.dvd_service.get_by_id(dvd_id)
    if not dvd:
        raise HTTPException(status_code=404, detail="DVD not found")
    return DVDResponse(**dvd)

# Artigos endpoints
@router.post("/artigos", response_model=ArtigoResponse, status_code=201)
async def create_artigo(artigo: ArtigoCreate):
    """Create a new article"""
    try:
        article_data = artigo.dict(exclude={'id_artigo'})
        title_id = media_service.create_media_with_title('artigo', article_data)
        
        if not title_id:
            raise HTTPException(status_code=500, detail="Failed to create article")
        
        details = media_service.get_media_details(title_id)
        return ArtigoResponse(**details['media_details'])
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/artigos/{article_id}", response_model=ArtigoResponse)
async def get_artigo(article_id: int):
    """Get article by ID"""
    article = media_service.artigo_service.get_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return ArtigoResponse(**article)
