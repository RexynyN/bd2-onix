package routes

import (
	"database/sql"

	"onix/handlers"

	"github.com/gofiber/fiber/v2"
)

func Setup(app *fiber.App, db *sql.DB) {
	// Rota principal - Dashboard
	app.Get("/", handlers.Dashboard(db))

	// API Routes
	api := app.Group("/api")

	// Dashboard API
	api.Get("/dashboard", handlers.DashboardAPI(db))

	// Usuários
	usuarios := api.Group("/usuarios")
	usuarios.Get("/", handlers.GetUsuarios(db))
	usuarios.Get("/:id", handlers.GetUsuario(db))
	usuarios.Post("/", handlers.CreateUsuario(db))
	usuarios.Put("/:id", handlers.UpdateUsuario(db))
	usuarios.Delete("/:id", handlers.DeleteUsuario(db))

	// Bibliotecas
	bibliotecas := api.Group("/bibliotecas")
	bibliotecas.Get("/", handlers.GetBibliotecas(db))
	bibliotecas.Get("/:id", handlers.GetBiblioteca(db))
	bibliotecas.Post("/", handlers.CreateBiblioteca(db))
	bibliotecas.Put("/:id", handlers.UpdateBiblioteca(db))
	bibliotecas.Delete("/:id", handlers.DeleteBiblioteca(db))

	// Mídias
	midias := api.Group("/midias")
	midias.Get("/", handlers.GetMidias(db))
	midias.Get("/:id", handlers.GetMidia(db))
	midias.Post("/", handlers.CreateMidia(db))
	midias.Put("/:id", handlers.UpdateMidia(db))
	midias.Delete("/:id", handlers.DeleteMidia(db))

	// Empréstimos
	emprestimos := api.Group("/emprestimos")
	emprestimos.Get("/", handlers.GetEmprestimos(db))
	emprestimos.Get("/ativos", handlers.GetEmprestimosAtivos(db))
	emprestimos.Get("/:id", handlers.GetEmprestimo(db))
	emprestimos.Post("/", handlers.CreateEmprestimo(db))
	emprestimos.Put("/:id/devolucao", handlers.RegistrarDevolucao(db))
	emprestimos.Delete("/:id", handlers.DeleteEmprestimo(db))

	// Penalizações
	penalizacoes := api.Group("/penalizacoes")
	penalizacoes.Get("/", handlers.GetPenalizacoes(db))
	penalizacoes.Get("/:id", handlers.GetPenalizacao(db))
	penalizacoes.Post("/", handlers.CreatePenalizacao(db))
	penalizacoes.Put("/:id", handlers.UpdatePenalizacao(db))
	penalizacoes.Delete("/:id", handlers.DeletePenalizacao(db))

	// Autores
	autores := api.Group("/autores")
	autores.Get("/", handlers.GetAutores(db))
	autores.Get("/:id", handlers.GetAutor(db))
	autores.Post("/", handlers.CreateAutor(db))
	autores.Put("/:id", handlers.UpdateAutor(db))
	autores.Delete("/:id", handlers.DeleteAutor(db))

	// Autorias
	autorias := api.Group("/autorias")
	autorias.Get("/", handlers.GetAutorias(db))
	autorias.Post("/", handlers.CreateAutoria(db))
	autorias.Delete("/:id", handlers.DeleteAutoria(db))

	// Páginas de visualização
	app.Get("/biblioteca", func(c *fiber.Ctx) error {
		return c.Render("biblioteca/index", fiber.Map{
			"Title": "Gestão da Biblioteca",
		})
	})

	app.Get("/emprestimos", func(c *fiber.Ctx) error {
		return c.Render("emprestimos/index", fiber.Map{
			"Title": "Gestão de Empréstimos",
		})
	})
}
