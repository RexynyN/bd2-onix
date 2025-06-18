from typing import List, Optional
from app.database.connection import Database
from app.schemas.revista import RevistaCreate, RevistaUpdate, RevistaResponse, RevistaWithAuthors
import logging

logger = logging.getLogger(__name__)

class RevistaService:
    def __init__(self):
        self.db = Database()

    async def create_revista(self, revista_data: RevistaCreate) -> RevistaResponse:
        """Criar uma nova revista"""
        conn = await self.db.get_connection()
        try:
            # Primeiro inserir na tabela Titulo
            titulo_query = """
                INSERT INTO Titulo (tipo_midia) 
                VALUES ('revista') 
                RETURNING id_titulo
            """
            cursor = conn.cursor()
            cursor.execute(titulo_query)
            id_titulo = cursor.fetchone()[0]
            
            # Depois inserir na tabela Revistas
            revista_query = """
                INSERT INTO Revistas (id_revista, titulo, ISSN, periodicidade, editora, data_publicacao)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id_revista, titulo, ISSN, periodicidade, editora, data_publicacao
            """
            cursor.execute(revista_query, (
                id_titulo,
                revista_data.titulo,
                revista_data.ISSN,
                revista_data.periodicidade,
                revista_data.editora,
                revista_data.data_publicacao
            ))
            
            result = cursor.fetchone()
            conn.commit()
            
            return RevistaResponse(
                id_revista=result[0],
                titulo=result[1],
                ISSN=result[2],
                periodicidade=result[3],
                editora=result[4],
                data_publicacao=result[5]
            )
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Erro ao criar revista: {e}")
            raise
        finally:
            cursor.close()
            await self.db.close_connection(conn)

    async def get_revista_by_id(self, revista_id: int) -> Optional[RevistaResponse]:
        """Buscar revista por ID"""
        conn = await self.db.get_connection()
        try:
            query = """
                SELECT id_revista, titulo, ISSN, periodicidade, editora, data_publicacao
                FROM Revistas 
                WHERE id_revista = %s
            """
            cursor = conn.cursor()
            cursor.execute(query, (revista_id,))
            result = cursor.fetchone()
            
            if result:
                return RevistaResponse(
                    id_revista=result[0],
                    titulo=result[1],
                    ISSN=result[2],
                    periodicidade=result[3],
                    editora=result[4],
                    data_publicacao=result[5]
                )
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar revista {revista_id}: {e}")
            raise
        finally:
            cursor.close()
            await self.db.close_connection(conn)

    async def get_revistas(self, skip: int = 0, limit: int = 100) -> List[RevistaResponse]:
        """Listar revistas com paginação"""
        conn = await self.db.get_connection()
        try:
            query = """
                SELECT id_revista, titulo, ISSN, periodicidade, editora, data_publicacao
                FROM Revistas 
                ORDER BY titulo
                LIMIT %s OFFSET %s
            """
            cursor = conn.cursor()
            cursor.execute(query, (limit, skip))
            results = cursor.fetchall()
            
            return [
                RevistaResponse(
                    id_revista=row[0],
                    titulo=row[1],
                    ISSN=row[2],
                    periodicidade=row[3],
                    editora=row[4],
                    data_publicacao=row[5]
                )
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Erro ao listar revistas: {e}")
            raise
        finally:
            cursor.close()
            await self.db.close_connection(conn)

    async def update_revista(self, revista_id: int, revista_data: RevistaUpdate) -> Optional[RevistaResponse]:
        """Atualizar revista"""
        conn = await self.db.get_connection()
        try:
            # Construir query dinamicamente baseado nos campos fornecidos
            fields = []
            values = []
            
            if revista_data.titulo is not None:
                fields.append("titulo = %s")
                values.append(revista_data.titulo)
            if revista_data.ISSN is not None:
                fields.append("ISSN = %s")
                values.append(revista_data.ISSN)
            if revista_data.periodicidade is not None:
                fields.append("periodicidade = %s")
                values.append(revista_data.periodicidade)
            if revista_data.editora is not None:
                fields.append("editora = %s")
                values.append(revista_data.editora)
            if revista_data.data_publicacao is not None:
                fields.append("data_publicacao = %s")
                values.append(revista_data.data_publicacao)
            
            if not fields:
                return await self.get_revista_by_id(revista_id)
            
            values.append(revista_id)
            query = f"""
                UPDATE Revistas 
                SET {', '.join(fields)}
                WHERE id_revista = %s
                RETURNING id_revista, titulo, ISSN, periodicidade, editora, data_publicacao
            """
            
            cursor = conn.cursor()
            cursor.execute(query, values)
            result = cursor.fetchone()
            
            if result:
                conn.commit()
                return RevistaResponse(
                    id_revista=result[0],
                    titulo=result[1],
                    ISSN=result[2],
                    periodicidade=result[3],
                    editora=result[4],
                    data_publicacao=result[5]
                )
            return None
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Erro ao atualizar revista {revista_id}: {e}")
            raise
        finally:
            cursor.close()
            await self.db.close_connection(conn)

    async def delete_revista(self, revista_id: int) -> bool:
        """Excluir revista"""
        conn = await self.db.get_connection()
        try:
            # Verificar se existe no estoque
            check_query = """
                SELECT COUNT(*) FROM Estoque e
                INNER JOIN Titulo t ON e.id_titulo = t.id_titulo
                WHERE t.id_titulo = %s
            """
            cursor = conn.cursor()
            cursor.execute(check_query, (revista_id,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                raise ValueError("Não é possível excluir revista que possui exemplares no estoque")
            
            # Excluir revista
            delete_revista_query = "DELETE FROM Revistas WHERE id_revista = %s"
            cursor.execute(delete_revista_query, (revista_id,))
            
            # Excluir da tabela Titulo
            delete_titulo_query = "DELETE FROM Titulo WHERE id_titulo = %s"
            cursor.execute(delete_titulo_query, (revista_id,))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Erro ao excluir revista {revista_id}: {e}")
            raise
        finally:
            cursor.close()
            await self.db.close_connection(conn)

    async def search_revistas(self, query: str) -> List[RevistaResponse]:
        """Buscar revistas por título, ISSN ou editora"""
        conn = await self.db.get_connection()
        try:
            search_query = """
                SELECT id_revista, titulo, ISSN, periodicidade, editora, data_publicacao
                FROM Revistas 
                WHERE titulo ILIKE %s OR ISSN ILIKE %s OR editora ILIKE %s
                ORDER BY titulo
            """
            search_param = f"%{query}%"
            cursor = conn.cursor()
            cursor.execute(search_query, (search_param, search_param, search_param))
            results = cursor.fetchall()
            
            return [
                RevistaResponse(
                    id_revista=row[0],
                    titulo=row[1],
                    ISSN=row[2],
                    periodicidade=row[3],
                    editora=row[4],
                    data_publicacao=row[5]
                )
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Erro ao buscar revistas: {e}")
            raise
        finally:
            cursor.close()
            await self.db.close_connection(conn)

    async def get_revista_with_authors(self, revista_id: int) -> Optional[RevistaWithAuthors]:
        """Buscar revista com seus autores"""
        conn = await self.db.get_connection()
        try:
            query = """
                SELECT r.id_revista, r.titulo, r.ISSN, r.periodicidade, r.editora, r.data_publicacao,
                       a.id_autor, a.nome as autor_nome
                FROM Revistas r
                LEFT JOIN Autorias au ON r.id_revista = au.id_titulo
                LEFT JOIN Autores a ON au.id_autor = a.id_autor
                WHERE r.id_revista = %s
            """
            cursor = conn.cursor()
            cursor.execute(query, (revista_id,))
            results = cursor.fetchall()
            
            if not results:
                return None
            
            # Primeira linha contém dados da revista
            first_row = results[0]
            revista = RevistaWithAuthors(
                id_revista=first_row[0],
                titulo=first_row[1],
                ISSN=first_row[2],
                periodicidade=first_row[3],
                editora=first_row[4],
                data_publicacao=first_row[5],
                autores=[]
            )
            
            # Adicionar autores se existirem
            for row in results:
                if row[6]:  # Se tem autor
                    revista.autores.append({
                        "id_autor": row[6],
                        "nome": row[7]
                    })
            
            return revista
            
        except Exception as e:
            logger.error(f"Erro ao buscar revista com autores {revista_id}: {e}")
            raise
        finally:
            cursor.close()
            await self.db.close_connection(conn)
