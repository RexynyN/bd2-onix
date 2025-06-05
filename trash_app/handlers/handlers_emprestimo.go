package handlers

import (
	"database/sql"
	"fmt"
	"strconv"
	"time"

	"onix/models"

	"github.com/gofiber/fiber/v2"
)

func GetEmprestimos(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		emprestimos, err := models.GetAllEmprestimos(db)
		if err != nil {
			fmt.Println("Erro ao buscar empréstimos:", err)
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}
		return c.JSON(emprestimos)
	}
}

func GetEmprestimosAtivos(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		emprestimos, err := models.GetEmprestimosAtivos(db)
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}
		return c.JSON(emprestimos)
	}
}

func GetEmprestimo(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		id, err := strconv.Atoi(c.Params("id"))
		if err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "ID inválido"})
		}

		emprestimo, err := models.GetEmprestimoByID(db, id)
		if err != nil {
			if err == sql.ErrNoRows {
				return c.Status(404).JSON(fiber.Map{"error": "Empréstimo não encontrado"})
			}
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}
		return c.JSON(emprestimo)
	}
}

func CreateEmprestimo(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		var emprestimo models.Emprestimo
		if err := c.BodyParser(&emprestimo); err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "Dados inválidos"})
		}

		// Validações
		if emprestimo.IDUsuario == 0 {
			return c.Status(400).JSON(fiber.Map{"error": "Usuário é obrigatório"})
		}
		if emprestimo.IDMidia == 0 {
			return c.Status(400).JSON(fiber.Map{"error": "Mídia é obrigatória"})
		}

		// Verificar se a mídia já está emprestada
		var count int
		err := db.QueryRow("SELECT COUNT(*) FROM Emprestimo WHERE id_midia = $1 AND data_devolucao IS NULL", emprestimo.IDMidia).Scan(&count)
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}
		if count > 0 {
			return c.Status(400).JSON(fiber.Map{"error": "Esta mídia já está emprestada"})
		}

		// Definir data de empréstimo como hoje se não fornecida
		if emprestimo.DataEmprestimo.IsZero() {
			emprestimo.DataEmprestimo = time.Now()
		}

		// Definir data de devolução prevista (15 dias por padrão)
		if emprestimo.DataDevolucaoPrevista == nil {
			devolucao := emprestimo.DataEmprestimo.AddDate(0, 0, 15)
			emprestimo.DataDevolucaoPrevista = &devolucao
		}

		err = models.CreateEmprestimo(db, &emprestimo)
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}

		return c.Status(201).JSON(emprestimo)
	}
}

func RegistrarDevolucao(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		id, err := strconv.Atoi(c.Params("id"))
		if err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "ID inválido"})
		}

		err = models.RegistrarDevolucao(db, id)
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}

		return c.JSON(fiber.Map{"message": "Devolução registrada com sucesso"})
	}
}

func DeleteEmprestimo(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		id, err := strconv.Atoi(c.Params("id"))
		if err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "ID inválido"})
		}

		err = models.DeleteEmprestimo(db, id)
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}

		return c.JSON(fiber.Map{"message": "Empréstimo deletado com sucesso"})
	}
}
