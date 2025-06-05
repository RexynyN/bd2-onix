package database

import (
	"database/sql"
	"fmt"

	_ "github.com/lib/pq"
)

// Connect conecta ao PostgreSQL usando database/sql
func Connect(databaseURL string) (*sql.DB, error) {
	db, err := sql.Open("postgres", databaseURL)
	if err != nil {
		return nil, fmt.Errorf("erro ao abrir conexão com banco: %w", err)
	}

	// Testa a conexão
	if err := db.Ping(); err != nil {
		return nil, fmt.Errorf("erro ao conectar com banco: %w", err)
	}

	// Configura pool de conexões
	db.SetMaxOpenConns(25)
	db.SetMaxIdleConns(5)

	return db, nil
}

// InitSchema inicializa o schema do banco de dados
func InitSchema(db *sql.DB) error {
	schema := `
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
	`

	_, err := db.Exec(schema)
	return err
}
