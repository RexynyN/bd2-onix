package models

import (
	"database/sql"
)

type Usuario struct {
	IDUsuario int    `json:"id_usuario"`
	Nome      string `json:"nome"`
	Email     string `json:"email"`
	Endereco  string `json:"endereco"`
	Telefone  string `json:"telefone"`
}

func GetAllUsuarios(db *sql.DB) ([]Usuario, error) {
	rows, err := db.Query("SELECT id_usuario, nome, COALESCE(email, ''), COALESCE(endereco, ''), COALESCE(telefone, '') FROM Usuario ORDER BY nome")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var usuarios []Usuario
	for rows.Next() {
		var u Usuario
		err := rows.Scan(&u.IDUsuario, &u.Nome, &u.Email, &u.Endereco, &u.Telefone)
		if err != nil {
			return nil, err
		}
		usuarios = append(usuarios, u)
	}
	return usuarios, nil
}

func GetUsuarioByID(db *sql.DB, id int) (*Usuario, error) {
	var u Usuario
	err := db.QueryRow("SELECT id_usuario, nome, COALESCE(email, ''), COALESCE(endereco, ''), COALESCE(telefone, '') FROM Usuario WHERE id_usuario = $1", id).
		Scan(&u.IDUsuario, &u.Nome, &u.Email, &u.Endereco, &u.Telefone)
	if err != nil {
		return nil, err
	}
	return &u, nil
}

func CreateUsuario(db *sql.DB, u *Usuario) error {
	err := db.QueryRow("INSERT INTO Usuario (nome, email, endereco, telefone) VALUES ($1, $2, $3, $4) RETURNING id_usuario",
		u.Nome, nullString(u.Email), nullString(u.Endereco), nullString(u.Telefone)).Scan(&u.IDUsuario)
	return err
}

func UpdateUsuario(db *sql.DB, u *Usuario) error {
	_, err := db.Exec("UPDATE Usuario SET nome = $1, email = $2, endereco = $3, telefone = $4 WHERE id_usuario = $5",
		u.Nome, nullString(u.Email), nullString(u.Endereco), nullString(u.Telefone), u.IDUsuario)
	return err
}

func DeleteUsuario(db *sql.DB, id int) error {
	_, err := db.Exec("DELETE FROM Usuario WHERE id_usuario = $1", id)
	return err
}

func nullString(s string) interface{} {
	if s == "" {
		return nil
	}
	return s
}
