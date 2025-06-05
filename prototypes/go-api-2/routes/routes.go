package routes

import (
	"database/sql"

	"biblioteca-api/handlers"
	"biblioteca-api/utils"

	"github.com/gofiber/fiber/v2"
)

// SetupRoutes configura todas as rotas da API
func SetupRoutes(app *fiber.App, db *sql.DB) {
	// Inicializa handlers
	usuarioHandler := handlers.NewUsuarioHandler(db)
	bibliotecaHandler := handlers.NewBibliotecaHandler(db)
	midiaHandler := handlers.NewMidiaHandler(db)
	emprestimoHandler := handlers.NewEmprestimoHandler(db)
	livroHandler := handlers.NewLivroHandler(db)
	autorHandler := handlers.NewAutorHandler(db)
	dashboardHandler := handlers.NewDashboardHandler(db)

	// Grupo da API v1
	api := app.Group("/api/v1")

	// Middleware de logging para todas as rotas da API
	api.Use(func(c *fiber.Ctx) error {
		return c.Next()
	})

	// Rota de informações da API
	api.Get("/", func(c *fiber.Ctx) error {
		return c.JSON(utils.SuccessResponse(fiber.Map{
			"name":        "Biblioteca API",
			"version":     "1.0.0",
			"description": "Sistema de Gerenciamento de Biblioteca",
			"endpoints": fiber.Map{
				"usuarios":    "/api/v1/usuarios",
				"bibliotecas": "/api/v1/bibliotecas",
				"midias":      "/api/v1/midias",
				"emprestimos": "/api/v1/emprestimos",
				"livros":      "/api/v1/livros",
				"autores":     "/api/v1/autores",
				"dashboard":   "/api/v1/dashboard",
			},
		}))
	})

	// Rotas de Usuários
	usuarios := api.Group("/usuarios")
	usuarios.Get("/", usuarioHandler.GetUsuarios)
	usuarios.Get("/:id", usuarioHandler.GetUsuario)
	usuarios.Post("/", usuarioHandler.CreateUsuario)
	usuarios.Put("/:id", usuarioHandler.UpdateUsuario)
	usuarios.Delete("/:id", usuarioHandler.DeleteUsuario)
	usuarios.Get("/:id/emprestimos", usuarioHandler.GetUsuarioEmprestimos)

	// Rotas de Bibliotecas
	bibliotecas := api.Group("/bibliotecas")
	bibliotecas.Get("/", bibliotecaHandler.GetBibliotecas)
	bibliotecas.Get("/:id", bibliotecaHandler.GetBiblioteca)
	bibliotecas.Post("/", bibliotecaHandler.CreateBiblioteca)
	bibliotecas.Put("/:id", bibliotecaHandler.UpdateBiblioteca)
	bibliotecas.Delete("/:id", bibliotecaHandler.DeleteBiblioteca)
	bibliotecas.Get("/:id/midias", bibliotecaHandler.GetBibliotecaMidias)

	// Rotas de Mídias
	midias := api.Group("/midias")
	midias.Get("/", midiaHandler.GetMidias)
	midias.Get("/:id", midiaHandler.GetMidia)
	midias.Post("/", midiaHandler.CreateMidia)
	midias.Put("/:id", midiaHandler.UpdateMidia)
	midias.Delete("/:id", midiaHandler.DeleteMidia)

	// Rotas de Empréstimos
	emprestimos := api.Group("/emprestimos")
	emprestimos.Get("/", emprestimoHandler.GetEmprestimos)
	emprestimos.Get("/:id", emprestimoHandler.GetEmprestimo)
	emprestimos.Post("/", emprestimoHandler.CreateEmprestimo)
	emprestimos.Put("/:id/devolver", emprestimoHandler.DevolverEmprestimo)
	emprestimos.Put("/:id/renovar", emprestimoHandler.RenovarEmprestimo)
	emprestimos.Get("/atrasados", emprestimoHandler.GetEmprestimosAtrasados)

	// Rotas de Livros
	livros := api.Group("/livros")
	livros.Get("/", livroHandler.GetLivros)
	livros.Get("/:id", livroHandler.GetLivro)
	livros.Post("/", livroHandler.CreateLivro)
	livros.Put("/:id", livroHandler.UpdateLivro)
	livros.Delete("/:id", livroHandler.DeleteLivro)
	livros.Post("/:id/autores", livroHandler.AddAutorToLivro)
	livros.Delete("/:id/autores/:autor_id", livroHandler.RemoveAutorFromLivro)

	// Rotas de Autores
	autores := api.Group("/autores")
	autores.Get("/", autorHandler.GetAutores)
	autores.Get("/:id", autorHandler.GetAutor)
	autores.Post("/", autorHandler.CreateAutor)
	autores.Put("/:id", autorHandler.UpdateAutor)
	autores.Delete("/:id", autorHandler.DeleteAutor)
	autores.Get("/:id/obras", autorHandler.GetAutorObras)

	// Rotas de Dashboard/Relatórios
	dashboard := api.Group("/dashboard")
	dashboard.Get("/", dashboardHandler.GetDashboard)
	dashboard.Get("/estatisticas", dashboardHandler.GetEstatisticas)
	dashboard.Get("/emprestimos-por-mes", dashboardHandler.GetEmprestimosPorMes)
	dashboard.Get("/livros-mais-emprestados", dashboardHandler.GetLivrosMaisEmprestados)
	dashboard.Get("/usuarios-mais-ativos", dashboardHandler.GetUsuariosMaisAtivos)

	// Rotas de busca global
	search := api.Group("/search")
	search.Get("/", func(c *fiber.Ctx) error {
		query := c.Query("q")
		if query == "" {
			return utils.ErrorResponse(c, fiber.StatusBadRequest, "Parâmetro de busca 'q' é obrigatório", nil)
		}

		// Busca em múltiplas entidades
		results := fiber.Map{
			"livros":   []interface{}{},
			"autores":  []interface{}{},
			"usuarios": []interface{}{},
		}

		// Busca livros
		livrosQuery := `
			SELECT l.id_livro, l.titulo, l.isbn, m.condicao
			FROM Livros l
			INNER JOIN Midia m ON l.id_livro = m.id_midia
			WHERE LOWER(l.titulo) LIKE LOWER($1) OR LOWER(l.isbn) LIKE LOWER($1)
			LIMIT 5
		`
		rows, err := db.Query(livrosQuery, "%"+query+"%")
		if err == nil {
			defer rows.Close()
			var livros []fiber.Map
			for rows.Next() {
				var livro fiber.Map = make(fiber.Map)
				var id int
				var titulo, isbn string
				var condicao *string

				err := rows.Scan(&id, &titulo, &isbn, &condicao)
				if err == nil {
					livro["id"] = id
					livro["titulo"] = titulo
					livro["isbn"] = isbn
					livro["condicao"] = condicao
					livros = append(livros, livro)
				}
			}
			results["livros"] = livros
		}

		// Busca autores
		autoresQuery := `
			SELECT id_autor, nome
			FROM Autores
			WHERE LOWER(nome) LIKE LOWER($1)
			LIMIT 5
		`
		rows, err = db.Query(autoresQuery, "%"+query+"%")
		if err == nil {
			defer rows.Close()
			var autores []fiber.Map
			for rows.Next() {
				var autor fiber.Map = make(fiber.Map)
				var id int
				var nome string

				err := rows.Scan(&id, &nome)
				if err == nil {
					autor["id"] = id
					autor["nome"] = nome
					autores = append(autores, autor)
				}
			}
			results["autores"] = autores
		}

		// Busca usuários
		usuariosQuery := `
			SELECT id_usuario, nome, email
			FROM Usuario
			WHERE LOWER(nome) LIKE LOWER($1) OR LOWER(email) LIKE LOWER($1)
			LIMIT 5
		`
		rows, err = db.Query(usuariosQuery, "%"+query+"%")
		if err == nil {
			defer rows.Close()
			var usuarios []fiber.Map
			for rows.Next() {
				var usuario fiber.Map = make(fiber.Map)
				var id int
				var nome string
				var email *string

				err := rows.Scan(&id, &nome, &email)
				if err == nil {
					usuario["id"] = id
					usuario["nome"] = nome
					usuario["email"] = email
					usuarios = append(usuarios, usuario)
				}
			}
			results["usuarios"] = usuarios
		}

		return c.JSON(utils.SuccessResponse(results))
	})

	// Middleware para rotas não encontradas
	app.Use(func(c *fiber.Ctx) error {
		return utils.ErrorResponse(c, fiber.StatusNotFound, "Rota não encontrada", nil)
	})
}
