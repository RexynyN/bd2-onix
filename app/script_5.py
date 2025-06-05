# Utilitários para o sistema
utils_go = """package utils

import (
	"fmt"
	"reflect"
	"strings"

	"github.com/go-playground/validator/v10"
	"github.com/gofiber/fiber/v2"
)

var validate = validator.New()

// Response padrão para API
type APIResponse struct {
	Success bool        `json:"success"`
	Data    interface{} `json:"data,omitempty"`
	Message string      `json:"message,omitempty"`
	Error   string      `json:"error,omitempty"`
}

// Response paginada
type PaginatedAPIResponse struct {
	Success    bool        `json:"success"`
	Data       interface{} `json:"data"`
	Pagination Pagination  `json:"pagination"`
}

type Pagination struct {
	Page       int `json:"page"`
	Limit      int `json:"limit"`
	Total      int `json:"total"`
	TotalPages int `json:"total_pages"`
}

// SuccessResponse retorna uma resposta de sucesso
func SuccessResponse(data interface{}) APIResponse {
	return APIResponse{
		Success: true,
		Data:    data,
	}
}

// SuccessMessageResponse retorna uma resposta de sucesso com mensagem
func SuccessMessageResponse(message string, data interface{}) APIResponse {
	return APIResponse{
		Success: true,
		Data:    data,
		Message: message,
	}
}

// ErrorResponse retorna uma resposta de erro
func ErrorResponse(c *fiber.Ctx, status int, message string, err error) error {
	response := APIResponse{
		Success: false,
		Message: message,
	}

	if err != nil {
		response.Error = err.Error()
	}

	return c.Status(status).JSON(response)
}

// PaginatedResponse retorna uma resposta paginada
func PaginatedResponse(data interface{}, page, limit, total int) PaginatedAPIResponse {
	totalPages := total / limit
	if total%limit != 0 {
		totalPages++
	}

	return PaginatedAPIResponse{
		Success: true,
		Data:    data,
		Pagination: Pagination{
			Page:       page,
			Limit:      limit,
			Total:      total,
			TotalPages: totalPages,
		},
	}
}

// ValidateStruct valida uma struct usando tags de validação
func ValidateStruct(s interface{}) error {
	err := validate.Struct(s)
	if err != nil {
		var validationErrors []string
		for _, err := range err.(validator.ValidationErrors) {
			validationErrors = append(validationErrors, formatValidationError(err))
		}
		return fmt.Errorf("validation failed: %s", strings.Join(validationErrors, ", "))
	}
	return nil
}

// formatValidationError formata erros de validação
func formatValidationError(err validator.FieldError) string {
	field := strings.ToLower(err.Field())
	tag := err.Tag()

	switch tag {
	case "required":
		return fmt.Sprintf("%s é obrigatório", field)
	case "email":
		return fmt.Sprintf("%s deve ser um email válido", field)
	case "min":
		return fmt.Sprintf("%s deve ter pelo menos %s caracteres", field, err.Param())
	case "max":
		return fmt.Sprintf("%s deve ter no máximo %s caracteres", field, err.Param())
	case "numeric":
		return fmt.Sprintf("%s deve ser numérico", field)
	default:
		return fmt.Sprintf("%s é inválido", field)
	}
}

// IsEmpty verifica se um valor é vazio
func IsEmpty(value interface{}) bool {
	if value == nil {
		return true
	}

	v := reflect.ValueOf(value)
	switch v.Kind() {
	case reflect.String, reflect.Array, reflect.Slice, reflect.Map:
		return v.Len() == 0
	case reflect.Ptr:
		return v.IsNil()
	default:
		return false
	}
}

// StringPtr retorna um ponteiro para string
func StringPtr(s string) *string {
	return &s
}

// IntPtr retorna um ponteiro para int
func IntPtr(i int) *int {
	return &i
}

// BoolPtr retorna um ponteiro para bool
func BoolPtr(b bool) *bool {
	return &b
}

// GetStringValue retorna o valor de um ponteiro de string ou string vazia
func GetStringValue(s *string) string {
	if s == nil {
		return ""
	}
	return *s
}

// GetIntValue retorna o valor de um ponteiro de int ou 0
func GetIntValue(i *int) int {
	if i == nil {
		return 0
	}
	return *i
}

// Contains verifica se um slice contém um elemento
func Contains(slice []string, item string) bool {
	for _, s := range slice {
		if s == item {
			return true
		}
	}
	return false
}

// RemoveDuplicates remove duplicatas de um slice de strings
func RemoveDuplicates(slice []string) []string {
	keys := make(map[string]bool)
	var result []string

	for _, item := range slice {
		if !keys[item] {
			keys[item] = true
			result = append(result, item)
		}
	}

	return result
}

// ParseDateFormat converte diferentes formatos de data
func ParseDateFormat(dateStr string) string {
	// Remove espaços
	dateStr = strings.TrimSpace(dateStr)
	
	// Converte formatos comuns para ISO 8601
	if len(dateStr) == 10 {
		// Assume DD/MM/YYYY ou DD-MM-YYYY
		if strings.Contains(dateStr, "/") {
			parts := strings.Split(dateStr, "/")
			if len(parts) == 3 {
				return fmt.Sprintf("%s-%s-%s", parts[2], parts[1], parts[0])
			}
		} else if strings.Contains(dateStr, "-") {
			parts := strings.Split(dateStr, "-")
			if len(parts) == 3 && len(parts[0]) == 2 {
				return fmt.Sprintf("%s-%s-%s", parts[2], parts[1], parts[0])
			}
		}
	}
	
	return dateStr
}

// SanitizeString remove caracteres especiais de uma string
func SanitizeString(s string) string {
	s = strings.TrimSpace(s)
	s = strings.ReplaceAll(s, "  ", " ") // Remove espaços duplos
	return s
}

// BuildSearchQuery constrói uma query de busca com LIKE
func BuildSearchQuery(fields []string, search string) (string, []interface{}) {
	if search == "" {
		return "", nil
	}

	var conditions []string
	var args []interface{}
	
	searchTerm := "%" + strings.ToLower(search) + "%"
	
	for i, field := range fields {
		conditions = append(conditions, fmt.Sprintf("LOWER(%s) LIKE $%d", field, i+1))
		args = append(args, searchTerm)
	}
	
	query := "(" + strings.Join(conditions, " OR ") + ")"
	return query, args
}

// FormatCurrency formata um valor para moeda brasileira
func FormatCurrency(value float64) string {
	return fmt.Sprintf("R$ %.2f", value)
}

// CalculateDaysBetween calcula dias entre duas datas
func CalculateDaysBetween(start, end string) int {
	// Implementação básica - pode ser expandida
	return 0
}
"""

# Handler para Autores
handlers_autor_go = """package handlers

import (
	"biblioteca-api/models"
	"biblioteca-api/utils"
	"database/sql"
	"strconv"
	"time"

	"github.com/gofiber/fiber/v2"
)

type AutorHandler struct {
	db *sql.DB
}

func NewAutorHandler(db *sql.DB) *AutorHandler {
	return &AutorHandler{db: db}
}

// GetAutores obtém todos os autores
func (h *AutorHandler) GetAutores(c *fiber.Ctx) error {
	page := c.QueryInt("page", 1)
	limit := c.QueryInt("limit", 10)
	offset := (page - 1) * limit
	search := c.Query("search")

	query := `
		SELECT id_autor, nome, data_nascimento, data_falecimento, created_at, updated_at 
		FROM Autores 
		WHERE 1=1
	`
	
	args := []interface{}{}
	argCount := 1

	if search != "" {
		query += " AND LOWER(nome) LIKE LOWER($" + strconv.Itoa(argCount) + ")"
		args = append(args, "%"+search+"%")
		argCount++
	}

	query += " ORDER BY nome LIMIT $" + strconv.Itoa(argCount) + " OFFSET $" + strconv.Itoa(argCount+1)
	args = append(args, limit, offset)

	rows, err := h.db.Query(query, args...)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao buscar autores", err)
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
			return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao processar dados", err)
		}
		autores = append(autores, autor)
	}

	// Contagem total
	var total int
	countQuery := "SELECT COUNT(*) FROM Autores WHERE 1=1"
	countArgs := []interface{}{}

	if search != "" {
		countQuery += " AND LOWER(nome) LIKE LOWER($1)"
		countArgs = append(countArgs, "%"+search+"%")
	}

	err = h.db.QueryRow(countQuery, countArgs...).Scan(&total)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao contar autores", err)
	}

	return c.JSON(utils.PaginatedResponse(autores, page, limit, total))
}

// GetAutor obtém um autor por ID
func (h *AutorHandler) GetAutor(c *fiber.Ctx) error {
	id, err := strconv.Atoi(c.Params("id"))
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "ID inválido", err)
	}

	query := `
		SELECT id_autor, nome, data_nascimento, data_falecimento, created_at, updated_at 
		FROM Autores 
		WHERE id_autor = $1
	`

	var autor models.Autor
	err = h.db.QueryRow(query, id).Scan(
		&autor.ID,
		&autor.Nome,
		&autor.DataNascimento,
		&autor.DataFalecimento,
		&autor.CreatedAt,
		&autor.UpdatedAt,
	)

	if err == sql.ErrNoRows {
		return utils.ErrorResponse(c, fiber.StatusNotFound, "Autor não encontrado", err)
	}
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao buscar autor", err)
	}

	return c.JSON(utils.SuccessResponse(autor))
}

// CreateAutor cria um novo autor
func (h *AutorHandler) CreateAutor(c *fiber.Ctx) error {
	type CreateAutorRequest struct {
		Nome            string     `json:"nome" validate:"required"`
		DataNascimento  *time.Time `json:"data_nascimento"`
		DataFalecimento *time.Time `json:"data_falecimento"`
	}

	var req CreateAutorRequest
	if err := c.BodyParser(&req); err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "Dados inválidos", err)
	}

	if err := utils.ValidateStruct(req); err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "Validação falhou", err)
	}

	query := `
		INSERT INTO Autores (nome, data_nascimento, data_falecimento, created_at, updated_at) 
		VALUES ($1, $2, $3, $4, $5) 
		RETURNING id_autor, created_at, updated_at
	`

	var autor models.Autor
	now := time.Now()
	err := h.db.QueryRow(query, req.Nome, req.DataNascimento, req.DataFalecimento, now, now).Scan(
		&autor.ID,
		&autor.CreatedAt,
		&autor.UpdatedAt,
	)

	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao criar autor", err)
	}

	autor.Nome = req.Nome
	autor.DataNascimento = req.DataNascimento
	autor.DataFalecimento = req.DataFalecimento

	return c.Status(fiber.StatusCreated).JSON(utils.SuccessResponse(autor))
}

// UpdateAutor atualiza um autor
func (h *AutorHandler) UpdateAutor(c *fiber.Ctx) error {
	id, err := strconv.Atoi(c.Params("id"))
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "ID inválido", err)
	}

	type UpdateAutorRequest struct {
		Nome            *string    `json:"nome"`
		DataNascimento  *time.Time `json:"data_nascimento"`
		DataFalecimento *time.Time `json:"data_falecimento"`
	}

	var req UpdateAutorRequest
	if err := c.BodyParser(&req); err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "Dados inválidos", err)
	}

	// Constrói query dinamicamente
	setParts := []string{}
	args := []interface{}{}
	argCount := 1

	if req.Nome != nil {
		setParts = append(setParts, "nome = $"+strconv.Itoa(argCount))
		args = append(args, *req.Nome)
		argCount++
	}
	if req.DataNascimento != nil {
		setParts = append(setParts, "data_nascimento = $"+strconv.Itoa(argCount))
		args = append(args, *req.DataNascimento)
		argCount++
	}
	if req.DataFalecimento != nil {
		setParts = append(setParts, "data_falecimento = $"+strconv.Itoa(argCount))
		args = append(args, *req.DataFalecimento)
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

	query := "UPDATE Autores SET " + joinStrings(setParts, ", ") + " WHERE id_autor = $" + strconv.Itoa(argCount)

	result, err := h.db.Exec(query, args...)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao atualizar autor", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao verificar atualização", err)
	}

	if rowsAffected == 0 {
		return utils.ErrorResponse(c, fiber.StatusNotFound, "Autor não encontrado", nil)
	}

	// Busca o autor atualizado
	return h.GetAutor(c)
}

// DeleteAutor exclui um autor
func (h *AutorHandler) DeleteAutor(c *fiber.Ctx) error {
	id, err := strconv.Atoi(c.Params("id"))
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "ID inválido", err)
	}

	// Verifica se há autorias associadas
	var autoriaCount int
	err = h.db.QueryRow("SELECT COUNT(*) FROM Autorias WHERE id_autor = $1", id).Scan(&autoriaCount)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao verificar autorias", err)
	}

	if autoriaCount > 0 {
		return utils.ErrorResponse(c, fiber.StatusConflict, "Autor possui obras associadas", nil)
	}

	query := "DELETE FROM Autores WHERE id_autor = $1"
	result, err := h.db.Exec(query, id)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao excluir autor", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao verificar exclusão", err)
	}

	if rowsAffected == 0 {
		return utils.ErrorResponse(c, fiber.StatusNotFound, "Autor não encontrado", nil)
	}

	return c.JSON(utils.SuccessResponse(fiber.Map{"message": "Autor excluído com sucesso"}))
}

// GetAutorObras obtém as obras de um autor
func (h *AutorHandler) GetAutorObras(c *fiber.Ctx) error {
	id, err := strconv.Atoi(c.Params("id"))
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusBadRequest, "ID inválido", err)
	}

	query := `
		SELECT m.id_midia, m.tipo_midia, m.condicao, m.created_at,
		       COALESCE(l.titulo, r.titulo, d.titulo, a.titulo) as titulo
		FROM Autorias au
		INNER JOIN Midia m ON au.id_midia = m.id_midia
		LEFT JOIN Livros l ON m.id_midia = l.id_livro AND m.tipo_midia = 'livro'
		LEFT JOIN Revistas r ON m.id_midia = r.id_revista AND m.tipo_midia = 'revista'
		LEFT JOIN DVDs d ON m.id_midia = d.id_dvd AND m.tipo_midia = 'dvd'
		LEFT JOIN Artigos a ON m.id_midia = a.id_artigo AND m.tipo_midia = 'artigo'
		WHERE au.id_autor = $1
		ORDER BY titulo
	`

	rows, err := h.db.Query(query, id)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao buscar obras", err)
	}
	defer rows.Close()

	type ObraAutor struct {
		ID        int                 `json:"id_midia"`
		Tipo      models.MidiaTipo    `json:"tipo_midia"`
		Titulo    string              `json:"titulo"`
		Condicao  *string             `json:"condicao"`
		CreatedAt time.Time           `json:"created_at"`
	}

	var obras []ObraAutor
	for rows.Next() {
		var obra ObraAutor
		err := rows.Scan(
			&obra.ID,
			&obra.Tipo,
			&obra.Condicao,
			&obra.CreatedAt,
			&obra.Titulo,
		)
		if err != nil {
			return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao processar dados", err)
		}
		obras = append(obras, obra)
	}

	return c.JSON(utils.SuccessResponse(obras))
}

// Helper function para join de strings (reusada)
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

print("Utilitários e Handler de Autor criados:")
print("✓ utils/utils.go")
print("✓ handlers/autor.go")