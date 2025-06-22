"""
Media service for handling different media types
"""
import psycopg2.extras
from typing import List, Optional, Dict, Any
from .base_service import BaseService
from app.db.database import get_db_connection
import logging

logger = logging.getLogger(__name__)

class MediaService:
    """Service for handling different media types (Livros, Revistas, DVDs, Artigos)"""
    
    def __init__(self):
        self.titulo_service = BaseService("Titulo", "id_titulo")
        self.livro_service = BaseService("Livros", "id_livro")
        self.revista_service = BaseService("Revistas", "id_revista")
        self.dvd_service = BaseService("DVDs", "id_dvd")
        self.artigo_service = BaseService("Artigos", "id_artigo")
    
    def create_media_with_title(self, media_type: str, media_data: Dict[str, Any]) -> Optional[int]:
        """Create a title and its corresponding media record"""
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    # Create title first
                    cursor.execute(
                        "INSERT INTO Titulo (tipo_midia) VALUES (%s) RETURNING id_titulo",
                        (media_type,)
                    )
                    title_id = cursor.fetchone()['id_titulo']
                    
                    # Add title_id to media_data
                    media_data[f'id_{media_type.lower()}'] = title_id
                    
                    # Create media record
                    service = self._get_media_service(media_type)
                    if service:
                        service.create(media_data)
                    
                    conn.commit()
                    return title_id
                    
                except Exception as e:
                    conn.rollback()
                    logger.error(f"Error creating {media_type}: {e}")
                    raise
    
    def get_media_details(self, title_id: int) -> Optional[Dict[str, Any]]:
        """Get complete media details including title and specific media info"""
        # First get title info
        title = self.titulo_service.get_by_id(title_id)
        if not title:
            return None
        
        media_type = title['tipo_midia']
        
        # Get specific media details
        media_details = None
        if media_type == 'livro':
            media_details = self.livro_service.get_by_id(title_id)
        elif media_type == 'revista':
            media_details = self.revista_service.get_by_id(title_id)
        elif media_type == 'dvd':
            media_details = self.dvd_service.get_by_id(title_id)
        elif media_type == 'artigo':
            media_details = self.artigo_service.get_by_id(title_id)
        
        return {
            'title_info': title,
            'media_details': media_details
        }
    
    def search_media(self, search_term: str, media_type: str = None, page: int = 1, size: int = 10) -> tuple[List[Dict[str, Any]], int]:
        """Search across all media types or specific type"""
        offset = (page - 1) * size
        search_pattern = f"%{search_term}%"
        
        where_conditions = []
        params = []
        
        if media_type:
            where_conditions.append("t.tipo_midia = %s")
            params.append(media_type)
        
        # Build query for each media type
        union_queries = []
        
        # Livros
        if not media_type or media_type == 'livro':
            union_queries.append("""
                SELECT t.id_titulo, t.tipo_midia, l.titulo, l.isbn as codigo,
                       l.editora, l.data_publicacao::text as data_pub
                FROM Titulo t
                JOIN Livros l ON t.id_titulo = l.id_livro
                WHERE l.titulo ILIKE %s
            """)
            params.extend([search_pattern])
        
        # Revistas
        if not media_type or media_type == 'revista':
            union_queries.append("""
                SELECT t.id_titulo, t.tipo_midia, r.titulo, r.issn as codigo,
                       r.editora, r.data_publicacao::text as data_pub
                FROM Titulo t
                JOIN Revistas r ON t.id_titulo = r.id_revista
                WHERE r.titulo ILIKE %s
            """)
            params.extend([search_pattern])
        
        # DVDs
        if not media_type or media_type == 'dvd':
            union_queries.append("""
                SELECT t.id_titulo, t.tipo_midia, d.titulo, d.isan as codigo,
                       d.distribuidora as editora, d.data_lancamento::text as data_pub
                FROM Titulo t
                JOIN DVDs d ON t.id_titulo = d.id_dvd
                WHERE d.titulo ILIKE %s
            """)
            params.extend([search_pattern])
        
        # Artigos
        if not media_type or media_type == 'artigo':
            union_queries.append("""
                SELECT t.id_titulo, t.tipo_midia, a.titulo, a.doi as codigo,
                       a.publicadora as editora, a.data_publicacao::text as data_pub
                FROM Titulo t
                JOIN Artigos a ON t.id_titulo = a.id_artigo
                WHERE a.titulo ILIKE %s
            """)
            params.extend([search_pattern])
        
        if not union_queries:
            return [], 0
        
        # Combine all queries
        full_query = f"""
            SELECT * FROM (
                {' UNION ALL '.join(union_queries)}
            ) AS combined_results
            ORDER BY titulo
            LIMIT %s OFFSET %s
        """
        
        # Count query
        count_query = f"""
            SELECT COUNT(*) as counter FROM (
                {' UNION ALL '.join(union_queries)}
            ) AS combined_results
        """
        
        params_with_pagination = params + [size, offset]
        
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                # Get total count
                cursor.execute(count_query, params)
                total = cursor.fetchone()['counter']
                
                # Get data
                cursor.execute(full_query, params_with_pagination)
                results = cursor.fetchall()
                
                return [dict(row) for row in results], total
    
    def _get_media_service(self, media_type: str) -> Optional[BaseService]:
        """Get the appropriate service for media type"""
        services = {
            'livro': self.livro_service,
            'revista': self.revista_service,
            'dvd': self.dvd_service,
            'artigo': self.artigo_service
        }
        return services.get(media_type.lower())

media_service = MediaService()
