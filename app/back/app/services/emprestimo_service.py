from typing import List, Optional
from datetime import date, timedelta
from app.database.connection import get_db_cursor
from app.schemas.schemas import EmprestimoCreate, EmprestimoUpdate, Emprestimo, EmprestimoCompleto, RelatorioEmprestimos
from fastapi import HTTPException

class EmprestimoService:
    
    def create_emprestimo(self, emprestimo: EmprestimoCreate) -> Emprestimo:
        with get_db_cursor() as cursor:
            # Verificar se o item está disponível
            cursor.execute('''
                SELECT COUNT(*) FROM Emprestimo 
                WHERE id_estoque = %s AND data_devolucao IS NULL
            ''', (emprestimo.id_estoque,))
            
            if cursor.fetchone()['count'] > 0:
                raise HTTPException(
                    status_code=400,
                    detail="Item já está emprestado"
                )
            
            # Verificar se o usuário existe
            cursor.execute("SELECT id_usuario FROM Usuario WHERE id_usuario = %s", (emprestimo.id_usuario,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Usuário não encontrado")
            
            # Verificar se o estoque existe
            cursor.execute("SELECT id_estoque FROM Estoque WHERE id_estoque = %s", (emprestimo.id_estoque,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Item de estoque não encontrado")
            
            # Definir data de devolução padrão (15 dias)
            data_devolucao_prevista = emprestimo.data_devolucao_prevista or (emprestimo.data_emprestimo + timedelta(days=15))
            
            query = '''
                INSERT INTO Emprestimo (data_emprestimo, data_devolucao_prevista, id_estoque, id_usuario)
                VALUES (%s, %s, %s, %s)
                RETURNING id_emprestimo, data_emprestimo, data_devolucao_prevista, data_devolucao, id_estoque, id_usuario
            '''
            cursor.execute(query, (
                emprestimo.data_emprestimo,
                data_devolucao_prevista,
                emprestimo.id_estoque,
                emprestimo.id_usuario
            ))
            result = cursor.fetchone()
            return Emprestimo(**result)
    
    def get_emprestimo(self, id_emprestimo: int) -> Optional[Emprestimo]:
        with get_db_cursor() as cursor:
            query = "SELECT * FROM Emprestimo WHERE id_emprestimo = %s"
            cursor.execute(query, (id_emprestimo,))
            result = cursor.fetchone()
            if result:
                return Emprestimo(**result)
            return None
    
    def get_emprestimos(self, skip: int = 0, limit: int = 100) -> List[Emprestimo]:
        with get_db_cursor() as cursor:
            query = "SELECT * FROM Emprestimo ORDER BY id_emprestimo OFFSET %s LIMIT %s"
            cursor.execute(query, (skip, limit))
            results = cursor.fetchall()
            return [Emprestimo(**result) for result in results]
    
    def devolver_item(self, id_emprestimo: int, data_devolucao: date = None) -> Optional[Emprestimo]:
        if data_devolucao is None:
            data_devolucao = date.today()
        
        with get_db_cursor() as cursor:
            query = '''
                UPDATE Emprestimo 
                SET data_devolucao = %s
                WHERE id_emprestimo = %s AND data_devolucao IS NULL
                RETURNING id_emprestimo, data_emprestimo, data_devolucao_prevista, data_devolucao, id_estoque, id_usuario
            '''
            cursor.execute(query, (data_devolucao, id_emprestimo))
            result = cursor.fetchone()
            if result:
                return Emprestimo(**result)
            else:
                raise HTTPException(
                    status_code=400, 
                    detail="Empréstimo não encontrado ou já devolvido"
                )
    
    def get_emprestimos_em_andamento(self) -> List[EmprestimoCompleto]:
        with get_db_cursor() as cursor:
            query = '''
                SELECT 
                    e.id_emprestimo,
                    e.data_emprestimo,
                    e.data_devolucao_prevista,
                    e.data_devolucao,
                    u.id_usuario, u.nome as usuario_nome, u.email, u.endereco, u.telefone,
                    COALESCE(l.titulo, r.titulo, d.titulo, a.titulo) as item_titulo,
                    t.tipo_midia,
                    b.nome as biblioteca_nome
                FROM Emprestimo e
                INNER JOIN Usuario u ON e.id_usuario = u.id_usuario
                INNER JOIN Estoque est ON e.id_estoque = est.id_estoque
                INNER JOIN Titulo t ON est.id_titulo = t.id_titulo
                INNER JOIN Biblioteca b ON est.id_biblioteca = b.id_biblioteca
                LEFT JOIN Livros l ON t.id_titulo = l.id_livro
                LEFT JOIN Revistas r ON t.id_titulo = r.id_revista
                LEFT JOIN DVDs d ON t.id_titulo = d.id_dvd
                LEFT JOIN Artigos a ON t.id_titulo = a.id_artigo
                WHERE e.data_devolucao IS NULL
                ORDER BY e.data_emprestimo DESC
            '''
            cursor.execute(query)
            results = cursor.fetchall()
            
            emprestimos = []
            for result in results:
                emprestimos.append(EmprestimoCompleto(
                    id_emprestimo=result['id_emprestimo'],
                    data_emprestimo=result['data_emprestimo'],
                    data_devolucao_prevista=result['data_devolucao_prevista'],
                    data_devolucao=result['data_devolucao'],
                    usuario={
                        'id_usuario': result['id_usuario'],
                        'nome': result['usuario_nome'],
                        'email': result['email'],
                        'endereco': result['endereco'],
                        'telefone': result['telefone']
                    },
                    item_titulo=result['item_titulo'],
                    tipo_midia=result['tipo_midia'],
                    biblioteca=result['biblioteca_nome']
                ))
            return emprestimos
    
    def get_emprestimos_vencidos(self) -> List[EmprestimoCompleto]:
        with get_db_cursor() as cursor:
            query = '''
                SELECT 
                    e.id_emprestimo,
                    e.data_emprestimo,
                    e.data_devolucao_prevista,
                    e.data_devolucao,
                    u.id_usuario, u.nome as usuario_nome, u.email, u.endereco, u.telefone,
                    COALESCE(l.titulo, r.titulo, d.titulo, a.titulo) as item_titulo,
                    t.tipo_midia,
                    b.nome as biblioteca_nome
                FROM Emprestimo e
                INNER JOIN Usuario u ON e.id_usuario = u.id_usuario
                INNER JOIN Estoque est ON e.id_estoque = est.id_estoque
                INNER JOIN Titulo t ON est.id_titulo = t.id_titulo
                INNER JOIN Biblioteca b ON est.id_biblioteca = b.id_biblioteca
                LEFT JOIN Livros l ON t.id_titulo = l.id_livro
                LEFT JOIN Revistas r ON t.id_titulo = r.id_revista
                LEFT JOIN DVDs d ON t.id_titulo = d.id_dvd
                LEFT JOIN Artigos a ON t.id_titulo = a.id_artigo
                WHERE e.data_devolucao IS NULL AND e.data_devolucao_prevista < %s
                ORDER BY e.data_devolucao_prevista ASC
            '''
            cursor.execute(query, (date.today(),))
            results = cursor.fetchall()
            
            emprestimos = []
            for result in results:
                emprestimos.append(EmprestimoCompleto(
                    id_emprestimo=result['id_emprestimo'],
                    data_emprestimo=result['data_emprestimo'],
                    data_devolucao_prevista=result['data_devolucao_prevista'],
                    data_devolucao=result['data_devolucao'],
                    usuario={
                        'id_usuario': result['id_usuario'],
                        'nome': result['usuario_nome'],
                        'email': result['email'],
                        'endereco': result['endereco'],
                        'telefone': result['telefone']
                    },
                    item_titulo=result['item_titulo'],
                    tipo_midia=result['tipo_midia'],
                    biblioteca=result['biblioteca_nome']
                ))
            return emprestimos
    
    def get_relatorio_emprestimos(self) -> RelatorioEmprestimos:
        with get_db_cursor() as cursor:
            # Total de empréstimos
            cursor.execute("SELECT COUNT(*) FROM Emprestimo")
            total_emprestimos = cursor.fetchone()['count']
            
            # Empréstimos em andamento
            cursor.execute("SELECT COUNT(*) FROM Emprestimo WHERE data_devolucao IS NULL")
            emprestimos_em_andamento = cursor.fetchone()['count']
            
            # Empréstimos vencidos
            cursor.execute(
                "SELECT COUNT(*) FROM Emprestimo WHERE data_devolucao IS NULL AND data_devolucao_prevista < %s",
                (date.today(),)
            )
            emprestimos_vencidos = cursor.fetchone()['count']
            
            # Empréstimos devolvidos
            cursor.execute("SELECT COUNT(*) FROM Emprestimo WHERE data_devolucao IS NOT NULL")
            emprestimos_devolvidos = cursor.fetchone()['count']
            
            return RelatorioEmprestimos(
                total_emprestimos=total_emprestimos,
                emprestimos_em_andamento=emprestimos_em_andamento,
                emprestimos_vencidos=emprestimos_vencidos,
                emprestimos_devolvidos=emprestimos_devolvidos
            )

emprestimo_service = EmprestimoService()
