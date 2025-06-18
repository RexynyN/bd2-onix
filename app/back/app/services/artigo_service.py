from typing import List, Optional
from app.database.connection import Database
from app.schemas.artigo import ArtigoCreate, ArtigoUpdate, ArtigoResponse, ArtigoWithAuthors
import logging

logger = logging.getLogger(__name__)

class ArtigoService:
    def __init__(self):
        self.db = Database()

    async def create_artigo(self, artigo_data: ArtigoCreate) -> ArtigoResponse:
        """Criar um novo artigo"""
        conn = await self.db.get_connection()
        try:
            # Primeiro inserir na tabela Titulo
            titulo_query = """
                INSERT INTO Titulo (tipo_midia) 
                VALUES ('artigo') 
                RETURNING id_titulo
            """
            cursor = conn.cursor()
            cursor.execute(titulo_query)
            id_titulo = cursor.fetchone()[0]
            
            # Depois inserir na tabela Artigos
            artigo_query = """
                INSERT INTO Artigos (id_artigo, titulo, DOI, publicadora, data_publicacao)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id_artigo, titulo, DOI, publicadora, data_publicacao
            """
            cursor.execute(artigo_query, (
                id_titulo,
                artigo_data.titulo,
                artigo_data.DOI,
                artigo_data.publicadora,
                artigo_data.data_publicacao
            ))
            
            result = cursor.fetchone()
            conn.commit()
            
            return ArtigoResponse(
                id_artigo=result[0],
                titulo=result[1],
                DOI=result[2],
                publicadora=result[3],
                data_publicacao=result[4]
            )
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Erro ao criar artigo: {e}")
            raise
        finally:
            cursor.close()
            await self.db.close_connection(conn)

    async def get_artigo_by_id(self, artigo_id: int) -> Optional[ArtigoResponse]:
        """Buscar artigo por ID"""
        conn = await self.db.get_connection()
        try:
            query = """
                SELECT id_artigo, titulo, DOI, publicadora, data_publicacao
                FROM Artigos 
                WHERE id_artigo = %s
            """
            cursor = conn.cursor()
            cursor.execute(query, (artigo_id,))
            result = cursor.fetchone()
            
            if result:
                return ArtigoResponse(
                    id_artigo=result[0],
                    titulo=result[1],
                    DOI=result[2],
                    publicadora=result[3],
                    data_publicacao=result[4]
                )
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar artigo {artigo_id}: {e}")
            raise
        finally:
            cursor.close()
            await self.db.close_connection(conn)

    async def get_artigos(self, skip: int = 0, limit: int = 100) -> List[ArtigoResponse]:
        """Listar artigos com paginação"""
        conn = await self.db.get_connection()
        try:
            query = """
                SELECT id_artigo, titulo, DOI, publicadora, data_publicacao
                FROM Artigos 
                ORDER BY titulo
                LIMIT %s OFFSET %s
            """
            cursor = conn.cursor()
            cursor.execute(query, (limit, skip))
            results = cursor.fetchall()
            
            return [
                ArtigoResponse(
                    id_artigo=row[0],
                    titulo=row[1],
                    DOI=row[2],
                    publicadora=row[3],
                    data_publicacao=row[4]
                )
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Erro ao listar artigos: {e}")
            raise
        finally:
            cursor.close()
            await self.db.close_connection(conn)

    async def update_artigo(self, artigo_id: int, artigo_data: ArtigoUpdate) -> Optional[ArtigoResponse]:
        """Atualizar artigo"""
        conn = await self.db.get_connection()
        try:
            # Construir query dinamicamente baseado nos campos fornecidos
            fields = []
            values = []
            
            if artigo_data.titulo is not None:
                fields.append("titulo = %s")
                values.append(artigo_data.titulo)
            if artigo_data.DOI is not None:
                fields.append("DOI = %s")
                values.append(artigo_data.DOI)
            if artigo_data.publicadora is not None:
                fields.append("publicadora = %s")
                values.append(artigo_data.publicadora)
            if artigo_data.data_publicacao is not None:
                fields.append("data_publicacao = %s")
                values.append(artigo_data.data_publicacao)
            
            if not fields:
                return await self.get_artigo_by_id(artigo_id)
            
            values.append(artigo_id)
            query = f"""
                UPDATE Artigos 
                SET {', '.join(fields)}
                WHERE id_artigo = %s
                RETURNING id_artigo, titulo, DOI, publicadora, data_publicacao
            """
            
            cursor = conn.cursor()
            cursor.execute(query, values)
            result = cursor.fetchone()
            
            if result:
                conn.commit()
                return ArtigoResponse(
                    id_artigo=result[0],
                    titulo=result[1],
                    DOI=result[2],
                    publicadora=result[3],
                    data_publicacao=result[4]
                )
            return None
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Erro ao atualizar artigo {artigo_id}: {e}")
            raise
        finally:
            cursor.close()
            await self.db.close_connection(conn)

    async def delete_artigo(self, artigo_id: int) -> bool:
        """Excluir artigo"""
        conn = await self.db.get_connection()
        try:
            # Verificar se existe no estoque
            check_query = """
                SELECT COUNT(*) FROM Estoque e
                INNER JOIN Titulo t ON e.id_titulo = t.id_titulo
                WHERE t.id_titulo = %s
            """
            cursor = conn.cursor()
            cursor.execute(check_query, (artigo_id,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                raise ValueError("Não é possível excluir artigo que possui exemplares no estoque")
            
            # Excluir artigo
            delete_artigo_query = "DELETE FROM Artigos WHERE id_artigo = %s"
            cursor.execute(delete_artigo_query, (artigo_id,))
            
            # Excluir da tabela Titulo
            delete_titulo_query = "DELETE FROM Titulo WHERE id_titulo = %s"
            cursor.execute(delete_titulo_query, (artigo_id,))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Erro ao excluir artigo {artigo_id}: {e}")
            raise
        finally:
            cursor.close()
            await self.db.close_connection(conn)

    async def search_artigos(self, query: str) -> List[ArtigoResponse]:
        """Buscar artigos por título, DOI ou publicadora"""
        conn = await self.db.get_connection()
        try:
            search_query = """
                SELECT id_artigo, titulo, DOI, publicadora, data_publicacao
                FROM Artigos 
                WHERE titulo ILIKE %s OR DOI ILIKE %s OR publicadora ILIKE %s
                ORDER BY titulo
            """
            search_param = f"%{query}%"
            cursor = conn.cursor()
            cursor.execute(search_query, (search_param, search_param, search_param))
            results = cursor.fetchall()
            
            return [
                ArtigoResponse(
                    id_artigo=row[0],
                    titulo=row[1],
                    DOI=row[2],
                    publicadora=row[3],
                    data_publicacao=row[4]
                )
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Erro ao buscar artigos: {e}")
            raise
        finally:
            cursor.close()
            await self.db.close_connection(conn)

    async def get_artigo_with_authors(self, artigo_id: int) -> Optional[ArtigoWithAuthors]:
        """Buscar artigo com seus autores"""
        conn = await self.db.get_connection()
        try:
            query = """
                SELECT a.id_artigo, a.titulo, a.DOI, a.publicadora, a.data_publicacao,
                       au.id_autor, au.nome as autor_nome
                FROM Artigos a
                LEFT JOIN Autorias aut ON a.id_artigo = aut.id_titulo
                LEFT JOIN Autores au ON aut.id_autor = au.id_autor
                WHERE a.id_artigo = %s
            """
            cursor = conn.cursor()
            cursor.execute(query, (artigo_id,))
            results = cursor.fetchall()
            
            if not results:
                return None
            
            # Primeira linha contém dados do artigo
            first_row = results[0]
            artigo = ArtigoWithAuthors(
                id_artigo=first_row[0],
                titulo=first_row[1],
                DOI=first_row[2],
                publicadora=first_row[3],
                data_publicacao=first_row[4],
                autores=[]
            )
            
            # Adicionar autores se existirem
            for row in results:
                if row[5]:  # Se tem autor
                    artigo.autores.append({
                        "id_autor": row[5],
                        "nome": row[6]
                    })
            
            return artigo
            
        except Exception as e:
            logger.error(f"Erro ao buscar artigo com autores {artigo_id}: {e}")
            raise
        finally:
            cursor.close()
            await self.db.close_connection(conn)
