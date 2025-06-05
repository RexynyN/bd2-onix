package handlers

import (
	"biblioteca-api/models"
	"biblioteca-api/utils"
	"database/sql"
	"strconv"
	"time"

	"github.com/gofiber/fiber/v2"
)

type LivroHandler struct {
	db *sql.DB
}

func NewLivroHandler(db *sql.DB) *LivroHandler {
	return &LivroHandler{db: db}
}

// GetLivros obtém todos os livros
func (h *LivroHandler) GetLivros(c *fiber.Ctx) error {
	page := c.QueryInt("page", 1)
	limit := c.QueryInt("limit", 10)
	offset := (page - 1) * limit
	search := c.Query("search")
	biblioteca := c.Query("biblioteca")

	query := `
		SELECT l.id_livro, l.titulo, l.isbn, l.numero_paginas, l.editora, l.data_publicacao,
		       l.created_at, l.updated_at,
		       m.condicao, m.id_biblioteca,
		       b.nome as biblioteca_nome,
		       CASE WHEN e.id_emprestimo IS NOT NULL THEN true ELSE false END as emprestado
		FROM Livros l
		INNER JOIN Midia m ON l.id_livro = m.id_midia
		LEFT JOIN Biblioteca b ON m.id_biblioteca = b.id_biblioteca
		LEFT JOIN Emprestimo e ON m.id_midia = e.id_midia AND e.data_devolucao IS NULL AND e.status = 'ativo'
		WHERE m.tipo_midia = 'livro'
	`

	args := []interface{}{}
	argCount := 1

	if search != "" {
		query += " AND (LOWER(l.titulo) LIKE LOWER($" + strconv.Itoa(argCount) + ") OR LOWER(l.isbn) LIKE LOWER($" + strconv.Itoa(argCount) + "))"
		args = append(args, "%"+search+"%")
		argCount++
	}

	if biblioteca != "" {
		bibliotecaID, err := strconv.Atoi(biblioteca)
		if err == nil {
			query += " AND m.id_biblioteca = $" + strconv.Itoa(argCount)
			args = append(args, bibliotecaID)
			argCount++
		}
	}

	query += " ORDER BY l.titulo LIMIT $" + strconv.Itoa(argCount) + " OFFSET $" + strconv.Itoa(argCount+1)
	args = append(args, limit, offset)

	rows, err := h.db.Query(query, args...)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao buscar livros", err)
	}
	defer rows.Close()

	type LivroComDetalhes struct {
		models.Livro
		Condicao       *string `json:"condicao"`
		IDBiblioteca   *int    `json:"id_biblioteca"`
		BibliotecaNome *string `json:"biblioteca_nome"`
		Emprestado     bool    `json:"emprestado"`
	}

	var livros []LivroComDetalhes
	for rows.Next() {
		var livro LivroComDetalhes
		var bibliotecaNome sql.NullString

		err := rows.Scan(
			&livro.ID,
			&livro.Titulo,
			&livro.ISBN,
			&livro.NumeroPaginas,
			&livro.Editora,
			&livro.DataPublicacao,
			&livro.CreatedAt,
			&livro.UpdatedAt,
			&livro.Condicao,
			&livro.IDBiblioteca,
			&bibliotecaNome,
			&livro.Emprestado,
		)
		if err != nil {
			return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao processar dados", err)
		}

		if bibliotecaNome.Valid {
			livro.BibliotecaNome = &bibliotecaNome.String
		}

		livros = append(livros, livro)
	}

	// Contagem total
	var total int
	countQuery := `
		SELECT COUNT(*) 
		FROM Livros l
		INNER JOIN Midia m ON l.id_livro = m.id_midia
		WHERE m.tipo_midia = 'livro'
	`
	countArgs := []interface{}{}
	countArgIndex := 1

	if search != "" {
		countQuery += " AND (LOWER(l.titulo) LIKE LOWER($" + strconv.Itoa(countArgIndex) + ") OR LOWER(l.isbn) LIKE LOWER($" + strconv.Itoa(countArgIndex) + "))"
		countArgs = append(countArgs, "%"+search+"%")
		countArgIndex++
	}

	if biblioteca != "" {
		bibliotecaID, err := strconv.Atoi(biblioteca)
		if err == nil {
			countQuery += " AND m.id_biblioteca = $" + strconv.Itoa(countArgIndex)
			countArgs = append(countArgs, bibliotecaID)
		}
	}

	err = h.db.QueryRow(countQuery, countArgs...).Scan(&total)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao contar livros", err)
	}

	return c.JSON(utils.PaginatedResponse(livros, page, limit, total))
}

// GetLivro obtém um livro por ID
func (h *LivroHandler) GetLivro(c *fiber.Ctx) error {
	id, err := strconv.Atoi(c.Params("id"))
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "ID inválido", err)
	}

	query := `
		SELECT l.id_livro, l.titulo, l.isbn, l.numero_paginas, l.editora, l.data_publicacao,
		       l.created_at, l.updated_at,
		       m.condicao, m.id_biblioteca,
		       b.id_biblioteca, b.nome as biblioteca_nome, b.endereco as biblioteca_endereco,
		       CASE WHEN e.id_emprestimo IS NOT NULL THEN true ELSE false END as emprestado
		FROM Livros l
		INNER JOIN Midia m ON l.id_livro = m.id_midia
		LEFT JOIN Biblioteca b ON m.id_biblioteca = b.id_biblioteca
		LEFT JOIN Emprestimo e ON m.id_midia = e.id_midia AND e.data_devolucao IS NULL AND e.status = 'ativo'
		WHERE l.id_livro = $1
	`

	type LivroDetalhado struct {
		models.Livro
		Condicao     *string            `json:"condicao"`
		IDBiblioteca *int               `json:"id_biblioteca"`
		Biblioteca   *models.Biblioteca `json:"biblioteca,omitempty"`
		Emprestado   bool               `json:"emprestado"`
		Autores      []models.Autor     `json:"autores,omitempty"`
	}

	var livro LivroDetalhado
	var bibliotecaID sql.NullInt64
	var bibliotecaNome, bibliotecaEndereco sql.NullString

	err = h.db.QueryRow(query, id).Scan(
		&livro.ID,
		&livro.Titulo,
		&livro.ISBN,
		&livro.NumeroPaginas,
		&livro.Editora,
		&livro.DataPublicacao,
		&livro.CreatedAt,
		&livro.UpdatedAt,
		&livro.Condicao,
		&livro.IDBiblioteca,
		&bibliotecaID,
		&bibliotecaNome,
		&bibliotecaEndereco,
		&livro.Emprestado,
	)

	if err == sql.ErrNoRows {
		return utils.ErrorResponse(c, fiber.StatusNotFound, "Livro não encontrado", err)
	}
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao buscar livro", err)
	}

	// Adiciona dados da biblioteca se existir
	if bibliotecaID.Valid {
		livro.Biblioteca = &models.Biblioteca{
			ID:       int(bibliotecaID.Int64),
			Nome:     bibliotecaNome.String,
			Endereco: &bibliotecaEndereco.String,
		}
	}

	// Busca autores do livro
	autoresQuery := `
		SELECT a.id_autor, a.nome, a.data_nascimento, a.data_falecimento, a.created_at, a.updated_at
		FROM Autores a
		INNER JOIN Autorias au ON a.id_autor = au.id_autor
		WHERE au.id_midia = $1
		ORDER BY a.nome
	`

	rows, err := h.db.Query(autoresQuery, id)
	if err == nil {
		defer rows.Close()
		for rows.Next() {
			var autor models.Autor
			err := rows.Scan(
				&autor.ID,
				&autor.Nome,
				&autor.DataNascimento,
				&autor.DataFalecimento,
				&autor.CreatedAt,
				&autor.UpdatedAt,
			)
			if err == nil {
				livro.Autores = append(livro.Autores, autor)
			}
		}
	}

	return c.JSON(utils.SuccessResponse(livro))
}

// CreateLivro cria um novo livro
func (h *LivroHandler) CreateLivro(c *fiber.Ctx) error {
	var req models.CreateLivroRequest
	if err := c.BodyParser(&req); err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "Dados inválidos", err)
	}

	if err := utils.ValidateStruct(req); err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "Validação falhou", err)
	}

	// Verifica se a biblioteca existe (se fornecida)
	if req.IDBiblioteca != nil {
		var existe bool
		err := h.db.QueryRow("SELECT EXISTS(SELECT 1 FROM Biblioteca WHERE id_biblioteca = $1)",
			*req.IDBiblioteca).Scan(&existe)
		if err != nil {
			return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao verificar biblioteca", err)
		}
		if !existe {
			return utils.ErrorResponse(c, fiber.StatusBadRequest, "Biblioteca não encontrada", nil)
		}
	}

	// Inicia transação
	tx, err := h.db.Begin()
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao iniciar transação", err)
	}
	defer tx.Rollback()

	// Insere a mídia primeiro
	var midiaID int
	now := time.Now()
	err = tx.QueryRow(`
		INSERT INTO Midia (tipo_midia, condicao, id_biblioteca, created_at, updated_at) 
		VALUES ($1, $2, $3, $4, $5) 
		RETURNING id_midia`,
		models.LivroTipo, req.Condicao, req.IDBiblioteca, now, now).Scan(&midiaID)

	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao criar mídia", err)
	}

	// Insere o livro
	var livro models.Livro
	err = tx.QueryRow(`
		INSERT INTO Livros (id_livro, titulo, isbn, numero_paginas, editora, data_publicacao, created_at, updated_at) 
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8) 
		RETURNING id_livro, created_at, updated_at`,
		midiaID, req.Titulo, req.ISBN, req.NumeroPaginas, req.Editora, req.DataPublicacao, now, now).Scan(
		&livro.ID,
		&livro.CreatedAt,
		&livro.UpdatedAt,
	)

	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao criar livro", err)
	}

	err = tx.Commit()
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao confirmar transação", err)
	}

	livro.Titulo = req.Titulo
	livro.ISBN = req.ISBN
	livro.NumeroPaginas = req.NumeroPaginas
	livro.Editora = req.Editora
	livro.DataPublicacao = req.DataPublicacao

	return c.Status(fiber.StatusCreated).JSON(utils.SuccessResponse(livro))
}

// UpdateLivro atualiza um livro
func (h *LivroHandler) UpdateLivro(c *fiber.Ctx) error {
	id, err := strconv.Atoi(c.Params("id"))
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "ID inválido", err)
	}

	var req models.CreateLivroRequest
	if err := c.BodyParser(&req); err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "Dados inválidos", err)
	}

	// Verifica se a biblioteca existe (se fornecida)
	if req.IDBiblioteca != nil {
		var existe bool
		err := h.db.QueryRow("SELECT EXISTS(SELECT 1 FROM Biblioteca WHERE id_biblioteca = $1)",
			*req.IDBiblioteca).Scan(&existe)
		if err != nil {
			return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao verificar biblioteca", err)
		}
		if !existe {
			return utils.ErrorResponse(c, fiber.StatusBadRequest, "Biblioteca não encontrada", nil)
		}
	}

	// Inicia transação
	tx, err := h.db.Begin()
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao iniciar transação", err)
	}
	defer tx.Rollback()

	// Atualiza o livro
	_, err = tx.Exec(`
		UPDATE Livros 
		SET titulo = $1, isbn = $2, numero_paginas = $3, editora = $4, data_publicacao = $5, updated_at = $6 
		WHERE id_livro = $7`,
		req.Titulo, req.ISBN, req.NumeroPaginas, req.Editora, req.DataPublicacao, time.Now(), id)

	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao atualizar livro", err)
	}

	// Atualiza a mídia
	result, err := tx.Exec(`
		UPDATE Midia 
		SET condicao = $1, id_biblioteca = $2, updated_at = $3 
		WHERE id_midia = $4`,
		req.Condicao, req.IDBiblioteca, time.Now(), id)

	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao atualizar mídia", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao verificar atualização", err)
	}

	if rowsAffected == 0 {
		return utils.ErrorResponse(c, fiber.StatusNotFound, "Livro não encontrado", nil)
	}

	err = tx.Commit()
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao confirmar transação", err)
	}

	// Busca o livro atualizado
	return h.GetLivro(c)
}

// DeleteLivro exclui um livro
func (h *LivroHandler) DeleteLivro(c *fiber.Ctx) error {
	id, err := strconv.Atoi(c.Params("id"))
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "ID inválido", err)
	}

	// Verifica se há empréstimos ativos
	var emprestimosAtivos int
	err = h.db.QueryRow(
		"SELECT COUNT(*) FROM Emprestimo WHERE id_midia = $1 AND data_devolucao IS NULL",
		id,
	).Scan(&emprestimosAtivos)

	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao verificar empréstimos", err)
	}

	if emprestimosAtivos > 0 {
		return utils.ErrorResponse(c, fiber.StatusConflict, "Livro possui empréstimos ativos", nil)
	}

	// Inicia transação para deletar livro e dados relacionados
	tx, err := h.db.Begin()
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao iniciar transação", err)
	}
	defer tx.Rollback()

	// Remove autorias
	_, err = tx.Exec("DELETE FROM Autorias WHERE id_midia = $1", id)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao remover autorias", err)
	}

	// Remove o livro
	_, err = tx.Exec("DELETE FROM Livros WHERE id_livro = $1", id)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao excluir livro", err)
	}

	// Remove a mídia
	result, err := tx.Exec("DELETE FROM Midia WHERE id_midia = $1", id)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao excluir mídia", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao verificar exclusão", err)
	}

	if rowsAffected == 0 {
		return utils.ErrorResponse(c, fiber.StatusNotFound, "Livro não encontrado", nil)
	}

	err = tx.Commit()
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao confirmar transação", err)
	}

	return c.JSON(utils.SuccessResponse(fiber.Map{"message": "Livro excluído com sucesso"}))
}

// AddAutorToLivro adiciona um autor a um livro
func (h *LivroHandler) AddAutorToLivro(c *fiber.Ctx) error {
	livroID, err := strconv.Atoi(c.Params("id"))
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "ID do livro inválido", err)
	}

	type AddAutorRequest struct {
		IDAutor int `json:"id_autor" validate:"required"`
	}

	var req AddAutorRequest
	if err := c.BodyParser(&req); err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "Dados inválidos", err)
	}

	if err := utils.ValidateStruct(req); err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "Validação falhou", err)
	}

	// Verifica se o livro existe
	var livroExiste bool
	err = h.db.QueryRow("SELECT EXISTS(SELECT 1 FROM Livros WHERE id_livro = $1)", livroID).Scan(&livroExiste)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao verificar livro", err)
	}
	if !livroExiste {
		return utils.ErrorResponse(c, fiber.StatusNotFound, "Livro não encontrado", nil)
	}

	// Verifica se o autor existe
	var autorExiste bool
	err = h.db.QueryRow("SELECT EXISTS(SELECT 1 FROM Autores WHERE id_autor = $1)", req.IDAutor).Scan(&autorExiste)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao verificar autor", err)
	}
	if !autorExiste {
		return utils.ErrorResponse(c, fiber.StatusNotFound, "Autor não encontrado", nil)
	}

	// Verifica se a associação já existe
	var associacaoExiste bool
	err = h.db.QueryRow(
		"SELECT EXISTS(SELECT 1 FROM Autorias WHERE id_autor = $1 AND id_midia = $2)",
		req.IDAutor, livroID).Scan(&associacaoExiste)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao verificar associação", err)
	}
	if associacaoExiste {
		return utils.ErrorResponse(c, fiber.StatusConflict, "Autor já associado ao livro", nil)
	}

	// Cria a associação
	_, err = h.db.Exec(
		"INSERT INTO Autorias (id_autor, id_midia, created_at) VALUES ($1, $2, $3)",
		req.IDAutor, livroID, time.Now())

	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao associar autor", err)
	}

	return c.JSON(utils.SuccessResponse(fiber.Map{"message": "Autor associado com sucesso"}))
}

// RemoveAutorFromLivro remove um autor de um livro
func (h *LivroHandler) RemoveAutorFromLivro(c *fiber.Ctx) error {
	livroID, err := strconv.Atoi(c.Params("id"))
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "ID do livro inválido", err)
	}

	autorID, err := strconv.Atoi(c.Params("autor_id"))
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "ID do autor inválido", err)
	}

	result, err := h.db.Exec(
		"DELETE FROM Autorias WHERE id_autor = $1 AND id_midia = $2",
		autorID, livroID)

	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao remover associação", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao verificar remoção", err)
	}

	if rowsAffected == 0 {
		return utils.ErrorResponse(c, fiber.StatusNotFound, "Associação não encontrada", nil)
	}

	return c.JSON(utils.SuccessResponse(fiber.Map{"message": "Associação removida com sucesso"}))
}
