package handlers

import (
	"database/sql"
	"strconv"

	"onix/models"

	"github.com/gofiber/fiber/v2"
)

func GetBibliotecas(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		bibliotecas, err := models.GetAllBibliotecas(db)
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}
		return c.JSON(bibliotecas)
	}
}

func GetBiblioteca(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		id, err := strconv.Atoi(c.Params("id"))
		if err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "ID inválido"})
		}

		biblioteca, err := models.GetBibliotecaByID(db, id)
		if err != nil {
			if err == sql.ErrNoRows {
				return c.Status(404).JSON(fiber.Map{"error": "Biblioteca não encontrada"})
			}
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}
		return c.JSON(biblioteca)
	}
}

func CreateBiblioteca(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		var biblioteca models.Biblioteca
		if err := c.BodyParser(&biblioteca); err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "Dados inválidos"})
		}

		if biblioteca.Nome == "" {
			return c.Status(400).JSON(fiber.Map{"error": "Nome é obrigatório"})
		}

		err := models.CreateBiblioteca(db, &biblioteca)
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}

		return c.Status(201).JSON(biblioteca)
	}
}

func UpdateBiblioteca(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		id, err := strconv.Atoi(c.Params("id"))
		if err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "ID inválido"})
		}

		var biblioteca models.Biblioteca
		if err := c.BodyParser(&biblioteca); err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "Dados inválidos"})
		}

		biblioteca.IDBiblioteca = id

		if biblioteca.Nome == "" {
			return c.Status(400).JSON(fiber.Map{"error": "Nome é obrigatório"})
		}

		err = models.UpdateBiblioteca(db, &biblioteca)
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}

		return c.JSON(biblioteca)
	}
}

func DeleteBiblioteca(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		id, err := strconv.Atoi(c.Params("id"))
		if err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "ID inválido"})
		}

		err = models.DeleteBiblioteca(db, id)
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}

		return c.JSON(fiber.Map{"message": "Biblioteca deletada com sucesso"})
	}
}
