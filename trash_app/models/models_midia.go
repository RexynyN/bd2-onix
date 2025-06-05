package models

import (
	"database/sql"
	"time"
)

type Midia struct {
	IDMidia        int    `json:"id_midia"`
	TipoMidia      string `json:"tipo_midia"`
	Condicao       string `json:"condicao"`
	IDBiblioteca   int    `json:"id_biblioteca"`
	BibliotecaNome string `json:"biblioteca_nome,omitempty"`

	// Campos específicos por tipo
	Titulo         string     `json:"titulo,omitempty"`
	ISBN           string     `json:"isbn,omitempty"`
	ISSN           string     `json:"issn,omitempty"`
	ISAN           string     `json:"isan,omitempty"`
	DOI            string     `json:"doi,omitempty"`
	NumeroPaginas  int        `json:"numero_paginas,omitempty"`
	Duracao        int        `json:"duracao,omitempty"`
	Editora        string     `json:"editora,omitempty"`
	Distribuidora  string     `json:"distribuidora,omitempty"`
	Publicadora    string     `json:"publicadora,omitempty"`
	Periodicidade  string     `json:"periodicidade,omitempty"`
	DataPublicacao *time.Time `json:"data_publicacao,omitempty"`
	DataLancamento *time.Time `json:"data_lancamento,omitempty"`
}

func GetAllMidias(db *sql.DB) ([]Midia, error) {
	query := `
		SELECT 
			m.id_midia, m.tipo_midia, COALESCE(m.condicao, ''), m.id_biblioteca, b.nome,
			CASE 
				WHEN m.tipo_midia = 'livro' THEN l.titulo
				WHEN m.tipo_midia = 'revista' THEN r.titulo
				WHEN m.tipo_midia = 'dvd' THEN d.titulo
				WHEN m.tipo_midia = 'artigo' THEN a.titulo
			END as titulo,
			CASE 
				WHEN m.tipo_midia = 'livro' THEN l.ISBN
				ELSE ''
			END as isbn,
			CASE 
				WHEN m.tipo_midia = 'revista' THEN r.ISSN
				ELSE ''
			END as issn,
			CASE 
				WHEN m.tipo_midia = 'dvd' THEN d.ISAN
				ELSE ''
			END as isan,
			CASE 
				WHEN m.tipo_midia = 'artigo' THEN a.DOI
				ELSE ''
			END as doi
		FROM Midia m
		JOIN Biblioteca b ON m.id_biblioteca = b.id_biblioteca
		LEFT JOIN Livros l ON m.id_midia = l.id_livro AND m.tipo_midia = 'livro'
		LEFT JOIN Revistas r ON m.id_midia = r.id_revista AND m.tipo_midia = 'revista'
		LEFT JOIN DVDs d ON m.id_midia = d.id_dvd AND m.tipo_midia = 'dvd'
		LEFT JOIN Artigos a ON m.id_midia = a.id_artigo AND m.tipo_midia = 'artigo'
		ORDER BY titulo
	`

	rows, err := db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var midias []Midia
	for rows.Next() {
		var m Midia
		err := rows.Scan(&m.IDMidia, &m.TipoMidia, &m.Condicao, &m.IDBiblioteca, &m.BibliotecaNome,
			&m.Titulo, &m.ISBN, &m.ISSN, &m.ISAN, &m.DOI)
		if err != nil {
			return nil, err
		}
		midias = append(midias, m)
	}
	return midias, nil
}

func GetMidiaByID(db *sql.DB, id int) (*Midia, error) {
	var m Midia
	err := db.QueryRow(`
		SELECT m.id_midia, m.tipo_midia, COALESCE(m.condicao, ''), m.id_biblioteca, b.nome
		FROM Midia m
		JOIN Biblioteca b ON m.id_biblioteca = b.id_biblioteca
		WHERE m.id_midia = $1
	`, id).Scan(&m.IDMidia, &m.TipoMidia, &m.Condicao, &m.IDBiblioteca, &m.BibliotecaNome)

	if err != nil {
		return nil, err
	}

	// Buscar detalhes específicos baseado no tipo
	switch m.TipoMidia {
	case "livro":
		err = db.QueryRow("SELECT titulo, COALESCE(ISBN, ''), COALESCE(numero_paginas, 0), COALESCE(editora, ''), data_publicacao FROM Livros WHERE id_livro = $1", id).
			Scan(&m.Titulo, &m.ISBN, &m.NumeroPaginas, &m.Editora, &m.DataPublicacao)
	case "revista":
		err = db.QueryRow("SELECT titulo, COALESCE(ISSN, ''), COALESCE(periodicidade, ''), COALESCE(editora, ''), data_publicacao FROM Revistas WHERE id_revista = $1", id).
			Scan(&m.Titulo, &m.ISSN, &m.Periodicidade, &m.Editora, &m.DataPublicacao)
	case "dvd":
		err = db.QueryRow("SELECT titulo, COALESCE(ISAN, ''), COALESCE(duracao, 0), COALESCE(distribuidora, ''), data_lancamento FROM DVDs WHERE id_dvd = $1", id).
			Scan(&m.Titulo, &m.ISAN, &m.Duracao, &m.Distribuidora, &m.DataLancamento)
	case "artigo":
		err = db.QueryRow("SELECT titulo, COALESCE(DOI, ''), COALESCE(publicadora, ''), data_publicacao FROM Artigos WHERE id_artigo = $1", id).
			Scan(&m.Titulo, &m.DOI, &m.Publicadora, &m.DataPublicacao)
	}

	return &m, err
}

func CreateMidia(db *sql.DB, m *Midia) error {
	tx, err := db.Begin()
	if err != nil {
		return err
	}
	defer tx.Rollback()

	// Inserir na tabela Midia
	err = tx.QueryRow("INSERT INTO Midia (tipo_midia, condicao, id_biblioteca) VALUES ($1, $2, $3) RETURNING id_midia",
		m.TipoMidia, nullString(m.Condicao), m.IDBiblioteca).Scan(&m.IDMidia)
	if err != nil {
		return err
	}

	// Inserir na tabela específica do tipo
	switch m.TipoMidia {
	case "livro":
		_, err = tx.Exec("INSERT INTO Livros (id_livro, titulo, ISBN, numero_paginas, editora, data_publicacao) VALUES ($1, $2, $3, $4, $5, $6)",
			m.IDMidia, m.Titulo, nullString(m.ISBN), nullInt(m.NumeroPaginas), nullString(m.Editora), m.DataPublicacao)
	case "revista":
		_, err = tx.Exec("INSERT INTO Revistas (id_revista, titulo, ISSN, periodicidade, editora, data_publicacao) VALUES ($1, $2, $3, $4, $5, $6)",
			m.IDMidia, m.Titulo, nullString(m.ISSN), nullString(m.Periodicidade), nullString(m.Editora), m.DataPublicacao)
	case "dvd":
		_, err = tx.Exec("INSERT INTO DVDs (id_dvd, titulo, ISAN, duracao, distribuidora, data_lancamento) VALUES ($1, $2, $3, $4, $5, $6)",
			m.IDMidia, m.Titulo, nullString(m.ISAN), nullInt(m.Duracao), nullString(m.Distribuidora), m.DataLancamento)
	case "artigo":
		_, err = tx.Exec("INSERT INTO Artigos (id_artigo, titulo, DOI, publicadora, data_publicacao) VALUES ($1, $2, $3, $4, $5)",
			m.IDMidia, m.Titulo, nullString(m.DOI), nullString(m.Publicadora), m.DataPublicacao)
	}

	if err != nil {
		return err
	}

	return tx.Commit()
}

func UpdateMidia(db *sql.DB, m *Midia) error {
	tx, err := db.Begin()
	if err != nil {
		return err
	}
	defer tx.Rollback()

	// Atualizar tabela Midia
	_, err = tx.Exec("UPDATE Midia SET condicao = $1, id_biblioteca = $2 WHERE id_midia = $3",
		nullString(m.Condicao), m.IDBiblioteca, m.IDMidia)
	if err != nil {
		return err
	}

	// Atualizar tabela específica do tipo
	switch m.TipoMidia {
	case "livro":
		_, err = tx.Exec("UPDATE Livros SET titulo = $1, ISBN = $2, numero_paginas = $3, editora = $4, data_publicacao = $5 WHERE id_livro = $6",
			m.Titulo, nullString(m.ISBN), nullInt(m.NumeroPaginas), nullString(m.Editora), m.DataPublicacao, m.IDMidia)
	case "revista":
		_, err = tx.Exec("UPDATE Revistas SET titulo = $1, ISSN = $2, periodicidade = $3, editora = $4, data_publicacao = $5 WHERE id_revista = $6",
			m.Titulo, nullString(m.ISSN), nullString(m.Periodicidade), nullString(m.Editora), m.DataPublicacao, m.IDMidia)
	case "dvd":
		_, err = tx.Exec("UPDATE DVDs SET titulo = $1, ISAN = $2, duracao = $3, distribuidora = $4, data_lancamento = $5 WHERE id_dvd = $6",
			m.Titulo, nullString(m.ISAN), nullInt(m.Duracao), nullString(m.Distribuidora), m.DataLancamento, m.IDMidia)
	case "artigo":
		_, err = tx.Exec("UPDATE Artigos SET titulo = $1, DOI = $2, publicadora = $3, data_publicacao = $4 WHERE id_artigo = $5",
			m.Titulo, nullString(m.DOI), nullString(m.Publicadora), m.DataPublicacao, m.IDMidia)
	}

	if err != nil {
		return err
	}

	return tx.Commit()
}

func DeleteMidia(db *sql.DB, id int) error {
	tx, err := db.Begin()
	if err != nil {
		return err
	}
	defer tx.Rollback()

	// Primeiro obter o tipo da mídia
	var tipoMidia string
	err = tx.QueryRow("SELECT tipo_midia FROM Midia WHERE id_midia = $1", id).Scan(&tipoMidia)
	if err != nil {
		return err
	}

	// Deletar da tabela específica
	switch tipoMidia {
	case "livro":
		_, err = tx.Exec("DELETE FROM Livros WHERE id_livro = $1", id)
	case "revista":
		_, err = tx.Exec("DELETE FROM Revistas WHERE id_revista = $1", id)
	case "dvd":
		_, err = tx.Exec("DELETE FROM DVDs WHERE id_dvd = $1", id)
	case "artigo":
		_, err = tx.Exec("DELETE FROM Artigos WHERE id_artigo = $1", id)
	}

	if err != nil {
		return err
	}

	// Deletar da tabela Midia
	_, err = tx.Exec("DELETE FROM Midia WHERE id_midia = $1", id)
	if err != nil {
		return err
	}

	return tx.Commit()
}

func nullInt(i int) interface{} {
	if i == 0 {
		return nil
	}
	return i
}
