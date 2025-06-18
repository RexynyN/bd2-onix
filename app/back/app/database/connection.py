import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import time
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                self.connection = psycopg2.connect(
                    host=settings.DATABASE_HOST,
                    port=settings.DATABASE_PORT,
                    database=settings.DATABASE_NAME,
                    user=settings.DATABASE_USER,
                    password=settings.DATABASE_PASSWORD,
                    cursor_factory=RealDictCursor
                )
                logger.info("Conectado ao banco de dados PostgreSQL")
                break
            except Exception as error:
                retry_count += 1
                logger.error(f"Erro ao conectar ao banco (tentativa {retry_count}): {error}")
                if retry_count < max_retries:
                    time.sleep(2)
                else:
                    raise
    
    def close(self):
        if self.connection:
            self.connection.close()
            logger.info("Conexão com banco de dados fechada")
    
    @contextmanager
    def get_cursor(self):
        cursor = self.connection.cursor()
        try:
            yield cursor
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise e
        finally:
            cursor.close()

# Instância global do banco
db = Database()

def get_db_connection():
    return db.connection

def get_db_cursor():
    return db.get_cursor()
