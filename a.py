import pandas as pd
import os
import random
from faker import Faker
from os.path import join as path_join
from datetime import datetime as dt

Faker.seed(16042002)
faker_br = Faker('pt_BR')
faker_en = Faker('en_IN')
faker_jp = Faker('ja_JP')


CHUNKSIZE = 50000

LIVRO_PATH = "livros/treated/"
ARTIGO_PATH = "artigos/treated/"
DVD_PATH = "dvds/treated/"
REVISTA_PATH = "revistas/treated/"

import psycopg2
from psycopg2.extras import execute_values

# Conexão com o banco de dados PostgreSQL
conn = psycopg2.connect(
    dbname="onixlibrary",
    user="super_user",
    password="carimboatrasado",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Função para inserir dados no banco
def insert_data(table_name, data, columns):
    query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES %s"
    execute_values(cursor, query, data)
    conn.commit()

def generate_user():
    user = {}
    user['name'] = faker_br.name()
    user['email'] = faker_br.email()
    user['address'] = ' - '.join(faker_br.address().split('\n'))
    user['phone_number'] = faker_br.phone_number()
    return user

def generate_user_list():
    user = []
    user.append(faker_br.name())
    user.append(faker_br.email())
    user.append(' - '.join(faker_br.address().split('\n')))
    user.append(faker_br.phone_number())
    return user


biblio_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

author_df = pd.read_sql("SELECT * FROM autores", conn)




artigos = pd.concat([pd.read_csv(path_join(ARTIGO_PATH, file), dtype=str, sep=",") for file in os.listdir(ARTIGO_PATH)], ignore_index=True)
leng = artigos.shape[0]
for idx, row in artigos.iterrows():
    print(f"Artigos: {idx}/{leng}")
    biblios = random.randint(1, 2)
    try:
        for id_biblioteca in random.sample(biblio_ids, biblios):
            cursor.execute("""
                INSERT INTO Midia (tipo_midia, condicao, id_biblioteca)
                VALUES (%s, %s, %s)
                RETURNING id_midia;
            """, ('artigo', random.choice(['NOVO', 'SEMINOVO', 'DESGASTADO', 'DANIFICADO', 'ARQUIVADO']), id_biblioteca))

            id_midia = cursor.fetchone()[0]

            if not row['DOI']: 
                row['DOI'] = faker_en.isbn13()
            
            if not row['data_publicacao'] or row['data_publicacao'] == 'nan': 
                row['data_publicacao'] = faker_br.date_between(start_date='-60y', end_date='today').strftime('%Y-%m-%d')

            # 2. Inserir em Livros (com o mesmo id)
            cursor.execute("""
                INSERT INTO artigos (id_artigo, titulo, DOI, publicadora, data_publicacao)
                VALUES (%s, %s, %s, %s, %s);
            """, (id_midia, row['titulo'], row['DOI'].replace('-', '').replace('/', ''), row['publicadora'], row['data_publicacao']))

            for ath in row['autores'].split('|'):
                id_autor = int(author_df.loc[author_df['nome'].str.strip() == ath.strip()]['id_autor'].values[0])

                cursor.execute("""
                    INSERT INTO Autorias (id_autor, id_midia)
                    VALUES (%s, %s);
                """, (id_autor, id_midia))
    except Exception as e:
        print(e)
        continue
        

conn.commit()
del artigos