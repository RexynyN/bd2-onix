from typing import List, Optional
from app.database.connection import get_db_cursor
from app.schemas.schemas import LivroCreate, LivroUpdate, Livro, MidiaTipo
from fastapi import HTTPException

class LivroService:
    
    def create_livro(self, livro: LivroCreate) -> Livro:
        with get_db_cursor() as cursor:
            try:
                # Primeiro inserir na tabela Titulo
                cursor.execute(
                    "INSERT INTO Titulo (tipo_midia) VALUES (%s) RETURNING id_titulo",
                    (MidiaTipo.livro.value,)
                )
                id_titulo = cursor.fetchone()['id_titulo']
                
                # Depois inserir na tabela Livros
                query = '''
                    INSERT INTO Livros (id_livro, titulo, isbn, numero_paginas, editora, data_publicacao)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id_livro, titulo, isbn, numero_paginas, editora, data_publicacao
                '''
                cursor.execute(query, (
                    id_titulo,
                    livro.titulo,
                    livro.isbn,
                    livro.numero_paginas,
                    livro.editora,
                    livro.data_publicacao
                ))
                result = cursor.fetchone()
                return Livro(**result)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Erro ao criar livro: {str(e)}")
    
    def get_livro(self, id_livro: int) -> Optional[Livro]:
        with get_db_cursor() as cursor:
            query = "SELECT * FROM Livros WHERE id_livro = %s"
            cursor.execute(query, (id_livro,))
            result = cursor.fetchone()
            if result:
                return Livro(**result)
            return None
    
    def get_livros(self, skip: int = 0, limit: int = 100) -> List[Livro]:
        with get_db_cursor() as cursor:
            query = "SELECT * FROM Livros ORDER BY id_livro OFFSET %s LIMIT %s"
            cursor.execute(query, (skip, limit))
            results = cursor.fetchall()
            return [Livro(**result) for result in results]
    
    def update_livro(self, id_livro: int, livro: LivroUpdate) -> Optional[Livro]:
        fields = []
        values = []
        
        if livro.titulo is not None:
            fields.append("titulo = %s")
            values.append(livro.titulo)
        if livro.isbn is not None:
            fields.append("isbn = %s")
            values.append(livro.isbn)
        if livro.numero_paginas is not None:
            fields.append("numero_paginas = %s")
            values.append(livro.numero_paginas)
        if livro.editora is not None:
            fields.append("editora = %s")
            values.append(livro.editora)
        if livro.data_publicacao is not None:
            fields.append("data_publicacao = %s")
            values.append(livro.data_publicacao)
        
        if not fields:
            return self.get_livro(id_livro)
        
        values.append(id_livro)
        
        with get_db_cursor() as cursor:
            query = f'''
                UPDATE Livros 
                SET {", ".join(fields)}
                WHERE id_livro = %s
                RETURNING id_livro, titulo, isbn, numero_paginas, editora, data_publicacao
            '''
            cursor.execute(query, values)
            result = cursor.fetchone()
            if result:
                return Livro(**result)
            return None
    
    def delete_livro(self, id_livro: int) -> bool:
        with get_db_cursor() as cursor:
            # Verificar se há estoque associado
            cursor.execute("SELECT COUNT(*) FROM Estoque WHERE id_titulo = %s", (id_livro,))
            count = cursor.fetchone()['count']
            
            if count > 0:
                raise HTTPException(
                    status_code=400,
                    detail="Não é possível excluir livro com exemplares no estoque"
                )
            
            # Excluir livro e título
            cursor.execute("DELETE FROM Livros WHERE id_livro = %s", (id_livro,))
            cursor.execute("DELETE FROM Titulo WHERE id_titulo = %s", (id_livro,))
            return cursor.rowcount > 0
    
    def search_livros(self, query: str) -> List[Livro]:
        with get_db_cursor() as cursor:
            search_query = '''
                SELECT * FROM Livros 
                WHERE titulo ILIKE %s OR isbn ILIKE %s OR editora ILIKE %s
                ORDER BY titulo
            '''
            search_term = f"%{query}%"
            cursor.execute(search_query, (search_term, search_term, search_term))
            results = cursor.fetchall()
            return [Livro(**result) for result in results]

livro_service = LivroService()
