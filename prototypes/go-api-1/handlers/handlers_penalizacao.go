package handlers

import (
	"database/sql"
	"strconv"

	"onix/models"

	"github.com/gofiber/fiber/v2"
)

func GetPenalizacoes(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		penalizacoes, err := models.GetAllPenalizacoes(db)
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}
		return c.JSON(penalizacoes)
	}
}

func GetPenalizacao(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		id, err := strconv.Atoi(c.Params("id"))
		if err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "ID inválido"})
		}

		penalizacao, err := models.GetPenalizacaoByID(db, id)
		if err != nil {
			if err == sql.ErrNoRows {
				return c.Status(404).JSON(fiber.Map{"error": "Penalização não encontrada"})
			}
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}
		return c.JSON(penalizacao)
	}
}

func CreatePenalizacao(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		var penalizacao models.Penalizacao
		if err := c.BodyParser(&penalizacao); err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "Dados inválidos"})
		}

		// Validações
		if penalizacao.IDUsuario == 0 {
			return c.Status(400).JSON(fiber.Map{"error": "Usuário é obrigatório"})
		}
		if penalizacao.Descricao == "" {
			return c.Status(400).JSON(fiber.Map{"error": "Descrição é obrigatória"})
		}

		err := models.CreatePenalizacao(db, &penalizacao)
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}

		return c.Status(201).JSON(penalizacao)
	}
}

func UpdatePenalizacao(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		id, err := strconv.Atoi(c.Params("id"))
		if err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "ID inválido"})
		}

		var penalizacao models.Penalizacao
		if err := c.BodyParser(&penalizacao); err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "Dados inválidos"})
		}

		penalizacao.IDPenalizacao = id

		// Validações
		if penalizacao.IDUsuario == 0 {
			return c.Status(400).JSON(fiber.Map{"error": "Usuário é obrigatório"})
		}
		if penalizacao.Descricao == "" {
			return c.Status(400).JSON(fiber.Map{"error": "Descrição é obrigatória"})
		}

		err = models.UpdatePenalizacao(db, &penalizacao)
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}

		return c.JSON(penalizacao)
	}
}

func DeletePenalizacao(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		id, err := strconv.Atoi(c.Params("id"))
		if err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "ID inválido"})
		}

		err = models.DeletePenalizacao(db, id)
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}

		return c.JSON(fiber.Map{"message": "Penalização deletada com sucesso"})
	}
}
