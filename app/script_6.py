# Sistema de rotas
routes_go = """package routes

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
				"usuarios":     "/api/v1/usuarios",
				"bibliotecas":  "/api/v1/bibliotecas", 
				"midias":       "/api/v1/midias",
				"emprestimos":  "/api/v1/emprestimos",
				"livros":       "/api/v1/livros",
				"autores":      "/api/v1/autores",
				"dashboard":    "/api/v1/dashboard",
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
"""

# Handler para Dashboard/Relatórios
handlers_dashboard_go = """package handlers

import (
	"biblioteca-api/utils"
	"database/sql"

	"github.com/gofiber/fiber/v2"
)

type DashboardHandler struct {
	db *sql.DB
}

func NewDashboardHandler(db *sql.DB) *DashboardHandler {
	return &DashboardHandler{db: db}
}

// GetDashboard retorna dados gerais do dashboard
func (h *DashboardHandler) GetDashboard(c *fiber.Ctx) error {
	dashboard := fiber.Map{}

	// Total de usuários
	var totalUsuarios int
	err := h.db.QueryRow("SELECT COUNT(*) FROM Usuario").Scan(&totalUsuarios)
	if err != nil {
		totalUsuarios = 0
	}
	dashboard["total_usuarios"] = totalUsuarios

	// Total de livros
	var totalLivros int
	err = h.db.QueryRow("SELECT COUNT(*) FROM Livros").Scan(&totalLivros)
	if err != nil {
		totalLivros = 0
	}
	dashboard["total_livros"] = totalLivros

	// Total de empréstimos ativos
	var emprestimosAtivos int
	err = h.db.QueryRow(`
		SELECT COUNT(*) FROM Emprestimo 
		WHERE status = 'ativo' AND data_devolucao IS NULL
	`).Scan(&emprestimosAtivos)
	if err != nil {
		emprestimosAtivos = 0
	}
	dashboard["emprestimos_ativos"] = emprestimosAtivos

	// Total de empréstimos em atraso
	var emprestimosAtrasados int
	err = h.db.QueryRow(`
		SELECT COUNT(*) FROM Emprestimo 
		WHERE status = 'ativo' 
		  AND data_devolucao IS NULL 
		  AND data_devolucao_prevista < CURRENT_DATE
	`).Scan(&emprestimosAtrasados)
	if err != nil {
		emprestimosAtrasados = 0
	}
	dashboard["emprestimos_atrasados"] = emprestimosAtrasados

	// Total de bibliotecas
	var totalBibliotecas int
	err = h.db.QueryRow("SELECT COUNT(*) FROM Biblioteca").Scan(&totalBibliotecas)
	if err != nil {
		totalBibliotecas = 0
	}
	dashboard["total_bibliotecas"] = totalBibliotecas

	// Total de autores
	var totalAutores int
	err = h.db.QueryRow("SELECT COUNT(*) FROM Autores").Scan(&totalAutores)
	if err != nil {
		totalAutores = 0
	}
	dashboard["total_autores"] = totalAutores

	// Penalizações ativas
	var penalizacoesAtivas int
	err = h.db.QueryRow(`
		SELECT COUNT(*) FROM Penalizacao 
		WHERE final_penalizacao IS NULL OR final_penalizacao > CURRENT_DATE
	`).Scan(&penalizacoesAtivas)
	if err != nil {
		penalizacoesAtivas = 0
	}
	dashboard["penalizacoes_ativas"] = penalizacoesAtivas

	return c.JSON(utils.SuccessResponse(dashboard))
}

// GetEstatisticas retorna estatísticas detalhadas
func (h *DashboardHandler) GetEstatisticas(c *fiber.Ctx) error {
	stats := fiber.Map{}

	// Distribuição por tipo de mídia
	rows, err := h.db.Query(`
		SELECT tipo_midia, COUNT(*) as total
		FROM Midia
		GROUP BY tipo_midia
		ORDER BY total DESC
	`)
	if err == nil {
		defer rows.Close()
		var distribuicaoMidia []fiber.Map
		for rows.Next() {
			var tipo string
			var total int
			err := rows.Scan(&tipo, &total)
			if err == nil {
				distribuicaoMidia = append(distribuicaoMidia, fiber.Map{
					"tipo":  tipo,
					"total": total,
				})
			}
		}
		stats["distribuicao_midia"] = distribuicaoMidia
	}

	// Status dos empréstimos
	rows, err = h.db.Query(`
		SELECT status, COUNT(*) as total
		FROM Emprestimo
		GROUP BY status
		ORDER BY total DESC
	`)
	if err == nil {
		defer rows.Close()
		var statusEmprestimos []fiber.Map
		for rows.Next() {
			var status string
			var total int
			err := rows.Scan(&status, &total)
			if err == nil {
				statusEmprestimos = append(statusEmprestimos, fiber.Map{
					"status": status,
					"total":  total,
				})
			}
		}
		stats["status_emprestimos"] = statusEmprestimos
	}

	// Mídias por biblioteca
	rows, err = h.db.Query(`
		SELECT b.nome, COUNT(m.id_midia) as total
		FROM Biblioteca b
		LEFT JOIN Midia m ON b.id_biblioteca = m.id_biblioteca
		GROUP BY b.id_biblioteca, b.nome
		ORDER BY total DESC
	`)
	if err == nil {
		defer rows.Close()
		var midiasPorBiblioteca []fiber.Map
		for rows.Next() {
			var nome string
			var total int
			err := rows.Scan(&nome, &total)
			if err == nil {
				midiasPorBiblioteca = append(midiasPorBiblioteca, fiber.Map{
					"biblioteca": nome,
					"total":      total,
				})
			}
		}
		stats["midias_por_biblioteca"] = midiasPorBiblioteca
	}

	return c.JSON(utils.SuccessResponse(stats))
}

// GetEmprestimosPorMes retorna empréstimos agrupados por mês
func (h *DashboardHandler) GetEmprestimosPorMes(c *fiber.Ctx) error {
	query := `
		SELECT 
			DATE_TRUNC('month', data_emprestimo) as mes,
			COUNT(*) as total
		FROM Emprestimo
		WHERE data_emprestimo >= CURRENT_DATE - INTERVAL '12 months'
		GROUP BY DATE_TRUNC('month', data_emprestimo)
		ORDER BY mes DESC
		LIMIT 12
	`

	rows, err := h.db.Query(query)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao buscar dados", err)
	}
	defer rows.Close()

	var emprestimosPorMes []fiber.Map
	for rows.Next() {
		var mes string
		var total int
		err := rows.Scan(&mes, &total)
		if err == nil {
			emprestimosPorMes = append(emprestimosPorMes, fiber.Map{
				"mes":   mes,
				"total": total,
			})
		}
	}

	return c.JSON(utils.SuccessResponse(emprestimosPorMes))
}

// GetLivrosMaisEmprestados retorna os livros mais emprestados
func (h *DashboardHandler) GetLivrosMaisEmprestados(c *fiber.Ctx) error {
	limit := c.QueryInt("limit", 10)

	query := `
		SELECT 
			l.id_livro,
			l.titulo,
			l.isbn,
			COUNT(e.id_emprestimo) as total_emprestimos
		FROM Livros l
		INNER JOIN Emprestimo e ON l.id_livro = e.id_midia
		GROUP BY l.id_livro, l.titulo, l.isbn
		ORDER BY total_emprestimos DESC
		LIMIT $1
	`

	rows, err := h.db.Query(query, limit)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao buscar dados", err)
	}
	defer rows.Close()

	var livrosMaisEmprestados []fiber.Map
	for rows.Next() {
		var id, totalEmprestimos int
		var titulo, isbn string
		err := rows.Scan(&id, &titulo, &isbn, &totalEmprestimos)
		if err == nil {
			livrosMaisEmprestados = append(livrosMaisEmprestados, fiber.Map{
				"id":                id,
				"titulo":            titulo,
				"isbn":              isbn,
				"total_emprestimos": totalEmprestimos,
			})
		}
	}

	return c.JSON(utils.SuccessResponse(livrosMaisEmprestados))
}

// GetUsuariosMaisAtivos retorna os usuários mais ativos
func (h *DashboardHandler) GetUsuariosMaisAtivos(c *fiber.Ctx) error {
	limit := c.QueryInt("limit", 10)

	query := `
		SELECT 
			u.id_usuario,
			u.nome,
			u.email,
			COUNT(e.id_emprestimo) as total_emprestimos
		FROM Usuario u
		INNER JOIN Emprestimo e ON u.id_usuario = e.id_usuario
		GROUP BY u.id_usuario, u.nome, u.email
		ORDER BY total_emprestimos DESC
		LIMIT $1
	`

	rows, err := h.db.Query(query, limit)
	if err != nil {
		return utils.ErrorResponse(c, fiber.StatusInternalServerError, "Erro ao buscar dados", err)
	}
	defer rows.Close()

	var usuariosMaisAtivos []fiber.Map
	for rows.Next() {
		var id, totalEmprestimos int
		var nome string
		var email *string
		err := rows.Scan(&id, &nome, &email, &totalEmprestimos)
		if err == nil {
			usuariosMaisAtivos = append(usuariosMaisAtivos, fiber.Map{
				"id":                id,
				"nome":              nome,
				"email":             email,
				"total_emprestimos": totalEmprestimos,
			})
		}
	}

	return c.JSON(utils.SuccessResponse(usuariosMaisAtivos))
}
"""

print("Rotas e Handler de Dashboard criados:")
print("✓ routes/routes.go")
print("✓ handlers/dashboard.go")