# Agora vou criar os handlers para cada entidade

# Handler para Usuários
handlers_usuario_go = """package handlers

import (
	"biblioteca-api/models"
	"biblioteca-api/utils"
	"database/sql"
	"strconv"
	"time"

	"github.com/gofiber/fiber/v2"
)

type UsuarioHandler struct {
	db *sql.DB
}

func NewUsuarioHandler(db *sql.DB) *UsuarioHandler {
	return &UsuarioHandler{db: db}
}

// GetUsuarios obtém todos os usuários
func (h *UsuarioHandler) GetUsuarios(c *fiber.Ctx) error {
	page := c.QueryInt("page", 1)
	limit := c.QueryInt("limit", 10)
	offset := (page - 1) * limit

	query := `
		SELECT id_usuario, nome, email, endereco, telefone, created_at, updated_at 
		FROM Usuario 
		ORDER BY created_at DESC 
		LIMIT $1 OFFSET $2
	`

	rows, err := h.db.Query(query, limit, offset)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao buscar usuários", err)
	}
	defer rows.Close()

	var usuarios []models.Usuario
	for rows.Next() {
		var usuario models.Usuario
		err := rows.Scan(
			&usuario.ID,
			&usuario.Nome,
			&usuario.Email,
			&usuario.Endereco,
			&usuario.Telefone,
			&usuario.CreatedAt,
			&usuario.UpdatedAt,
		)
		if err != nil {
			return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao processar dados", err)
		}
		usuarios = append(usuarios, usuario)
	}

	// Contagem total
	var total int
	err = h.db.QueryRow("SELECT COUNT(*) FROM Usuario").Scan(&total)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao contar usuários", err)
	}

	return c.JSON(utils.PaginatedResponse(usuarios, page, limit, total))
}

// GetUsuario obtém um usuário por ID
func (h *UsuarioHandler) GetUsuario(c *fiber.Ctx) error {
	id, err := strconv.Atoi(c.Params("id"))
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "ID inválido", err)
	}

	query := `
		SELECT id_usuario, nome, email, endereco, telefone, created_at, updated_at 
		FROM Usuario 
		WHERE id_usuario = $1
	`

	var usuario models.Usuario
	err = h.db.QueryRow(query, id).Scan(
		&usuario.ID,
		&usuario.Nome,
		&usuario.Email,
		&usuario.Endereco,
		&usuario.Telefone,
		&usuario.CreatedAt,
		&usuario.UpdatedAt,
	)

	if err == sql.ErrNoRows {
		return utils.ErrorResponse(c, fiber.StatusNotFound, "Usuário não encontrado", err)
	}
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao buscar usuário", err)
	}

	return c.JSON(utils.SuccessResponse(usuario))
}

// CreateUsuario cria um novo usuário
func (h *UsuarioHandler) CreateUsuario(c *fiber.Ctx) error {
	var req models.CreateUsuarioRequest
	if err := c.BodyParser(&req); err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "Dados inválidos", err)
	}

	if err := utils.ValidateStruct(req); err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "Validação falhou", err)
	}

	query := `
		INSERT INTO Usuario (nome, email, endereco, telefone, created_at, updated_at) 
		VALUES ($1, $2, $3, $4, $5, $6) 
		RETURNING id_usuario, created_at, updated_at
	`

	var usuario models.Usuario
	now := time.Now()
	err := h.db.QueryRow(query, req.Nome, req.Email, req.Endereco, req.Telefone, now, now).Scan(
		&usuario.ID,
		&usuario.CreatedAt,
		&usuario.UpdatedAt,
	)

	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao criar usuário", err)
	}

	usuario.Nome = req.Nome
	usuario.Email = req.Email
	usuario.Endereco = req.Endereco
	usuario.Telefone = req.Telefone

	return c.Status(fiber.StatusCreated).JSON(utils.SuccessResponse(usuario))
}

// UpdateUsuario atualiza um usuário
func (h *UsuarioHandler) UpdateUsuario(c *fiber.Ctx) error {
	id, err := strconv.Atoi(c.Params("id"))
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "ID inválido", err)
	}

	var req models.UpdateUsuarioRequest
	if err := c.BodyParser(&req); err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "Dados inválidos", err)
	}

	// Constrói query dinamicamente baseada nos campos fornecidos
	setParts := []string{}
	args := []interface{}{}
	argCount := 1

	if req.Nome != nil {
		setParts = append(setParts, "nome = $"+strconv.Itoa(argCount))
		args = append(args, *req.Nome)
		argCount++
	}
	if req.Email != nil {
		setParts = append(setParts, "email = $"+strconv.Itoa(argCount))
		args = append(args, *req.Email)
		argCount++
	}
	if req.Endereco != nil {
		setParts = append(setParts, "endereco = $"+strconv.Itoa(argCount))
		args = append(args, *req.Endereco)
		argCount++
	}
	if req.Telefone != nil {
		setParts = append(setParts, "telefone = $"+strconv.Itoa(argCount))
		args = append(args, *req.Telefone)
		argCount++
	}

	if len(setParts) == 0 {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "Nenhum campo para atualizar", nil)
	}

	// Adiciona updated_at
	setParts = append(setParts, "updated_at = $"+strconv.Itoa(argCount))
	args = append(args, time.Now())
	argCount++

	// Adiciona ID como último parâmetro
	args = append(args, id)

	query := "UPDATE Usuario SET " + joinStrings(setParts, ", ") + " WHERE id_usuario = $" + strconv.Itoa(argCount)

	result, err := h.db.Exec(query, args...)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao atualizar usuário", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao verificar atualização", err)
	}

	if rowsAffected == 0 {
		return utils.ErrorResponse(c, fiber.StatusNotFound, "Usuário não encontrado", nil)
	}

	// Busca o usuário atualizado
	return h.GetUsuario(c)
}

// DeleteUsuario exclui um usuário
func (h *UsuarioHandler) DeleteUsuario(c *fiber.Ctx) error {
	id, err := strconv.Atoi(c.Params("id"))
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "ID inválido", err)
	}

	// Verifica se o usuário tem empréstimos ativos
	var emprestimosAtivos int
	err = h.db.QueryRow(
		"SELECT COUNT(*) FROM Emprestimo WHERE id_usuario = $1 AND data_devolucao IS NULL",
		id,
	).Scan(&emprestimosAtivos)

	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao verificar empréstimos", err)
	}

	if emprestimosAtivos > 0 {
		return utils.ErrorResponse(c, fiber.StatusConflict, "Usuário possui empréstimos ativos", nil)
	}

	query := "DELETE FROM Usuario WHERE id_usuario = $1"
	result, err := h.db.Exec(query, id)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao excluir usuário", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao verificar exclusão", err)
	}

	if rowsAffected == 0 {
		return utils.ErrorResponse(c, fiber.StatusNotFound, "Usuário não encontrado", nil)
	}

	return c.JSON(utils.SuccessResponse(fiber.Map{"message": "Usuário excluído com sucesso"}))
}

// GetUsuarioEmprestimos obtém os empréstimos de um usuário
func (h *UsuarioHandler) GetUsuarioEmprestimos(c *fiber.Ctx) error {
	id, err := strconv.Atoi(c.Params("id"))
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "ID inválido", err)
	}

	status := c.Query("status", "")
	
	query := `
		SELECT e.id_emprestimo, e.data_emprestimo, e.data_devolucao_prevista, 
		       e.data_devolucao, e.id_midia, e.id_usuario, e.status, 
		       e.created_at, e.updated_at
		FROM Emprestimo e
		WHERE e.id_usuario = $1
	`
	
	args := []interface{}{id}
	
	if status != "" {
		query += " AND e.status = $2"
		args = append(args, status)
	}
	
	query += " ORDER BY e.created_at DESC"

	rows, err := h.db.Query(query, args...)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao buscar empréstimos", err)
	}
	defer rows.Close()

	var emprestimos []models.Emprestimo
	for rows.Next() {
		var emp models.Emprestimo
		err := rows.Scan(
			&emp.ID,
			&emp.DataEmprestimo,
			&emp.DataDevolucaoPrevista,
			&emp.DataDevolucao,
			&emp.IDMidia,
			&emp.IDUsuario,
			&emp.Status,
			&emp.CreatedAt,
			&emp.UpdatedAt,
		)
		if err != nil {
			return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao processar dados", err)
		}
		emprestimos = append(emprestimos, emp)
	}

	return c.JSON(utils.SuccessResponse(emprestimos))
}

// Helper function para join de strings
func joinStrings(strs []string, sep string) string {
	if len(strs) == 0 {
		return ""
	}
	if len(strs) == 1 {
		return strs[0]
	}
	
	result := strs[0]
	for _, s := range strs[1:] {
		result += sep + s
	}
	return result
}
"""

# Handler para Bibliotecas
handlers_biblioteca_go = """package handlers

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
"""

print("Handlers criados:")
print("✓ handlers/usuario.go")
print("✓ handlers/biblioteca.go")