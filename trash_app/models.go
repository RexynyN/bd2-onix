package models

import (
	"database/sql"
	"database/sql/driver"
	"errors"
	"time"
)

// Enum para tipo de mídia
type MidiaTipo string

const (
	TipoLivro   MidiaTipo = "livro"
	TipoRevista MidiaTipo = "revista"
	TipoDVD     MidiaTipo = "dvd"
	TipoArtigo  MidiaTipo = "artigo"
)

// Implementar interfaces para PostgreSQL enum
func (m *MidiaTipo) Scan(value interface{}) error {
	if value == nil {
		*m = ""
		return nil
	}
	if bv, ok := value.([]byte); ok {
		*m = MidiaTipo(bv)
		return nil
	}
	if sv, ok := value.(string); ok {
		*m = MidiaTipo(sv)
		return nil
	}
	return errors.New("cannot scan into MidiaTipo")
}

func (m MidiaTipo) Value() (driver.Value, error) {
	return string(m), nil
}

// Usuario representa a tabela Usuario
type Usuario struct {
	ID       int    `json:"id_usuario" form:"id_usuario"`
	Nome     string `json:"nome" form:"nome" validate:"required,min=2,max=100"`
	Email    string `json:"email" form:"email" validate:"email"`
	Endereco string `json:"endereco" form:"endereco"`
	Telefone string `json:"telefone" form:"telefone"`
}

// Biblioteca representa a tabela Biblioteca
type Biblioteca struct {
	ID       int    `json:"id_biblioteca" form:"id_biblioteca"`
	Nome     string `json:"nome" form:"nome" validate:"required,min=2,max=100"`
	Endereco string `json:"endereco" form:"endereco"`
}

// Midia representa a tabela Midia
type Midia struct {
	ID           int       `json:"id_midia" form:"id_midia"`
	TipoMidia    MidiaTipo `json:"tipo_midia" form:"tipo_midia" validate:"required"`
	Condicao     string    `json:"condicao" form:"condicao"`
	IDBiblioteca int       `json:"id_biblioteca" form:"id_biblioteca" validate:"required"`
	// Dados relacionados para exibição
	NomeBiblioteca string `json:"nome_biblioteca,omitempty"`
}

// Emprestimo representa a tabela Emprestimo
type Emprestimo struct {
	ID                   int        `json:"id_emprestimo" form:"id_emprestimo"`
	DataEmprestimo       time.Time  `json:"data_emprestimo" form:"data_emprestimo" validate:"required"`
	DataDevolucaoPrevista *time.Time `json:"data_devolucao_prevista" form:"data_devolucao_prevista"`
	DataDevolucao        *time.Time `json:"data_devolucao" form:"data_devolucao"`
	IDMidia              int        `json:"id_midia" form:"id_midia" validate:"required"`
	IDUsuario            int        `json:"id_usuario" form:"id_usuario" validate:"required"`
	// Dados relacionados para exibição
	NomeUsuario  string `json:"nome_usuario,omitempty"`
	TipoMidia    string `json:"tipo_midia,omitempty"`
}

// Penalizacao representa a tabela Penalizacao
type Penalizacao struct {
	ID              int        `json:"id_penalizacao" form:"id_penalizacao"`
	Descricao       string     `json:"descricao" form:"descricao" validate:"required"`
	FinalPenalizacao *time.Time `json:"final_penalizacao" form:"final_penalizacao"`
	IDUsuario       int        `json:"id_usuario" form:"id_usuario" validate:"required"`
	IDEmprestimo    int        `json:"id_emprestimo" form:"id_emprestimo" validate:"required"`
	// Dados relacionados para exibição
	NomeUsuario string `json:"nome_usuario,omitempty"`
}

// Livro representa a tabela Livros
type Livro struct {
	ID              int        `json:"id_livro" form:"id_livro"`
	Titulo          string     `json:"titulo" form:"titulo" validate:"required,min=2,max=200"`
	ISBN            string     `json:"isbn" form:"isbn"`
	NumeroPaginas   int        `json:"numero_paginas" form:"numero_paginas" validate:"gte=1"`
	Editora         string     `json:"editora" form:"editora"`
	DataPublicacao  *time.Time `json:"data_publicacao" form:"data_publicacao"`
	// Dados da mídia relacionada
	Condicao     string `json:"condicao,omitempty" form:"condicao"`
	IDBiblioteca int    `json:"id_biblioteca" form:"id_biblioteca" validate:"required"`
}

// Revista representa a tabela Revistas
type Revista struct {
	ID             int        `json:"id_revista" form:"id_revista"`
	Titulo         string     `json:"titulo" form:"titulo" validate:"required,min=2,max=200"`
	ISSN           string     `json:"issn" form:"issn"`
	Periodicidade  string     `json:"periodicidade" form:"periodicidade"`
	Editora        string     `json:"editora" form:"editora"`
	DataPublicacao *time.Time `json:"data_publicacao" form:"data_publicacao"`
	// Dados da mídia relacionada
	Condicao     string `json:"condicao,omitempty" form:"condicao"`
	IDBiblioteca int    `json:"id_biblioteca" form:"id_biblioteca" validate:"required"`
}

// DVD representa a tabela DVDs
type DVD struct {
	ID             int        `json:"id_dvd" form:"id_dvd"`
	Titulo         string     `json:"titulo" form:"titulo" validate:"required,min=2,max=200"`
	ISAN           string     `json:"isan" form:"isan"`
	Duracao        int        `json:"duracao" form:"duracao" validate:"gte=1"`
	Distribuidora  string     `json:"distribuidora" form:"distribuidora"`
	DataLancamento *time.Time `json:"data_lancamento" form:"data_lancamento"`
	// Dados da mídia relacionada
	Condicao     string `json:"condicao,omitempty" form:"condicao"`
	IDBiblioteca int    `json:"id_biblioteca" form:"id_biblioteca" validate:"required"`
}

// Artigo representa a tabela Artigos
type Artigo struct {
	ID             int        `json:"id_artigo" form:"id_artigo"`
	Titulo         string     `json:"titulo" form:"titulo" validate:"required,min=2,max=200"`
	DOI            string     `json:"doi" form:"doi"`
	Publicadora    string     `json:"publicadora" form:"publicadora"`
	DataPublicacao *time.Time `json:"data_publicacao" form:"data_publicacao"`
	// Dados da mídia relacionada
	Condicao     string `json:"condicao,omitempty" form:"condicao"`
	IDBiblioteca int    `json:"id_biblioteca" form:"id_biblioteca" validate:"required"`
}

// Autor representa a tabela Autores
type Autor struct {
	ID              int        `json:"id_autor" form:"id_autor"`
	Nome            string     `json:"nome" form:"nome" validate:"required,min=2,max=100"`
	DataNascimento  *time.Time `json:"data_nascimento" form:"data_nascimento"`
	DataFalecimento *time.Time `json:"data_falecimento" form:"data_falecimento"`
}

// Autoria representa a tabela Autorias
type Autoria struct {
	ID      int `json:"id_autorias" form:"id_autorias"`
	IDAutor int `json:"id_autor" form:"id_autor" validate:"required"`
	IDMidia int `json:"id_midia" form:"id_midia" validate:"required"`
	// Dados relacionados para exibição
	NomeAutor string `json:"nome_autor,omitempty"`
	TipoMidia string `json:"tipo_midia,omitempty"`
}
