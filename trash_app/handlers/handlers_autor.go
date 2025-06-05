package handlers

import (
	"database/sql"
	"strconv"

	"onix/models"

	"github.com/gofiber/fiber/v2"
)

func GetAutores(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		autores, err := models.GetAllAutores(db)
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}
		return c.JSON(autores)
	}
}

func GetAutor(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		id, err := strconv.Atoi(c.Params("id"))
		if err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "ID inválido"})
		}

		autor, err := models.GetAutorByID(db, id)
		if err != nil {
			if err == sql.ErrNoRows {
				return c.Status(404).JSON(fiber.Map{"error": "Autor não encontrado"})
			}
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}
		return c.JSON(autor)
	}
}

func CreateAutor(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		var autor models.Autor
		if err := c.BodyParser(&autor); err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "Dados inválidos"})
		}

		if autor.Nome == "" {
			return c.Status(400).JSON(fiber.Map{"error": "Nome é obrigatório"})
		}

		err := models.CreateAutor(db, &autor)
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}

		return c.Status(201).JSON(autor)
	}
}

func UpdateAutor(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		id, err := strconv.Atoi(c.Params("id"))
		if err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "ID inválido"})
		}

		var autor models.Autor
		if err := c.BodyParser(&autor); err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "Dados inválidos"})
		}

		autor.IDAutor = id

		if autor.Nome == "" {
			return c.Status(400).JSON(fiber.Map{"error": "Nome é obrigatório"})
		}

		err = models.UpdateAutor(db, &autor)
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}

		return c.JSON(autor)
	}
}

func DeleteAutor(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		id, err := strconv.Atoi(c.Params("id"))
		if err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "ID inválido"})
		}

		err = models.DeleteAutor(db, id)
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}

		return c.JSON(fiber.Map{"message": "Autor deletado com sucesso"})
	}
}

func GetAutorias(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		autorias, err := models.GetAllAutorias(db)
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}
		return c.JSON(autorias)
	}
}

func CreateAutoria(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		var autoria models.Autoria
		if err := c.BodyParser(&autoria); err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "Dados inválidos"})
		}

		if autoria.IDAutor == 0 {
			return c.Status(400).JSON(fiber.Map{"error": "Autor é obrigatório"})
		}
		if autoria.IDMidia == 0 {
			return c.Status(400).JSON(fiber.Map{"error": "Mídia é obrigatória"})
		}

		err := models.CreateAutoria(db, &autoria)
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}

		return c.Status(201).JSON(autoria)
	}
}

func DeleteAutoria(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		id, err := strconv.Atoi(c.Params("id"))
		if err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "ID inválido"})
		}

		err = models.DeleteAutoria(db, id)
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}

		return c.JSON(fiber.Map{"message": "Autoria deletada com sucesso"})
	}
}
