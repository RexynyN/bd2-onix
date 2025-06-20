from typing import List, Optional
from app.database.connection import Database
from app.database.connection import get_db_cursor
from app.schemas.dvd import DVDCreate, DVDUpdate, DVDResponse, DVDWithAuthors
from app.schemas.schemas import DVD
import logging

logger = logging.getLogger(__name__)

class DVDService:
    def __init__(self):
        self.db = Database()

    async def create_dvd(self, dvd_data: DVDCreate) -> DVDResponse:
        """Criar um novo DVD"""
        with get_db_cursor() as cursor:
            try:
                # Primeiro inserir na tabela Titulo
                titulo_query = """
                    INSERT INTO Titulo (tipo_midia) 
                    VALUES ('dvd') 
                    RETURNING id_titulo
                """
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
                
                return DVDResponse(**result)
                
            except Exception as e:
                logger.error(f"Erro ao criar DVD: {e}")
                raise
        

    async def get_dvd_by_id(self, dvd_id: int) -> Optional[DVDResponse]:
        """Buscar DVD por ID"""
        with get_db_cursor() as cursor:
            try:
                query = """
                    SELECT id_dvd, titulo, ISAN, duracao, distribuidora, data_lancamento
                    FROM DVDs 
                    WHERE id_dvd = %s
                """
                cursor.execute(query, (dvd_id,))
                result = cursor.fetchone()
                
                if result:
                    return DVDResponse(**result)
                return None
                
            except Exception as e:
                logger.error(f"Erro ao buscar DVD {dvd_id}: {e}")
                raise
        

    async def get_dvds(self, skip: int = 0, limit: int = 100) -> List[DVDResponse]:
        """Listar DVDs com paginação"""
        with get_db_cursor() as cursor:
            try:
                query = """
                    SELECT id_dvd, titulo, ISAN, duracao, distribuidora, data_lancamento
                    FROM DVDs 
                    ORDER BY titulo
                    LIMIT %s OFFSET %s
                """
                cursor.execute(query, (limit, skip))
                results = cursor.fetchall()
                
                return [
                    DVDResponse(**row)
                    for row in results
                ]
                
            except Exception as e:
                logger.error(f"Erro ao listar DVDs: {e}")
                raise


    async def update_dvd(self, dvd_id: int, dvd_data: DVDUpdate) -> Optional[DVDResponse]:
        """Atualizar DVD"""
        with get_db_cursor() as cursor:
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
                
                cursor.execute(query, values)
                result = cursor.fetchone()
                
                if result:
                    return DVDResponse(**result)
                return None
                
            except Exception as e:
                logger.error(f"Erro ao atualizar DVD {dvd_id}: {e}")
                raise


    async def delete_dvd(self, dvd_id: int) -> bool:
        """Excluir DVD"""
        with get_db_cursor() as cursor:
            try:
                # Verificar se existe no estoque
                check_query = """
                    SELECT COUNT(*) FROM Estoque e
                    INNER JOIN Titulo t ON e.id_titulo = t.id_titulo
                    WHERE t.id_titulo = %s
                """
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

                return cursor.rowcount > 0
                
            except Exception as e:
                logger.error(f"Erro ao excluir DVD {dvd_id}: {e}")
                raise
      

    async def search_dvds(self, query: str) -> List[DVDResponse]:
        """Buscar DVDs por título, ISAN ou distribuidora"""
        with get_db_cursor() as cursor:
            try:
                search_query = """
                    SELECT id_dvd, titulo, ISAN, duracao, distribuidora, data_lancamento
                    FROM DVDs 
                    WHERE titulo ILIKE %s OR ISAN ILIKE %s OR distribuidora ILIKE %s
                    ORDER BY titulo
                """
                search_param = f"%{query}%"

                cursor.execute(search_query, (search_param, search_param, search_param))
                results = cursor.fetchall()
                
                return [
                    DVDResponse(**row)
                    for row in results
                ]
                
            except Exception as e:
                logger.error(f"Erro ao buscar DVDs: {e}")
                raise


    async def get_dvd_with_authors(self, dvd_id: int) -> Optional[DVDWithAuthors]:
        """Buscar DVD com seus autores/diretores"""
        with get_db_cursor() as cursor:
            try:
                query = """
                    SELECT d.id_dvd, d.titulo, d.ISAN, d.duracao, d.distribuidora, d.data_lancamento,
                        a.id_autor, a.nome as autor_nome
                    FROM DVDs d
                    LEFT JOIN Autorias au ON d.id_dvd = au.id_titulo
                    LEFT JOIN Autores a ON au.id_autor = a.id_autor
                    WHERE d.id_dvd = %s
                """
                cursor.execute(query, (dvd_id,))
                results = cursor.fetchall()
                
                if not results:
                    return None
                
                # Primeira linha contém dados do DVD
                first_row = results[0]
                dvd = DVDWithAuthors(
                    autores=[],
                    **first_row
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

