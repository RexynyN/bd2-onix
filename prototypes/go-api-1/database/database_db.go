package database

import (
	"database/sql"
	"fmt"

	_ "github.com/lib/pq"
)

const (
	host     = "localhost"
	port     = 5432
	user     = "super_user"
	password = "carimboatrasado"
	dbname   = "onixlibrary"
)

func Connect() (*sql.DB, error) {
	psqlInfo := fmt.Sprintf("host=%s port=%d user=%s password=%s dbname=%s sslmode=disable",
		host, port, user, password, dbname)

	db, err := sql.Open("postgres", psqlInfo)
	if err != nil {
		return nil, err
	}

	err = db.Ping()
	if err != nil {
		return nil, err
	}

	fmt.Println("Conectado ao PostgreSQL com sucesso!")
	return db, nil
}

// InitTables cria as tabelas se não existirem
func InitTables(db *sql.DB) error {
	queries := []string{
		`CREATE TYPE IF NOT EXISTS MidiaTipo AS ENUM ('livro', 'revista', 'dvd', 'artigo');`,

		`CREATE TABLE IF NOT EXISTS Usuario (
			id_usuario SERIAL PRIMARY KEY,
			nome VARCHAR NOT NULL,
			email VARCHAR,
			endereco VARCHAR,
			telefone VARCHAR
		);`,

		`CREATE TABLE IF NOT EXISTS Biblioteca (
			id_biblioteca SERIAL PRIMARY KEY,
			nome VARCHAR NOT NULL,
			endereco VARCHAR
		);`,

		`CREATE TABLE IF NOT EXISTS Midia (
			id_midia SERIAL PRIMARY KEY,
			tipo_midia MidiaTipo NOT NULL,
			condicao VARCHAR,
			id_biblioteca INT,
			FOREIGN KEY (id_biblioteca) REFERENCES Biblioteca(id_biblioteca)
		);`,

		`CREATE TABLE IF NOT EXISTS Emprestimo (
			id_emprestimo SERIAL PRIMARY KEY,
			data_emprestimo DATE NOT NULL,
			data_devolucao_prevista DATE,
			data_devolucao DATE,
			id_midia INT NOT NULL,
			id_usuario INT NOT NULL,
			FOREIGN KEY (id_midia) REFERENCES Midia(id_midia),
			FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario)
		);`,

		`CREATE TABLE IF NOT EXISTS Penalizacao (
			id_penalizacao SERIAL PRIMARY KEY,
			descricao TEXT,
			Final_penalizacao DATE,
			id_usuario INT,
			id_emprestimo INT,
			FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario),
			FOREIGN KEY (id_emprestimo) REFERENCES Emprestimo(id_emprestimo)
		);`,

		`CREATE TABLE IF NOT EXISTS Livros (
			id_livro SERIAL PRIMARY KEY,
			titulo VARCHAR NOT NULL,
			ISBN VARCHAR,
			numero_paginas INT,
			editora VARCHAR,
			data_publicacao DATE,
			FOREIGN KEY (id_livro) REFERENCES Midia(id_midia)
		);`,

		`CREATE TABLE IF NOT EXISTS Revistas (
			id_revista SERIAL PRIMARY KEY,
			titulo VARCHAR NOT NULL,
			ISSN VARCHAR,
			periodicidade VARCHAR,
			editora VARCHAR,
			data_publicacao DATE,
			FOREIGN KEY (id_revista) REFERENCES Midia(id_midia)
		);`,

		`CREATE TABLE IF NOT EXISTS DVDs (
			id_dvd SERIAL PRIMARY KEY,
			titulo VARCHAR NOT NULL,
			ISAN VARCHAR,
			duracao INT,
			distribuidora VARCHAR,
			data_lancamento DATE,
			FOREIGN KEY (id_dvd) REFERENCES Midia(id_midia)
		);`,

		`CREATE TABLE IF NOT EXISTS Artigos (
			id_artigo SERIAL PRIMARY KEY,
			titulo VARCHAR NOT NULL,
			DOI VARCHAR,
			publicadora VARCHAR,
			data_publicacao DATE,
			FOREIGN KEY (id_artigo) REFERENCES Midia(id_midia)
		);`,

		`CREATE TABLE IF NOT EXISTS Autores (
			id_autor SERIAL PRIMARY KEY,
			nome VARCHAR NOT NULL,
			data_nascimento DATE,
			data_falecimento DATE
		);`,

		`CREATE TABLE IF NOT EXISTS Autorias (
			id_autorias SERIAL PRIMARY KEY,
			id_autor INT NOT NULL,
			id_midia INT NOT NULL,
			FOREIGN KEY (id_autor) REFERENCES Autores(id_autor),
			FOREIGN KEY (id_midia) REFERENCES Midia(id_midia)
		);`,
	}

	for _, query := range queries {
		_, err := db.Exec(query)
		if err != nil {
			return fmt.Errorf("erro ao criar tabela: %v", err)
		}
	}

	fmt.Println("Tabelas criadas/verificadas com sucesso!")
	return nil
}
