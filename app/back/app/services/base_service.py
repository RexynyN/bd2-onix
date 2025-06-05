"""
Base service class with common database operations
"""
import psycopg2
from typing import List, Optional, Dict, Any, Tuple
from app.db.database import get_db_connection
import logging

logger = logging.getLogger(__name__)

class BaseService:
    """Base service class with common CRUD operations"""
    
    def __init__(self, table_name: str, primary_key: str = "id"):
        self.table_name = table_name
        self.primary_key = primary_key
    
    def create(self, data: Dict[str, Any]) -> Optional[int]:
        """Create a new record"""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"""
            INSERT INTO {self.table_name} ({columns})
            VALUES ({placeholders})
            RETURNING {self.primary_key}
        """
        
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute(query, list(data.values()))
                    result = cursor.fetchone()
                    conn.commit()
                    return result[0] if result else None
                except Exception as e:
                    conn.rollback()
                    logger.error(f"Error creating record in {self.table_name}: {e}")
                    raise
    
    def get_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """Get a record by ID"""
        query = f"SELECT * FROM {self.table_name} WHERE {self.primary_key} = %s"
        
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(query, (record_id,))
                result = cursor.fetchone()
                return dict(result) if result else None
    
    def get_all(self, page: int = 1, size: int = 10, filters: Dict[str, Any] = None) -> Tuple[List[Dict[str, Any]], int]:
        """Get all records with pagination and optional filters"""
        offset = (page - 1) * size
        where_clause = ""
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                if value is not None:
                    conditions.append(f"{key} = %s")
                    params.append(value)
            if conditions:
                where_clause = "WHERE " + " AND ".join(conditions)
        
        # Count query
        count_query = f"SELECT COUNT(*) FROM {self.table_name} {where_clause}"
        
        # Data query
        data_query = f"""
            SELECT * FROM {self.table_name} {where_clause}
            ORDER BY {self.primary_key}
            LIMIT %s OFFSET %s
        """
        
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                # Get total count
                cursor.execute(count_query, params)
                total = cursor.fetchone()[0]
                
                # Get data
                cursor.execute(data_query, params + [size, offset])
                results = cursor.fetchall()
                
                return [dict(row) for row in results], total
    
    def update(self, record_id: int, data: Dict[str, Any]) -> bool:
        """Update a record"""
        if not data:
            return False
            
        set_clause = ', '.join([f"{key} = %s" for key in data.keys()])
        query = f"""
            UPDATE {self.table_name}
            SET {set_clause}
            WHERE {self.primary_key} = %s
        """
        
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute(query, list(data.values()) + [record_id])
                    conn.commit()
                    return cursor.rowcount > 0
                except Exception as e:
                    conn.rollback()
                    logger.error(f"Error updating record in {self.table_name}: {e}")
                    raise
    
    def delete(self, record_id: int) -> bool:
        """Delete a record"""
        query = f"DELETE FROM {self.table_name} WHERE {self.primary_key} = %s"
        
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute(query, (record_id,))
                    conn.commit()
                    return cursor.rowcount > 0
                except Exception as e:
                    conn.rollback()
                    logger.error(f"Error deleting record from {self.table_name}: {e}")
                    raise
    
    def exists(self, record_id: int) -> bool:
        """Check if a record exists"""
        query = f"SELECT 1 FROM {self.table_name} WHERE {self.primary_key} = %s"
        
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (record_id,))
                return cursor.fetchone() is not None
