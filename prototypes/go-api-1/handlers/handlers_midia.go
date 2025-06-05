package handlers

import (
	"database/sql"
	"strconv"

	"onix/models"

	"github.com/gofiber/fiber/v2"
)

func GetMidias(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		midias, err := models.GetAllMidias(db)
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}
		return c.JSON(midias)
	}
}

func GetMidia(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		id, err := strconv.Atoi(c.Params("id"))
		if err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "ID inválido"})
		}

		midia, err := models.GetMidiaByID(db, id)
		if err != nil {
			if err == sql.ErrNoRows {
				return c.Status(404).JSON(fiber.Map{"error": "Mídia não encontrada"})
			}
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}
		return c.JSON(midia)
	}
}

func CreateMidia(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		var midia models.Midia
		if err := c.BodyParser(&midia); err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "Dados inválidos"})
		}

		// Validações básicas
		if midia.TipoMidia == "" {
			return c.Status(400).JSON(fiber.Map{"error": "Tipo de mídia é obrigatório"})
		}
		if midia.Titulo == "" {
			return c.Status(400).JSON(fiber.Map{"error": "Título é obrigatório"})
		}
		if midia.IDBiblioteca == 0 {
			return c.Status(400).JSON(fiber.Map{"error": "Biblioteca é obrigatória"})
		}

		// Validar tipo de mídia
		validTypes := map[string]bool{"livro": true, "revista": true, "dvd": true, "artigo": true}
		if !validTypes[midia.TipoMidia] {
			return c.Status(400).JSON(fiber.Map{"error": "Tipo de mídia inválido"})
		}

		err := models.CreateMidia(db, &midia)
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}

		return c.Status(201).JSON(midia)
	}
}

func UpdateMidia(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		id, err := strconv.Atoi(c.Params("id"))
		if err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "ID inválido"})
		}

		var midia models.Midia
		if err := c.BodyParser(&midia); err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "Dados inválidos"})
		}

		midia.IDMidia = id

		// Validações básicas
		if midia.Titulo == "" {
			return c.Status(400).JSON(fiber.Map{"error": "Título é obrigatório"})
		}
		if midia.IDBiblioteca == 0 {
			return c.Status(400).JSON(fiber.Map{"error": "Biblioteca é obrigatória"})
		}

		err = models.UpdateMidia(db, &midia)
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}

		return c.JSON(midia)
	}
}

func DeleteMidia(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		id, err := strconv.Atoi(c.Params("id"))
		if err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "ID inválido"})
		}

		err = models.DeleteMidia(db, id)
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}

		return c.JSON(fiber.Map{"message": "Mídia deletada com sucesso"})
	}
}
