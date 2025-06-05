package models

import "database/sql"

type Biblioteca struct {
	IDBiblioteca int    `json:"id_biblioteca"`
	Nome         string `json:"nome"`
	Endereco     string `json:"endereco"`
}

func GetAllBibliotecas(db *sql.DB) ([]Biblioteca, error) {
	rows, err := db.Query("SELECT id_biblioteca, nome, COALESCE(endereco, '') FROM Biblioteca ORDER BY nome")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var bibliotecas []Biblioteca
	for rows.Next() {
		var b Biblioteca
		err := rows.Scan(&b.IDBiblioteca, &b.Nome, &b.Endereco)
		if err != nil {
			return nil, err
		}
		bibliotecas = append(bibliotecas, b)
	}
	return bibliotecas, nil
}

func GetBibliotecaByID(db *sql.DB, id int) (*Biblioteca, error) {
	var b Biblioteca
	err := db.QueryRow("SELECT id_biblioteca, nome, COALESCE(endereco, '') FROM Biblioteca WHERE id_biblioteca = $1", id).
		Scan(&b.IDBiblioteca, &b.Nome, &b.Endereco)
	if err != nil {
		return nil, err
	}
	return &b, nil
}

func CreateBiblioteca(db *sql.DB, b *Biblioteca) error {
	err := db.QueryRow("INSERT INTO Biblioteca (nome, endereco) VALUES ($1, $2) RETURNING id_biblioteca",
		b.Nome, nullString(b.Endereco)).Scan(&b.IDBiblioteca)
	return err
}

func UpdateBiblioteca(db *sql.DB, b *Biblioteca) error {
	_, err := db.Exec("UPDATE Biblioteca SET nome = $1, endereco = $2 WHERE id_biblioteca = $3",
		b.Nome, nullString(b.Endereco), b.IDBiblioteca)
	return err
}

func DeleteBiblioteca(db *sql.DB, id int) error {
	_, err := db.Exec("DELETE FROM Biblioteca WHERE id_biblioteca = $1", id)
	return err
}
