package handlers

import (
	"biblioteca-api/models"
	"biblioteca-api/utils"
	"database/sql"
	"strconv"
	"time"

	"github.com/gofiber/fiber/v2"
)

type MidiaHandler struct {
	db *sql.DB
}

func NewMidiaHandler(db *sql.DB) *MidiaHandler {
	return &MidiaHandler{db: db}
}

// GetMidias obtém todas as mídias
func (h *MidiaHandler) GetMidias(c *fiber.Ctx) error {
	page := c.QueryInt("page", 1)
	limit := c.QueryInt("limit", 10)
	offset := (page - 1) * limit
	tipoMidia := c.Query("tipo")
	biblioteca := c.Query("biblioteca")

	query := `
		SELECT m.id_midia, m.tipo_midia, m.condicao, m.id_biblioteca, 
		       m.created_at, m.updated_at,
		       b.nome as biblioteca_nome
		FROM Midia m
		LEFT JOIN Biblioteca b ON m.id_biblioteca = b.id_biblioteca
		WHERE 1=1
	`

	args := []interface{}{}
	argCount := 1

	if tipoMidia != "" {
		query += " AND m.tipo_midia = $" + strconv.Itoa(argCount)
		args = append(args, tipoMidia)
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

	query += " ORDER BY m.created_at DESC LIMIT $" + strconv.Itoa(argCount) + " OFFSET $" + strconv.Itoa(argCount+1)
	args = append(args, limit, offset)

	rows, err := h.db.Query(query, args...)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao buscar mídias", err)
	}
	defer rows.Close()

	var midias []models.MidiaDetalhada
	for rows.Next() {
		var midia models.MidiaDetalhada
		var bibliotecaNome sql.NullString

		err := rows.Scan(
			&midia.ID,
			&midia.TipoMidia,
			&midia.Condicao,
			&midia.IDBiblioteca,
			&midia.CreatedAt,
			&midia.UpdatedAt,
			&bibliotecaNome,
		)
		if err != nil {
			return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao processar dados", err)
		}

		if bibliotecaNome.Valid && midia.IDBiblioteca != nil {
			midia.Biblioteca = &models.Biblioteca{
				ID:   *midia.IDBiblioteca,
				Nome: bibliotecaNome.String,
			}
		}

		midias = append(midias, midia)
	}

	// Contagem total
	var total int
	countQuery := "SELECT COUNT(*) FROM Midia WHERE 1=1"
	countArgs := []interface{}{}
	countArgIndex := 1

	if tipoMidia != "" {
		countQuery += " AND tipo_midia = $" + strconv.Itoa(countArgIndex)
		countArgs = append(countArgs, tipoMidia)
		countArgIndex++
	}

	if biblioteca != "" {
		bibliotecaID, err := strconv.Atoi(biblioteca)
		if err == nil {
			countQuery += " AND id_biblioteca = $" + strconv.Itoa(countArgIndex)
			countArgs = append(countArgs, bibliotecaID)
		}
	}

	err = h.db.QueryRow(countQuery, countArgs...).Scan(&total)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao contar mídias", err)
	}

	return c.JSON(utils.PaginatedResponse(midias, page, limit, total))
}

// GetMidia obtém uma mídia por ID com detalhes
func (h *MidiaHandler) GetMidia(c *fiber.Ctx) error {
	id, err := strconv.Atoi(c.Params("id"))
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "ID inválido", err)
	}

	// Busca a mídia base
	query := `
		SELECT m.id_midia, m.tipo_midia, m.condicao, m.id_biblioteca, 
		       m.created_at, m.updated_at,
		       b.id_biblioteca, b.nome, b.endereco
		FROM Midia m
		LEFT JOIN Biblioteca b ON m.id_biblioteca = b.id_biblioteca
		WHERE m.id_midia = $1
	`

	var midia models.MidiaDetalhada
	var bibliotecaID sql.NullInt64
	var bibliotecaNome, bibliotecaEndereco sql.NullString

	err = h.db.QueryRow(query, id).Scan(
		&midia.ID,
		&midia.TipoMidia,
		&midia.Condicao,
		&midia.IDBiblioteca,
		&midia.CreatedAt,
		&midia.UpdatedAt,
		&bibliotecaID,
		&bibliotecaNome,
		&bibliotecaEndereco,
	)

	if err == sql.ErrNoRows {
		return utils.ErrorResponse(c, fiber.StatusNotFound, "Mídia não encontrada", err)
	}
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao buscar mídia", err)
	}

	// Adiciona dados da biblioteca se existir
	if bibliotecaID.Valid {
		midia.Biblioteca = &models.Biblioteca{
			ID:       int(bibliotecaID.Int64),
			Nome:     bibliotecaNome.String,
			Endereco: &bibliotecaEndereco.String,
		}
	}

	// Busca detalhes específicos baseado no tipo
	switch midia.TipoMidia {
	case models.LivroTipo:
		livro, err := h.getLivroDetails(id)
		if err == nil {
			midia.Livro = livro
		}
	case models.RevistaTipo:
		revista, err := h.getRevistaDetails(id)
		if err == nil {
			midia.Revista = revista
		}
	case models.DVDTipo:
		dvd, err := h.getDVDDetails(id)
		if err == nil {
			midia.DVD = dvd
		}
	case models.ArtigoTipo:
		artigo, err := h.getArtigoDetails(id)
		if err == nil {
			midia.Artigo = artigo
		}
	}

	// Busca autores
	autores, err := h.getAutoresByMidia(id)
	if err == nil {
		midia.Autores = autores
	}

	return c.JSON(utils.SuccessResponse(midia))
}

// CreateMidia cria uma nova mídia
func (h *MidiaHandler) CreateMidia(c *fiber.Ctx) error {
	var req models.CreateMidiaRequest
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

	query := `
		INSERT INTO Midia (tipo_midia, condicao, id_biblioteca, created_at, updated_at) 
		VALUES ($1, $2, $3, $4, $5) 
		RETURNING id_midia, created_at, updated_at
	`

	var midia models.Midia
	now := time.Now()
	err := h.db.QueryRow(query, req.TipoMidia, req.Condicao, req.IDBiblioteca, now, now).Scan(
		&midia.ID,
		&midia.CreatedAt,
		&midia.UpdatedAt,
	)

	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao criar mídia", err)
	}

	midia.TipoMidia = req.TipoMidia
	midia.Condicao = req.Condicao
	midia.IDBiblioteca = req.IDBiblioteca

	return c.Status(fiber.StatusCreated).JSON(utils.SuccessResponse(midia))
}

// UpdateMidia atualiza uma mídia
func (h *MidiaHandler) UpdateMidia(c *fiber.Ctx) error {
	id, err := strconv.Atoi(c.Params("id"))
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "ID inválido", err)
	}

	var req models.CreateMidiaRequest
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

	query := `
		UPDATE Midia 
		SET condicao = $1, id_biblioteca = $2, updated_at = $3 
		WHERE id_midia = $4
	`

	result, err := h.db.Exec(query, req.Condicao, req.IDBiblioteca, time.Now(), id)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao atualizar mídia", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao verificar atualização", err)
	}

	if rowsAffected == 0 {
		return utils.ErrorResponse(c, fiber.StatusNotFound, "Mídia não encontrada", nil)
	}

	// Busca a mídia atualizada
	return h.GetMidia(c)
}

// DeleteMidia exclui uma mídia
func (h *MidiaHandler) DeleteMidia(c *fiber.Ctx) error {
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
		return utils.ErrorResponse(c, fiber.StatusConflict, "Mídia possui empréstimos ativos", nil)
	}

	// Inicia transação para deletar mídia e dados relacionados
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

	// Remove detalhes específicos baseado no tipo
	var tipoMidia models.MidiaTipo
	err = tx.QueryRow("SELECT tipo_midia FROM Midia WHERE id_midia = $1", id).Scan(&tipoMidia)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao buscar tipo da mídia", err)
	}

	switch tipoMidia {
	case models.LivroTipo:
		_, err = tx.Exec("DELETE FROM Livros WHERE id_livro = $1", id)
	case models.RevistaTipo:
		_, err = tx.Exec("DELETE FROM Revistas WHERE id_revista = $1", id)
	case models.DVDTipo:
		_, err = tx.Exec("DELETE FROM DVDs WHERE id_dvd = $1", id)
	case models.ArtigoTipo:
		_, err = tx.Exec("DELETE FROM Artigos WHERE id_artigo = $1", id)
	}

	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao remover detalhes da mídia", err)
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
		return utils.ErrorResponse(c, fiber.StatusNotFound, "Mídia não encontrada", nil)
	}

	err = tx.Commit()
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao confirmar transação", err)
	}

	return c.JSON(utils.SuccessResponse(fiber.Map{"message": "Mídia excluída com sucesso"}))
}

// Métodos auxiliares para buscar detalhes específicos
func (h *MidiaHandler) getLivroDetails(idMidia int) (*models.Livro, error) {
	query := `
		SELECT id_livro, titulo, isbn, numero_paginas, editora, data_publicacao, created_at, updated_at
		FROM Livros WHERE id_livro = $1
	`

	var livro models.Livro
	err := h.db.QueryRow(query, idMidia).Scan(
		&livro.ID,
		&livro.Titulo,
		&livro.ISBN,
		&livro.NumeroPaginas,
		&livro.Editora,
		&livro.DataPublicacao,
		&livro.CreatedAt,
		&livro.UpdatedAt,
	)

	return &livro, err
}

func (h *MidiaHandler) getRevistaDetails(idMidia int) (*models.Revista, error) {
	query := `
		SELECT id_revista, titulo, issn, periodicidade, editora, data_publicacao, created_at, updated_at
		FROM Revistas WHERE id_revista = $1
	`

	var revista models.Revista
	err := h.db.QueryRow(query, idMidia).Scan(
		&revista.ID,
		&revista.Titulo,
		&revista.ISSN,
		&revista.Periodicidade,
		&revista.Editora,
		&revista.DataPublicacao,
		&revista.CreatedAt,
		&revista.UpdatedAt,
	)

	return &revista, err
}

func (h *MidiaHandler) getDVDDetails(idMidia int) (*models.DVD, error) {
	query := `
		SELECT id_dvd, titulo, isan, duracao, distribuidora, data_lancamento, created_at, updated_at
		FROM DVDs WHERE id_dvd = $1
	`

	var dvd models.DVD
	err := h.db.QueryRow(query, idMidia).Scan(
		&dvd.ID,
		&dvd.Titulo,
		&dvd.ISAN,
		&dvd.Duracao,
		&dvd.Distribuidora,
		&dvd.DataLancamento,
		&dvd.CreatedAt,
		&dvd.UpdatedAt,
	)

	return &dvd, err
}

func (h *MidiaHandler) getArtigoDetails(idMidia int) (*models.Artigo, error) {
	query := `
		SELECT id_artigo, titulo, doi, publicadora, data_publicacao, created_at, updated_at
		FROM Artigos WHERE id_artigo = $1
	`

	var artigo models.Artigo
	err := h.db.QueryRow(query, idMidia).Scan(
		&artigo.ID,
		&artigo.Titulo,
		&artigo.DOI,
		&artigo.Publicadora,
		&artigo.DataPublicacao,
		&artigo.CreatedAt,
		&artigo.UpdatedAt,
	)

	return &artigo, err
}

func (h *MidiaHandler) getAutoresByMidia(idMidia int) ([]models.Autor, error) {
	query := `
		SELECT a.id_autor, a.nome, a.data_nascimento, a.data_falecimento, a.created_at, a.updated_at
		FROM Autores a
		INNER JOIN Autorias au ON a.id_autor = au.id_autor
		WHERE au.id_midia = $1
		ORDER BY a.nome
	`

	rows, err := h.db.Query(query, idMidia)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var autores []models.Autor
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
		if err != nil {
			return nil, err
		}
		autores = append(autores, autor)
	}

	return autores, nil
}
