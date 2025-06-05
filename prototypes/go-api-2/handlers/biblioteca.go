package handlers

import (
	"biblioteca-api/models"
	"biblioteca-api/utils"
	"database/sql"
	"strconv"
	"time"

	"github.com/gofiber/fiber/v2"
)

type BibliotecaHandler struct {
	db *sql.DB
}

func NewBibliotecaHandler(db *sql.DB) *BibliotecaHandler {
	return &BibliotecaHandler{db: db}
}

// GetBibliotecas obtém todas as bibliotecas
func (h *BibliotecaHandler) GetBibliotecas(c *fiber.Ctx) error {
	page := c.QueryInt("page", 1)
	limit := c.QueryInt("limit", 10)
	offset := (page - 1) * limit

	query := `
		SELECT id_biblioteca, nome, endereco, created_at, updated_at 
		FROM Biblioteca 
		ORDER BY nome 
		LIMIT $1 OFFSET $2
	`

	rows, err := h.db.Query(query, limit, offset)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao buscar bibliotecas", err)
	}
	defer rows.Close()

	var bibliotecas []models.Biblioteca
	for rows.Next() {
		var biblioteca models.Biblioteca
		err := rows.Scan(
			&biblioteca.ID,
			&biblioteca.Nome,
			&biblioteca.Endereco,
			&biblioteca.CreatedAt,
			&biblioteca.UpdatedAt,
		)
		if err != nil {
			return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao processar dados", err)
		}
		bibliotecas = append(bibliotecas, biblioteca)
	}

	// Contagem total
	var total int
	err = h.db.QueryRow("SELECT COUNT(*) FROM Biblioteca").Scan(&total)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao contar bibliotecas", err)
	}

	return c.JSON(utils.PaginatedResponse(bibliotecas, page, limit, total))
}

// GetBiblioteca obtém uma biblioteca por ID
func (h *BibliotecaHandler) GetBiblioteca(c *fiber.Ctx) error {
	id, err := strconv.Atoi(c.Params("id"))
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "ID inválido", err)
	}

	query := `
		SELECT id_biblioteca, nome, endereco, created_at, updated_at 
		FROM Biblioteca 
		WHERE id_biblioteca = $1
	`

	var biblioteca models.Biblioteca
	err = h.db.QueryRow(query, id).Scan(
		&biblioteca.ID,
		&biblioteca.Nome,
		&biblioteca.Endereco,
		&biblioteca.CreatedAt,
		&biblioteca.UpdatedAt,
	)

	if err == sql.ErrNoRows {
		return utils.ErrorResponse(c, fiber.StatusNotFound, "Biblioteca não encontrada", err)
	}
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao buscar biblioteca", err)
	}

	return c.JSON(utils.SuccessResponse(biblioteca))
}

// CreateBiblioteca cria uma nova biblioteca
func (h *BibliotecaHandler) CreateBiblioteca(c *fiber.Ctx) error {
	var req models.CreateBibliotecaRequest
	if err := c.BodyParser(&req); err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "Dados inválidos", err)
	}

	if err := utils.ValidateStruct(req); err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "Validação falhou", err)
	}

	query := `
		INSERT INTO Biblioteca (nome, endereco, created_at, updated_at) 
		VALUES ($1, $2, $3, $4) 
		RETURNING id_biblioteca, created_at, updated_at
	`

	var biblioteca models.Biblioteca
	now := time.Now()
	err := h.db.QueryRow(query, req.Nome, req.Endereco, now, now).Scan(
		&biblioteca.ID,
		&biblioteca.CreatedAt,
		&biblioteca.UpdatedAt,
	)

	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao criar biblioteca", err)
	}

	biblioteca.Nome = req.Nome
	biblioteca.Endereco = req.Endereco

	return c.Status(fiber.StatusCreated).JSON(utils.SuccessResponse(biblioteca))
}

// UpdateBiblioteca atualiza uma biblioteca
func (h *BibliotecaHandler) UpdateBiblioteca(c *fiber.Ctx) error {
	id, err := strconv.Atoi(c.Params("id"))
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "ID inválido", err)
	}

	var req models.CreateBibliotecaRequest
	if err := c.BodyParser(&req); err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "Dados inválidos", err)
	}

	query := `
		UPDATE Biblioteca 
		SET nome = $1, endereco = $2, updated_at = $3 
		WHERE id_biblioteca = $4
	`

	result, err := h.db.Exec(query, req.Nome, req.Endereco, time.Now(), id)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao atualizar biblioteca", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao verificar atualização", err)
	}

	if rowsAffected == 0 {
		return utils.ErrorResponse(c, fiber.StatusNotFound, "Biblioteca não encontrada", nil)
	}

	// Busca a biblioteca atualizada
	return h.GetBiblioteca(c)
}

// DeleteBiblioteca exclui uma biblioteca
func (h *BibliotecaHandler) DeleteBiblioteca(c *fiber.Ctx) error {
	id, err := strconv.Atoi(c.Params("id"))
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "ID inválido", err)
	}

	// Verifica se há mídias associadas
	var midiasCount int
	err = h.db.QueryRow("SELECT COUNT(*) FROM Midia WHERE id_biblioteca = $1", id).Scan(&midiasCount)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao verificar mídias", err)
	}

	if midiasCount > 0 {
		return utils.ErrorResponse(c, fiber.StatusConflict, "Biblioteca possui mídias associadas", nil)
	}

	query := "DELETE FROM Biblioteca WHERE id_biblioteca = $1"
	result, err := h.db.Exec(query, id)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao excluir biblioteca", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao verificar exclusão", err)
	}

	if rowsAffected == 0 {
		return utils.ErrorResponse(c, fiber.StatusNotFound, "Biblioteca não encontrada", nil)
	}

	return c.JSON(utils.SuccessResponse(fiber.Map{"message": "Biblioteca excluída com sucesso"}))
}

// GetBibliotecaMidias obtém todas as mídias de uma biblioteca
func (h *BibliotecaHandler) GetBibliotecaMidias(c *fiber.Ctx) error {
	id, err := strconv.Atoi(c.Params("id"))
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "ID inválido", err)
	}

	page := c.QueryInt("page", 1)
	limit := c.QueryInt("limit", 10)
	offset := (page - 1) * limit
	tipoMidia := c.Query("tipo")

	query := `
		SELECT id_midia, tipo_midia, condicao, id_biblioteca, created_at, updated_at 
		FROM Midia 
		WHERE id_biblioteca = $1
	`

	args := []interface{}{id}
	argCount := 2

	if tipoMidia != "" {
		query += " AND tipo_midia = $" + strconv.Itoa(argCount)
		args = append(args, tipoMidia)
		argCount++
	}

	query += " ORDER BY created_at DESC LIMIT $" + strconv.Itoa(argCount) + " OFFSET $" + strconv.Itoa(argCount+1)
	args = append(args, limit, offset)

	rows, err := h.db.Query(query, args...)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao buscar mídias", err)
	}
	defer rows.Close()

	var midias []models.Midia
	for rows.Next() {
		var midia models.Midia
		err := rows.Scan(
			&midia.ID,
			&midia.TipoMidia,
			&midia.Condicao,
			&midia.IDBiblioteca,
			&midia.CreatedAt,
			&midia.UpdatedAt,
		)
		if err != nil {
			return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao processar dados", err)
		}
		midias = append(midias, midia)
	}

	// Contagem total
	var total int
	countQuery := "SELECT COUNT(*) FROM Midia WHERE id_biblioteca = $1"
	countArgs := []interface{}{id}

	if tipoMidia != "" {
		countQuery += " AND tipo_midia = $2"
		countArgs = append(countArgs, tipoMidia)
	}

	err = h.db.QueryRow(countQuery, countArgs...).Scan(&total)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao contar mídias", err)
	}

	return c.JSON(utils.PaginatedResponse(midias, page, limit, total))
}
