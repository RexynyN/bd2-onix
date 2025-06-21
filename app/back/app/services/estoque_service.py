from typing import List, Optional
from app.database.connection import get_db_cursor
from app.schemas.schemas import EstoqueCreate, EstoqueUpdate, Estoque, DisponibilidadeItem, TituloSearch
from fastapi import HTTPException

class EstoqueService:
    
    def create_estoque(self, estoque: EstoqueCreate) -> Estoque:
        with get_db_cursor() as cursor:
            # Verificar se o título existe
            cursor.execute("SELECT id_titulo FROM Titulo WHERE id_titulo = %s", (estoque.id_titulo,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Título não encontrado")
            
            # Verificar se a biblioteca existe
            cursor.execute("SELECT id_biblioteca FROM Biblioteca WHERE id_biblioteca = %s", (estoque.id_biblioteca,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Biblioteca não encontrada")
            
            query = '''
                INSERT INTO Estoque (condicao, id_titulo, id_biblioteca)
                VALUES (%s, %s, %s)
                RETURNING id_estoque, condicao, id_titulo, id_biblioteca
            '''
            cursor.execute(query, (
                estoque.condicao,
                estoque.id_titulo,
                estoque.id_biblioteca
            ))
            result = cursor.fetchone()
            return Estoque(**result)
    
    def get_estoque(self, id_estoque: int) -> Optional[Estoque]:
        with get_db_cursor() as cursor:
            query = "SELECT * FROM Estoque WHERE id_estoque = %s"
            cursor.execute(query, (id_estoque,))
            result = cursor.fetchone()
            if result:
                return Estoque(**result)
            return None
    
    def get_estoques(self, skip: int = 0, limit: int = 100) -> List[Estoque]:
        with get_db_cursor() as cursor:
            query = "SELECT * FROM Estoque ORDER BY id_estoque OFFSET %s LIMIT %s"
            cursor.execute(query, (skip, limit))
            results = cursor.fetchall()
            return [Estoque(**result) for result in results]
    
    def get_estoque_por_biblioteca(self, id_biblioteca: int, skip: int = 0, limit: int = 100) -> List[Estoque]:
        with get_db_cursor() as cursor:
            query = "SELECT * FROM Estoque WHERE id_biblioteca = %s ORDER BY id_estoque OFFSET %s LIMIT %s"
            cursor.execute(query, (id_biblioteca, skip, limit))
            results = cursor.fetchall()
            return [Estoque(**result) for result in results]
    
    def get_disponibilidade_item(self, id_titulo: int) -> Optional[DisponibilidadeItem]:
        with get_db_cursor() as cursor:
            # Buscar informações do título
            cursor.execute('''
                SELECT t.tipo_midia,
                       COALESCE(l.titulo, r.titulo, d.titulo, a.titulo) as titulo
                FROM Titulo t
                LEFT JOIN Livros l ON t.id_titulo = l.id_livro
                LEFT JOIN Revistas r ON t.id_titulo = r.id_revista
                LEFT JOIN DVDs d ON t.id_titulo = d.id_dvd
                LEFT JOIN Artigos a ON t.id_titulo = a.id_artigo
                WHERE t.id_titulo = %s
            ''', (id_titulo,))
            
            titulo_info = cursor.fetchone()
            if not titulo_info:
                return None
            
            # Contar exemplares
            cursor.execute('''
                SELECT COUNT(*) as total_exemplares
                FROM Estoque 
                WHERE id_titulo = %s
            ''', (id_titulo,))
            total_exemplares = cursor.fetchone()['total_exemplares']
            
            # Contar exemplares emprestados
            cursor.execute('''
                SELECT COUNT(*) as emprestados
                FROM Estoque e
                INNER JOIN Emprestimo emp ON e.id_estoque = emp.id_estoque
                WHERE e.id_titulo = %s AND emp.data_devolucao IS NULL
            ''', (id_titulo,))
            exemplares_emprestados = cursor.fetchone()['emprestados']
            
            exemplares_disponiveis = total_exemplares - exemplares_emprestados
            
            return DisponibilidadeItem(
                id_titulo=id_titulo,
                titulo=titulo_info['titulo'],
                tipo_midia=titulo_info['tipo_midia'],
                total_exemplares=total_exemplares,
                exemplares_disponiveis=exemplares_disponiveis,
                exemplares_emprestados=exemplares_emprestados
            )
    
    def update_estoque(self, id_estoque: int, estoque: EstoqueUpdate) -> Optional[Estoque]:
        fields = []
        values = []
        
        if estoque.condicao is not None:
            fields.append("condicao = %s")
            values.append(estoque.condicao)
        if estoque.id_titulo is not None:
            fields.append("id_titulo = %s")
            values.append(estoque.id_titulo)
        if estoque.id_biblioteca is not None:
            fields.append("id_biblioteca = %s")
            values.append(estoque.id_biblioteca)
        
        if not fields:
            return self.get_estoque(id_estoque)
        
        values.append(id_estoque)
        
        with get_db_cursor() as cursor:
            query = f'''
                UPDATE Estoque 
                SET {", ".join(fields)}
                WHERE id_estoque = %s
                RETURNING id_estoque, condicao, id_titulo, id_biblioteca
            '''
            cursor.execute(query, values)
            result = cursor.fetchone()
            if result:
                return Estoque(**result)
            return None
    
    def delete_estoque(self, id_estoque: int) -> bool:
        with get_db_cursor() as cursor:
            # Verificar se há empréstimos associados
            cursor.execute("SELECT COUNT(*) FROM Emprestimo WHERE id_estoque = %s", (id_estoque,))
            count = cursor.fetchone()['count']
            
            if count > 0:
                raise HTTPException(
                    status_code=400,
                    detail="Não é possível excluir item do estoque com empréstimos associados"
                )
            
            query = "DELETE FROM Estoque WHERE id_estoque = %s"
            cursor.execute(query, (id_estoque,))
            return cursor.rowcount > 0
        
    def search_from_title(self, search_query: str) -> List[Estoque]:
        with get_db_cursor() as cursor:
            search_query = f"%{search_query}%"
            query = '''
                SELECT 
                    t.id_titulo,
                    t.tipo_midia,
                    COALESCE(l.titulo, r.titulo, d.titulo, a.titulo) as titulo
                FROM titulo AS t
                LEFT JOIN Livros AS l ON t.id_titulo = l.id_livro
                LEFT JOIN Revistas AS r ON t.id_titulo = r.id_revista
                LEFT JOIN DVDs AS d ON t.id_titulo = d.id_dvd
                LEFT JOIN Artigos AS a ON t.id_titulo = a.id_artigo
                WHERE a.titulo ILIKE %s
                    OR r.titulo ILIKE %s
                    OR l.titulo ILIKE %s
                    OR d.titulo ILIKE %s
                ORDER BY COALESCE(l.titulo, r.titulo, d.titulo, a.titulo) ASC 
                LIMIT 200; 
            '''
            cursor.execute(query, tuple([search_query for _ in range(4)]))
            results = cursor.fetchall()
            return [TituloSearch(**result) for result in results]

    def search_from_estoque(self, search_query: str) -> List[Estoque]:
        with get_db_cursor() as cursor:
            search_query = f"%{search_query}%"
            query = '''
                SELECT 
                    e.id_estoque,
                    e.condicao,
                    e.id_titulo,
                    e.id_biblioteca
                FROM Estoque AS e
                JOIN Titulo AS t ON e.id_titulo = t.id_titulo
                WHERE t.titulo ILIKE %s
                ORDER BY e.id_estoque ASC 
                LIMIT 200; 
            '''
            cursor.execute(query, (search_query,))
            results = cursor.fetchall()
            return [Estoque(**result) for result in results]

estoque_service = EstoqueService()
