package handlers

import (
	"biblioteca-api/models"
	"biblioteca-api/utils"
	"database/sql"
	"strconv"
	"time"

	"github.com/gofiber/fiber/v2"
)

type EmprestimoHandler struct {
	db *sql.DB
}

func NewEmprestimoHandler(db *sql.DB) *EmprestimoHandler {
	return &EmprestimoHandler{db: db}
}

// GetEmprestimos obtém todos os empréstimos
func (h *EmprestimoHandler) GetEmprestimos(c *fiber.Ctx) error {
	page := c.QueryInt("page", 1)
	limit := c.QueryInt("limit", 10)
	offset := (page - 1) * limit
	status := c.Query("status")
	usuario := c.Query("usuario")

	query := `
		SELECT e.id_emprestimo, e.data_emprestimo, e.data_devolucao_prevista, 
		       e.data_devolucao, e.id_midia, e.id_usuario, e.status, 
		       e.created_at, e.updated_at,
		       u.nome as usuario_nome, u.email as usuario_email,
		       m.tipo_midia, m.condicao
		FROM Emprestimo e
		INNER JOIN Usuario u ON e.id_usuario = u.id_usuario
		INNER JOIN Midia m ON e.id_midia = m.id_midia
		WHERE 1=1
	`

	args := []interface{}{}
	argCount := 1

	if status != "" {
		query += " AND e.status = $" + strconv.Itoa(argCount)
		args = append(args, status)
		argCount++
	}

	if usuario != "" {
		usuarioID, err := strconv.Atoi(usuario)
		if err == nil {
			query += " AND e.id_usuario = $" + strconv.Itoa(argCount)
			args = append(args, usuarioID)
			argCount++
		}
	}

	query += " ORDER BY e.created_at DESC LIMIT $" + strconv.Itoa(argCount) + " OFFSET $" + strconv.Itoa(argCount+1)
	args = append(args, limit, offset)

	rows, err := h.db.Query(query, args...)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao buscar empréstimos", err)
	}
	defer rows.Close()

	var emprestimos []models.EmprestimoDetalhado
	for rows.Next() {
		var emp models.EmprestimoDetalhado
		var usuarioEmail sql.NullString

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
			&emp.Usuario.Nome,
			&usuarioEmail,
			&emp.Midia.TipoMidia,
			&emp.Midia.Condicao,
		)
		if err != nil {
			return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao processar dados", err)
		}

		emp.Usuario.ID = emp.IDUsuario
		if usuarioEmail.Valid {
			emp.Usuario.Email = &usuarioEmail.String
		}
		emp.Midia.ID = emp.IDMidia

		emprestimos = append(emprestimos, emp)
	}

	// Contagem total
	var total int
	countQuery := "SELECT COUNT(*) FROM Emprestimo WHERE 1=1"
	countArgs := []interface{}{}
	countArgIndex := 1

	if status != "" {
		countQuery += " AND status = $" + strconv.Itoa(countArgIndex)
		countArgs = append(countArgs, status)
		countArgIndex++
	}

	if usuario != "" {
		usuarioID, err := strconv.Atoi(usuario)
		if err == nil {
			countQuery += " AND id_usuario = $" + strconv.Itoa(countArgIndex)
			countArgs = append(countArgs, usuarioID)
		}
	}

	err = h.db.QueryRow(countQuery, countArgs...).Scan(&total)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao contar empréstimos", err)
	}

	return c.JSON(utils.PaginatedResponse(emprestimos, page, limit, total))
}

// GetEmprestimo obtém um empréstimo por ID
func (h *EmprestimoHandler) GetEmprestimo(c *fiber.Ctx) error {
	id, err := strconv.Atoi(c.Params("id"))
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "ID inválido", err)
	}

	query := `
		SELECT e.id_emprestimo, e.data_emprestimo, e.data_devolucao_prevista, 
		       e.data_devolucao, e.id_midia, e.id_usuario, e.status, 
		       e.created_at, e.updated_at,
		       u.id_usuario, u.nome, u.email, u.endereco, u.telefone,
		       m.id_midia, m.tipo_midia, m.condicao, m.id_biblioteca
		FROM Emprestimo e
		INNER JOIN Usuario u ON e.id_usuario = u.id_usuario
		INNER JOIN Midia m ON e.id_midia = m.id_midia
		WHERE e.id_emprestimo = $1
	`

	var emp models.EmprestimoDetalhado
	err = h.db.QueryRow(query, id).Scan(
		&emp.ID,
		&emp.DataEmprestimo,
		&emp.DataDevolucaoPrevista,
		&emp.DataDevolucao,
		&emp.IDMidia,
		&emp.IDUsuario,
		&emp.Status,
		&emp.CreatedAt,
		&emp.UpdatedAt,
		&emp.Usuario.ID,
		&emp.Usuario.Nome,
		&emp.Usuario.Email,
		&emp.Usuario.Endereco,
		&emp.Usuario.Telefone,
		&emp.Midia.ID,
		&emp.Midia.TipoMidia,
		&emp.Midia.Condicao,
		&emp.Midia.IDBiblioteca,
	)

	if err == sql.ErrNoRows {
		return utils.ErrorResponse(c, fiber.StatusNotFound, "Empréstimo não encontrado", err)
	}
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao buscar empréstimo", err)
	}

	return c.JSON(utils.SuccessResponse(emp))
}

// CreateEmprestimo cria um novo empréstimo
func (h *EmprestimoHandler) CreateEmprestimo(c *fiber.Ctx) error {
	var req models.CreateEmprestimoRequest
	if err := c.BodyParser(&req); err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "Dados inválidos", err)
	}

	if err := utils.ValidateStruct(req); err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "Validação falhou", err)
	}

	// Verifica se o usuário existe
	var usuarioExiste bool
	err := h.db.QueryRow("SELECT EXISTS(SELECT 1 FROM Usuario WHERE id_usuario = $1)",
		req.IDUsuario).Scan(&usuarioExiste)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao verificar usuário", err)
	}
	if !usuarioExiste {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "Usuário não encontrado", nil)
	}

	// Verifica se a mídia existe
	var midiaExiste bool
	err = h.db.QueryRow("SELECT EXISTS(SELECT 1 FROM Midia WHERE id_midia = $1)",
		req.IDMidia).Scan(&midiaExiste)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao verificar mídia", err)
	}
	if !midiaExiste {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "Mídia não encontrada", nil)
	}

	// Verifica se a mídia já está emprestada
	var emprestimoAtivo bool
	err = h.db.QueryRow(`
		SELECT EXISTS(SELECT 1 FROM Emprestimo 
		WHERE id_midia = $1 AND data_devolucao IS NULL AND status = 'ativo')`,
		req.IDMidia).Scan(&emprestimoAtivo)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao verificar disponibilidade", err)
	}
	if emprestimoAtivo {
		return utils.ErrorResponse(c, fiber.StatusConflict, "Mídia já está emprestada", nil)
	}

	// Verifica se o usuário tem penalidades ativas
	var penalizacaoAtiva bool
	err = h.db.QueryRow(`
		SELECT EXISTS(SELECT 1 FROM Penalizacao 
		WHERE id_usuario = $1 AND (final_penalizacao IS NULL OR final_penalizacao > CURRENT_DATE))`,
		req.IDUsuario).Scan(&penalizacaoAtiva)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao verificar penalizações", err)
	}
	if penalizacaoAtiva {
		return utils.ErrorResponse(c, fiber.StatusConflict, "Usuário possui penalizações ativas", nil)
	}

	// Define data de devolução prevista se não fornecida (15 dias por padrão)
	if req.DataDevolucaoPrevista == nil {
		dataPrevista := req.DataEmprestimo.AddDate(0, 0, 15)
		req.DataDevolucaoPrevista = &dataPrevista
	}

	query := `
		INSERT INTO Emprestimo (data_emprestimo, data_devolucao_prevista, id_midia, id_usuario, status, created_at, updated_at) 
		VALUES ($1, $2, $3, $4, $5, $6, $7) 
		RETURNING id_emprestimo, created_at, updated_at
	`

	var emprestimo models.Emprestimo
	now := time.Now()
	err = h.db.QueryRow(query,
		req.DataEmprestimo,
		req.DataDevolucaoPrevista,
		req.IDMidia,
		req.IDUsuario,
		"ativo",
		now,
		now).Scan(
		&emprestimo.ID,
		&emprestimo.CreatedAt,
		&emprestimo.UpdatedAt,
	)

	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao criar empréstimo", err)
	}

	emprestimo.DataEmprestimo = req.DataEmprestimo
	emprestimo.DataDevolucaoPrevista = req.DataDevolucaoPrevista
	emprestimo.IDMidia = req.IDMidia
	emprestimo.IDUsuario = req.IDUsuario
	emprestimo.Status = "ativo"

	return c.Status(fiber.StatusCreated).JSON(utils.SuccessResponse(emprestimo))
}

// DevolverEmprestimo processa a devolução de um empréstimo
func (h *EmprestimoHandler) DevolverEmprestimo(c *fiber.Ctx) error {
	id, err := strconv.Atoi(c.Params("id"))
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "ID inválido", err)
	}

	type DevolucaoRequest struct {
		DataDevolucao time.Time `json:"data_devolucao"`
		Condicao      *string   `json:"condicao"`
	}

	var req DevolucaoRequest
	if err := c.BodyParser(&req); err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "Dados inválidos", err)
	}

	// Inicia transação
	tx, err := h.db.Begin()
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao iniciar transação", err)
	}
	defer tx.Rollback()

	// Busca o empréstimo
	var emprestimo models.Emprestimo
	err = tx.QueryRow(`
		SELECT id_emprestimo, data_emprestimo, data_devolucao_prevista, 
		       data_devolucao, id_midia, id_usuario, status 
		FROM Emprestimo WHERE id_emprestimo = $1`, id).Scan(
		&emprestimo.ID,
		&emprestimo.DataEmprestimo,
		&emprestimo.DataDevolucaoPrevista,
		&emprestimo.DataDevolucao,
		&emprestimo.IDMidia,
		&emprestimo.IDUsuario,
		&emprestimo.Status,
	)

	if err == sql.ErrNoRows {
		return utils.ErrorResponse(c, fiber.StatusNotFound, "Empréstimo não encontrado", err)
	}
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao buscar empréstimo", err)
	}

	if emprestimo.Status != "ativo" {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "Empréstimo não está ativo", nil)
	}

	if emprestimo.DataDevolucao != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "Empréstimo já foi devolvido", nil)
	}

	// Atualiza o empréstimo
	_, err = tx.Exec(`
		UPDATE Emprestimo 
		SET data_devolucao = $1, status = $2, updated_at = $3 
		WHERE id_emprestimo = $4`,
		req.DataDevolucao, "devolvido", time.Now(), id)

	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao atualizar empréstimo", err)
	}

	// Atualiza condição da mídia se fornecida
	if req.Condicao != nil {
		_, err = tx.Exec(`
			UPDATE Midia 
			SET condicao = $1, updated_at = $2 
			WHERE id_midia = $3`,
			*req.Condicao, time.Now(), emprestimo.IDMidia)

		if err != nil {
			return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao atualizar mídia", err)
		}
	}

	// Verifica se há atraso e cria penalização se necessário
	if emprestimo.DataDevolucaoPrevista != nil && req.DataDevolucao.After(*emprestimo.DataDevolucaoPrevista) {
		diasAtraso := int(req.DataDevolucao.Sub(*emprestimo.DataDevolucaoPrevista).Hours() / 24)
		valorMulta := float64(diasAtraso) * 1.50 // R$ 1,50 por dia de atraso

		_, err = tx.Exec(`
			INSERT INTO Penalizacao (descricao, final_penalizacao, valor, id_usuario, id_emprestimo, created_at, updated_at)
			VALUES ($1, $2, $3, $4, $5, $6, $7)`,
			"Multa por atraso na devolução",
			req.DataDevolucao.AddDate(0, 0, 30), // 30 dias para pagar
			valorMulta,
			emprestimo.IDUsuario,
			emprestimo.ID,
			time.Now(),
			time.Now())

		if err != nil {
			return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao criar penalização", err)
		}
	}

	err = tx.Commit()
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao confirmar transação", err)
	}

	// Busca o empréstimo atualizado
	return h.GetEmprestimo(c)
}

// RenovarEmprestimo renova um empréstimo ativo
func (h *EmprestimoHandler) RenovarEmprestimo(c *fiber.Ctx) error {
	id, err := strconv.Atoi(c.Params("id"))
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "ID inválido", err)
	}

	type RenovacaoRequest struct {
		NovaDataDevolucao time.Time `json:"nova_data_devolucao" validate:"required"`
	}

	var req RenovacaoRequest
	if err := c.BodyParser(&req); err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "Dados inválidos", err)
	}

	if err := utils.ValidateStruct(req); err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "Validação falhou", err)
	}

	// Verifica se o empréstimo existe e está ativo
	var emprestimo models.Emprestimo
	err = h.db.QueryRow(`
		SELECT id_emprestimo, data_emprestimo, data_devolucao_prevista, 
		       id_midia, id_usuario, status 
		FROM Emprestimo WHERE id_emprestimo = $1`, id).Scan(
		&emprestimo.ID,
		&emprestimo.DataEmprestimo,
		&emprestimo.DataDevolucaoPrevista,
		&emprestimo.IDMidia,
		&emprestimo.IDUsuario,
		&emprestimo.Status,
	)

	if err == sql.ErrNoRows {
		return utils.ErrorResponse(c, fiber.StatusNotFound, "Empréstimo não encontrado", err)
	}
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao buscar empréstimo", err)
	}

	if emprestimo.Status != "ativo" {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "Empréstimo não está ativo", nil)
	}

	// Verifica se o usuário tem penalizações ativas
	var penalizacaoAtiva bool
	err = h.db.QueryRow(`
		SELECT EXISTS(SELECT 1 FROM Penalizacao 
		WHERE id_usuario = $1 AND (final_penalizacao IS NULL OR final_penalizacao > CURRENT_DATE))`,
		emprestimo.IDUsuario).Scan(&penalizacaoAtiva)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao verificar penalizações", err)
	}
	if penalizacaoAtiva {
		return utils.ErrorResponse(c, fiber.StatusConflict, "Usuário possui penalizações ativas", nil)
	}

	// Atualiza a data de devolução prevista
	query := `
		UPDATE Emprestimo 
		SET data_devolucao_prevista = $1, updated_at = $2 
		WHERE id_emprestimo = $3
	`

	_, err = h.db.Exec(query, req.NovaDataDevolucao, time.Now(), id)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao renovar empréstimo", err)
	}

	// Busca o empréstimo atualizado
	return h.GetEmprestimo(c)
}

// GetEmprestimosAtrasados obtém empréstimos em atraso
func (h *EmprestimoHandler) GetEmprestimosAtrasados(c *fiber.Ctx) error {
	query := `
		SELECT e.id_emprestimo, e.data_emprestimo, e.data_devolucao_prevista, 
		       e.data_devolucao, e.id_midia, e.id_usuario, e.status, 
		       e.created_at, e.updated_at,
		       u.nome as usuario_nome, u.email as usuario_email, u.telefone,
		       m.tipo_midia, m.condicao
		FROM Emprestimo e
		INNER JOIN Usuario u ON e.id_usuario = u.id_usuario
		INNER JOIN Midia m ON e.id_midia = m.id_midia
		WHERE e.status = 'ativo' 
		  AND e.data_devolucao IS NULL 
		  AND e.data_devolucao_prevista < CURRENT_DATE
		ORDER BY e.data_devolucao_prevista ASC
	`

	rows, err := h.db.Query(query)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao buscar empréstimos atrasados", err)
	}
	defer rows.Close()

	var emprestimos []models.EmprestimoDetalhado
	for rows.Next() {
		var emp models.EmprestimoDetalhado
		var usuarioEmail, telefone sql.NullString

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
			&emp.Usuario.Nome,
			&usuarioEmail,
			&telefone,
			&emp.Midia.TipoMidia,
			&emp.Midia.Condicao,
		)
		if err != nil {
			return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao processar dados", err)
		}

		emp.Usuario.ID = emp.IDUsuario
		if usuarioEmail.Valid {
			emp.Usuario.Email = &usuarioEmail.String
		}
		if telefone.Valid {
			emp.Usuario.Telefone = &telefone.String
		}
		emp.Midia.ID = emp.IDMidia

		emprestimos = append(emprestimos, emp)
	}

	return c.JSON(utils.SuccessResponse(emprestimos))
}
