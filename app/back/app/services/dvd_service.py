from typing import List, Optional
from app.database.connection import Database
from app.schemas.dvd import DVDCreate, DVDUpdate, DVDResponse, DVDWithAuthors
import logging

logger = logging.getLogger(__name__)

class DVDService:
    def __init__(self):
        self.db = Database()

    async def create_dvd(self, dvd_data: DVDCreate) -> DVDResponse:
        """Criar um novo DVD"""
        conn = await self.db.get_connection()
        try:
            # Primeiro inserir na tabela Titulo
            titulo_query = """
                INSERT INTO Titulo (tipo_midia) 
                VALUES ('dvd') 
                RETURNING id_titulo
            """
            cursor = conn.cursor()
            cursor.execute(titulo_query)
            id_titulo = cursor.fetchone()[0]
            
            # Depois inserir na tabela DVDs
            dvd_query = """
                INSERT INTO DVDs (id_dvd, titulo, ISAN, duracao, distribuidora, data_lancamento)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id_dvd, titulo, ISAN, duracao, distribuidora, data_lancamento
            """
            cursor.execute(dvd_query, (
                id_titulo,
                dvd_data.titulo,
                dvd_data.ISAN,
                dvd_data.duracao,
                dvd_data.distribuidora,
                dvd_data.data_lancamento
            ))
            
            result = cursor.fetchone()
            conn.commit()
            
            return DVDResponse(
                id_dvd=result[0],
                titulo=result[1],
                ISAN=result[2],
                duracao=result[3],
                distribuidora=result[4],
                data_lancamento=result[5]
            )
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Erro ao criar DVD: {e}")
            raise
        finally:
            cursor.close()
            await self.db.close_connection(conn)

    async def get_dvd_by_id(self, dvd_id: int) -> Optional[DVDResponse]:
        """Buscar DVD por ID"""
        conn = await self.db.get_connection()
        try:
            query = """
                SELECT id_dvd, titulo, ISAN, duracao, distribuidora, data_lancamento
                FROM DVDs 
                WHERE id_dvd = %s
            """
            cursor = conn.cursor()
            cursor.execute(query, (dvd_id,))
            result = cursor.fetchone()
            
            if result:
                return DVDResponse(
                    id_dvd=result[0],
                    titulo=result[1],
                    ISAN=result[2],
                    duracao=result[3],
                    distribuidora=result[4],
                    data_lancamento=result[5]
                )
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar DVD {dvd_id}: {e}")
            raise
        finally:
            cursor.close()
            await self.db.close_connection(conn)

    async def get_dvds(self, skip: int = 0, limit: int = 100) -> List[DVDResponse]:
        """Listar DVDs com paginação"""
        conn = await self.db.get_connection()
        try:
            query = """
                SELECT id_dvd, titulo, ISAN, duracao, distribuidora, data_lancamento
                FROM DVDs 
                ORDER BY titulo
                LIMIT %s OFFSET %s
            """
            cursor = conn.cursor()
            cursor.execute(query, (limit, skip))
            results = cursor.fetchall()
            
            return [
                DVDResponse(
                    id_dvd=row[0],
                    titulo=row[1],
                    ISAN=row[2],
                    duracao=row[3],
                    distribuidora=row[4],
                    data_lancamento=row[5]
                )
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Erro ao listar DVDs: {e}")
            raise
        finally:
            cursor.close()
            await self.db.close_connection(conn)

    async def update_dvd(self, dvd_id: int, dvd_data: DVDUpdate) -> Optional[DVDResponse]:
        """Atualizar DVD"""
        conn = await self.db.get_connection()
        try:
            # Construir query dinamicamente baseado nos campos fornecidos
            fields = []
            values = []
            
            if dvd_data.titulo is not None:
                fields.append("titulo = %s")
                values.append(dvd_data.titulo)
            if dvd_data.ISAN is not None:
                fields.append("ISAN = %s")
                values.append(dvd_data.ISAN)
            if dvd_data.duracao is not None:
                fields.append("duracao = %s")
                values.append(dvd_data.duracao)
            if dvd_data.distribuidora is not None:
                fields.append("distribuidora = %s")
                values.append(dvd_data.distribuidora)
            if dvd_data.data_lancamento is not None:
                fields.append("data_lancamento = %s")
                values.append(dvd_data.data_lancamento)
            
            if not fields:
                return await self.get_dvd_by_id(dvd_id)
            
            values.append(dvd_id)
            query = f"""
                UPDATE DVDs 
                SET {', '.join(fields)}
                WHERE id_dvd = %s
                RETURNING id_dvd, titulo, ISAN, duracao, distribuidora, data_lancamento
            """
            
            cursor = conn.cursor()
            cursor.execute(query, values)
            result = cursor.fetchone()
            
            if result:
                conn.commit()
                return DVDResponse(
                    id_dvd=result[0],
                    titulo=result[1],
                    ISAN=result[2],
                    duracao=result[3],
                    distribuidora=result[4],
                    data_lancamento=result[5]
                )
            return None
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Erro ao atualizar DVD {dvd_id}: {e}")
            raise
        finally:
            cursor.close()
            await self.db.close_connection(conn)

    async def delete_dvd(self, dvd_id: int) -> bool:
        """Excluir DVD"""
        conn = await self.db.get_connection()
        try:
            # Verificar se existe no estoque
            check_query = """
                SELECT COUNT(*) FROM Estoque e
                INNER JOIN Titulo t ON e.id_titulo = t.id_titulo
                WHERE t.id_titulo = %s
            """
            cursor = conn.cursor()
            cursor.execute(check_query, (dvd_id,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                raise ValueError("Não é possível excluir DVD que possui exemplares no estoque")
            
            # Excluir DVD
            delete_dvd_query = "DELETE FROM DVDs WHERE id_dvd = %s"
            cursor.execute(delete_dvd_query, (dvd_id,))
            
            # Excluir da tabela Titulo
            delete_titulo_query = "DELETE FROM Titulo WHERE id_titulo = %s"
            cursor.execute(delete_titulo_query, (dvd_id,))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Erro ao excluir DVD {dvd_id}: {e}")
            raise
        finally:
            cursor.close()
            await self.db.close_connection(conn)

    async def search_dvds(self, query: str) -> List[DVDResponse]:
        """Buscar DVDs por título, ISAN ou distribuidora"""
        conn = await self.db.get_connection()
        try:
            search_query = """
                SELECT id_dvd, titulo, ISAN, duracao, distribuidora, data_lancamento
                FROM DVDs 
                WHERE titulo ILIKE %s OR ISAN ILIKE %s OR distribuidora ILIKE %s
                ORDER BY titulo
            """
            search_param = f"%{query}%"
            cursor = conn.cursor()
            cursor.execute(search_query, (search_param, search_param, search_param))
            results = cursor.fetchall()
            
            return [
                DVDResponse(
                    id_dvd=row[0],
                    titulo=row[1],
                    ISAN=row[2],
                    duracao=row[3],
                    distribuidora=row[4],
                    data_lancamento=row[5]
                )
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Erro ao buscar DVDs: {e}")
            raise
        finally:
            cursor.close()
            await self.db.close_connection(conn)

    async def get_dvd_with_authors(self, dvd_id: int) -> Optional[DVDWithAuthors]:
        """Buscar DVD com seus autores/diretores"""
        conn = await self.db.get_connection()
        try:
            query = """
                SELECT d.id_dvd, d.titulo, d.ISAN, d.duracao, d.distribuidora, d.data_lancamento,
                       a.id_autor, a.nome as autor_nome
                FROM DVDs d
                LEFT JOIN Autorias au ON d.id_dvd = au.id_titulo
                LEFT JOIN Autores a ON au.id_autor = a.id_autor
                WHERE d.id_dvd = %s
            """
            cursor = conn.cursor()
            cursor.execute(query, (dvd_id,))
            results = cursor.fetchall()
            
            if not results:
                return None
            
            # Primeira linha contém dados do DVD
            first_row = results[0]
            dvd = DVDWithAuthors(
                id_dvd=first_row[0],
                titulo=first_row[1],
                ISAN=first_row[2],
                duracao=first_row[3],
                distribuidora=first_row[4],
                data_lancamento=first_row[5],
                autores=[]
            )
            
            # Adicionar autores se existirem
            for row in results:
                if row[6]:  # Se tem autor
                    dvd.autores.append({
                        "id_autor": row[6],
                        "nome": row[7]
                    })
            
            return dvd
            
        except Exception as e:
            logger.error(f"Erro ao buscar DVD com autores {dvd_id}: {e}")
            raise
        finally:
            cursor.close()
            await self.db.close_connection(conn)
