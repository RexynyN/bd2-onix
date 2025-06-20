"""
Estoque API routes
"""
from fastapi import APIRouter, HTTPException, Query
from app.schemas.estoque import (
    EstoqueCreate, EstoqueUpdate, EstoqueResponse, 
    EstoqueListResponse
)
from app.schemas.base import BaseResponse
from app.services.base_service import BaseService

router = APIRouter(prefix="/estoque", tags=["estoque"])

# Initialize service
estoque_service = BaseService("Estoque", "id_estoque")

@router.post("/", response_model=EstoqueResponse, status_code=201)
async def create_estoque(estoque: EstoqueCreate):
    """Create a new stock item"""
    try:
        stock_data = estoque.dict(exclude_unset=True)
        stock_id = estoque_service.create(stock_data)
        
        if not stock_id:
            raise HTTPException(status_code=500, detail="Failed to create stock item")
        
        created_stock = estoque_service.get_by_id(stock_id)
        return EstoqueResponse(**created_stock)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=EstoqueListResponse)
async def list_estoque(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    id_biblioteca: int = Query(None, description="Filter by library ID"),
    id_titulo: int = Query(None, description="Filter by title ID")
):
    """Get list of stock items"""
    try:
        filters = {}
        if id_biblioteca:
            filters['id_biblioteca'] = id_biblioteca
        if id_titulo:
            filters['id_titulo'] = id_titulo
            
        stock_items, total = estoque_service.get_all(page, size, filters)
        
        return EstoqueListResponse(
            data=[EstoqueResponse(**item) for item in stock_items],
            total=total,
            message=f"Found {total} stock items"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{stock_id}", response_model=EstoqueResponse)
async def get_estoque(stock_id: int):
    """Get stock item by ID"""
    stock = estoque_service.get_by_id(stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock item not found")
    return EstoqueResponse(**stock)

@router.put("/{stock_id}", response_model=EstoqueResponse)
async def update_estoque(stock_id: int, estoque: EstoqueUpdate):
    """Update stock item"""
    if not estoque_service.exists(stock_id):
        raise HTTPException(status_code=404, detail="Stock item not found")
    
    try:
        stock_data = estoque.dict(exclude_unset=True, exclude_none=True)
        if not stock_data:
            raise HTTPException(status_code=400, detail="No data provided for update")
        
        success = estoque_service.update(stock_id, stock_data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update stock item")
        
        updated_stock = estoque_service.get_by_id(stock_id)
        return EstoqueResponse(**updated_stock)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{stock_id}", response_model=BaseResponse)
async def delete_estoque(stock_id: int):
    """Delete stock item"""
    if not estoque_service.exists(stock_id):
        raise HTTPException(status_code=404, detail="Stock item not found")
    
    try:
        success = estoque_service.delete(stock_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete stock item")
        
        return BaseResponse(message="Stock item deleted successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
