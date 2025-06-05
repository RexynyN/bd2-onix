"""
Emprestimo service for business logic
"""
import psycopg2.extras
from typing import List, Optional, Dict, Any
from datetime import date, timedelta
from .base_service import BaseService
from app.db.database import get_db_connection
import logging

logger = logging.getLogger(__name__)

class EmprestimoService(BaseService):
    def __init__(self):
        super().__init__("Emprestimo", "id_emprestimo")
    
    def create_loan(self, user_id: int, stock_id: int, loan_date: date = None, due_date: date = None) -> Optional[int]:
        """Create a new loan with business logic validation"""
        loan_date = loan_date or date.today()
        due_date = due_date or (loan_date + timedelta(days=14))  # Default 2 weeks
        
        # Check if item is available
        if not self._is_item_available(stock_id):
            raise ValueError("Item is not available for loan")
        
        # Check if user has penalties
        if self._user_has_active_penalties(user_id):
            raise ValueError("User has active penalties and cannot borrow items")
        
        data = {
            'data_emprestimo': loan_date,
            'data_devolucao_prevista': due_date,
            'id_estoque': stock_id,
            'id_usuario': user_id
        }
        
        return self.create(data)
    
    def return_item(self, loan_id: int, return_date: date = None) -> bool:
        """Return an item and handle late return penalties"""
        return_date = return_date or date.today()
        
        # Get loan details
        loan = self.get_by_id(loan_id)
        if not loan:
            raise ValueError("Loan not found")
        
        if loan['data_devolucao']:
            raise ValueError("Item already returned")
        
        # Update loan with return date
        update_success = self.update(loan_id, {'data_devolucao': return_date})
        
        # Check for late return and create penalty if needed
        if loan['data_devolucao_prevista'] and return_date > loan['data_devolucao_prevista']:
            self._create_late_penalty(loan_id, loan['id_usuario'], return_date, loan['data_devolucao_prevista'])
        
        return update_success
    
    def get_active_loans(self, page: int = 1, size: int = 10) -> tuple[List[Dict[str, Any]], int]:
        """Get all active loans"""
        offset = (page - 1) * size
        
        # Count query
        count_query = """
            SELECT COUNT(*) FROM Emprestimo
            WHERE data_devolucao IS NULL
        """
        
        # Data query
        data_query = """
            SELECT e.*, u.nome as usuario_nome, u.email as usuario_email,
                   est.condicao, t.tipo_midia
            FROM Emprestimo e
            JOIN Usuario u ON e.id_usuario = u.id_usuario
            JOIN Estoque est ON e.id_estoque = est.id_estoque
            JOIN Titulo t ON est.id_titulo = t.id_titulo
            WHERE e.data_devolucao IS NULL
            ORDER BY e.data_emprestimo DESC
            LIMIT %s OFFSET %s
        """
        
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                # Get total count
                cursor.execute(count_query)
                total = cursor.fetchone()[0]
                
                # Get data
                cursor.execute(data_query, (size, offset))
                results = cursor.fetchall()
                
                return [dict(row) for row in results], total
    
    def get_overdue_loans(self) -> List[Dict[str, Any]]:
        """Get all overdue loans"""
        query = """
            SELECT e.*, u.nome as usuario_nome, u.email as usuario_email,
                   est.condicao, t.tipo_midia
            FROM Emprestimo e
            JOIN Usuario u ON e.id_usuario = u.id_usuario
            JOIN Estoque est ON e.id_estoque = est.id_estoque
            JOIN Titulo t ON est.id_titulo = t.id_titulo
            WHERE e.data_devolucao IS NULL 
            AND e.data_devolucao_prevista < CURRENT_DATE
            ORDER BY e.data_devolucao_prevista
        """
        
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(query)
                return [dict(row) for row in cursor.fetchall()]
    
    def get_loan_history(self, page: int = 1, size: int = 10) -> tuple[List[Dict[str, Any]], int]:
        """Get complete loan history"""
        offset = (page - 1) * size
        
        # Count query
        count_query = "SELECT COUNT(*) FROM Emprestimo"
        
        # Data query
        data_query = """
            SELECT e.*, u.nome as usuario_nome, u.email as usuario_email,
                   est.condicao, t.tipo_midia,
                   CASE 
                       WHEN e.data_devolucao IS NOT NULL THEN 'devolvido'
                       WHEN e.data_devolucao_prevista < CURRENT_DATE THEN 'atrasado'
                       ELSE 'ativo'
                   END as status
            FROM Emprestimo e
            JOIN Usuario u ON e.id_usuario = u.id_usuario
            JOIN Estoque est ON e.id_estoque = est.id_estoque
            JOIN Titulo t ON est.id_titulo = t.id_titulo
            ORDER BY e.data_emprestimo DESC
            LIMIT %s OFFSET %s
        """
        
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                # Get total count
                cursor.execute(count_query)
                total = cursor.fetchone()[0]
                
                # Get data
                cursor.execute(data_query, (size, offset))
                results = cursor.fetchall()
                
                return [dict(row) for row in results], total
    
    def _is_item_available(self, stock_id: int) -> bool:
        """Check if an item is available for loan"""
        query = """
            SELECT 1 FROM Estoque est
            LEFT JOIN Emprestimo emp ON est.id_estoque = emp.id_estoque 
                AND emp.data_devolucao IS NULL
            WHERE est.id_estoque = %s AND emp.id_emprestimo IS NULL
        """
        
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (stock_id,))
                return cursor.fetchone() is not None
    
    def _user_has_active_penalties(self, user_id: int) -> bool:
        """Check if user has active penalties"""
        query = """
            SELECT 1 FROM Penalizacao
            WHERE id_usuario = %s 
            AND (final_penalizacao IS NULL OR final_penalizacao > CURRENT_DATE)
        """
        
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (user_id,))
                return cursor.fetchone() is not None
    
    def _create_late_penalty(self, loan_id: int, user_id: int, return_date: date, due_date: date):
        """Create penalty for late return"""
        days_late = (return_date - due_date).days
        description = f"Devolução atrasada em {days_late} dia(s)"
        penalty_end = return_date + timedelta(days=days_late)  # Penalty duration equals late days
        
        penalty_query = """
            INSERT INTO Penalizacao (descricao, final_penalizacao, id_usuario, id_emprestimo)
            VALUES (%s, %s, %s, %s)
        """
        
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(penalty_query, (description, penalty_end, user_id, loan_id))
                conn.commit()

emprestimo_service = EmprestimoService()
