package models

import (
	"database/sql"
	"time"
)

type Autor struct {
	IDAutor         int        `json:"id_autor"`
	Nome            string     `json:"nome"`
	DataNascimento  *time.Time `json:"data_nascimento"`
	DataFalecimento *time.Time `json:"data_falecimento"`
}

type Autoria struct {
	IDAutorias int `json:"id_autorias"`
	IDAutor    int `json:"id_autor"`
	IDMidia    int `json:"id_midia"`

	// Campos relacionados
	NomeAutor   string `json:"nome_autor,omitempty"`
	TituloMidia string `json:"titulo_midia,omitempty"`
}

func GetAllAutores(db *sql.DB) ([]Autor, error) {
	rows, err := db.Query("SELECT id_autor, nome, data_nascimento, data_falecimento FROM Autores ORDER BY nome")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var autores []Autor
	for rows.Next() {
		var a Autor
		err := rows.Scan(&a.IDAutor, &a.Nome, &a.DataNascimento, &a.DataFalecimento)
		if err != nil {
			return nil, err
		}
		autores = append(autores, a)
	}
	return autores, nil
}

func GetAutorByID(db *sql.DB, id int) (*Autor, error) {
	var a Autor
	err := db.QueryRow("SELECT id_autor, nome, data_nascimento, data_falecimento FROM Autores WHERE id_autor = $1", id).
		Scan(&a.IDAutor, &a.Nome, &a.DataNascimento, &a.DataFalecimento)
	if err != nil {
		return nil, err
	}
	return &a, nil
}

func CreateAutor(db *sql.DB, a *Autor) error {
	err := db.QueryRow("INSERT INTO Autores (nome, data_nascimento, data_falecimento) VALUES ($1, $2, $3) RETURNING id_autor",
		a.Nome, a.DataNascimento, a.DataFalecimento).Scan(&a.IDAutor)
	return err
}

func UpdateAutor(db *sql.DB, a *Autor) error {
	_, err := db.Exec("UPDATE Autores SET nome = $1, data_nascimento = $2, data_falecimento = $3 WHERE id_autor = $4",
		a.Nome, a.DataNascimento, a.DataFalecimento, a.IDAutor)
	return err
}

func DeleteAutor(db *sql.DB, id int) error {
	_, err := db.Exec("DELETE FROM Autores WHERE id_autor = $1", id)
	return err
}

func GetAllAutorias(db *sql.DB) ([]Autoria, error) {
	query := `
		SELECT 
			a.id_autorias, a.id_autor, a.id_midia, au.nome,
			CASE 
				WHEN m.tipo_midia = 'livro' THEN l.titulo
				WHEN m.tipo_midia = 'revista' THEN r.titulo
				WHEN m.tipo_midia = 'dvd' THEN d.titulo
				WHEN m.tipo_midia = 'artigo' THEN ar.titulo
			END as titulo_midia
		FROM Autorias a
		JOIN Autores au ON a.id_autor = au.id_autor
		JOIN Midia m ON a.id_midia = m.id_midia
		LEFT JOIN Livros l ON m.id_midia = l.id_livro AND m.tipo_midia = 'livro'
		LEFT JOIN Revistas r ON m.id_midia = r.id_revista AND m.tipo_midia = 'revista'
		LEFT JOIN DVDs d ON m.id_midia = d.id_dvd AND m.tipo_midia = 'dvd'
		LEFT JOIN Artigos ar ON m.id_midia = ar.id_artigo AND m.tipo_midia = 'artigo'
		ORDER BY au.nome, titulo_midia
	`

	rows, err := db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var autorias []Autoria
	for rows.Next() {
		var a Autoria
		err := rows.Scan(&a.IDAutorias, &a.IDAutor, &a.IDMidia, &a.NomeAutor, &a.TituloMidia)
		if err != nil {
			return nil, err
		}
		autorias = append(autorias, a)
	}
	return autorias, nil
}

func CreateAutoria(db *sql.DB, a *Autoria) error {
	err := db.QueryRow("INSERT INTO Autorias (id_autor, id_midia) VALUES ($1, $2) RETURNING id_autorias",
		a.IDAutor, a.IDMidia).Scan(&a.IDAutorias)
	return err
}

func DeleteAutoria(db *sql.DB, id int) error {
	_, err := db.Exec("DELETE FROM Autorias WHERE id_autorias = $1", id)
	return err
}
