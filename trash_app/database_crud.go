package database

import (
	"database/sql"
	"fmt"
	"strconv"
	"strings"
	"time"

	_ "github.com/lib/pq"
)

var DB *sql.DB

// ConnectDB estabelece conexão com PostgreSQL
func ConnectDB() {
	var err error
	connStr := "user=postgres password=postgres dbname=biblioteca sslmode=disable"
	DB, err = sql.Open("postgres", connStr)
	if err != nil {
		panic(err)
	}

	if err = DB.Ping(); err != nil {
		panic(err)
	}

	fmt.Println("Conectado ao PostgreSQL!")
}

// ==== CRUD para Usuario ====

func CreateUsuario(nome, email, endereco, telefone string) (int, error) {
	var id int
	query := `INSERT INTO Usuario (nome, email, endereco, telefone) 
			  VALUES ($1, $2, $3, $4) RETURNING id_usuario`
	err := DB.QueryRow(query, nome, email, endereco, telefone).Scan(&id)
	return id, err
}

func GetUsuario(id int) (*Usuario, error) {
	usuario := &Usuario{}
	query := `SELECT id_usuario, nome, COALESCE(email, ''), COALESCE(endereco, ''), COALESCE(telefone, '') 
			  FROM Usuario WHERE id_usuario = $1`
	err := DB.QueryRow(query, id).Scan(&usuario.ID, &usuario.Nome, &usuario.Email, &usuario.Endereco, &usuario.Telefone)
	if err != nil {
		return nil, err
	}
	return usuario, nil
}

func GetAllUsuarios() ([]Usuario, error) {
	usuarios := []Usuario{}
	query := `SELECT id_usuario, nome, COALESCE(email, ''), COALESCE(endereco, ''), COALESCE(telefone, '') 
			  FROM Usuario ORDER BY nome`
	rows, err := DB.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	for rows.Next() {
		var usuario Usuario
		err := rows.Scan(&usuario.ID, &usuario.Nome, &usuario.Email, &usuario.Endereco, &usuario.Telefone)
		if err != nil {
			return nil, err
		}
		usuarios = append(usuarios, usuario)
	}
	return usuarios, nil
}

func UpdateUsuario(id int, nome, email, endereco, telefone string) error {
	query := `UPDATE Usuario SET nome = $1, email = $2, endereco = $3, telefone = $4 
			  WHERE id_usuario = $5`
	_, err := DB.Exec(query, nome, email, endereco, telefone, id)
	return err
}

func DeleteUsuario(id int) error {
	query := `DELETE FROM Usuario WHERE id_usuario = $1`
	_, err := DB.Exec(query, id)
	return err
}

// ==== CRUD para Biblioteca ====

func CreateBiblioteca(nome, endereco string) (int, error) {
	var id int
	query := `INSERT INTO Biblioteca (nome, endereco) VALUES ($1, $2) RETURNING id_biblioteca`
	err := DB.QueryRow(query, nome, endereco).Scan(&id)
	return id, err
}

func GetBiblioteca(id int) (*Biblioteca, error) {
	biblioteca := &Biblioteca{}
	query := `SELECT id_biblioteca, nome, COALESCE(endereco, '') FROM Biblioteca WHERE id_biblioteca = $1`
	err := DB.QueryRow(query, id).Scan(&biblioteca.ID, &biblioteca.Nome, &biblioteca.Endereco)
	if err != nil {
		return nil, err
	}
	return biblioteca, nil
}

func GetAllBibliotecas() ([]Biblioteca, error) {
	bibliotecas := []Biblioteca{}
	query := `SELECT id_biblioteca, nome, COALESCE(endereco, '') FROM Biblioteca ORDER BY nome`
	rows, err := DB.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	for rows.Next() {
		var biblioteca Biblioteca
		err := rows.Scan(&biblioteca.ID, &biblioteca.Nome, &biblioteca.Endereco)
		if err != nil {
			return nil, err
		}
		bibliotecas = append(bibliotecas, biblioteca)
	}
	return bibliotecas, nil
}

func UpdateBiblioteca(id int, nome, endereco string) error {
	query := `UPDATE Biblioteca SET nome = $1, endereco = $2 WHERE id_biblioteca = $3`
	_, err := DB.Exec(query, nome, endereco, id)
	return err
}

func DeleteBiblioteca(id int) error {
	query := `DELETE FROM Biblioteca WHERE id_biblioteca = $1`
	_, err := DB.Exec(query, id)
	return err
}

// ==== CRUD para Midia ====

func CreateMidia(tipoMidia, condicao string, idBiblioteca int) (int, error) {
	var id int
	query := `INSERT INTO Midia (tipo_midia, condicao, id_biblioteca) 
			  VALUES ($1, $2, $3) RETURNING id_midia`
	err := DB.QueryRow(query, tipoMidia, condicao, idBiblioteca).Scan(&id)
	return id, err
}

func GetMidia(id int) (*Midia, error) {
	midia := &Midia{}
	query := `SELECT m.id_midia, m.tipo_midia, COALESCE(m.condicao, ''), m.id_biblioteca, b.nome 
			  FROM Midia m LEFT JOIN Biblioteca b ON m.id_biblioteca = b.id_biblioteca 
			  WHERE m.id_midia = $1`
	var tipoMidia string
	err := DB.QueryRow(query, id).Scan(&midia.ID, &tipoMidia, &midia.Condicao, &midia.IDBiblioteca, &midia.NomeBiblioteca)
	if err != nil {
		return nil, err
	}
	midia.TipoMidia = MidiaTipo(tipoMidia)
	return midia, nil
}

func GetAllMidias() ([]Midia, error) {
	midias := []Midia{}
	query := `SELECT m.id_midia, m.tipo_midia, COALESCE(m.condicao, ''), m.id_biblioteca, COALESCE(b.nome, '') 
			  FROM Midia m LEFT JOIN Biblioteca b ON m.id_biblioteca = b.id_biblioteca 
			  ORDER BY m.tipo_midia, m.id_midia`
	rows, err := DB.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	for rows.Next() {
		var midia Midia
		var tipoMidia string
		err := rows.Scan(&midia.ID, &tipoMidia, &midia.Condicao, &midia.IDBiblioteca, &midia.NomeBiblioteca)
		if err != nil {
			return nil, err
		}
		midia.TipoMidia = MidiaTipo(tipoMidia)
		midias = append(midias, midia)
	}
	return midias, nil
}

func UpdateMidia(id int, tipoMidia, condicao string, idBiblioteca int) error {
	query := `UPDATE Midia SET tipo_midia = $1, condicao = $2, id_biblioteca = $3 WHERE id_midia = $4`
	_, err := DB.Exec(query, tipoMidia, condicao, idBiblioteca, id)
	return err
}

func DeleteMidia(id int) error {
	query := `DELETE FROM Midia WHERE id_midia = $1`
	_, err := DB.Exec(query, id)
	return err
}

// ==== CRUD para Emprestimo ====

func CreateEmprestimo(dataEmprestimo, dataDevolucaoPrevista string, idMidia, idUsuario int) (int, error) {
	var id int
	var dataPrev *time.Time

	if dataDevolucaoPrevista != "" {
		parsed, err := time.Parse("2006-01-02", dataDevolucaoPrevista)
		if err == nil {
			dataPrev = &parsed
		}
	}

	dataEmp, err := time.Parse("2006-01-02", dataEmprestimo)
	if err != nil {
		return 0, err
	}

	query := `INSERT INTO Emprestimo (data_emprestimo, data_devolucao_prevista, id_midia, id_usuario) 
			  VALUES ($1, $2, $3, $4) RETURNING id_emprestimo`
	err = DB.QueryRow(query, dataEmp, dataPrev, idMidia, idUsuario).Scan(&id)
	return id, err
}

func GetEmprestimo(id int) (*Emprestimo, error) {
	emprestimo := &Emprestimo{}
	query := `SELECT e.id_emprestimo, e.data_emprestimo, e.data_devolucao_prevista, 
			  e.data_devolucao, e.id_midia, e.id_usuario, u.nome, m.tipo_midia
			  FROM Emprestimo e 
			  LEFT JOIN Usuario u ON e.id_usuario = u.id_usuario 
			  LEFT JOIN Midia m ON e.id_midia = m.id_midia
			  WHERE e.id_emprestimo = $1`

	err := DB.QueryRow(query, id).Scan(&emprestimo.ID, &emprestimo.DataEmprestimo, 
		&emprestimo.DataDevolucaoPrevista, &emprestimo.DataDevolucao, 
		&emprestimo.IDMidia, &emprestimo.IDUsuario, &emprestimo.NomeUsuario, &emprestimo.TipoMidia)
	if err != nil {
		return nil, err
	}
	return emprestimo, nil
}

func GetAllEmprestimos() ([]Emprestimo, error) {
	emprestimos := []Emprestimo{}
	query := `SELECT e.id_emprestimo, e.data_emprestimo, e.data_devolucao_prevista, 
			  e.data_devolucao, e.id_midia, e.id_usuario, COALESCE(u.nome, ''), COALESCE(m.tipo_midia::text, '')
			  FROM Emprestimo e 
			  LEFT JOIN Usuario u ON e.id_usuario = u.id_usuario 
			  LEFT JOIN Midia m ON e.id_midia = m.id_midia
			  ORDER BY e.data_emprestimo DESC`
	rows, err := DB.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	for rows.Next() {
		var emprestimo Emprestimo
		err := rows.Scan(&emprestimo.ID, &emprestimo.DataEmprestimo, 
			&emprestimo.DataDevolucaoPrevista, &emprestimo.DataDevolucao, 
			&emprestimo.IDMidia, &emprestimo.IDUsuario, &emprestimo.NomeUsuario, &emprestimo.TipoMidia)
		if err != nil {
			return nil, err
		}
		emprestimos = append(emprestimos, emprestimo)
	}
	return emprestimos, nil
}

func UpdateEmprestimo(id int, dataEmprestimo, dataDevolucaoPrevista, dataDevolucao string, idMidia, idUsuario int) error {
	var dataPrev, dataDev *time.Time

	dataEmp, err := time.Parse("2006-01-02", dataEmprestimo)
	if err != nil {
		return err
	}

	if dataDevolucaoPrevista != "" {
		parsed, err := time.Parse("2006-01-02", dataDevolucaoPrevista)
		if err == nil {
			dataPrev = &parsed
		}
	}

	if dataDevolucao != "" {
		parsed, err := time.Parse("2006-01-02", dataDevolucao)
		if err == nil {
			dataDev = &parsed
		}
	}

	query := `UPDATE Emprestimo SET data_emprestimo = $1, data_devolucao_prevista = $2, 
			  data_devolucao = $3, id_midia = $4, id_usuario = $5 WHERE id_emprestimo = $6`
	_, err = DB.Exec(query, dataEmp, dataPrev, dataDev, idMidia, idUsuario, id)
	return err
}

func DeleteEmprestimo(id int) error {
	query := `DELETE FROM Emprestimo WHERE id_emprestimo = $1`
	_, err := DB.Exec(query, id)
	return err
}

// ==== CRUD para Livro ====

func CreateLivro(titulo, isbn, editora, condicao string, numeroPaginas, idBiblioteca int, dataPublicacao string) (int, error) {
	// Primeiro criar a mídia
	idMidia, err := CreateMidia("livro", condicao, idBiblioteca)
	if err != nil {
		return 0, err
	}

	var dataPub *time.Time
	if dataPublicacao != "" {
		parsed, err := time.Parse("2006-01-02", dataPublicacao)
		if err == nil {
			dataPub = &parsed
		}
	}

	query := `INSERT INTO Livros (id_livro, titulo, isbn, numero_paginas, editora, data_publicacao) 
			  VALUES ($1, $2, $3, $4, $5, $6)`
	_, err = DB.Exec(query, idMidia, titulo, isbn, numeroPaginas, editora, dataPub)
	if err != nil {
		// Se falhar, remover a mídia criada
		DeleteMidia(idMidia)
		return 0, err
	}
	return idMidia, nil
}

func GetLivro(id int) (*Livro, error) {
	livro := &Livro{}
	query := `SELECT l.id_livro, l.titulo, COALESCE(l.isbn, ''), l.numero_paginas, 
			  COALESCE(l.editora, ''), l.data_publicacao, COALESCE(m.condicao, ''), m.id_biblioteca
			  FROM Livros l 
			  LEFT JOIN Midia m ON l.id_livro = m.id_midia
			  WHERE l.id_livro = $1`
	err := DB.QueryRow(query, id).Scan(&livro.ID, &livro.Titulo, &livro.ISBN, 
		&livro.NumeroPaginas, &livro.Editora, &livro.DataPublicacao, &livro.Condicao, &livro.IDBiblioteca)
	if err != nil {
		return nil, err
	}
	return livro, nil
}

func GetAllLivros() ([]Livro, error) {
	livros := []Livro{}
	query := `SELECT l.id_livro, l.titulo, COALESCE(l.isbn, ''), COALESCE(l.numero_paginas, 0), 
			  COALESCE(l.editora, ''), l.data_publicacao, COALESCE(m.condicao, ''), COALESCE(m.id_biblioteca, 0)
			  FROM Livros l 
			  LEFT JOIN Midia m ON l.id_livro = m.id_midia
			  ORDER BY l.titulo`
	rows, err := DB.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	for rows.Next() {
		var livro Livro
		err := rows.Scan(&livro.ID, &livro.Titulo, &livro.ISBN, &livro.NumeroPaginas, 
			&livro.Editora, &livro.DataPublicacao, &livro.Condicao, &livro.IDBiblioteca)
		if err != nil {
			return nil, err
		}
		livros = append(livros, livro)
	}
	return livros, nil
}

func UpdateLivro(id int, titulo, isbn, editora, condicao string, numeroPaginas, idBiblioteca int, dataPublicacao string) error {
	var dataPub *time.Time
	if dataPublicacao != "" {
		parsed, err := time.Parse("2006-01-02", dataPublicacao)
		if err == nil {
			dataPub = &parsed
		}
	}

	// Atualizar livro
	query := `UPDATE Livros SET titulo = $1, isbn = $2, numero_paginas = $3, editora = $4, data_publicacao = $5 
			  WHERE id_livro = $6`
	_, err := DB.Exec(query, titulo, isbn, numeroPaginas, editora, dataPub, id)
	if err != nil {
		return err
	}

	// Atualizar mídia
	return UpdateMidia(id, "livro", condicao, idBiblioteca)
}

func DeleteLivro(id int) error {
	// Primeiro deletar o livro
	query := `DELETE FROM Livros WHERE id_livro = $1`
	_, err := DB.Exec(query, id)
	if err != nil {
		return err
	}
	// Depois deletar a mídia
	return DeleteMidia(id)
}

// Adicionar as importações necessárias no início do arquivo
type Usuario struct {
	ID       int    `json:"id_usuario"`
	Nome     string `json:"nome"`
	Email    string `json:"email"`
	Endereco string `json:"endereco"`
	Telefone string `json:"telefone"`
}

type Biblioteca struct {
	ID       int    `json:"id_biblioteca"`
	Nome     string `json:"nome"`
	Endereco string `json:"endereco"`
}

type MidiaTipo string

type Midia struct {
	ID             int       `json:"id_midia"`
	TipoMidia      MidiaTipo `json:"tipo_midia"`
	Condicao       string    `json:"condicao"`
	IDBiblioteca   int       `json:"id_biblioteca"`
	NomeBiblioteca string    `json:"nome_biblioteca,omitempty"`
}

type Emprestimo struct {
	ID                    int        `json:"id_emprestimo"`
	DataEmprestimo        time.Time  `json:"data_emprestimo"`
	DataDevolucaoPrevista *time.Time `json:"data_devolucao_prevista"`
	DataDevolucao         *time.Time `json:"data_devolucao"`
	IDMidia               int        `json:"id_midia"`
	IDUsuario             int        `json:"id_usuario"`
	NomeUsuario           string     `json:"nome_usuario,omitempty"`
	TipoMidia             string     `json:"tipo_midia,omitempty"`
}

type Livro struct {
	ID             int        `json:"id_livro"`
	Titulo         string     `json:"titulo"`
	ISBN           string     `json:"isbn"`
	NumeroPaginas  int        `json:"numero_paginas"`
	Editora        string     `json:"editora"`
	DataPublicacao *time.Time `json:"data_publicacao"`
	Condicao       string     `json:"condicao,omitempty"`
	IDBiblioteca   int        `json:"id_biblioteca"`
}
