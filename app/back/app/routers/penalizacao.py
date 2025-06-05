"""
Penalizacao API routes
"""
from fastapi import APIRouter, HTTPException, Query
from app.schemas.penalizacao import (
    PenalizacaoCreate, PenalizacaoUpdate, PenalizacaoResponse, 
    PenalizacaoListResponse
)
from app.schemas.base import BaseResponse
from app.services.base_service import BaseService

router = APIRouter(prefix="/penalizacoes", tags=["penalizacoes"])

# Initialize service
penalizacao_service = BaseService("Penalizacao", "id_penalizacao")

@router.post("/", response_model=PenalizacaoResponse, status_code=201)
async def create_penalizacao(penalizacao: PenalizacaoCreate):
    """Create a new penalty"""
    try:
        penalty_data = penalizacao.dict(exclude_unset=True)
        penalty_id = penalizacao_service.create(penalty_data)
        
        if not penalty_id:
            raise HTTPException(status_code=500, detail="Failed to create penalty")
        
        created_penalty = penalizacao_service.get_by_id(penalty_id)
        return PenalizacaoResponse(**created_penalty)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=PenalizacaoListResponse)
async def list_penalizacoes(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    id_usuario: int = Query(None, description="Filter by user ID"),
    ativas: bool = Query(None, description="Filter active penalties")
):
    """Get list of penalties"""
    try:
        filters = {}
        if id_usuario:
            filters['id_usuario'] = id_usuario
            
        penalties, total = penalizacao_service.get_all(page, size, filters)
        
        # Filter active penalties if requested
        if ativas is not None:
            from datetime import date
            today = date.today()
            if ativas:
                penalties = [p for p in penalties if not p.get('final_penalizacao') or p['final_penalizacao'] > today]
            else:
                penalties = [p for p in penalties if p.get('final_penalizacao') and p['final_penalizacao'] <= today]
            total = len(penalties)
        
        return PenalizacaoListResponse(
            data=[PenalizacaoResponse(**penalty) for penalty in penalties],
            total=total,
            message=f"Found {total} penalties"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{penalty_id}", response_model=PenalizacaoResponse)
async def get_penalizacao(penalty_id: int):
    """Get penalty by ID"""
    penalty = penalizacao_service.get_by_id(penalty_id)
    if not penalty:
        raise HTTPException(status_code=404, detail="Penalty not found")
    return PenalizacaoResponse(**penalty)

@router.put("/{penalty_id}", response_model=PenalizacaoResponse)
async def update_penalizacao(penalty_id: int, penalizacao: PenalizacaoUpdate):
    """Update penalty"""
    if not penalizacao_service.exists(penalty_id):
        raise HTTPException(status_code=404, detail="Penalty not found")
    
    try:
        penalty_data = penalizacao.dict(exclude_unset=True, exclude_none=True)
        if not penalty_data:
            raise HTTPException(status_code=400, detail="No data provided for update")
        
        success = penalizacao_service.update(penalty_id, penalty_data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update penalty")
        
        updated_penalty = penalizacao_service.get_by_id(penalty_id)
        return PenalizacaoResponse(**updated_penalty)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{penalty_id}", response_model=BaseResponse)
async def delete_penalizacao(penalty_id: int):
    """Delete penalty"""
    if not penalizacao_service.exists(penalty_id):
        raise HTTPException(status_code=404, detail="Penalty not found")
    
    try:
        success = penalizacao_service.delete(penalty_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete penalty")
        
        return BaseResponse(message="Penalty deleted successfully")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
