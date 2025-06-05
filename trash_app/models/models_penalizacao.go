package models

import (
	"database/sql"
	"time"
)

type Penalizacao struct {
	IDPenalizacao   int        `json:"id_penalizacao"`
	Descricao       string     `json:"descricao"`
	FinalPenalizacao *time.Time `json:"final_penalizacao"`
	IDUsuario       int        `json:"id_usuario"`
	IDEmprestimo    int        `json:"id_emprestimo"`

	// Campos relacionados
	NomeUsuario string `json:"nome_usuario,omitempty"`
	Status      string `json:"status,omitempty"`
}

func GetAllPenalizacoes(db *sql.DB) ([]Penalizacao, error) {
	query := `
		SELECT 
			p.id_penalizacao, COALESCE(p.descricao, ''), p.Final_penalizacao,
			p.id_usuario, COALESCE(p.id_emprestimo, 0), u.nome
		FROM Penalizacao p
		JOIN Usuario u ON p.id_usuario = u.id_usuario
		ORDER BY p.Final_penalizacao DESC
	`

	rows, err := db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var penalizacoes []Penalizacao
	for rows.Next() {
		var p Penalizacao
		err := rows.Scan(&p.IDPenalizacao, &p.Descricao, &p.FinalPenalizacao,
			&p.IDUsuario, &p.IDEmprestimo, &p.NomeUsuario)
		if err != nil {
			return nil, err
		}

		// Determinar status
		if p.FinalPenalizacao != nil && time.Now().After(*p.FinalPenalizacao) {
			p.Status = "expirada"
		} else {
			p.Status = "ativa"
		}

		penalizacoes = append(penalizacoes, p)
	}
	return penalizacoes, nil
}

func GetPenalizacaoByID(db *sql.DB, id int) (*Penalizacao, error) {
	var p Penalizacao
	err := db.QueryRow(`
		SELECT 
			p.id_penalizacao, COALESCE(p.descricao, ''), p.Final_penalizacao,
			p.id_usuario, COALESCE(p.id_emprestimo, 0), u.nome
		FROM Penalizacao p
		JOIN Usuario u ON p.id_usuario = u.id_usuario
		WHERE p.id_penalizacao = $1
	`, id).Scan(&p.IDPenalizacao, &p.Descricao, &p.FinalPenalizacao,
		&p.IDUsuario, &p.IDEmprestimo, &p.NomeUsuario)

	if err != nil {
		return nil, err
	}

	// Determinar status
	if p.FinalPenalizacao != nil && time.Now().After(*p.FinalPenalizacao) {
		p.Status = "expirada"
	} else {
		p.Status = "ativa"
	}

	return &p, nil
}

func CreatePenalizacao(db *sql.DB, p *Penalizacao) error {
	var idEmprestimo interface{}
	if p.IDEmprestimo == 0 {
		idEmprestimo = nil
	} else {
		idEmprestimo = p.IDEmprestimo
	}

	err := db.QueryRow(`
		INSERT INTO Penalizacao (descricao, Final_penalizacao, id_usuario, id_emprestimo) 
		VALUES ($1, $2, $3, $4) RETURNING id_penalizacao
	`, nullString(p.Descricao), p.FinalPenalizacao, p.IDUsuario, idEmprestimo).Scan(&p.IDPenalizacao)
	return err
}

func UpdatePenalizacao(db *sql.DB, p *Penalizacao) error {
	var idEmprestimo interface{}
	if p.IDEmprestimo == 0 {
		idEmprestimo = nil
	} else {
		idEmprestimo = p.IDEmprestimo
	}

	_, err := db.Exec(`
		UPDATE Penalizacao 
		SET descricao = $1, Final_penalizacao = $2, id_usuario = $3, id_emprestimo = $4 
		WHERE id_penalizacao = $5
	`, nullString(p.Descricao), p.FinalPenalizacao, p.IDUsuario, idEmprestimo, p.IDPenalizacao)
	return err
}

func DeletePenalizacao(db *sql.DB, id int) error {
	_, err := db.Exec("DELETE FROM Penalizacao WHERE id_penalizacao = $1", id)
	return err
}
