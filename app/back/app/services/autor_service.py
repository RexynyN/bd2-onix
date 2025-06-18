from typing import List, Optional
from app.database.connection import get_db_cursor
from app.schemas.schemas import AutorCreate, AutorUpdate, Autor
from fastapi import HTTPException

class AutorService:
    
    def create_autor(self, autor: AutorCreate) -> Autor:
        with get_db_cursor() as cursor:
            query = '''
                INSERT INTO Autores (nome, data_nascimento, data_falecimento)
                VALUES (%s, %s, %s)
                RETURNING id_autor, nome, data_nascimento, data_falecimento
            '''
            cursor.execute(query, (
                autor.nome,
                autor.data_nascimento,
                autor.data_falecimento
            ))
            result = cursor.fetchone()
            return Autor(**result)
    
    def get_autor(self, id_autor: int) -> Optional[Autor]:
        with get_db_cursor() as cursor:
            query = "SELECT * FROM Autores WHERE id_autor = %s"
            cursor.execute(query, (id_autor,))
            result = cursor.fetchone()
            if result:
                return Autor(**result)
            return None
    
    def get_autores(self, skip: int = 0, limit: int = 100) -> List[Autor]:
        with get_db_cursor() as cursor:
            query = "SELECT * FROM Autores ORDER BY nome OFFSET %s LIMIT %s"
            cursor.execute(query, (skip, limit))
            results = cursor.fetchall()
            return [Autor(**result) for result in results]
    
    def search_autores(self, query: str) -> List[Autor]:
        with get_db_cursor() as cursor:
            search_query = '''
                SELECT * FROM Autores 
                WHERE nome ILIKE %s
                ORDER BY nome
            '''
            search_term = f"%{query}%"
            cursor.execute(search_query, (search_term,))
            results = cursor.fetchall()
            return [Autor(**result) for result in results]
    
    def update_autor(self, id_autor: int, autor: AutorUpdate) -> Optional[Autor]:
        fields = []
        values = []
        
        if autor.nome is not None:
            fields.append("nome = %s")
            values.append(autor.nome)
        if autor.data_nascimento is not None:
            fields.append("data_nascimento = %s")
            values.append(autor.data_nascimento)
        if autor.data_falecimento is not None:
            fields.append("data_falecimento = %s")
            values.append(autor.data_falecimento)
        
        if not fields:
            return self.get_autor(id_autor)
        
        values.append(id_autor)
        
        with get_db_cursor() as cursor:
            query = f'''
                UPDATE Autores 
                SET {", ".join(fields)}
                WHERE id_autor = %s
                RETURNING id_autor, nome, data_nascimento, data_falecimento
            '''
            cursor.execute(query, values)
            result = cursor.fetchone()
            if result:
                return Autor(**result)
            return None
    
    def delete_autor(self, id_autor: int) -> bool:
        with get_db_cursor() as cursor:
            # Verificar se há autorias associadas
            cursor.execute("SELECT COUNT(*) FROM Autorias WHERE id_autor = %s", (id_autor,))
            count = cursor.fetchone()['count']
            
            if count > 0:
                raise HTTPException(
                    status_code=400,
                    detail="Não é possível excluir autor com obras associadas"
                )
            
            query = "DELETE FROM Autores WHERE id_autor = %s"
            cursor.execute(query, (id_autor,))
            return cursor.rowcount > 0

autor_service = AutorService()
