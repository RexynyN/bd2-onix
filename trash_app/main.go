package main

import (
	"log"
	"onix/database"
	"onix/routes"
	"os"
	"os/signal"
	"syscall"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/cors"
	"github.com/gofiber/fiber/v2/middleware/logger"
	"github.com/gofiber/fiber/v2/middleware/recover"
	"github.com/gofiber/template/html/v2"
)

func main() {
	// Conectar ao banco de dados
	db, err := database.Connect()
	if err != nil {
		log.Fatal("Erro ao conectar com o banco de dados:\n", err)
	}
	defer db.Close()

	// Configurar template engine
	engine := html.New("./templates", ".html")
	engine.Reload(true) // desenvolvimento

	// Criar aplicação Fiber
	app := fiber.New(fiber.Config{
		Views:       engine,
		ViewsLayout: "layouts/main",
	})

	// Middlewares
	app.Use(logger.New())
	app.Use(recover.New())
	app.Use(cors.New())

	// Servir arquivos estáticos
	app.Static("/", "./static")

	// Configurar rotas
	routes.Setup(app, db)

	// Iniciar servidor em uma goroutine
	go func() {
		if err := app.Listen(":3000"); err != nil {
			log.Fatal("Erro ao iniciar servidor:", err)
		}
	}()

	// Aguardar sinal de interrupção
	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt, syscall.SIGTERM)
	<-c

	log.Println("Encerrando servidor...")
	if err := app.Shutdown(); err != nil {
		log.Fatal("Erro ao encerrar servidor:", err)
	}
}
