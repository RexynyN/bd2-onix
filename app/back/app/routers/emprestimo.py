"""
Emprestimo API routes
"""
from fastapi import APIRouter, HTTPException, Query
from datetime import date
from app.schemas.emprestimo import (
    EmprestimoCreate, EmprestimoUpdate, EmprestimoResponse,
    EmprestimoListResponse, DevolucaoRequest
)
from app.schemas.base import BaseResponse
from app.services.emprestimo_service import emprestimo_service

router = APIRouter(prefix="/emprestimos", tags=["emprestimos"])

@router.post("/", response_model=EmprestimoResponse, status_code=201)
async def create_emprestimo(emprestimo: EmprestimoCreate):
    """Create a new loan"""
    try:
        loan_data = emprestimo.dict(exclude_unset=True)
        loan_id = emprestimo_service.create(loan_data)
        
        if not loan_id:
            raise HTTPException(status_code=500, detail="Failed to create loan")
        
        created_loan = emprestimo_service.get_by_id(loan_id)
        return EmprestimoResponse(**created_loan)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/emprestar", response_model=EmprestimoResponse, status_code=201)
async def create_loan_simplified(
    id_usuario: int,
    id_estoque: int,
    data_devolucao_prevista: date = None
):
    """Create a loan with business logic validation"""
    try:
        loan_id = emprestimo_service.create_loan(
            user_id=id_usuario,
            stock_id=id_estoque,
            due_date=data_devolucao_prevista
        )
        
        if not loan_id:
            raise HTTPException(status_code=500, detail="Failed to create loan")
        
        created_loan = emprestimo_service.get_by_id(loan_id)
        return EmprestimoResponse(**created_loan)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{loan_id}/devolver", response_model=BaseResponse)
async def return_item(loan_id: int, devolucao: DevolucaoRequest = None):
    """Return a loaned item"""
    try:
        return_date = devolucao.data_devolucao if devolucao else date.today()
        success = emprestimo_service.return_item(loan_id, return_date)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to process return")
        
        return BaseResponse(message="Item returned successfully")
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=EmprestimoListResponse)
async def list_emprestimos(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    apenas_ativos: bool = Query(False, description="Show only active loans")
):
    """Get list of loans"""
    try:
        if apenas_ativos:
            loans, total = emprestimo_service.get_active_loans(page, size)
        else:
            loans, total = emprestimo_service.get_loan_history(page, size)
        
        return EmprestimoListResponse(
            data=[EmprestimoResponse(**loan) for loan in loans],
            total=total,
            message=f"Found {total} loans"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/ativos")
async def get_active_loans(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page")
):
    """Get all active loans with detailed information"""
    try:
        loans, total = emprestimo_service.get_active_loans(page, size)
        return {
            "success": True,
            "data": loans,
            "total": total,
            "message": f"Found {total} active loans"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/atrasados")
async def get_overdue_loans():
    """Get all overdue loans"""
    try:
        overdue_loans = emprestimo_service.get_overdue_loans()
        return {
            "success": True,
            "data": overdue_loans,
            "total": len(overdue_loans),
            "message": f"Found {len(overdue_loans)} overdue loans"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{loan_id}", response_model=EmprestimoResponse)
async def get_emprestimo(loan_id: int):
    """Get loan by ID"""
    loan = emprestimo_service.get_by_id(loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return EmprestimoResponse(**loan)

@router.put("/{loan_id}", response_model=EmprestimoResponse)
async def update_emprestimo(loan_id: int, emprestimo: EmprestimoUpdate):
    """Update loan"""
    if not emprestimo_service.exists(loan_id):
        raise HTTPException(status_code=404, detail="Loan not found")
    
    try:
        loan_data = emprestimo.dict(exclude_unset=True, exclude_none=True)
        if not loan_data:
            raise HTTPException(status_code=400, detail="No data provided for update")
        
        success = emprestimo_service.update(loan_id, loan_data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update loan")
        
        updated_loan = emprestimo_service.get_by_id(loan_id)
        return EmprestimoResponse(**updated_loan)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{loan_id}", response_model=BaseResponse)
async def delete_emprestimo(loan_id: int):
    """Delete loan"""
    if not emprestimo_service.exists(loan_id):
        raise HTTPException(status_code=404, detail="Loan not found")
    
    try:
        success = emprestimo_service.delete(loan_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete loan")
        
        return BaseResponse(message="Loan deleted successfully")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
