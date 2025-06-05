"""
Biblioteca service for business logic
"""
import psycopg2.extras
from typing import List, Optional, Dict, Any
from .base_service import BaseService
from app.db.database import get_db_connection
import logging

logger = logging.getLogger(__name__)

class BibliotecaService(BaseService):
    def __init__(self):
        super().__init__("Biblioteca", "id_biblioteca")
    
    def get_library_stock(self, library_id: int, page: int = 1, size: int = 10) -> tuple[List[Dict[str, Any]], int]:
        """Get stock items for a specific library"""
        offset = (page - 1) * size
        
        # Count query
        count_query = """
            SELECT COUNT(*) FROM Estoque est
            JOIN Titulo t ON est.id_titulo = t.id_titulo
            WHERE est.id_biblioteca = %s
        """
        
        # Data query
        data_query = """
            SELECT est.*, t.tipo_midia
            FROM Estoque est
            JOIN Titulo t ON est.id_titulo = t.id_titulo
            WHERE est.id_biblioteca = %s
            ORDER BY est.id_estoque
            LIMIT %s OFFSET %s
        """
        
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                # Get total count
                cursor.execute(count_query, (library_id,))
                total = cursor.fetchone()[0]
                
                # Get data
                cursor.execute(data_query, (library_id, size, offset))
                results = cursor.fetchall()
                
                return [dict(row) for row in results], total
    
    def get_available_items(self, library_id: int) -> List[Dict[str, Any]]:
        """Get available items for loan in a library"""
        query = """
            SELECT est.*, t.tipo_midia
            FROM Estoque est
            JOIN Titulo t ON est.id_titulo = t.id_titulo
            LEFT JOIN Emprestimo emp ON est.id_estoque = emp.id_estoque 
                AND emp.data_devolucao IS NULL
            WHERE est.id_biblioteca = %s AND emp.id_emprestimo IS NULL
            ORDER BY t.tipo_midia, est.id_estoque
        """
        
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(query, (library_id,))
                return [dict(row) for row in cursor.fetchall()]

biblioteca_service = BibliotecaService()
