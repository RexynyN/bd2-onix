import psycopg2

# Configurações de conexão
conn = psycopg2.connect(
    dbname="onixlibrary",
    user="super_user",
    password="carimboatrasado",
    host="localhost",
    port="5432"
)

print("Conexão estabelecida com sucesso!")
print(conn)

# Criando um cursor
cur = conn.cursor()

# Query de inserção
query = """
INSERT INTO sua_tabela (coluna1, coluna2, coluna3)
VALUES (%s, %s, %s)
"""
valores = ('valor1', 'valor2', 'valor3')

# Executando a query
cur.execute(query, valores)

# Confirmando a transação
conn.commit()

print("Dados inseridos com sucesso!")

# Fechando o cursor
cur.close()
conn.close()
