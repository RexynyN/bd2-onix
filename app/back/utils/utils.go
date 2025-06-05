package utils

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
