import os
import re
import ast
import random
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
from faker import Faker

fake = Faker('pt_BR')

# Configuração de conexão (substituir com suas credenciais)
DB_CONFIG = {
    'host': 'localhost',
    'dbname': 'meubanco',
    'user': 'usuario',
    'password': 'senha',
    'port': 5432
}

# ======== FUNÇÕES PRINCIPAIS ========

def conectar_db():
    """Estabelece conexão com o banco PostgreSQL"""
    return psycopg2.connect(**DB_CONFIG)

def ler_csv(caminho_csv, header):
    """Lê CSV e valida estrutura"""
    df = pd.read_csv(caminho_csv)
    if not set(header).issubset(df.columns):
        raise ValueError(f"Header inválido. Esperado: {header}")
    return df

def processar_autores(conn, caminho_csv):
    """Processa CSV de Autores"""
    df = ler_csv(caminho_csv, ["author_id", "author_name"])
    dados = df[['author_id', 'author_name']].to_records(index=False)
    
    with conn.cursor() as cur:
        execute_batch(cur,
            "INSERT INTO Autores (id_autor, nome) VALUES (%s, %s)",
            dados
        )
    conn.commit()

def processar_livros(conn, caminho_csv):
    """Processa CSV de Livros com verificação de autores"""
    df = ler_csv(caminho_csv, ['id','title','authors_ids','isbn13','lang','publication-date','pages','publisher'])
    
    # Inserir títulos
    titulos = [(row['id'], 'livro') for _, row in df.iterrows()]
    with conn.cursor() as cur:
        execute_batch(cur,
            "INSERT INTO Titulo (id_titulo, tipo_midia) VALUES (%s, %s)",
            titulos
        )
    
    # Inserir livros
    livros = [(row['id'], row['title'], row['isbn13'], row['pages'], row['publisher'], row['publication-date']) 
              for _, row in df.iterrows()]
    with conn.cursor() as cur:
        execute_batch(cur,
            """INSERT INTO Livros (id_livro, titulo, ISBN, numero_paginas, editora, data_publicacao)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            livros
        )
    
    # Processar autorias
    autorias = []
    for _, row in df.iterrows():
        authors_ids = ast.literal_eval(row['authors_ids'])
        for author_id in authors_ids:
            autorias.append((author_id, row['id']))
    
    with conn.cursor() as cur:
        execute_batch(cur,
            "INSERT INTO Autorias (id_autor, id_titulo) VALUES (%s, %s)",
            autorias
        )
    conn.commit()

def processar_midia_com_autores(conn, caminho_csv, tipo_midia):
    """Processa Revistas/Artigos com autores em formato de texto"""
    df = ler_csv(caminho_csv, ['titulo','autores','data_publicacao','editora'] + 
                 (['ISSN'] if tipo_midia == 'revista' else ['DOI']))
    
    # Inserir títulos e obter IDs gerados
    with conn.cursor() as cur:
        titulos = [(tipo_midia,) for _ in range(len(df))]
        cur.executemany(
            "INSERT INTO Titulo (tipo_midia) VALUES (%s) RETURNING id_titulo",
            titulos
        )
        titulo_ids = [row[0] for row in cur.fetchall()]
    
    # Inserir registros específicos
    tabela = 'Revistas' if tipo_midia == 'revista' else 'Artigos'
    colunas = ['ISSN', 'periodicidade'] if tipo_midia == 'revista' else ['DOI', 'publicadora']
    
    registros = []
    for i, row in df.iterrows():
        if tipo_midia == 'revista':
            registros.append((titulo_ids[i], row['titulo'], row['ISSN'], row['periodicidade'], 
                             row['editora'], row['data_publicacao']))
        else:
            registros.append((titulo_ids[i], row['titulo'], row['DOI'], row['publicadora'], 
                             row['data_publicacao']))
    
    with conn.cursor() as cur:
        if tipo_midia == 'revista':
            execute_batch(cur,
                """INSERT INTO Revistas (id_revista, titulo, ISSN, periodicidade, editora, data_publicacao)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                registros
            )
        else:
            execute_batch(cur,
                """INSERT INTO Artigos (id_artigo, titulo, DOI, publicadora, data_publicacao)
                   VALUES (%s, %s, %s, %s, %s)""",
                registros
            )
    
    # Processar autores
    autorias = []
    for i, row in df.iterrows():
        for autor in row['autores'].split('|'):
            autor_id = get_or_create_autor(conn, autor.strip())
            autorias.append((autor_id, titulo_ids[i]))
    
    with conn.cursor() as cur:
        execute_batch(cur,
            "INSERT INTO Autorias (id_autor, id_titulo) VALUES (%s, %s)",
            autorias
        )
    conn.commit()

# ======== FUNÇÕES AUXILIARES ========

def get_or_create_autor(conn, nome):
    """Obtém ou cria autor com dados fictícios"""
    with conn.cursor() as cur:
        cur.execute("SELECT id_autor FROM Autores WHERE nome = %s", (nome,))
        if result := cur.fetchone():
            return result[0]
        
        # Gerar dados fictícios para novo autor
        dados = (
            nome,
            fake.date_of_birth(minimum_age=20, maximum_age=80),
            fake.date_between(start_date='-30y') if random.random() < 0.3 else None
        )
        cur.execute(
            """INSERT INTO Autores (nome, data_nascimento, data_falecimento)
               VALUES (%s, %s, %s) RETURNING id_autor""",
            dados
        )
        return cur.fetchone()[0]

def gerar_dados_fake(conn):
    """Gera dados para tabelas sem CSV"""
    # Gerar usuários
    usuarios = []
    for _ in range(1000):
        usuarios.append((
            fake.name(),
            fake.email(),
            fake.address().replace('\n', ', '),
            fake.phone_number()
        ))
    
    with conn.cursor() as cur:
        execute_batch(cur,
            "INSERT INTO Usuario (nome, email, endereco, telefone) VALUES (%s, %s, %s, %s)",
            usuarios
        )
    
    # Gerar bibliotecas
    bibliotecas = [(fake.company(), fake.address()) for _ in range(50)]
    with conn.cursor() as cur:
        execute_batch(cur,
            "INSERT INTO Biblioteca (nome, endereco) VALUES (%s, %s)",
            bibliotecas
        )
    
    # Gerar estoque
    cur.execute("SELECT id_titulo FROM Titulo")
    titulos = [row[0] for row in cur.fetchall()]
    
    cur.execute("SELECT id_biblioteca FROM Biblioteca")
    bibliotecas_ids = [row[0] for row in cur.fetchall()]
    
    estoque = [(
        random.choice(['novo', 'usado', 'danificado']),
        random.choice(titulos),
        random.choice(bibliotecas_ids)
    ) for _ in range(5000)]
    
    execute_batch(cur,
        "INSERT INTO Estoque (condicao, id_titulo, id_biblioteca) VALUES (%s, %s, %s)",
        estoque
    )
    conn.commit()

def criar_indices(conn):
    """Cria índices para otimização"""
    with conn.cursor() as cur:
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_autorias_titulo 
            ON Autorias(id_titulo) INCLUDE (id_autor)
        ''')
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_estoque_biblioteca 
            ON Estoque(id_biblioteca) INCLUDE (id_titulo)
        ''')
    conn.commit()

# ======== EXECUÇÃO PRINCIPAL ========
if __name__ == "__main__":
    conn = conectar_db()
    
    try:
        # Processar CSVs fornecidos
        processar_autores(conn, 'autores.csv')
        processar_livros(conn, 'livros.csv')
        processar_midia_com_autores(conn, 'revistas.csv', 'revista')
        processar_midia_com_autores(conn, 'artigos.csv', 'artigo')
        
        # Gerar dados fictícios para outras tabelas
        gerar_dados_fake(conn)
        
        # Otimizações finais
        criar_indices(conn)
        
    finally:
        conn.close()
