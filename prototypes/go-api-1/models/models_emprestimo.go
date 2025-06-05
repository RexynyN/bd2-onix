package models

import (
	"database/sql"
	"fmt"
	"time"
)

type Emprestimo struct {
	IDEmprestimo          int        `json:"id_emprestimo"`
	DataEmprestimo        time.Time  `json:"data_emprestimo"`
	DataDevolucaoPrevista *time.Time `json:"data_devolucao_prevista"`
	DataDevolucao         *time.Time `json:"data_devolucao"`
	IDMidia               int        `json:"id_midia"`
	IDUsuario             int        `json:"id_usuario"`

	// Campos relacionados
	NomeUsuario string `json:"nome_usuario,omitempty"`
	TituloMidia string `json:"titulo_midia,omitempty"`
	TipoMidia   string `json:"tipo_midia,omitempty"`
	Status      string `json:"status,omitempty"`
}

func GetAllEmprestimos(db *sql.DB) ([]Emprestimo, error) {
	query := `
		SELECT 
			e.id_emprestimo, e.data_emprestimo, e.data_devolucao_prevista, e.data_devolucao,
			e.id_midia, e.id_usuario, u.nome,
			CASE 
				WHEN m.tipo_midia = 'livro' THEN l.titulo
				WHEN m.tipo_midia = 'revista' THEN r.titulo
				WHEN m.tipo_midia = 'dvd' THEN d.titulo
				WHEN m.tipo_midia = 'artigo' THEN a.titulo
			END as titulo_midia,
			m.tipo_midia
		FROM Emprestimo e
		JOIN Usuario u ON e.id_usuario = u.id_usuario
		JOIN Midia m ON e.id_midia = m.id_midia
		LEFT JOIN Livros l ON m.id_midia = l.id_livro AND m.tipo_midia = 'livro'
		LEFT JOIN Revistas r ON m.id_midia = r.id_revista AND m.tipo_midia = 'revista'
		LEFT JOIN DVDs d ON m.id_midia = d.id_dvd AND m.tipo_midia = 'dvd'
		LEFT JOIN Artigos a ON m.id_midia = a.id_artigo AND m.tipo_midia = 'artigo'
		ORDER BY e.data_emprestimo DESC
		LIMIT 1000
	`

	rows, err := db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	fmt.Println("Consultando empréstimos... [][[][][]]")
	var emprestimos []Emprestimo
	for rows.Next() {

		var e Emprestimo
		err := rows.Scan(&e.IDEmprestimo, &e.DataEmprestimo, &e.DataDevolucaoPrevista, &e.DataDevolucao,
			&e.IDMidia, &e.IDUsuario, &e.NomeUsuario, &e.TituloMidia, &e.TipoMidia)
		if err != nil {
			return nil, err
		}

		// Determinar status
		if e.DataDevolucao != nil {
			e.Status = "devolvido"
		} else if e.DataDevolucaoPrevista != nil && time.Now().After(*e.DataDevolucaoPrevista) {
			e.Status = "atrasado"
		} else {
			e.Status = "ativo"
		}

		emprestimos = append(emprestimos, e)
	}
	return emprestimos, nil
}

func GetEmprestimoByID(db *sql.DB, id int) (*Emprestimo, error) {
	var e Emprestimo
	err := db.QueryRow(`
		SELECT 
			e.id_emprestimo, e.data_emprestimo, e.data_devolucao_prevista, e.data_devolucao,
			e.id_midia, e.id_usuario, u.nome,
			CASE 
				WHEN m.tipo_midia = 'livro' THEN l.titulo
				WHEN m.tipo_midia = 'revista' THEN r.titulo
				WHEN m.tipo_midia = 'dvd' THEN d.titulo
				WHEN m.tipo_midia = 'artigo' THEN a.titulo
			END as titulo_midia,
			m.tipo_midia
		FROM Emprestimo e
		JOIN Usuario u ON e.id_usuario = u.id_usuario
		JOIN Midia m ON e.id_midia = m.id_midia
		LEFT JOIN Livros l ON m.id_midia = l.id_livro AND m.tipo_midia = 'livro'
		LEFT JOIN Revistas r ON m.id_midia = r.id_revista AND m.tipo_midia = 'revista'
		LEFT JOIN DVDs d ON m.id_midia = d.id_dvd AND m.tipo_midia = 'dvd'
		LEFT JOIN Artigos a ON m.id_midia = a.id_artigo AND m.tipo_midia = 'artigo'
		WHERE e.id_emprestimo = $1
	`, id).Scan(&e.IDEmprestimo, &e.DataEmprestimo, &e.DataDevolucaoPrevista, &e.DataDevolucao,
		&e.IDMidia, &e.IDUsuario, &e.NomeUsuario, &e.TituloMidia, &e.TipoMidia)

	if err != nil {
		return nil, err
	}

	// Determinar status
	if e.DataDevolucao != nil {
		e.Status = "devolvido"
	} else if e.DataDevolucaoPrevista != nil && time.Now().After(*e.DataDevolucaoPrevista) {
		e.Status = "atrasado"
	} else {
		e.Status = "ativo"
	}

	return &e, nil
}

func CreateEmprestimo(db *sql.DB, e *Emprestimo) error {
	err := db.QueryRow(`
		INSERT INTO Emprestimo (data_emprestimo, data_devolucao_prevista, id_midia, id_usuario) 
		VALUES ($1, $2, $3, $4) RETURNING id_emprestimo
	`, e.DataEmprestimo, e.DataDevolucaoPrevista, e.IDMidia, e.IDUsuario).Scan(&e.IDEmprestimo)
	return err
}

func UpdateEmprestimo(db *sql.DB, e *Emprestimo) error {
	_, err := db.Exec(`
		UPDATE Emprestimo 
		SET data_emprestimo = $1, data_devolucao_prevista = $2, data_devolucao = $3, id_midia = $4, id_usuario = $5 
		WHERE id_emprestimo = $6
	`, e.DataEmprestimo, e.DataDevolucaoPrevista, e.DataDevolucao, e.IDMidia, e.IDUsuario, e.IDEmprestimo)
	return err
}

func RegistrarDevolucao(db *sql.DB, idEmprestimo int) error {
	_, err := db.Exec("UPDATE Emprestimo SET data_devolucao = CURRENT_DATE WHERE id_emprestimo = $1", idEmprestimo)
	return err
}

func DeleteEmprestimo(db *sql.DB, id int) error {
	_, err := db.Exec("DELETE FROM Emprestimo WHERE id_emprestimo = $1", id)
	return err
}

func GetEmprestimosAtivos(db *sql.DB) ([]Emprestimo, error) {
	query := `
		SELECT 
			e.id_emprestimo, e.data_emprestimo, e.data_devolucao_prevista, e.data_devolucao,
			e.id_midia, e.id_usuario, u.nome,
			CASE 
				WHEN m.tipo_midia = 'livro' THEN l.titulo
				WHEN m.tipo_midia = 'revista' THEN r.titulo
				WHEN m.tipo_midia = 'dvd' THEN d.titulo
				WHEN m.tipo_midia = 'artigo' THEN a.titulo
			END as titulo_midia,
			m.tipo_midia
		FROM Emprestimo e
		JOIN Usuario u ON e.id_usuario = u.id_usuario
		JOIN Midia m ON e.id_midia = m.id_midia
		LEFT JOIN Livros l ON m.id_midia = l.id_livro AND m.tipo_midia = 'livro'
		LEFT JOIN Revistas r ON m.id_midia = r.id_revista AND m.tipo_midia = 'revista'
		LEFT JOIN DVDs d ON m.id_midia = d.id_dvd AND m.tipo_midia = 'dvd'
		LEFT JOIN Artigos a ON m.id_midia = a.id_artigo AND m.tipo_midia = 'artigo'
		WHERE e.data_devolucao IS NULL
		ORDER BY e.data_emprestimo DESC
	`

	rows, err := db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var emprestimos []Emprestimo
	for rows.Next() {
		var e Emprestimo
		err := rows.Scan(&e.IDEmprestimo, &e.DataEmprestimo, &e.DataDevolucaoPrevista, &e.DataDevolucao,
			&e.IDMidia, &e.IDUsuario, &e.NomeUsuario, &e.TituloMidia, &e.TipoMidia)
		if err != nil {
			return nil, err
		}

		// Determinar status
		if e.DataDevolucaoPrevista != nil && time.Now().After(*e.DataDevolucaoPrevista) {
			e.Status = "atrasado"
		} else {
			e.Status = "ativo"
		}

		emprestimos = append(emprestimos, e)
	}
	return emprestimos, nil
}
