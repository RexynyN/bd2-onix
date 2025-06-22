from typing import List, Optional
from app.database.connection import get_db_cursor
from app.schemas.schemas import BibliotecaCreate, BibliotecaUpdate, Biblioteca
from fastapi import HTTPException

class BibliotecaService:
    
    def create_biblioteca(self, biblioteca: BibliotecaCreate) -> Biblioteca:
        with get_db_cursor() as cursor:
            query = '''
                INSERT INTO Biblioteca (nome, endereco)
                VALUES (%s, %s)
                RETURNING id_biblioteca, nome, endereco
            '''
            cursor.execute(query, (
                biblioteca.nome,
                biblioteca.endereco
            ))
            result = cursor.fetchone()
            return Biblioteca(**result)
    
    def get_biblioteca(self, id_biblioteca: int) -> Optional[Biblioteca]:
        with get_db_cursor() as cursor:
            query = "SELECT * FROM Biblioteca WHERE id_biblioteca = %s"
            cursor.execute(query, (id_biblioteca,))
            result = cursor.fetchone()
            if result:
                return Biblioteca(**result)
            return None
    
    def get_bibliotecas(self, skip: int = 0, limit: int = 100) -> List[Biblioteca]:
        with get_db_cursor() as cursor:
            query = "SELECT * FROM Biblioteca ORDER BY id_biblioteca OFFSET %s LIMIT %s"
            cursor.execute(query, (skip, limit))
            results = cursor.fetchall()
            return [Biblioteca(**result) for result in results]
    
    def update_biblioteca(self, id_biblioteca: int, biblioteca: BibliotecaUpdate) -> Optional[Biblioteca]:
        fields = []
        values = []
        
        if biblioteca.nome is not None:
            fields.append("nome = %s")
            values.append(biblioteca.nome)
        if biblioteca.endereco is not None:
            fields.append("endereco = %s")
            values.append(biblioteca.endereco)
        
        if not fields:
            return self.get_biblioteca(id_biblioteca)
        
        values.append(id_biblioteca)
        
        with get_db_cursor() as cursor:
            query = f'''
                UPDATE Biblioteca 
                SET {", ".join(fields)}
                WHERE id_biblioteca = %s
                RETURNING id_biblioteca, nome, endereco
            '''
            cursor.execute(query, values)
            result = cursor.fetchone()
            if result:
                return Biblioteca(**result)
            return None
    
    def delete_biblioteca(self, id_biblioteca: int) -> bool:
        with get_db_cursor() as cursor:
            # Verificar se há estoque associado
            cursor.execute("SELECT COUNT(*) FROM Estoque WHERE id_biblioteca = %s", (id_biblioteca,))
            count = cursor.fetchone()['count']
            
            if count > 0:
                raise HTTPException(
                    status_code=400,
                    detail="Não é possível excluir biblioteca com itens no estoque"
                )
            
            query = "DELETE FROM Biblioteca WHERE id_biblioteca = %s"
            cursor.execute(query, (id_biblioteca,))
            return cursor.rowcount > 0
        
    def search_bibliotecas(self, q: str):
        with get_db_cursor() as cursor:
            query = """
                SELECT id_biblioteca, nome, endereco
                FROM Biblioteca
                WHERE nome ILIKE %s OR endereco ILIKE %s
                ORDER BY nome
                LIMIT 200 
            """
            param = f"%{q}%"
            cursor.execute(query, tuple([param for _ in range(2)]))
            results = cursor.fetchall()
            return [Biblioteca(**row) for row in results]
        
biblioteca_service = BibliotecaService()
