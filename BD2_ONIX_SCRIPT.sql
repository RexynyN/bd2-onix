CREATE DATABASE onixlibrary; -- Nome do Database 

CREATE USER super_user ENCRYPTED PASSWORD 'carimboatrasado'; -- Usuário e senha

-- Faz como admin
GRANT ALL ON DATABASE onixlibrary TO super_user; 
ALTER DATABASE onixlibrary OWNER TO super_user; 


-- O DLL FOI FEITO JOGANDO O MODELO LÓGICO NO CHATGPT


-- Tabela: Usuario
CREATE TABLE Usuario (
    id_usuario SERIAL PRIMARY KEY NOT NULL,
    nome VARCHAR NOT NULL,
	email VARCHAR,
    endereco VARCHAR,
    telefone VARCHAR
);

-- Tabela: Biblioteca
CREATE TABLE Biblioteca (
    id_biblioteca SERIAL PRIMARY KEY NOT NULL,
    nome VARCHAR NOT NULL,
    endereco VARCHAR
);
-- Tabela: Mídia
CREATE TYPE MidiaTipo AS ENUM ('livro', 'revista', 'dvd', 'artigo');
CREATE TABLE Titulo (
    id_titulo SERIAL PRIMARY KEY NOT NULL,
    tipo_midia MidiaTipo NOT NULL
);


CREATE TABLE Estoque(
    id_estoque SERIAL PRIMARY KEY NOT NULL,
    condicao VARCHAR,
    id_titulo INT,
    id_biblioteca INT,
    FOREIGN KEY (id_titulo) REFERENCES Titulo(id_titulo),
    FOREIGN KEY (id_biblioteca) REFERENCES Biblioteca(id_biblioteca)
);


-- Tabela: Emprestimo
CREATE TABLE Emprestimo (
    id_emprestimo SERIAL PRIMARY KEY NOT NULL,
    data_emprestimo DATE NOT NULL,
    data_devolucao_prevista DATE,
    data_devolucao DATE,
    id_estoque INT NOT NULL,
    id_usuario INT NOT NULL,
    FOREIGN KEY (id_estoque) REFERENCES Estoque(id_estoque),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario)
);

-- Tabela: Penalizacao
CREATE TABLE Penalizacao (
    id_penalizacao SERIAL PRIMARY KEY NOT NULL,
    descricao TEXT,
	Final_penalizacao DATE,
    id_usuario INT,
    id_emprestimo INT,
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario),
    FOREIGN KEY (id_emprestimo) REFERENCES Emprestimo(id_emprestimo)
);

-- Tabela: Livros
CREATE TABLE Livros (
    id_livro SERIAL PRIMARY KEY NOT NULL,
    titulo VARCHAR NOT NULL,
    ISBN VARCHAR,
    numero_paginas INT,
    editora VARCHAR,
    data_publicacao DATE,
    FOREIGN KEY (id_livro) REFERENCES Titulo(id_titulo)
);

-- Tabela: Revistas
CREATE TABLE Revistas (
    id_revista SERIAL PRIMARY KEY NOT NULL,
    titulo VARCHAR NOT NULL,
    ISSN VARCHAR,
    periodicidade VARCHAR,
    editora VARCHAR,
    data_publicacao DATE,
    FOREIGN KEY (id_revista) REFERENCES Titulo(id_titulo)
);

-- Tabela: DVDs
CREATE TABLE DVDs (
    id_dvd SERIAL PRIMARY KEY NOT NULL,
    titulo VARCHAR NOT NULL,
    ISAN VARCHAR,
    duracao INT,
    distribuidora VARCHAR,
    data_lancamento DATE,
    FOREIGN KEY (id_dvd) REFERENCES Titulo(id_titulo)
);

-- Tabela: Artigos
CREATE TABLE Artigos (
    id_artigo SERIAL PRIMARY KEY NOT NULL,
    titulo VARCHAR NOT NULL,
    DOI VARCHAR,
    publicadora VARCHAR,
    data_publicacao DATE,
    FOREIGN KEY (id_artigo) REFERENCES Titulo(id_titulo)
);

-- Tabela: Autores
CREATE TABLE Autores (
    id_autor SERIAL PRIMARY KEY NOT NULL,
    nome VARCHAR NOT NULL,
    data_nascimento DATE,
    data_falecimento DATE
);

-- Tabela: Autorias
CREATE TABLE Autorias (
    id_autorias SERIAL PRIMARY KEY NOT NULL,
    id_autor INT NOT NULL,
    id_titulo INT NOT NULL,
    FOREIGN KEY (id_autor) REFERENCES Autores(id_autor),
    FOREIGN KEY (id_titulo) REFERENCES Titulo(id_titulo)
);



-- Livros
CREATE INDEX idx_livros_isbn_hash ON Livros USING HASH (ISBN);
CREATE INDEX idx_livros_titulo_hash ON Livros USING HASH (titulo);


-- Revistas
CREATE INDEX idx_revistas_issn_hash ON Revistas USING HASH (ISSN);
CREATE INDEX idx_revistas_titulo_hash ON Revistas USING HASH (titulo);


-- DVDs
CREATE INDEX idx_dvds_isan_hash ON DVDs USING HASH (ISAN);
CREATE INDEX idx_dvds_titulo_hash ON DVDs USING HASH (titulo);


-- Artigos
CREATE INDEX idx_artigos_doi_hash ON Artigos USING HASH (DOI);
CREATE INDEX idx_artigos_titulo_hash ON Artigos USING HASH (titulo);


-- Usuário (para busca rápida por email)
CREATE INDEX idx_usuario_email_hash ON Usuario USING HASH (email);
CREATE INDEX idx_usuario_nome_hash ON Usuario USING HASH (nome);



-- Biblioteca
CREATE INDEX idx_biblioteca_nome ON Biblioteca(nome);

-- Titulo
CREATE INDEX idx_titulo_tipo_midia ON Titulo(tipo_midia);

-- Estoque
CREATE INDEX idx_estoque_id_titulo ON Estoque(id_titulo);
CREATE INDEX idx_estoque_id_biblioteca ON Estoque(id_biblioteca);

-- Emprestimo
CREATE INDEX idx_emprestimo_id_estoque ON Emprestimo(id_estoque);
CREATE INDEX idx_emprestimo_id_usuario ON Emprestimo(id_usuario);
CREATE INDEX idx_emprestimo_data_emprestimo ON Emprestimo(data_emprestimo);
CREATE INDEX idx_emprestimo_data_devolucao_prevista ON Emprestimo(data_devolucao_prevista);
CREATE INDEX idx_emprestimo_data_devolucao ON Emprestimo(data_devolucao);

-- Penalizacao
CREATE INDEX idx_penalizacao_id_usuario ON Penalizacao(id_usuario);

CREATE INDEX idx_penalizacao_id_emprestimo ON Penalizacao(id_emprestimo);

-- Livros
CREATE INDEX idx_livros_titulo ON Livros(titulo);
CREATE INDEX idx_livros_ISBN ON Livros(ISBN);
CREATE INDEX idx_livros_editora ON Livros(editora);
CREATE INDEX idx_livros_data_publicacao ON Livros(data_publicacao);

-- Revistas
CREATE INDEX idx_revistas_titulo ON Revistas(titulo);
CREATE INDEX idx_revistas_ISSN ON Revistas(ISSN);
CREATE INDEX idx_revistas_editora ON Revistas(editora);
CREATE INDEX idx_revistas_data_publicacao ON Revistas(data_publicacao);

-- DVDs
CREATE INDEX idx_dvds_titulo ON DVDs(titulo);
CREATE INDEX idx_dvds_ISAN ON DVDs(ISAN);
CREATE INDEX idx_dvds_distribuidora ON DVDs(distribuidora);
CREATE INDEX idx_dvds_data_lancamento ON DVDs(data_lancamento);

-- Artigos
CREATE INDEX idx_artigos_titulo ON Artigos(titulo);
CREATE INDEX idx_artigos_DOI ON Artigos(DOI);
CREATE INDEX idx_artigos_publicadora ON Artigos(publicadora);
CREATE INDEX idx_artigos_data_publicacao ON Artigos(data_publicacao);

-- Autores
CREATE INDEX idx_autores_nome ON Autores(nome);

-- Autorias
CREATE INDEX idx_autorias_id_autor ON Autorias(id_autor);
CREATE INDEX idx_autorias_id_titulo ON Autorias(id_titulo);



-- Indices Trigram
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX ON livros USING gin (lower(titulo) gin_trgm_ops);
CREATE INDEX ON artigos USING gin (lower(titulo) gin_trgm_ops);
CREATE INDEX ON dvds USING gin (lower(titulo) gin_trgm_ops);
CREATE INDEX ON revistas USING gin (lower(titulo) gin_trgm_ops);



-- Cria a materialized view otimizando a junção e agregação dos títulos
DROP MATERIALIZED VIEW IF EXISTS mv_titulos_completos;
CREATE MATERIALIZED VIEW mv_titulos_completos AS
SELECT 
    t.id_titulo,
    t.tipo_midia,
    COALESCE(l.titulo, r.titulo, d.titulo, a.titulo) as titulo
FROM titulo AS t
LEFT JOIN Livros AS l ON t.id_titulo = l.id_livro
LEFT JOIN Revistas AS r ON t.id_titulo = r.id_revista
LEFT JOIN DVDs AS d ON t.id_titulo = d.id_dvd
LEFT JOIN Artigos AS a ON t.id_titulo = a.id_artigo
WHERE COALESCE(l.titulo, r.titulo, d.titulo, a.titulo) IS NOT NULL;

-- Cria um índice GIN para acelerar buscas textuais por título
CREATE INDEX idx_mv_titulos_titulo ON mv_titulos_completos USING gin (to_tsvector('portuguese', titulo));
CREATE INDEX idx_mv_titulos_titulo_en ON mv_titulos_completos USING gin (to_tsvector('english', titulo));
