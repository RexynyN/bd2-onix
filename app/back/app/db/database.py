"""
Database connection and pool management
"""
import psycopg2
from psycopg2 import pool
import logging
from typing import Optional
from contextlib import contextmanager
from app.core.config import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.connection_pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None
    
    def create_pool(self):
        """Create database connection pool"""
        try:
            self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=settings.MIN_CONNECTIONS,
                maxconn=settings.MAX_CONNECTIONS,
                host=settings.DATABASE_HOST,
                port=settings.DATABASE_PORT,
                database=settings.DATABASE_NAME,
                user=settings.DATABASE_USER,
                password=settings.DATABASE_PASSWORD
            )
            logger.info("Connection pool created successfully")
        except Exception as e:
            logger.error(f"Error creating connection pool: {e}")
            raise
    
    def close_pool(self):
        """Close all connections in the pool"""
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("Connection pool closed")
    
    @contextmanager
    def get_connection(self):
        """Get connection from pool with proper cleanup"""
        connection = None
        try:
            connection = self.connection_pool.getconn()
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if connection:
                self.connection_pool.putconn(connection)

# Global database manager instance
db_manager = DatabaseManager()

def get_db_connection():
    """Dependency to get database connection"""
    return db_manager.get_connection()
