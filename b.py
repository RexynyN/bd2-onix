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




dvds = pd.concat([pd.read_csv(path_join(DVD_PATH, file), dtype=str, sep=",") for file in os.listdir(DVD_PATH)], ignore_index=True)
dvds['data_lancamento'] = dvds['data_lancamento'].astype(str)
leng = dvds.shape[0]
for idx, row in dvds.iterrows():
    try:
        print(f"DVDs: {idx}/{leng}")
        biblios = random.randint(1, 5)
        for id_biblioteca in random.sample(biblio_ids, biblios):
            cursor.execute("""
                INSERT INTO Midia (tipo_midia, condicao, id_biblioteca)
                VALUES (%s, %s, %s)
                RETURNING id_midia;
            """, ('dvd', random.choice(['NOVO', 'SEMINOVO', 'DESGASTADO', 'DANIFICADO', 'ARQUIVADO']), id_biblioteca))

            id_midia = cursor.fetchone()[0]

            try: 
                duracao = int(row['duracao']) 
                if duracao > 5000:
                    duracao = 120
            except ValueError:
                duracao = 120

            try:
                # print(row['data_lancamento'])
                lancamento = dt.strptime(row['data_lancamento'], "%Y-%m-%d").date()
            except Exception as e:
                lancamento= faker_br.date_between(start_date='-100y', end_date='today').strftime('%Y-%m-%d')


            # 2. Inserir em Livros (com o mesmo id)
            cursor.execute("""
                INSERT INTO dvds (id_dvd, titulo, ISAN, duracao, distribuidora, data_lancamento)
                VALUES (%s, %s, %s, %s, %s, %s);
            """, (id_midia, row['titulo'], str(row['ISAN']).replace('-', ''), duracao , row['distribuidora'], lancamento))
    except Exception as e:
        print(e)
        continue
        
conn.commit()
del dvds