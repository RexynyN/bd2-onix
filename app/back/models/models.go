package models

import (
	"database/sql/driver"
	"fmt"
	"time"
)

// Tipo personalizado para MidiaTipo
type MidiaTipo string

const (
	LivroTipo   MidiaTipo = "livro"
	RevistaTipo MidiaTipo = "revista"
	DVDTipo     MidiaTipo = "dvd"
	ArtigoTipo  MidiaTipo = "artigo"
)

func (mt *MidiaTipo) Scan(value interface{}) error {
	if value == nil {
		*mt = ""
		return nil
	}
	switch s := value.(type) {
	case string:
		*mt = MidiaTipo(s)
	case []byte:
		*mt = MidiaTipo(s)
	default:
		return fmt.Errorf("cannot scan %T into MidiaTipo", value)
	}
	return nil
}

func (mt MidiaTipo) Value() (driver.Value, error) {
	return string(mt), nil
}

// Usuario representa a tabela Usuario
type Usuario struct {
	ID        int       `json:"id_usuario" db:"id_usuario"`
	Nome      string    `json:"nome" db:"nome"`
	Email     *string   `json:"email" db:"email"`
	Endereco  *string   `json:"endereco" db:"endereco"`
	Telefone  *string   `json:"telefone" db:"telefone"`
	CreatedAt time.Time `json:"created_at" db:"created_at"`
	UpdatedAt time.Time `json:"updated_at" db:"updated_at"`
}

// Biblioteca representa a tabela Biblioteca
type Biblioteca struct {
	ID        int       `json:"id_biblioteca" db:"id_biblioteca"`
	Nome      string    `json:"nome" db:"nome"`
	Endereco  *string   `json:"endereco" db:"endereco"`
	CreatedAt time.Time `json:"created_at" db:"created_at"`
	UpdatedAt time.Time `json:"updated_at" db:"updated_at"`
}

// Midia representa a tabela Midia
type Midia struct {
	ID           int       `json:"id_midia" db:"id_midia"`
	TipoMidia    MidiaTipo `json:"tipo_midia" db:"tipo_midia"`
	Condicao     *string   `json:"condicao" db:"condicao"`
	IDBiblioteca *int      `json:"id_biblioteca" db:"id_biblioteca"`
	CreatedAt    time.Time `json:"created_at" db:"created_at"`
	UpdatedAt    time.Time `json:"updated_at" db:"updated_at"`
}

// Emprestimo representa a tabela Emprestimo
type Emprestimo struct {
	ID                    int        `json:"id_emprestimo" db:"id_emprestimo"`
	DataEmprestimo        time.Time  `json:"data_emprestimo" db:"data_emprestimo"`
	DataDevolucaoPrevista *time.Time `json:"data_devolucao_prevista" db:"data_devolucao_prevista"`
	DataDevolucao         *time.Time `json:"data_devolucao" db:"data_devolucao"`
	IDMidia               int        `json:"id_midia" db:"id_midia"`
	IDUsuario             int        `json:"id_usuario" db:"id_usuario"`
	Status                string     `json:"status" db:"status"`
	CreatedAt             time.Time  `json:"created_at" db:"created_at"`
	UpdatedAt             time.Time  `json:"updated_at" db:"updated_at"`
}

// Penalizacao representa a tabela Penalizacao
type Penalizacao struct {
	ID               int        `json:"id_penalizacao" db:"id_penalizacao"`
	Descricao        *string    `json:"descricao" db:"descricao"`
	FinalPenalizacao *time.Time `json:"final_penalizacao" db:"final_penalizacao"`
	Valor            *float64   `json:"valor" db:"valor"`
	IDUsuario        *int       `json:"id_usuario" db:"id_usuario"`
	IDEmprestimo     *int       `json:"id_emprestimo" db:"id_emprestimo"`
	CreatedAt        time.Time  `json:"created_at" db:"created_at"`
	UpdatedAt        time.Time  `json:"updated_at" db:"updated_at"`
}

// Livro representa a tabela Livros
type Livro struct {
	ID             int        `json:"id_livro" db:"id_livro"`
	Titulo         string     `json:"titulo" db:"titulo"`
	ISBN           *string    `json:"isbn" db:"isbn"`
	NumeroPaginas  *int       `json:"numero_paginas" db:"numero_paginas"`
	Editora        *string    `json:"editora" db:"editora"`
	DataPublicacao *time.Time `json:"data_publicacao" db:"data_publicacao"`
	CreatedAt      time.Time  `json:"created_at" db:"created_at"`
	UpdatedAt      time.Time  `json:"updated_at" db:"updated_at"`
}

// Revista representa a tabela Revistas
type Revista struct {
	ID             int        `json:"id_revista" db:"id_revista"`
	Titulo         string     `json:"titulo" db:"titulo"`
	ISSN           *string    `json:"issn" db:"issn"`
	Periodicidade  *string    `json:"periodicidade" db:"periodicidade"`
	Editora        *string    `json:"editora" db:"editora"`
	DataPublicacao *time.Time `json:"data_publicacao" db:"data_publicacao"`
	CreatedAt      time.Time  `json:"created_at" db:"created_at"`
	UpdatedAt      time.Time  `json:"updated_at" db:"updated_at"`
}

// DVD representa a tabela DVDs
type DVD struct {
	ID             int        `json:"id_dvd" db:"id_dvd"`
	Titulo         string     `json:"titulo" db:"titulo"`
	ISAN           *string    `json:"isan" db:"isan"`
	Duracao        *int       `json:"duracao" db:"duracao"`
	Distribuidora  *string    `json:"distribuidora" db:"distribuidora"`
	DataLancamento *time.Time `json:"data_lancamento" db:"data_lancamento"`
	CreatedAt      time.Time  `json:"created_at" db:"created_at"`
	UpdatedAt      time.Time  `json:"updated_at" db:"updated_at"`
}

// Artigo representa a tabela Artigos
type Artigo struct {
	ID             int        `json:"id_artigo" db:"id_artigo"`
	Titulo         string     `json:"titulo" db:"titulo"`
	DOI            *string    `json:"doi" db:"doi"`
	Publicadora    *string    `json:"publicadora" db:"publicadora"`
	DataPublicacao *time.Time `json:"data_publicacao" db:"data_publicacao"`
	CreatedAt      time.Time  `json:"created_at" db:"created_at"`
	UpdatedAt      time.Time  `json:"updated_at" db:"updated_at"`
}

// Autor representa a tabela Autores
type Autor struct {
	ID              int        `json:"id_autor" db:"id_autor"`
	Nome            string     `json:"nome" db:"nome"`
	DataNascimento  *time.Time `json:"data_nascimento" db:"data_nascimento"`
	DataFalecimento *time.Time `json:"data_falecimento" db:"data_falecimento"`
	CreatedAt       time.Time  `json:"created_at" db:"created_at"`
	UpdatedAt       time.Time  `json:"updated_at" db:"updated_at"`
}

// Autoria representa a tabela Autorias
type Autoria struct {
	ID        int       `json:"id_autorias" db:"id_autorias"`
	IDAutor   int       `json:"id_autor" db:"id_autor"`
	IDMidia   int       `json:"id_midia" db:"id_midia"`
	CreatedAt time.Time `json:"created_at" db:"created_at"`
}

// DTOs para requests
type CreateUsuarioRequest struct {
	Nome     string  `json:"nome" validate:"required"`
	Email    *string `json:"email"`
	Endereco *string `json:"endereco"`
	Telefone *string `json:"telefone"`
}

type UpdateUsuarioRequest struct {
	Nome     *string `json:"nome"`
	Email    *string `json:"email"`
	Endereco *string `json:"endereco"`
	Telefone *string `json:"telefone"`
}

type CreateBibliotecaRequest struct {
	Nome     string  `json:"nome" validate:"required"`
	Endereco *string `json:"endereco"`
}

type CreateMidiaRequest struct {
	TipoMidia    MidiaTipo `json:"tipo_midia" validate:"required"`
	Condicao     *string   `json:"condicao"`
	IDBiblioteca *int      `json:"id_biblioteca"`
}

type CreateEmprestimoRequest struct {
	DataEmprestimo        time.Time  `json:"data_emprestimo" validate:"required"`
	DataDevolucaoPrevista *time.Time `json:"data_devolucao_prevista"`
	IDMidia               int        `json:"id_midia" validate:"required"`
	IDUsuario             int        `json:"id_usuario" validate:"required"`
}

type CreateLivroRequest struct {
	Titulo         string     `json:"titulo" validate:"required"`
	ISBN           *string    `json:"isbn"`
	NumeroPaginas  *int       `json:"numero_paginas"`
	Editora        *string    `json:"editora"`
	DataPublicacao *time.Time `json:"data_publicacao"`
	TipoMidia      MidiaTipo  `json:"tipo_midia" validate:"required"`
	Condicao       *string    `json:"condicao"`
	IDBiblioteca   *int       `json:"id_biblioteca"`
}

// Response com dados expandidos
type EmprestimoDetalhado struct {
	Emprestimo
	Usuario Usuario `json:"usuario"`
	Midia   Midia   `json:"midia"`
}

type MidiaDetalhada struct {
	Midia
	Biblioteca *Biblioteca `json:"biblioteca,omitempty"`
	Autores    []Autor     `json:"autores,omitempty"`
	Livro      *Livro      `json:"livro,omitempty"`
	Revista    *Revista    `json:"revista,omitempty"`
	DVD        *DVD        `json:"dvd,omitempty"`
	Artigo     *Artigo     `json:"artigo,omitempty"`
}
