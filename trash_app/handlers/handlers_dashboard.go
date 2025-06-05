package handlers

import (
	"database/sql"

	"github.com/gofiber/fiber/v2"
)

type DashboardData struct {
	TotalUsuarios     int
	TotalMidias       int
	EmprestimosAtivos int
	Penalizacoes      int
}

func Dashboard(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		var data DashboardData

		// Contar usuários
		db.QueryRow("SELECT COUNT(*) FROM Usuario").Scan(&data.TotalUsuarios)

		// Contar mídias
		db.QueryRow("SELECT COUNT(*) FROM Midia").Scan(&data.TotalMidias)

		// Contar empréstimos ativos
		db.QueryRow("SELECT COUNT(*) FROM Emprestimo WHERE data_devolucao IS NULL").Scan(&data.EmprestimosAtivos)

		// Contar penalizações ativas
		db.QueryRow("SELECT COUNT(*) FROM Penalizacao WHERE Final_penalizacao > CURRENT_DATE OR Final_penalizacao IS NULL").Scan(&data.Penalizacoes)

		return c.Render("dashboard/index", fiber.Map{
			"Data":  data,
			"Title": "Dashboard",
		})
	}
}

func DashboardAPI(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		var data DashboardData

		// Contar usuários
		db.QueryRow("SELECT COUNT(*) FROM Usuario").Scan(&data.TotalUsuarios)

		// Contar mídias
		db.QueryRow("SELECT COUNT(*) FROM Midia").Scan(&data.TotalMidias)

		// Contar empréstimos ativos
		db.QueryRow("SELECT COUNT(*) FROM Emprestimo WHERE data_devolucao IS NULL").Scan(&data.EmprestimosAtivos)

		// Contar penalizações ativas
		db.QueryRow("SELECT COUNT(*) FROM Penalizacao WHERE Final_penalizacao > CURRENT_DATE OR Final_penalizacao IS NULL").Scan(&data.Penalizacoes)

		return c.JSON(data)
	}
}
