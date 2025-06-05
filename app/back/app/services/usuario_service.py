"""
Usuario service for business logic
"""
import psycopg2.extras
from typing import List, Optional, Dict, Any
from .base_service import BaseService
from app.db.database import get_db_connection
import logging

logger = logging.getLogger(__name__)

class UsuarioService(BaseService):
    def __init__(self):
        super().__init__("Usuario", "id_usuario")
    
    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        query = "SELECT * FROM Usuario WHERE email = %s"
        
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(query, (email,))
                result = cursor.fetchone()
                return dict(result) if result else None
    
    def search_users(self, search_term: str, page: int = 1, size: int = 10) -> tuple[List[Dict[str, Any]], int]:
        """Search users by name or email"""
        offset = (page - 1) * size
        search_pattern = f"%{search_term}%"
        
        # Count query
        count_query = """
            SELECT COUNT(*) FROM Usuario
            WHERE nome ILIKE %s OR email ILIKE %s
        """
        
        # Data query
        data_query = """
            SELECT * FROM Usuario
            WHERE nome ILIKE %s OR email ILIKE %s
            ORDER BY nome
            LIMIT %s OFFSET %s
        """
        
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                # Get total count
                cursor.execute(count_query, (search_pattern, search_pattern))
                total = cursor.fetchone()[0]
                
                # Get data
                cursor.execute(data_query, (search_pattern, search_pattern, size, offset))
                results = cursor.fetchall()
                
                return [dict(row) for row in results], total
    
    def get_user_loans(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all loans for a specific user"""
        query = """
            SELECT e.*, est.condicao, t.tipo_midia
            FROM Emprestimo e
            JOIN Estoque est ON e.id_estoque = est.id_estoque
            JOIN Titulo t ON est.id_titulo = t.id_titulo
            WHERE e.id_usuario = %s
            ORDER BY e.data_emprestimo DESC
        """
        
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(query, (user_id,))
                return [dict(row) for row in cursor.fetchall()]
    
    def get_user_penalties(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all penalties for a specific user"""
        query = """
            SELECT * FROM Penalizacao
            WHERE id_usuario = %s
            ORDER BY final_penalizacao DESC
        """
        
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(query, (user_id,))
                return [dict(row) for row in cursor.fetchall()]

usuario_service = UsuarioService()
