import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
from faker import Faker
import ast
import random

fake = Faker('pt_BR')

DB_CONFIG = {
    'host': 'localhost',
    'dbname': 'onixlibrary',
    'user': 'super_user',
    'password': 'carimboatrasado',
    'port': 5432
}

def conectar_db():
    print("Conectando ao banco de dados...")
    return psycopg2.connect(**DB_CONFIG)

def ler_csv(caminho_csv, header):
    print(f"Lendo arquivo CSV: {caminho_csv}")
    df = pd.read_csv(caminho_csv)
    if not set(header).issubset(df.columns):
        raise ValueError(f"Header inválido. Esperado: {header}")
    return df

def get_or_create_autor(conn, nome):
    with conn.cursor() as cur:
        cur.execute("SELECT id_autor FROM Autores WHERE nome = %s", (nome,))
        res = cur.fetchone()
        if res:
            return res[0]
        nascimento = fake.date_of_birth(minimum_age=20, maximum_age=80)
        falecimento = fake.date_between(start_date='-30y') if random.random() < 0.3 else None
        cur.execute(
            "INSERT INTO Autores (nome, data_nascimento, data_falecimento) VALUES (%s, %s, %s) RETURNING id_autor",
            (nome, nascimento, falecimento)
        )
        return cur.fetchone()[0]

def processar_autores(conn, caminho_csv):
    print("Processando autores...")
    df = ler_csv(caminho_csv, ["author_id", "author_name"])
    dados = df[['author_id', 'author_name']].astype(str).to_records(index=False)
    with conn.cursor() as cur:
        execute_batch(cur,
            "INSERT INTO Autores (id_autor, nome) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            dados
        )
    conn.commit()
    print("Autores processados com sucesso.")

def processar_livros(conn, caminho_csv):
    print("Processando livros...")
    df = ler_csv(caminho_csv, ['id','title','authors_ids','isbn13','lang','publication-date','pages','publisher']).astype(str)
    livros = []
    autorias = []
    with conn.cursor() as cur:
        for _, row in df.iterrows():
            # Inserir na tabela Titulo e obter o id gerado
            cur.execute(
                "INSERT INTO Titulo (tipo_midia) VALUES (%s) RETURNING id_titulo",
                ('livro',)
            )
            id_titulo = cur.fetchone()[0]
            # Adicionar dados do livro
            livros.append((id_titulo, row['title'], row['isbn13'], random.randint(1, 2000), row['publisher'], fake.date_between(start_date='-100y', end_date='-1y')))
            # Adicionar autorias
            try: 
                authors_ids = ast.literal_eval(row['authors_ids'])
            except: 
                authors_ids = [random.randint(1, 10000)]  # Fallback caso não seja uma lista válida

            for author_id in authors_ids:
                autorias.append((author_id, id_titulo))
        # Inserir livros
        execute_batch(cur,
            """INSERT INTO Livros (id_livro, titulo, ISBN, numero_paginas, editora, data_publicacao)
               VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING""",
            livros
        )
        # Inserir autorias
        execute_batch(cur,
            "INSERT INTO Autorias (id_autor, id_titulo) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            autorias
        )
    conn.commit()
    print("Livros processados com sucesso.")

def processar_revistas(conn, caminho_csv):
    print(f"Processando revista: {caminho_csv}...")
    df = ler_csv(caminho_csv, ['titulo','autores','periodicidade','data_publicacao','editora','ISSN']).astype(str)
    revistas = []
    autorias = []
    with conn.cursor() as cur:
        for _, row in df.iterrows():
            # Inserir na tabela Titulo e obter o id gerado
            cur.execute(
                "INSERT INTO Titulo (tipo_midia) VALUES (%s) RETURNING id_titulo",
                ('revista',)
            )
            id_titulo = cur.fetchone()[0]
            # Adicionar dados da revista
            revistas.append((id_titulo, row['titulo'], row['ISSN'], row['periodicidade'], row['editora'], fake.date_between(start_date='-59y', end_date='-1y')))
            # Adicionar autorias
            for autor in row['autores'].split('|'):
                autor_id = get_or_create_autor(conn, autor.strip())
                autorias.append((autor_id, id_titulo))
        # Inserir revistas
        execute_batch(cur,
            """INSERT INTO Revistas (id_revista, titulo, ISSN, periodicidade, editora, data_publicacao)
               VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING""",
            revistas
        )
        # Inserir autorias
        execute_batch(cur,
            "INSERT INTO Autorias (id_autor, id_titulo) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            autorias
        )
    conn.commit()
    print(f"Revista {caminho_csv} processada com sucesso.")

def processar_artigos(conn, caminho_csv):
    print(f"Processando artigo: {caminho_csv}...")
    df = ler_csv(caminho_csv, ['titulo','DOI','publicadora','data_publicacao','autores']).astype(str)
    artigos = []
    autorias = []
    with conn.cursor() as cur:
        for _, row in df.iterrows():
            # Inserir na tabela Titulo e obter o id gerado
            cur.execute(
                "INSERT INTO Titulo (tipo_midia) VALUES (%s) RETURNING id_titulo",
                ('artigo',)
            )
            id_titulo = cur.fetchone()[0]
            # Adicionar dados do artigo
            artigos.append((id_titulo, row['titulo'], row['DOI'], row['publicadora'], fake.date_between(start_date='-59y', end_date='-1y')))
            # Adicionar autorias
            for autor in row['autores'].split('|'):
                autor_id = get_or_create_autor(conn, autor.strip())
                autorias.append((autor_id, id_titulo))
        # Inserir artigos
        execute_batch(cur,
            """INSERT INTO Artigos (id_artigo, titulo, DOI, publicadora, data_publicacao)
               VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING""",
            artigos
        )
        # Inserir autorias
        execute_batch(cur,
            "INSERT INTO Autorias (id_autor, id_titulo) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            autorias
        )
    conn.commit()
    print(f"Artigo {caminho_csv} processado com sucesso.")

def processar_dvds(conn, caminho_csv):
    print(f"Processando DVD: {caminho_csv}...")
    df = ler_csv(caminho_csv, ['titulo','ISAN','duracao','distribuidora','data_lancamento']).astype(str)
    dvds = []
    with conn.cursor() as cur:
        for _, row in df.iterrows():
            # Inserir na tabela Titulo e obter o id gerado
            cur.execute(
                "INSERT INTO Titulo (tipo_midia) VALUES (%s) RETURNING id_titulo",
                ('dvd',)
            )
            id_titulo = cur.fetchone()[0]

            try:
                duracao = int(float(float(row['duracao'])))
            except:
                duracao = random.randint(1, 400)  # Fallback caso a duração não seja válida
            # Adicionar dados do DVD
            dvds.append((id_titulo, row['titulo'], row['ISAN'], duracao, row['distribuidora'], fake.date_between(start_date='-59y', end_date='-1y')))
        # Inserir DVDs
        execute_batch(cur,
            """INSERT INTO DVDs (id_dvd, titulo, ISAN, duracao, distribuidora, data_lancamento)
               VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING""",
            dvds
        )
    conn.commit()
    print(f"DVD {caminho_csv} processado com sucesso.")

def gerar_dados_fake(conn):
    print("Gerando dados fake...")
    # Usuários
    usuarios = [(fake.name(), fake.email(), fake.address().replace('\n', ', '), fake.phone_number()) for _ in range(55715)]
    with conn.cursor() as cur:
        execute_batch(cur,
            "INSERT INTO Usuario (nome, email, endereco, telefone) VALUES (%s, %s, %s, %s)",
            usuarios
        )
    print("Usuários gerados.")
    # Bibliotecas
    fake_libraries = [
        "Biblioteca Onix Jaçanã",
        "Biblioteca Onix Tatuapé",
        "Biblioteca Onix Vila Prudente",
        "Biblioteca Onix Paulista",
        "Biblioteca Onix Santana",
        "Biblioteca Onix Santo André",
        "Biblioteca Onix São Bernardo do Campo",
        "Biblioteca Onix São Caetano do Sul",
        "Biblioteca Onix São José dos Campos",
        "Biblioteca Onix Higienópolis",
        "Biblioteca Onix Vila Madalena",
    ]
    fake_library_addresses = [
        "Rua das Palmeiras, 123 – Jaçanã, São Paulo – SP, 02260-000",
        "Av. Álvaro Ramos, 456 – Tatuapé, São Paulo – SP, 03310-000",
        "Rua José Zappi, 789 – Vila Prudente, São Paulo – SP, 03138-000",
        "Av. Paulista, 1001 – Bela Vista, São Paulo – SP, 01311-100",
        "Rua Voluntários da Pátria, 321 – Santana, São Paulo – SP, 02010-000",
        "Rua General Glicério, 159 – Centro, Santo André – SP, 09015-330",
        "Av. Faria Lima, 987 – Centro, São Bernardo do Campo – SP, 09710-000",
        "Rua Alegre, 202 – Santa Paula, São Caetano do Sul – SP, 09560-300",
        "Av. Adhemar de Barros, 1550 – Jardim São Dimas, São José dos Campos – SP, 12245-010",
        "Rua Itacolomi, 415 – Higienópolis, São Paulo – SP, 01239-000",
        "Rua Harmonia, 678 – Vila Madalena, São Paulo – SP, 05435-001",
    ]
    bibliotecas = [[bib, add] for bib, add in zip(fake_libraries, fake_library_addresses)]
    with conn.cursor() as cur:
        execute_batch(cur,
            "INSERT INTO Biblioteca (nome, endereco) VALUES (%s, %s)",
            bibliotecas
        )
    print("Bibliotecas geradas.")
    # Estoque
    with conn.cursor() as cur:
        cur.execute("SELECT id_titulo FROM Titulo") 
        titulos = [row[0] for row in cur.fetchall()]
        cur.execute("SELECT id_biblioteca FROM Biblioteca")
        bibliotecas_ids = [row[0] for row in cur.fetchall()]
        for _ in range(313):
            
            estoque = [(
                random.choice(['novo', 'usado', 'danificado']),
                random.choice(titulos),
                random.choice(bibliotecas_ids)
            ) for _ in range(20000)]
            execute_batch(cur,
                "INSERT INTO Estoque (condicao, id_titulo, id_biblioteca) VALUES (%s, %s, %s)",
                estoque
            )
    print("Estoque gerado.")
    # Empréstimos
    
    with conn.cursor() as cur:
        cur.execute("SELECT id_estoque FROM Estoque")
        estoques = [row[0] for row in cur.fetchall()]
        cur.execute("SELECT id_usuario FROM Usuario")
        usuarios_ids = [row[0] for row in cur.fetchall()]
        for _ in range(900):
            emprestimos = []
            for _ in range(4017):
                data_emprestimo = fake.date_between(start_date='-2y', end_date='today')
                data_prevista = fake.date_between(start_date=data_emprestimo, end_date='+30d')
                data_devolucao = data_prevista if random.random() > 0.2 else None
                emprestimos.append((
                    data_emprestimo, data_prevista, data_devolucao,
                    random.choice(estoques), random.choice(usuarios_ids)
                ))
            execute_batch(cur,
                """INSERT INTO Emprestimo (data_emprestimo, data_devolucao_prevista, data_devolucao, id_estoque, id_usuario)
                VALUES (%s, %s, %s, %s, %s)""",
                emprestimos
            )
    print("Empréstimos gerados.")
    # Penalizações
    penalizacao_range = (4017 * 900) * 0.12  
    with conn.cursor() as cur:
        cur.execute("SELECT id_emprestimo, id_usuario FROM Emprestimo")
        emprestimos = cur.fetchall()
        for _ in range(int(penalizacao_range/1000)):
            penalizacoes = []
            for _ in range(1000):
                emp = random.choice(emprestimos)
                penalizacoes.append((
                    fake.sentence(), fake.date_between(start_date='today', end_date='+60d'),
                    emp[1], emp[0]
                ))
            execute_batch(cur,
                """INSERT INTO Penalizacao (descricao, Final_penalizacao, id_usuario, id_emprestimo)
                VALUES (%s, %s, %s, %s)""",
                penalizacoes
            )
    conn.commit()
    print("Penalizações geradas.")

def criar_indices(conn):
    print("Criando índices...")
    with conn.cursor() as cur:
        cur.execute('CREATE INDEX IF NOT EXISTS idx_autorias_titulo ON Autorias(id_titulo)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_estoque_biblioteca ON Estoque(id_biblioteca)')
    conn.commit()
    print("Índices criados com sucesso.")

if __name__ == "__main__":
    print("Iniciando processamento...")
    conn = conectar_db()
    try:
        # processar_autores(conn, 'livros/authors.csv')
        # processar_livros(conn, 'livros/treated/data.csv')

        # for file in os.listdir("revistas/treated"):
        #     processar_revistas(conn, f"revistas/treated/{file}")
    
        # for file in os.listdir("artigos/treated"):
        #     processar_artigos(conn, f"artigos/treated/{file}")

        for file in os.listdir("dvds/treated"):
            processar_dvds(conn, f"dvds/treated/{file}")
        gerar_dados_fake(conn)
        criar_indices(conn)
    finally:
        conn.close()
        print("Processamento concluído.")
