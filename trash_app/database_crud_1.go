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

// ==== CRUD para Revista ====

func CreateRevista(titulo, issn, periodicidade, editora, condicao string, idBiblioteca int, dataPublicacao string) (int, error) {
	// Primeiro criar a mídia
	idMidia, err := CreateMidia("revista", condicao, idBiblioteca)
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

	query := `INSERT INTO Revistas (id_revista, titulo, issn, periodicidade, editora, data_publicacao) 
			  VALUES ($1, $2, $3, $4, $5, $6)`
	_, err = DB.Exec(query, idMidia, titulo, issn, periodicidade, editora, dataPub)
	if err != nil {
		DeleteMidia(idMidia)
		return 0, err
	}
	return idMidia, nil
}

func GetRevista(id int) (*Revista, error) {
	revista := &Revista{}
	query := `SELECT r.id_revista, r.titulo, COALESCE(r.issn, ''), COALESCE(r.periodicidade, ''), 
			  COALESCE(r.editora, ''), r.data_publicacao, COALESCE(m.condicao, ''), m.id_biblioteca
			  FROM Revistas r 
			  LEFT JOIN Midia m ON r.id_revista = m.id_midia
			  WHERE r.id_revista = $1`
	err := DB.QueryRow(query, id).Scan(&revista.ID, &revista.Titulo, &revista.ISSN, 
		&revista.Periodicidade, &revista.Editora, &revista.DataPublicacao, &revista.Condicao, &revista.IDBiblioteca)
	if err != nil {
		return nil, err
	}
	return revista, nil
}

func GetAllRevistas() ([]Revista, error) {
	revistas := []Revista{}
	query := `SELECT r.id_revista, r.titulo, COALESCE(r.issn, ''), COALESCE(r.periodicidade, ''), 
			  COALESCE(r.editora, ''), r.data_publicacao, COALESCE(m.condicao, ''), COALESCE(m.id_biblioteca, 0)
			  FROM Revistas r 
			  LEFT JOIN Midia m ON r.id_revista = m.id_midia
			  ORDER BY r.titulo`
	rows, err := DB.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	for rows.Next() {
		var revista Revista
		err := rows.Scan(&revista.ID, &revista.Titulo, &revista.ISSN, &revista.Periodicidade, 
			&revista.Editora, &revista.DataPublicacao, &revista.Condicao, &revista.IDBiblioteca)
		if err != nil {
			return nil, err
		}
		revistas = append(revistas, revista)
	}
	return revistas, nil
}

func UpdateRevista(id int, titulo, issn, periodicidade, editora, condicao string, idBiblioteca int, dataPublicacao string) error {
	var dataPub *time.Time
	if dataPublicacao != "" {
		parsed, err := time.Parse("2006-01-02", dataPublicacao)
		if err == nil {
			dataPub = &parsed
		}
	}

	query := `UPDATE Revistas SET titulo = $1, issn = $2, periodicidade = $3, editora = $4, data_publicacao = $5 
			  WHERE id_revista = $6`
	_, err := DB.Exec(query, titulo, issn, periodicidade, editora, dataPub, id)
	if err != nil {
		return err
	}

	return UpdateMidia(id, "revista", condicao, idBiblioteca)
}

func DeleteRevista(id int) error {
	query := `DELETE FROM Revistas WHERE id_revista = $1`
	_, err := DB.Exec(query, id)
	if err != nil {
		return err
	}
	return DeleteMidia(id)
}

// ==== CRUD para DVD ====

func CreateDVD(titulo, isan, distribuidora, condicao string, duracao, idBiblioteca int, dataLancamento string) (int, error) {
	idMidia, err := CreateMidia("dvd", condicao, idBiblioteca)
	if err != nil {
		return 0, err
	}

	var dataLanc *time.Time
	if dataLancamento != "" {
		parsed, err := time.Parse("2006-01-02", dataLancamento)
		if err == nil {
			dataLanc = &parsed
		}
	}

	query := `INSERT INTO DVDs (id_dvd, titulo, isan, duracao, distribuidora, data_lancamento) 
			  VALUES ($1, $2, $3, $4, $5, $6)`
	_, err = DB.Exec(query, idMidia, titulo, isan, duracao, distribuidora, dataLanc)
	if err != nil {
		DeleteMidia(idMidia)
		return 0, err
	}
	return idMidia, nil
}

func GetDVD(id int) (*DVD, error) {
	dvd := &DVD{}
	query := `SELECT d.id_dvd, d.titulo, COALESCE(d.isan, ''), COALESCE(d.duracao, 0), 
			  COALESCE(d.distribuidora, ''), d.data_lancamento, COALESCE(m.condicao, ''), m.id_biblioteca
			  FROM DVDs d 
			  LEFT JOIN Midia m ON d.id_dvd = m.id_midia
			  WHERE d.id_dvd = $1`
	err := DB.QueryRow(query, id).Scan(&dvd.ID, &dvd.Titulo, &dvd.ISAN, 
		&dvd.Duracao, &dvd.Distribuidora, &dvd.DataLancamento, &dvd.Condicao, &dvd.IDBiblioteca)
	if err != nil {
		return nil, err
	}
	return dvd, nil
}

func GetAllDVDs() ([]DVD, error) {
	dvds := []DVD{}
	query := `SELECT d.id_dvd, d.titulo, COALESCE(d.isan, ''), COALESCE(d.duracao, 0), 
			  COALESCE(d.distribuidora, ''), d.data_lancamento, COALESCE(m.condicao, ''), COALESCE(m.id_biblioteca, 0)
			  FROM DVDs d 
			  LEFT JOIN Midia m ON d.id_dvd = m.id_midia
			  ORDER BY d.titulo`
	rows, err := DB.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	for rows.Next() {
		var dvd DVD
		err := rows.Scan(&dvd.ID, &dvd.Titulo, &dvd.ISAN, &dvd.Duracao, 
			&dvd.Distribuidora, &dvd.DataLancamento, &dvd.Condicao, &dvd.IDBiblioteca)
		if err != nil {
			return nil, err
		}
		dvds = append(dvds, dvd)
	}
	return dvds, nil
}

func UpdateDVD(id int, titulo, isan, distribuidora, condicao string, duracao, idBiblioteca int, dataLancamento string) error {
	var dataLanc *time.Time
	if dataLancamento != "" {
		parsed, err := time.Parse("2006-01-02", dataLancamento)
		if err == nil {
			dataLanc = &parsed
		}
	}

	query := `UPDATE DVDs SET titulo = $1, isan = $2, duracao = $3, distribuidora = $4, data_lancamento = $5 
			  WHERE id_dvd = $6`
	_, err := DB.Exec(query, titulo, isan, duracao, distribuidora, dataLanc, id)
	if err != nil {
		return err
	}

	return UpdateMidia(id, "dvd", condicao, idBiblioteca)
}

func DeleteDVD(id int) error {
	query := `DELETE FROM DVDs WHERE id_dvd = $1`
	_, err := DB.Exec(query, id)
	if err != nil {
		return err
	}
	return DeleteMidia(id)
}

// ==== CRUD para Artigo ====

func CreateArtigo(titulo, doi, publicadora, condicao string, idBiblioteca int, dataPublicacao string) (int, error) {
	idMidia, err := CreateMidia("artigo", condicao, idBiblioteca)
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

	query := `INSERT INTO Artigos (id_artigo, titulo, doi, publicadora, data_publicacao) 
			  VALUES ($1, $2, $3, $4, $5)`
	_, err = DB.Exec(query, idMidia, titulo, doi, publicadora, dataPub)
	if err != nil {
		DeleteMidia(idMidia)
		return 0, err
	}
	return idMidia, nil
}

func GetArtigo(id int) (*Artigo, error) {
	artigo := &Artigo{}
	query := `SELECT a.id_artigo, a.titulo, COALESCE(a.doi, ''), 
			  COALESCE(a.publicadora, ''), a.data_publicacao, COALESCE(m.condicao, ''), m.id_biblioteca
			  FROM Artigos a 
			  LEFT JOIN Midia m ON a.id_artigo = m.id_midia
			  WHERE a.id_artigo = $1`
	err := DB.QueryRow(query, id).Scan(&artigo.ID, &artigo.Titulo, &artigo.DOI, 
		&artigo.Publicadora, &artigo.DataPublicacao, &artigo.Condicao, &artigo.IDBiblioteca)
	if err != nil {
		return nil, err
	}
	return artigo, nil
}

func GetAllArtigos() ([]Artigo, error) {
	artigos := []Artigo{}
	query := `SELECT a.id_artigo, a.titulo, COALESCE(a.doi, ''), 
			  COALESCE(a.publicadora, ''), a.data_publicacao, COALESCE(m.condicao, ''), COALESCE(m.id_biblioteca, 0)
			  FROM Artigos a 
			  LEFT JOIN Midia m ON a.id_artigo = m.id_midia
			  ORDER BY a.titulo`
	rows, err := DB.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	for rows.Next() {
		var artigo Artigo
		err := rows.Scan(&artigo.ID, &artigo.Titulo, &artigo.DOI, 
			&artigo.Publicadora, &artigo.DataPublicacao, &artigo.Condicao, &artigo.IDBiblioteca)
		if err != nil {
			return nil, err
		}
		artigos = append(artigos, artigo)
	}
	return artigos, nil
}

func UpdateArtigo(id int, titulo, doi, publicadora, condicao string, idBiblioteca int, dataPublicacao string) error {
	var dataPub *time.Time
	if dataPublicacao != "" {
		parsed, err := time.Parse("2006-01-02", dataPublicacao)
		if err == nil {
			dataPub = &parsed
		}
	}

	query := `UPDATE Artigos SET titulo = $1, doi = $2, publicadora = $3, data_publicacao = $4 
			  WHERE id_artigo = $5`
	_, err := DB.Exec(query, titulo, doi, publicadora, dataPub, id)
	if err != nil {
		return err
	}

	return UpdateMidia(id, "artigo", condicao, idBiblioteca)
}

func DeleteArtigo(id int) error {
	query := `DELETE FROM Artigos WHERE id_artigo = $1`
	_, err := DB.Exec(query, id)
	if err != nil {
		return err
	}
	return DeleteMidia(id)
}

// ==== CRUD para Autor ====

func CreateAutor(nome string, dataNascimento, dataFalecimento string) (int, error) {
	var id int
	var dataNasc, dataFalec *time.Time

	if dataNascimento != "" {
		parsed, err := time.Parse("2006-01-02", dataNascimento)
		if err == nil {
			dataNasc = &parsed
		}
	}

	if dataFalecimento != "" {
		parsed, err := time.Parse("2006-01-02", dataFalecimento)
		if err == nil {
			dataFalec = &parsed
		}
	}

	query := `INSERT INTO Autores (nome, data_nascimento, data_falecimento) 
			  VALUES ($1, $2, $3) RETURNING id_autor`
	err := DB.QueryRow(query, nome, dataNasc, dataFalec).Scan(&id)
	return id, err
}

func GetAutor(id int) (*Autor, error) {
	autor := &Autor{}
	query := `SELECT id_autor, nome, data_nascimento, data_falecimento FROM Autores WHERE id_autor = $1`
	err := DB.QueryRow(query, id).Scan(&autor.ID, &autor.Nome, &autor.DataNascimento, &autor.DataFalecimento)
	if err != nil {
		return nil, err
	}
	return autor, nil
}

func GetAllAutores() ([]Autor, error) {
	autores := []Autor{}
	query := `SELECT id_autor, nome, data_nascimento, data_falecimento FROM Autores ORDER BY nome`
	rows, err := DB.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	for rows.Next() {
		var autor Autor
		err := rows.Scan(&autor.ID, &autor.Nome, &autor.DataNascimento, &autor.DataFalecimento)
		if err != nil {
			return nil, err
		}
		autores = append(autores, autor)
	}
	return autores, nil
}

func UpdateAutor(id int, nome string, dataNascimento, dataFalecimento string) error {
	var dataNasc, dataFalec *time.Time

	if dataNascimento != "" {
		parsed, err := time.Parse("2006-01-02", dataNascimento)
		if err == nil {
			dataNasc = &parsed
		}
	}

	if dataFalecimento != "" {
		parsed, err := time.Parse("2006-01-02", dataFalecimento)
		if err == nil {
			dataFalec = &parsed
		}
	}

	query := `UPDATE Autores SET nome = $1, data_nascimento = $2, data_falecimento = $3 WHERE id_autor = $4`
	_, err := DB.Exec(query, nome, dataNasc, dataFalec, id)
	return err
}

func DeleteAutor(id int) error {
	query := `DELETE FROM Autores WHERE id_autor = $1`
	_, err := DB.Exec(query, id)
	return err
}

// ==== CRUD para Autoria ====

func CreateAutoria(idAutor, idMidia int) (int, error) {
	var id int
	query := `INSERT INTO Autorias (id_autor, id_midia) VALUES ($1, $2) RETURNING id_autorias`
	err := DB.QueryRow(query, idAutor, idMidia).Scan(&id)
	return id, err
}

func GetAutoria(id int) (*Autoria, error) {
	autoria := &Autoria{}
	query := `SELECT au.id_autorias, au.id_autor, au.id_midia, a.nome, m.tipo_midia
			  FROM Autorias au 
			  LEFT JOIN Autores a ON au.id_autor = a.id_autor 
			  LEFT JOIN Midia m ON au.id_midia = m.id_midia
			  WHERE au.id_autorias = $1`
	err := DB.QueryRow(query, id).Scan(&autoria.ID, &autoria.IDAutor, &autoria.IDMidia, 
		&autoria.NomeAutor, &autoria.TipoMidia)
	if err != nil {
		return nil, err
	}
	return autoria, nil
}

func GetAllAutorias() ([]Autoria, error) {
	autorias := []Autoria{}
	query := `SELECT au.id_autorias, au.id_autor, au.id_midia, COALESCE(a.nome, ''), COALESCE(m.tipo_midia::text, '')
			  FROM Autorias au 
			  LEFT JOIN Autores a ON au.id_autor = a.id_autor 
			  LEFT JOIN Midia m ON au.id_midia = m.id_midia
			  ORDER BY a.nome, m.tipo_midia`
	rows, err := DB.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	for rows.Next() {
		var autoria Autoria
		err := rows.Scan(&autoria.ID, &autoria.IDAutor, &autoria.IDMidia, 
			&autoria.NomeAutor, &autoria.TipoMidia)
		if err != nil {
			return nil, err
		}
		autorias = append(autorias, autoria)
	}
	return autorias, nil
}

func UpdateAutoria(id, idAutor, idMidia int) error {
	query := `UPDATE Autorias SET id_autor = $1, id_midia = $2 WHERE id_autorias = $3`
	_, err := DB.Exec(query, idAutor, idMidia, id)
	return err
}

func DeleteAutoria(id int) error {
	query := `DELETE FROM Autorias WHERE id_autorias = $1`
	_, err := DB.Exec(query, id)
	return err
}

// ==== CRUD para Penalizacao ====

func CreatePenalizacao(descricao string, finalPenalizacao string, idUsuario, idEmprestimo int) (int, error) {
	var id int
	var finalPenaliz *time.Time

	if finalPenalizacao != "" {
		parsed, err := time.Parse("2006-01-02", finalPenalizacao)
		if err == nil {
			finalPenaliz = &parsed
		}
	}

	query := `INSERT INTO Penalizacao (descricao, final_penalizacao, id_usuario, id_emprestimo) 
			  VALUES ($1, $2, $3, $4) RETURNING id_penalizacao`
	err := DB.QueryRow(query, descricao, finalPenaliz, idUsuario, idEmprestimo).Scan(&id)
	return id, err
}

func GetPenalizacao(id int) (*Penalizacao, error) {
	penalizacao := &Penalizacao{}
	query := `SELECT p.id_penalizacao, p.descricao, p.final_penalizacao, p.id_usuario, 
			  p.id_emprestimo, u.nome
			  FROM Penalizacao p 
			  LEFT JOIN Usuario u ON p.id_usuario = u.id_usuario
			  WHERE p.id_penalizacao = $1`
	err := DB.QueryRow(query, id).Scan(&penalizacao.ID, &penalizacao.Descricao, 
		&penalizacao.FinalPenalizacao, &penalizacao.IDUsuario, &penalizacao.IDEmprestimo, &penalizacao.NomeUsuario)
	if err != nil {
		return nil, err
	}
	return penalizacao, nil
}

func GetAllPenalizacoes() ([]Penalizacao, error) {
	penalizacoes := []Penalizacao{}
	query := `SELECT p.id_penalizacao, COALESCE(p.descricao, ''), p.final_penalizacao, 
			  p.id_usuario, p.id_emprestimo, COALESCE(u.nome, '')
			  FROM Penalizacao p 
			  LEFT JOIN Usuario u ON p.id_usuario = u.id_usuario
			  ORDER BY p.id_penalizacao DESC`
	rows, err := DB.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	for rows.Next() {
		var penalizacao Penalizacao
		err := rows.Scan(&penalizacao.ID, &penalizacao.Descricao, &penalizacao.FinalPenalizacao, 
			&penalizacao.IDUsuario, &penalizacao.IDEmprestimo, &penalizacao.NomeUsuario)
		if err != nil {
			return nil, err
		}
		penalizacoes = append(penalizacoes, penalizacao)
	}
	return penalizacoes, nil
}

func UpdatePenalizacao(id int, descricao string, finalPenalizacao string, idUsuario, idEmprestimo int) error {
	var finalPenaliz *time.Time

	if finalPenalizacao != "" {
		parsed, err := time.Parse("2006-01-02", finalPenalizacao)
		if err == nil {
			finalPenaliz = &parsed
		}
	}

	query := `UPDATE Penalizacao SET descricao = $1, final_penalizacao = $2, id_usuario = $3, id_emprestimo = $4 
			  WHERE id_penalizacao = $5`
	_, err := DB.Exec(query, descricao, finalPenaliz, idUsuario, idEmprestimo, id)
	return err
}

func DeletePenalizacao(id int) error {
	query := `DELETE FROM Penalizacao WHERE id_penalizacao = $1`
	_, err := DB.Exec(query, id)
	return err
}

// Adicionando tipos necessários
type Revista struct {
	ID             int        `json:"id_revista"`
	Titulo         string     `json:"titulo"`
	ISSN           string     `json:"issn"`
	Periodicidade  string     `json:"periodicidade"`
	Editora        string     `json:"editora"`
	DataPublicacao *time.Time `json:"data_publicacao"`
	Condicao       string     `json:"condicao,omitempty"`
	IDBiblioteca   int        `json:"id_biblioteca"`
}

type DVD struct {
	ID             int        `json:"id_dvd"`
	Titulo         string     `json:"titulo"`
	ISAN           string     `json:"isan"`
	Duracao        int        `json:"duracao"`
	Distribuidora  string     `json:"distribuidora"`
	DataLancamento *time.Time `json:"data_lancamento"`
	Condicao       string     `json:"condicao,omitempty"`
	IDBiblioteca   int        `json:"id_biblioteca"`
}

type Artigo struct {
	ID             int        `json:"id_artigo"`
	Titulo         string     `json:"titulo"`
	DOI            string     `json:"doi"`
	Publicadora    string     `json:"publicadora"`
	DataPublicacao *time.Time `json:"data_publicacao"`
	Condicao       string     `json:"condicao,omitempty"`
	IDBiblioteca   int        `json:"id_biblioteca"`
}

type Autor struct {
	ID              int        `json:"id_autor"`
	Nome            string     `json:"nome"`
	DataNascimento  *time.Time `json:"data_nascimento"`
	DataFalecimento *time.Time `json:"data_falecimento"`
}

type Autoria struct {
	ID        int    `json:"id_autorias"`
	IDAutor   int    `json:"id_autor"`
	IDMidia   int    `json:"id_midia"`
	NomeAutor string `json:"nome_autor,omitempty"`
	TipoMidia string `json:"tipo_midia,omitempty"`
}

type Penalizacao struct {
	ID               int        `json:"id_penalizacao"`
	Descricao        string     `json:"descricao"`
	FinalPenalizacao *time.Time `json:"final_penalizacao"`
	IDUsuario        int        `json:"id_usuario"`
	IDEmprestimo     int        `json:"id_emprestimo"`
	NomeUsuario      string     `json:"nome_usuario,omitempty"`
}
