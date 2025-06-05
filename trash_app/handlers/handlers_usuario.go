package handlers

import (
	"database/sql"
	"strconv"

	"onix/models"

	"github.com/gofiber/fiber/v2"
)

func GetUsuarios(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		usuarios, err := models.GetAllUsuarios(db)
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}
		return c.JSON(usuarios)
	}
}

func GetUsuario(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		id, err := strconv.Atoi(c.Params("id"))
		if err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "ID inválido"})
		}

		usuario, err := models.GetUsuarioByID(db, id)
		if err != nil {
			if err == sql.ErrNoRows {
				return c.Status(404).JSON(fiber.Map{"error": "Usuário não encontrado"})
			}
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}
		return c.JSON(usuario)
	}
}

func CreateUsuario(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		var usuario models.Usuario
		if err := c.BodyParser(&usuario); err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "Dados inválidos"})
		}

		if usuario.Nome == "" {
			return c.Status(400).JSON(fiber.Map{"error": "Nome é obrigatório"})
		}

		err := models.CreateUsuario(db, &usuario)
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}

		return c.Status(201).JSON(usuario)
	}
}

func UpdateUsuario(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		id, err := strconv.Atoi(c.Params("id"))
		if err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "ID inválido"})
		}

		var usuario models.Usuario
		if err := c.BodyParser(&usuario); err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "Dados inválidos"})
		}

		usuario.IDUsuario = id

		if usuario.Nome == "" {
			return c.Status(400).JSON(fiber.Map{"error": "Nome é obrigatório"})
		}

		err = models.UpdateUsuario(db, &usuario)
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}

		return c.JSON(usuario)
	}
}

func DeleteUsuario(db *sql.DB) fiber.Handler {
	return func(c *fiber.Ctx) error {
		id, err := strconv.Atoi(c.Params("id"))
		if err != nil {
			return c.Status(400).JSON(fiber.Map{"error": "ID inválido"})
		}

		err = models.DeleteUsuario(db, id)
		if err != nil {
			return c.Status(500).JSON(fiber.Map{"error": err.Error()})
		}

		return c.JSON(fiber.Map{"message": "Usuário deletado com sucesso"})
	}
}
