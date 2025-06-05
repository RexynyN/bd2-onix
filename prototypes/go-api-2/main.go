package main

import (
	"fmt"
	"log"
	"os"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/cors"
	"github.com/gofiber/fiber/v2/middleware/logger"
	"github.com/gofiber/fiber/v2/middleware/recover"

	"biblioteca-api/config"
	"biblioteca-api/database"
	"biblioteca-api/routes"
)

func main() {
	// Carrega configurações
	cfg := config.LoadConfig()

	// Conecta ao banco de dados
	db, err := database.Connect(cfg.DatabaseURL)
	if err != nil {
		log.Fatal("Falha ao conectar com o banco de dados:", err)
	}
	defer db.Close()

	// Testa a conexão
	if err := db.Ping(); err != nil {
		log.Fatal("Falha ao fazer ping no banco de dados:", err)
	}

	// Cria uma nova instância do Fiber
	app := fiber.New(fiber.Config{
		ErrorHandler: func(c *fiber.Ctx, err error) error {
			code := fiber.StatusInternalServerError
			message := "Internal Server Error"

			if e, ok := err.(*fiber.Error); ok {
				code = e.Code
				message = e.Message
			}

			return c.Status(code).JSON(fiber.Map{
				"error":   true,
				"message": message,
			})
		},
	})

	// Middleware
	app.Use(logger.New())
	app.Use(recover.New())
	app.Use(cors.New(cors.Config{
		AllowOrigins:     "http://localhost:3000, http://localhost:8080",
		AllowMethods:     "GET,POST,HEAD,PUT,DELETE,PATCH",
		AllowHeaders:     "Origin, Content-Type, Accept, Authorization",
		AllowCredentials: true,
	}))

	// Configura rotas
	routes.SetupRoutes(app, db)

	// Health check
	app.Get("/health", func(c *fiber.Ctx) error {
		return c.JSON(fiber.Map{
			"status":  "ok",
			"message": "API Biblioteca funcionando!",
		})
	})

	// Inicia o servidor
	port := os.Getenv("PORT")
	if port == "" {
		port = "3000"
	}

	fmt.Printf("🚀 Servidor rodando na porta %s\\n", port)
	log.Fatal(app.Listen(":" + port))
}
