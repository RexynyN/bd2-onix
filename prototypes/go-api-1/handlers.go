package handlers

import (
	"strconv"
	"time"

	"github.com/gofiber/fiber/v2"
	"github.com/go-playground/validator/v10"
)

var validate = validator.New()

// Estrutura para resposta de erro
type ErrorResponse struct {
	Error       bool   `json:"error"`
	FailedField string `json:"failed_field"`
	Tag         string `json:"tag"`
	Value       string `json:"value"`
}

// Função para validar structs
func ValidateStruct(data interface{}) []*ErrorResponse {
	var errors []*ErrorResponse
	err := validate.Struct(data)
	if err != nil {
		for _, err := range err.(validator.ValidationErrors) {
			var element ErrorResponse
			element.Error = true
			element.FailedField = err.StructNamespace()
			element.Tag = err.Tag()
			element.Value = err.Param()
			errors = append(errors, &element)
		}
	}
	return errors
}

// ==== HANDLERS PARA USUARIO ====

// Listar todos os usuários
func GetUsuarios(c *fiber.Ctx) error {
	usuarios, err := GetAllUsuarios()
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "Erro ao buscar usuários"})
	}

	return c.Render("usuarios/index", fiber.Map{
		"Title":    "Usuários",
		"Usuarios": usuarios,
	})
}

// Mostrar formulário de novo usuário
func ShowCreateUsuario(c *fiber.Ctx) error {
	return c.Render("usuarios/create", fiber.Map{
		"Title": "Novo Usuário",
	})
}

// Criar novo usuário
func CreateUsuario(c *fiber.Ctx) error {
	nome := c.FormValue("nome")
	email := c.FormValue("email")
	endereco := c.FormValue("endereco")
	telefone := c.FormValue("telefone")

	if nome == "" {
		return c.Status(400).JSON(fiber.Map{"error": "Nome é obrigatório"})
	}

	id, err := CreateUsuario(nome, email, endereco, telefone)
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "Erro ao criar usuário"})
	}

	return c.Redirect("/usuarios")
}

// Mostrar usuário específico
func ShowUsuario(c *fiber.Ctx) error {
	idStr := c.Params("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		return c.Status(400).JSON(fiber.Map{"error": "ID inválido"})
	}

	usuario, err := GetUsuario(id)
	if err != nil {
		return c.Status(404).JSON(fiber.Map{"error": "Usuário não encontrado"})
	}

	return c.Render("usuarios/show", fiber.Map{
		"Title":   "Detalhes do Usuário",
		"Usuario": usuario,
	})
}

// Mostrar formulário de edição
func ShowEditUsuario(c *fiber.Ctx) error {
	idStr := c.Params("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		return c.Status(400).JSON(fiber.Map{"error": "ID inválido"})
	}

	usuario, err := GetUsuario(id)
	if err != nil {
		return c.Status(404).JSON(fiber.Map{"error": "Usuário não encontrado"})
	}

	return c.Render("usuarios/edit", fiber.Map{
		"Title":   "Editar Usuário",
		"Usuario": usuario,
	})
}

// Atualizar usuário
func UpdateUsuario(c *fiber.Ctx) error {
	idStr := c.Params("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		return c.Status(400).JSON(fiber.Map{"error": "ID inválido"})
	}

	nome := c.FormValue("nome")
	email := c.FormValue("email")
	endereco := c.FormValue("endereco")
	telefone := c.FormValue("telefone")

	if nome == "" {
		return c.Status(400).JSON(fiber.Map{"error": "Nome é obrigatório"})
	}

	err = UpdateUsuario(id, nome, email, endereco, telefone)
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "Erro ao atualizar usuário"})
	}

	return c.Redirect("/usuarios")
}

// Deletar usuário
func DeleteUsuario(c *fiber.Ctx) error {
	idStr := c.Params("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		return c.Status(400).JSON(fiber.Map{"error": "ID inválido"})
	}

	err = DeleteUsuario(id)
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "Erro ao deletar usuário"})
	}

	return c.Redirect("/usuarios")
}

// ==== HANDLERS PARA BIBLIOTECA ====

func GetBibliotecas(c *fiber.Ctx) error {
	bibliotecas, err := GetAllBibliotecas()
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "Erro ao buscar bibliotecas"})
	}

	return c.Render("bibliotecas/index", fiber.Map{
		"Title":       "Bibliotecas",
		"Bibliotecas": bibliotecas,
	})
}

func ShowCreateBiblioteca(c *fiber.Ctx) error {
	return c.Render("bibliotecas/create", fiber.Map{
		"Title": "Nova Biblioteca",
	})
}

func CreateBiblioteca(c *fiber.Ctx) error {
	nome := c.FormValue("nome")
	endereco := c.FormValue("endereco")

	if nome == "" {
		return c.Status(400).JSON(fiber.Map{"error": "Nome é obrigatório"})
	}

	_, err := CreateBiblioteca(nome, endereco)
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "Erro ao criar biblioteca"})
	}

	return c.Redirect("/bibliotecas")
}

func ShowBiblioteca(c *fiber.Ctx) error {
	idStr := c.Params("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		return c.Status(400).JSON(fiber.Map{"error": "ID inválido"})
	}

	biblioteca, err := GetBiblioteca(id)
	if err != nil {
		return c.Status(404).JSON(fiber.Map{"error": "Biblioteca não encontrada"})
	}

	return c.Render("bibliotecas/show", fiber.Map{
		"Title":      "Detalhes da Biblioteca",
		"Biblioteca": biblioteca,
	})
}

func ShowEditBiblioteca(c *fiber.Ctx) error {
	idStr := c.Params("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		return c.Status(400).JSON(fiber.Map{"error": "ID inválido"})
	}

	biblioteca, err := GetBiblioteca(id)
	if err != nil {
		return c.Status(404).JSON(fiber.Map{"error": "Biblioteca não encontrada"})
	}

	return c.Render("bibliotecas/edit", fiber.Map{
		"Title":      "Editar Biblioteca",
		"Biblioteca": biblioteca,
	})
}

func UpdateBiblioteca(c *fiber.Ctx) error {
	idStr := c.Params("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		return c.Status(400).JSON(fiber.Map{"error": "ID inválido"})
	}

	nome := c.FormValue("nome")
	endereco := c.FormValue("endereco")

	if nome == "" {
		return c.Status(400).JSON(fiber.Map{"error": "Nome é obrigatório"})
	}

	err = UpdateBiblioteca(id, nome, endereco)
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "Erro ao atualizar biblioteca"})
	}

	return c.Redirect("/bibliotecas")
}

func DeleteBiblioteca(c *fiber.Ctx) error {
	idStr := c.Params("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		return c.Status(400).JSON(fiber.Map{"error": "ID inválido"})
	}

	err = DeleteBiblioteca(id)
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "Erro ao deletar biblioteca"})
	}

	return c.Redirect("/bibliotecas")
}

// ==== HANDLERS PARA LIVROS ====

func GetLivros(c *fiber.Ctx) error {
	livros, err := GetAllLivros()
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "Erro ao buscar livros"})
	}

	return c.Render("livros/index", fiber.Map{
		"Title":  "Livros",
		"Livros": livros,
	})
}

func ShowCreateLivro(c *fiber.Ctx) error {
	bibliotecas, err := GetAllBibliotecas()
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "Erro ao buscar bibliotecas"})
	}

	return c.Render("livros/create", fiber.Map{
		"Title":       "Novo Livro",
		"Bibliotecas": bibliotecas,
	})
}

func CreateLivro(c *fiber.Ctx) error {
	titulo := c.FormValue("titulo")
	isbn := c.FormValue("isbn")
	editora := c.FormValue("editora")
	condicao := c.FormValue("condicao")
	dataPublicacao := c.FormValue("data_publicacao")

	numeroPaginasStr := c.FormValue("numero_paginas")
	idBibliotecaStr := c.FormValue("id_biblioteca")

	if titulo == "" {
		return c.Status(400).JSON(fiber.Map{"error": "Título é obrigatório"})
	}

	numeroPaginas, err := strconv.Atoi(numeroPaginasStr)
	if err != nil {
		numeroPaginas = 0
	}

	idBiblioteca, err := strconv.Atoi(idBibliotecaStr)
	if err != nil {
		return c.Status(400).JSON(fiber.Map{"error": "Biblioteca é obrigatória"})
	}

	_, err = CreateLivro(titulo, isbn, editora, condicao, numeroPaginas, idBiblioteca, dataPublicacao)
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "Erro ao criar livro"})
	}

	return c.Redirect("/livros")
}

func ShowLivro(c *fiber.Ctx) error {
	idStr := c.Params("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		return c.Status(400).JSON(fiber.Map{"error": "ID inválido"})
	}

	livro, err := GetLivro(id)
	if err != nil {
		return c.Status(404).JSON(fiber.Map{"error": "Livro não encontrado"})
	}

	return c.Render("livros/show", fiber.Map{
		"Title": "Detalhes do Livro",
		"Livro": livro,
	})
}

func ShowEditLivro(c *fiber.Ctx) error {
	idStr := c.Params("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		return c.Status(400).JSON(fiber.Map{"error": "ID inválido"})
	}

	livro, err := GetLivro(id)
	if err != nil {
		return c.Status(404).JSON(fiber.Map{"error": "Livro não encontrado"})
	}

	bibliotecas, err := GetAllBibliotecas()
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "Erro ao buscar bibliotecas"})
	}

	return c.Render("livros/edit", fiber.Map{
		"Title":       "Editar Livro",
		"Livro":       livro,
		"Bibliotecas": bibliotecas,
	})
}

func UpdateLivro(c *fiber.Ctx) error {
	idStr := c.Params("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		return c.Status(400).JSON(fiber.Map{"error": "ID inválido"})
	}

	titulo := c.FormValue("titulo")
	isbn := c.FormValue("isbn")
	editora := c.FormValue("editora")
	condicao := c.FormValue("condicao")
	dataPublicacao := c.FormValue("data_publicacao")

	numeroPaginasStr := c.FormValue("numero_paginas")
	idBibliotecaStr := c.FormValue("id_biblioteca")

	if titulo == "" {
		return c.Status(400).JSON(fiber.Map{"error": "Título é obrigatório"})
	}

	numeroPaginas, err := strconv.Atoi(numeroPaginasStr)
	if err != nil {
		numeroPaginas = 0
	}

	idBiblioteca, err := strconv.Atoi(idBibliotecaStr)
	if err != nil {
		return c.Status(400).JSON(fiber.Map{"error": "Biblioteca é obrigatória"})
	}

	err = UpdateLivro(id, titulo, isbn, editora, condicao, numeroPaginas, idBiblioteca, dataPublicacao)
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "Erro ao atualizar livro"})
	}

	return c.Redirect("/livros")
}

func DeleteLivro(c *fiber.Ctx) error {
	idStr := c.Params("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		return c.Status(400).JSON(fiber.Map{"error": "ID inválido"})
	}

	err = DeleteLivro(id)
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "Erro ao deletar livro"})
	}

	return c.Redirect("/livros")
}

// ==== HANDLERS PARA EMPRESTIMOS ====

func GetEmprestimos(c *fiber.Ctx) error {
	emprestimos, err := GetAllEmprestimos()
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "Erro ao buscar empréstimos"})
	}

	return c.Render("emprestimos/index", fiber.Map{
		"Title":       "Empréstimos",
		"Emprestimos": emprestimos,
	})
}

func ShowCreateEmprestimo(c *fiber.Ctx) error {
	usuarios, err := GetAllUsuarios()
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "Erro ao buscar usuários"})
	}

	midias, err := GetAllMidias()
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "Erro ao buscar mídias"})
	}

	return c.Render("emprestimos/create", fiber.Map{
		"Title":    "Novo Empréstimo",
		"Usuarios": usuarios,
		"Midias":   midias,
	})
}

func CreateEmprestimo(c *fiber.Ctx) error {
	dataEmprestimo := c.FormValue("data_emprestimo")
	dataDevolucaoPrevista := c.FormValue("data_devolucao_prevista")
	idMidiaStr := c.FormValue("id_midia")
	idUsuarioStr := c.FormValue("id_usuario")

	if dataEmprestimo == "" {
		return c.Status(400).JSON(fiber.Map{"error": "Data do empréstimo é obrigatória"})
	}

	idMidia, err := strconv.Atoi(idMidiaStr)
	if err != nil {
		return c.Status(400).JSON(fiber.Map{"error": "Mídia é obrigatória"})
	}

	idUsuario, err := strconv.Atoi(idUsuarioStr)
	if err != nil {
		return c.Status(400).JSON(fiber.Map{"error": "Usuário é obrigatório"})
	}

	_, err = CreateEmprestimo(dataEmprestimo, dataDevolucaoPrevista, idMidia, idUsuario)
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "Erro ao criar empréstimo"})
	}

	return c.Redirect("/emprestimos")
}

func ShowEmprestimo(c *fiber.Ctx) error {
	idStr := c.Params("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		return c.Status(400).JSON(fiber.Map{"error": "ID inválido"})
	}

	emprestimo, err := GetEmprestimo(id)
	if err != nil {
		return c.Status(404).JSON(fiber.Map{"error": "Empréstimo não encontrado"})
	}

	return c.Render("emprestimos/show", fiber.Map{
		"Title":      "Detalhes do Empréstimo",
		"Emprestimo": emprestimo,
	})
}

func ShowEditEmprestimo(c *fiber.Ctx) error {
	idStr := c.Params("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		return c.Status(400).JSON(fiber.Map{"error": "ID inválido"})
	}

	emprestimo, err := GetEmprestimo(id)
	if err != nil {
		return c.Status(404).JSON(fiber.Map{"error": "Empréstimo não encontrado"})
	}

	usuarios, err := GetAllUsuarios()
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "Erro ao buscar usuários"})
	}

	midias, err := GetAllMidias()
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "Erro ao buscar mídias"})
	}

	return c.Render("emprestimos/edit", fiber.Map{
		"Title":      "Editar Empréstimo",
		"Emprestimo": emprestimo,
		"Usuarios":   usuarios,
		"Midias":     midias,
	})
}

func UpdateEmprestimo(c *fiber.Ctx) error {
	idStr := c.Params("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		return c.Status(400).JSON(fiber.Map{"error": "ID inválido"})
	}

	dataEmprestimo := c.FormValue("data_emprestimo")
	dataDevolucaoPrevista := c.FormValue("data_devolucao_prevista")
	dataDevolucao := c.FormValue("data_devolucao")
	idMidiaStr := c.FormValue("id_midia")
	idUsuarioStr := c.FormValue("id_usuario")

	if dataEmprestimo == "" {
		return c.Status(400).JSON(fiber.Map{"error": "Data do empréstimo é obrigatória"})
	}

	idMidia, err := strconv.Atoi(idMidiaStr)
	if err != nil {
		return c.Status(400).JSON(fiber.Map{"error": "Mídia é obrigatória"})
	}

	idUsuario, err := strconv.Atoi(idUsuarioStr)
	if err != nil {
		return c.Status(400).JSON(fiber.Map{"error": "Usuário é obrigatório"})
	}

	err = UpdateEmprestimo(id, dataEmprestimo, dataDevolucaoPrevista, dataDevolucao, idMidia, idUsuario)
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "Erro ao atualizar empréstimo"})
	}

	return c.Redirect("/emprestimos")
}

func DeleteEmprestimo(c *fiber.Ctx) error {
	idStr := c.Params("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		return c.Status(400).JSON(fiber.Map{"error": "ID inválido"})
	}

	err = DeleteEmprestimo(id)
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": "Erro ao deletar empréstimo"})
	}

	return c.Redirect("/emprestimos")
}

// Função para formatar datas para exibição
func FormatDate(t *time.Time) string {
	if t == nil {
		return ""
	}
	return t.Format("2006-01-02")
}

// Função para obter data atual em formato string
func GetCurrentDate() string {
	return time.Now().Format("2006-01-02")
}
