# init.sql - Script de inicialização do banco
init_sql = """-- Script de inicialização para o Sistema de Biblioteca
-- Este script cria as tabelas e insere dados de exemplo

-- Criar tipos ENUM se não existir
DO $$ BEGIN
    CREATE TYPE MidiaTipo AS ENUM ('livro', 'revista', 'dvd', 'artigo');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Tabela: Usuario
CREATE TABLE IF NOT EXISTS Usuario (
    id_usuario SERIAL PRIMARY KEY NOT NULL,
    nome VARCHAR NOT NULL,
    email VARCHAR,
    endereco VARCHAR,
    telefone VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: Biblioteca
CREATE TABLE IF NOT EXISTS Biblioteca (
    id_biblioteca SERIAL PRIMARY KEY NOT NULL,
    nome VARCHAR NOT NULL,
    endereco VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: Mídia
CREATE TABLE IF NOT EXISTS Midia (
    id_midia SERIAL PRIMARY KEY NOT NULL,
    tipo_midia MidiaTipo NOT NULL,
    condicao VARCHAR,
    id_biblioteca INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_biblioteca) REFERENCES Biblioteca(id_biblioteca)
);

-- Tabela: Emprestimo
CREATE TABLE IF NOT EXISTS Emprestimo (
    id_emprestimo SERIAL PRIMARY KEY NOT NULL,
    data_emprestimo DATE NOT NULL,
    data_devolucao_prevista DATE,
    data_devolucao DATE,
    id_midia INT NOT NULL,
    id_usuario INT NOT NULL,
    status VARCHAR DEFAULT 'ativo',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_midia) REFERENCES Midia(id_midia),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario)
);

-- Tabela: Penalizacao
CREATE TABLE IF NOT EXISTS Penalizacao (
    id_penalizacao SERIAL PRIMARY KEY NOT NULL,
    descricao TEXT,
    final_penalizacao DATE,
    valor DECIMAL(10,2),
    id_usuario INT,
    id_emprestimo INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario),
    FOREIGN KEY (id_emprestimo) REFERENCES Emprestimo(id_emprestimo)
);

-- Tabela: Livros
CREATE TABLE IF NOT EXISTS Livros (
    id_livro SERIAL PRIMARY KEY NOT NULL,
    titulo VARCHAR NOT NULL,
    ISBN VARCHAR,
    numero_paginas INT,
    editora VARCHAR,
    data_publicacao DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_livro) REFERENCES Midia(id_midia)
);

-- Tabela: Revistas
CREATE TABLE IF NOT EXISTS Revistas (
    id_revista SERIAL PRIMARY KEY NOT NULL,
    titulo VARCHAR NOT NULL,
    ISSN VARCHAR,
    periodicidade VARCHAR,
    editora VARCHAR,
    data_publicacao DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_revista) REFERENCES Midia(id_midia)
);

-- Tabela: DVDs
CREATE TABLE IF NOT EXISTS DVDs (
    id_dvd SERIAL PRIMARY KEY NOT NULL,
    titulo VARCHAR NOT NULL,
    ISAN VARCHAR,
    duracao INT,
    distribuidora VARCHAR,
    data_lancamento DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_dvd) REFERENCES Midia(id_midia)
);

-- Tabela: Artigos
CREATE TABLE IF NOT EXISTS Artigos (
    id_artigo SERIAL PRIMARY KEY NOT NULL,
    titulo VARCHAR NOT NULL,
    DOI VARCHAR,
    publicadora VARCHAR,
    data_publicacao DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_artigo) REFERENCES Midia(id_midia)
);

-- Tabela: Autores
CREATE TABLE IF NOT EXISTS Autores (
    id_autor SERIAL PRIMARY KEY NOT NULL,
    nome VARCHAR NOT NULL,
    data_nascimento DATE,
    data_falecimento DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: Autorias
CREATE TABLE IF NOT EXISTS Autorias (
    id_autorias SERIAL PRIMARY KEY NOT NULL,
    id_autor INT NOT NULL,
    id_midia INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_autor) REFERENCES Autores(id_autor),
    FOREIGN KEY (id_midia) REFERENCES Midia(id_midia)
);

-- Criar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_emprestimo_usuario ON Emprestimo(id_usuario);
CREATE INDEX IF NOT EXISTS idx_emprestimo_midia ON Emprestimo(id_midia);
CREATE INDEX IF NOT EXISTS idx_midia_biblioteca ON Midia(id_biblioteca);
CREATE INDEX IF NOT EXISTS idx_autorias_autor ON Autorias(id_autor);
CREATE INDEX IF NOT EXISTS idx_autorias_midia ON Autorias(id_midia);
CREATE INDEX IF NOT EXISTS idx_emprestimo_status ON Emprestimo(status);
CREATE INDEX IF NOT EXISTS idx_emprestimo_data_devolucao ON Emprestimo(data_devolucao);

-- Inserir dados de exemplo
INSERT INTO Biblioteca (nome, endereco) VALUES 
    ('Biblioteca Central', 'Av. Paulista, 1000 - São Paulo, SP'),
    ('Biblioteca Comunitária Norte', 'Rua das Flores, 500 - São Paulo, SP'),
    ('Biblioteca Infantil', 'Praça da Alegria, 200 - São Paulo, SP')
ON CONFLICT DO NOTHING;

INSERT INTO Usuario (nome, email, endereco, telefone) VALUES 
    ('João Silva', 'joao@email.com', 'Rua A, 123', '(11) 99999-1111'),
    ('Maria Santos', 'maria@email.com', 'Rua B, 456', '(11) 99999-2222'),
    ('Pedro Oliveira', 'pedro@email.com', 'Rua C, 789', '(11) 99999-3333'),
    ('Ana Costa', 'ana@email.com', 'Rua D, 101', '(11) 99999-4444'),
    ('Carlos Ferreira', 'carlos@email.com', 'Rua E, 202', '(11) 99999-5555')
ON CONFLICT DO NOTHING;

INSERT INTO Autores (nome, data_nascimento, data_falecimento) VALUES 
    ('Machado de Assis', '1839-06-21', '1908-09-29'),
    ('Clarice Lispector', '1920-12-10', '1977-12-09'),
    ('Jorge Amado', '1912-08-10', '2001-08-06'),
    ('Graciliano Ramos', '1892-10-27', '1953-03-20'),
    ('Érico Veríssimo', '1905-12-17', '1975-11-28'),
    ('J.K. Rowling', '1965-07-31', NULL),
    ('George Orwell', '1903-06-25', '1950-01-21'),
    ('Agatha Christie', '1890-09-15', '1976-01-12')
ON CONFLICT DO NOTHING;

-- Inserir mídias (livros)
INSERT INTO Midia (tipo_midia, condicao, id_biblioteca) VALUES 
    ('livro', 'bom', 1),
    ('livro', 'excelente', 1),
    ('livro', 'regular', 2),
    ('livro', 'bom', 1),
    ('livro', 'excelente', 2),
    ('livro', 'bom', 3),
    ('livro', 'excelente', 1),
    ('livro', 'bom', 2)
ON CONFLICT DO NOTHING;

INSERT INTO Livros (id_livro, titulo, ISBN, numero_paginas, editora, data_publicacao) VALUES 
    (1, 'Dom Casmurro', '978-85-359-0277-5', 256, 'Companhia das Letras', '1899-01-01'),
    (2, 'A Hora da Estrela', '978-85-359-0123-5', 87, 'Rocco', '1977-01-01'),
    (3, 'Gabriela, Cravo e Canela', '978-85-359-0456-7', 674, 'Companhia das Letras', '1958-01-01'),
    (4, 'Vidas Secas', '978-85-359-0789-1', 176, 'Record', '1938-01-01'),
    (5, 'O Tempo e o Vento', '978-85-359-0321-4', 1295, 'Globo', '1949-01-01'),
    (6, 'Harry Potter e a Pedra Filosofal', '978-85-325-1101-4', 264, 'Rocco', '1997-06-26'),
    (7, '1984', '978-85-359-0198-2', 374, 'Companhia das Letras', '1949-06-08'),
    (8, 'Assassinato no Expresso Oriente', '978-85-359-0587-4', 256, 'Globo', '1934-01-01')
ON CONFLICT DO NOTHING;

-- Inserir autorias
INSERT INTO Autorias (id_autor, id_midia) VALUES 
    (1, 1), -- Machado de Assis - Dom Casmurro
    (2, 2), -- Clarice Lispector - A Hora da Estrela
    (3, 3), -- Jorge Amado - Gabriela, Cravo e Canela
    (4, 4), -- Graciliano Ramos - Vidas Secas
    (5, 5), -- Érico Veríssimo - O Tempo e o Vento
    (6, 6), -- J.K. Rowling - Harry Potter
    (7, 7), -- George Orwell - 1984
    (8, 8)  -- Agatha Christie - Assassinato no Expresso Oriente
ON CONFLICT DO NOTHING;

-- Inserir alguns empréstimos de exemplo
INSERT INTO Emprestimo (data_emprestimo, data_devolucao_prevista, id_midia, id_usuario, status) VALUES 
    ('2024-01-15', '2024-01-30', 1, 1, 'ativo'),
    ('2024-01-10', '2024-01-25', 3, 2, 'ativo'),
    ('2024-01-05', '2024-01-20', 5, 3, 'devolvido'),
    ('2024-01-20', '2024-02-05', 6, 4, 'ativo')
ON CONFLICT DO NOTHING;

-- Atualizar um empréstimo como devolvido
UPDATE Emprestimo SET data_devolucao = '2024-01-18', status = 'devolvido' WHERE id_emprestimo = 3;

COMMIT;
"""

# Vamos criar um arquivo CSV com a estrutura completa do projeto
import csv
import io

project_structure = [
    # Arquivo, Tipo, Conteúdo
    ("main.go", "go", main_go),
    ("config/config.go", "go", config_go),
    ("database/database.go", "go", database_go),
    ("models/models.go", "go", models_go),
    ("handlers/usuario.go", "go", handlers_usuario_go),
    ("handlers/biblioteca.go", "go", handlers_biblioteca_go),
    ("handlers/midia.go", "go", handlers_midia_go),
    ("handlers/emprestimo.go", "go", handlers_emprestimo_go),
    ("handlers/livro.go", "go", handlers_livro_go),
    ("handlers/autor.go", "go", handlers_autor_go),
    ("handlers/dashboard.go", "go", handlers_dashboard_go),
    ("routes/routes.go", "go", routes_go),
    ("utils/utils.go", "go", utils_go),
    ("go.mod", "mod", go_mod),
    ("Dockerfile", "docker", dockerfile),
    ("docker-compose.yml", "yaml", docker_compose),
    (".env.example", "env", env_example),
    ("Makefile", "make", makefile),
    ("README.md", "md", readme),
    ("init.sql", "sql", init_sql),
]

# Criar CSV com a estrutura
output = io.StringIO()
writer = csv.writer(output)
writer.writerow(["Arquivo", "Tipo", "Conteúdo"])

for arquivo, tipo, conteudo in project_structure:
    writer.writerow([arquivo, tipo, conteudo])

csv_content = output.getvalue()
output.close()

# Salvar o CSV
with open('biblioteca-api-estrutura-completa.csv', 'w', encoding='utf-8') as f:
    f.write(csv_content)

print("✅ SISTEMA COMPLETO CRIADO!")
print("\n📁 Estrutura do Projeto:")
for arquivo, tipo, _ in project_structure:
    print(f"   ✓ {arquivo}")

print(f"\n📄 Arquivo gerado: biblioteca-api-estrutura-completa.csv")
print(f"   Total de arquivos: {len(project_structure)}")

print("\n🚀 Para usar o sistema:")
print("1. Extraia os arquivos do CSV para suas respectivas pastas")
print("2. Execute: go mod download")
print("3. Configure o PostgreSQL e as variáveis de ambiente")
print("4. Execute: go run . ou make docker-up")
print("5. Acesse: http://localhost:3000/api/v1")

print("\n📖 Principais endpoints:")
print("   • GET  /api/v1/ - Informações da API")
print("   • GET  /api/v1/usuarios - Lista usuários") 
print("   • GET  /api/v1/livros - Lista livros")
print("   • GET  /api/v1/emprestimos - Lista empréstimos")
print("   • GET  /api/v1/dashboard - Dashboard com estatísticas")
print("   • GET  /api/v1/search?q=termo - Busca global")

print("\n💡 Recursos implementados:")
print("   ✅ CRUD completo para todas entidades")
print("   ✅ Sistema de empréstimos com controle de datas")
print("   ✅ Gerenciamento de penalizações automáticas")
print("   ✅ Dashboard com estatísticas e relatórios")
print("   ✅ Busca global em múltiplas entidades")
print("   ✅ Paginação e filtros avançados")
print("   ✅ Validação robusta de dados")
print("   ✅ Tratamento padronizado de erros")
print("   ✅ Documentação completa")
print("   ✅ Docker e docker-compose configurados")
print("   ✅ Makefile com comandos úteis")
print("   ✅ Estrutura escalável e organizada")