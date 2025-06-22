from typing import List, Optional
from app.database.connection import get_db_cursor
from app.schemas.schemas import UsuarioCreate, UsuarioUpdate, Usuario
from fastapi import HTTPException

class UsuarioService:
    def create_usuario(self, usuario: UsuarioCreate) -> Usuario:
        with get_db_cursor() as cursor:
            query = '''
                INSERT INTO Usuario (nome, email, endereco, telefone)
                VALUES (%s, %s, %s, %s)
                RETURNING id_usuario, nome, email, endereco, telefone
            '''
            cursor.execute(query, (
                usuario.nome,
                usuario.email,
                usuario.endereco,
                usuario.telefone
            ))
            result = cursor.fetchone()
            return Usuario(**result)
    
    def get_usuario(self, id_usuario: int) -> Optional[Usuario]:
        with get_db_cursor() as cursor:
            query = "SELECT * FROM Usuario WHERE id_usuario = %s"
            cursor.execute(query, (id_usuario,))
            result = cursor.fetchone()
            if result:
                return Usuario(**result)
            return None
    
    def get_usuarios(self, skip: int = 0, limit: int = 100) -> List[Usuario]:
        with get_db_cursor() as cursor:
            query = "SELECT * FROM Usuario ORDER BY id_usuario OFFSET %s LIMIT %s"
            cursor.execute(query, (skip, limit))
            results = cursor.fetchall()
            return [Usuario(**result) for result in results]
    
    def update_usuario(self, id_usuario: int, usuario: UsuarioUpdate) -> Optional[Usuario]:
        # Construir query dinamicamente baseado nos campos fornecidos
        fields = []
        values = []
        
        if usuario.nome is not None:
            fields.append("nome = %s")
            values.append(usuario.nome)
        if usuario.email is not None:
            fields.append("email = %s")
            values.append(usuario.email)
        if usuario.endereco is not None:
            fields.append("endereco = %s")
            values.append(usuario.endereco)
        if usuario.telefone is not None:
            fields.append("telefone = %s")
            values.append(usuario.telefone)
        
        if not fields:
            return self.get_usuario(id_usuario)
        
        values.append(id_usuario)
        
        with get_db_cursor() as cursor:
            query = f'''
                UPDATE Usuario 
                SET {", ".join(fields)}
                WHERE id_usuario = %s
                RETURNING id_usuario, nome, email, endereco, telefone
            '''
            cursor.execute(query, values)
            result = cursor.fetchone()
            if result:
                return Usuario(**result)
            return None
    
    def delete_usuario(self, id_usuario: int) -> bool:
        with get_db_cursor() as cursor:
            # Verificar se há empréstimos associados
            cursor.execute("SELECT COUNT(*) FROM Emprestimo WHERE id_usuario = %s", (id_usuario,))
            count = cursor.fetchone()['count']
            
            if count > 0:
                raise HTTPException(
                    status_code=400,
                    detail="Não é possível excluir usuário com empréstimos associados"
                )
            
            query = "DELETE FROM Usuario WHERE id_usuario = %s"
            cursor.execute(query, (id_usuario,))
            return cursor.rowcount > 0
    
    def get_usuarios_com_emprestimos_em_andamento(self, skip: int=0, limit: int=0) -> List[Usuario]:
        with get_db_cursor() as cursor:
            query = '''
                SELECT DISTINCT u.* 
                FROM Usuario u
                INNER JOIN Emprestimo e 
                    ON u.id_usuario = e.id_usuario
                WHERE e.data_devolucao IS NULL
                ORDER BY u.nome
                OFFSET %s LIMIT %s
            '''
            cursor.execute(query, (skip, limit))
            results = cursor.fetchall()
            return [Usuario(**result) for result in results]
    
    def search_usuarios(self, q: str):
        with get_db_cursor() as cursor:
            query = """
                SELECT id_usuario, nome, email, endereco, telefone
                FROM Usuario
                WHERE nome ILIKE %s OR email ILIKE %s OR telefone ILIKE %s
                LIMIT 200 
            """
            param = f"%{q}%"
            cursor.execute(query, tuple([param for _ in range(3)]))
            results = cursor.fetchall()
            return [Usuario(**row) for row in results]


usuario_service = UsuarioService()
