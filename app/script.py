# Vou criar toda a estrutura do projeto Go com Fiber para o sistema de biblioteca

# Primeiro, vamos criar o arquivo principal main.go
main_go = """package main

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
			"status": "ok",
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
"""

# Arquivo de configuração
config_go = """package config

import (
	"os"
)

type Config struct {
	DatabaseURL string
	Port        string
	Environment string
}

func LoadConfig() *Config {
	return &Config{
		DatabaseURL: getEnv("DATABASE_URL", "host=localhost port=5432 user=postgres password=postgres dbname=biblioteca sslmode=disable"),
		Port:        getEnv("PORT", "3000"),
		Environment: getEnv("ENVIRONMENT", "development"),
	}
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}
"""

# Conexão com banco de dados
database_go = """package database

import (
	"database/sql"
	"fmt"

	_ "github.com/lib/pq"
)

// Connect conecta ao PostgreSQL usando database/sql
func Connect(databaseURL string) (*sql.DB, error) {
	db, err := sql.Open("postgres", databaseURL)
	if err != nil {
		return nil, fmt.Errorf("erro ao abrir conexão com banco: %w", err)
	}

	// Testa a conexão
	if err := db.Ping(); err != nil {
		return nil, fmt.Errorf("erro ao conectar com banco: %w", err)
	}

	// Configura pool de conexões
	db.SetMaxOpenConns(25)
	db.SetMaxIdleConns(5)

	return db, nil
}

// InitSchema inicializa o schema do banco de dados
func InitSchema(db *sql.DB) error {
	schema := `
	-- Criar tipos ENUM se não existir
	DO $$ BEGIN
		CREATE TYPE MidiaTipo AS ENUM ('livro', 'revista', 'dvd', 'artigo');
	EXCEPTION
		WHEN duplicate_object THEN null;
	END $$;

	-- Tabela: Usuario
	CREATE TABLE IF NOT EXISTS Usuario (
		id_usuario SERIAL PRIMARY KEY NOT NULL,
		nome VARCHAR NOT NULL,
		email VARCHAR,
		endereco VARCHAR,
		telefone VARCHAR,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);

	-- Tabela: Biblioteca
	CREATE TABLE IF NOT EXISTS Biblioteca (
		id_biblioteca SERIAL PRIMARY KEY NOT NULL,
		nome VARCHAR NOT NULL,
		endereco VARCHAR,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);

	-- Tabela: Mídia
	CREATE TABLE IF NOT EXISTS Midia (
		id_midia SERIAL PRIMARY KEY NOT NULL,
		tipo_midia MidiaTipo NOT NULL,
		condicao VARCHAR,
		id_biblioteca INT,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		FOREIGN KEY (id_biblioteca) REFERENCES Biblioteca(id_biblioteca)
	);

	-- Tabela: Emprestimo
	CREATE TABLE IF NOT EXISTS Emprestimo (
		id_emprestimo SERIAL PRIMARY KEY NOT NULL,
		data_emprestimo DATE NOT NULL,
		data_devolucao_prevista DATE,
		data_devolucao DATE,
		id_midia INT NOT NULL,
		id_usuario INT NOT NULL,
		status VARCHAR DEFAULT 'ativo',
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		FOREIGN KEY (id_midia) REFERENCES Midia(id_midia),
		FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario)
	);

	-- Tabela: Penalizacao
	CREATE TABLE IF NOT EXISTS Penalizacao (
		id_penalizacao SERIAL PRIMARY KEY NOT NULL,
		descricao TEXT,
		final_penalizacao DATE,
		valor DECIMAL(10,2),
		id_usuario INT,
		id_emprestimo INT,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario),
		FOREIGN KEY (id_emprestimo) REFERENCES Emprestimo(id_emprestimo)
	);

	-- Tabela: Livros
	CREATE TABLE IF NOT EXISTS Livros (
		id_livro SERIAL PRIMARY KEY NOT NULL,
		titulo VARCHAR NOT NULL,
		ISBN VARCHAR,
		numero_paginas INT,
		editora VARCHAR,
		data_publicacao DATE,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		FOREIGN KEY (id_livro) REFERENCES Midia(id_midia)
	);

	-- Tabela: Revistas
	CREATE TABLE IF NOT EXISTS Revistas (
		id_revista SERIAL PRIMARY KEY NOT NULL,
		titulo VARCHAR NOT NULL,
		ISSN VARCHAR,
		periodicidade VARCHAR,
		editora VARCHAR,
		data_publicacao DATE,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		FOREIGN KEY (id_revista) REFERENCES Midia(id_midia)
	);

	-- Tabela: DVDs
	CREATE TABLE IF NOT EXISTS DVDs (
		id_dvd SERIAL PRIMARY KEY NOT NULL,
		titulo VARCHAR NOT NULL,
		ISAN VARCHAR,
		duracao INT,
		distribuidora VARCHAR,
		data_lancamento DATE,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		FOREIGN KEY (id_dvd) REFERENCES Midia(id_midia)
	);

	-- Tabela: Artigos
	CREATE TABLE IF NOT EXISTS Artigos (
		id_artigo SERIAL PRIMARY KEY NOT NULL,
		titulo VARCHAR NOT NULL,
		DOI VARCHAR,
		publicadora VARCHAR,
		data_publicacao DATE,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		FOREIGN KEY (id_artigo) REFERENCES Midia(id_midia)
	);

	-- Tabela: Autores
	CREATE TABLE IF NOT EXISTS Autores (
		id_autor SERIAL PRIMARY KEY NOT NULL,
		nome VARCHAR NOT NULL,
		data_nascimento DATE,
		data_falecimento DATE,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);

	-- Tabela: Autorias
	CREATE TABLE IF NOT EXISTS Autorias (
		id_autorias SERIAL PRIMARY KEY NOT NULL,
		id_autor INT NOT NULL,
		id_midia INT NOT NULL,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		FOREIGN KEY (id_autor) REFERENCES Autores(id_autor),
		FOREIGN KEY (id_midia) REFERENCES Midia(id_midia)
	);

	-- Criar índices para melhor performance
	CREATE INDEX IF NOT EXISTS idx_emprestimo_usuario ON Emprestimo(id_usuario);
	CREATE INDEX IF NOT EXISTS idx_emprestimo_midia ON Emprestimo(id_midia);
	CREATE INDEX IF NOT EXISTS idx_midia_biblioteca ON Midia(id_biblioteca);
	CREATE INDEX IF NOT EXISTS idx_autorias_autor ON Autorias(id_autor);
	CREATE INDEX IF NOT EXISTS idx_autorias_midia ON Autorias(id_midia);
	`

	_, err := db.Exec(schema)
	return err
}
"""

# Modelos/Estruturas
models_go = """package models

import (
	"database/sql/driver"
	"fmt"
	"time"
)

// Tipo personalizado para MidiaTipo
type MidiaTipo string

const (
	Livro   MidiaTipo = "livro"
	Revista MidiaTipo = "revista"
	DVD     MidiaTipo = "dvd"
	Artigo  MidiaTipo = "artigo"
)

func (mt *MidiaTipo) Scan(value interface{}) error {
	if value == nil {
		*mt = ""
		return nil
	}
	switch s := value.(type) {
	case string:
		*mt = MidiaTipo(s)
	case []byte:
		*mt = MidiaTipo(s)
	default:
		return fmt.Errorf("cannot scan %T into MidiaTipo", value)
	}
	return nil
}

func (mt MidiaTipo) Value() (driver.Value, error) {
	return string(mt), nil
}

// Usuario representa a tabela Usuario
type Usuario struct {
	ID        int       `json:"id_usuario" db:"id_usuario"`
	Nome      string    `json:"nome" db:"nome"`
	Email     *string   `json:"email" db:"email"`
	Endereco  *string   `json:"endereco" db:"endereco"`
	Telefone  *string   `json:"telefone" db:"telefone"`
	CreatedAt time.Time `json:"created_at" db:"created_at"`
	UpdatedAt time.Time `json:"updated_at" db:"updated_at"`
}

// Biblioteca representa a tabela Biblioteca
type Biblioteca struct {
	ID        int       `json:"id_biblioteca" db:"id_biblioteca"`
	Nome      string    `json:"nome" db:"nome"`
	Endereco  *string   `json:"endereco" db:"endereco"`
	CreatedAt time.Time `json:"created_at" db:"created_at"`
	UpdatedAt time.Time `json:"updated_at" db:"updated_at"`
}

// Midia representa a tabela Midia
type Midia struct {
	ID            int        `json:"id_midia" db:"id_midia"`
	TipoMidia     MidiaTipo  `json:"tipo_midia" db:"tipo_midia"`
	Condicao      *string    `json:"condicao" db:"condicao"`
	IDBiblioteca  *int       `json:"id_biblioteca" db:"id_biblioteca"`
	CreatedAt     time.Time  `json:"created_at" db:"created_at"`
	UpdatedAt     time.Time  `json:"updated_at" db:"updated_at"`
}

// Emprestimo representa a tabela Emprestimo
type Emprestimo struct {
	ID                     int        `json:"id_emprestimo" db:"id_emprestimo"`
	DataEmprestimo         time.Time  `json:"data_emprestimo" db:"data_emprestimo"`
	DataDevolucaoPrevista  *time.Time `json:"data_devolucao_prevista" db:"data_devolucao_prevista"`
	DataDevolucao          *time.Time `json:"data_devolucao" db:"data_devolucao"`
	IDMidia                int        `json:"id_midia" db:"id_midia"`
	IDUsuario              int        `json:"id_usuario" db:"id_usuario"`
	Status                 string     `json:"status" db:"status"`
	CreatedAt              time.Time  `json:"created_at" db:"created_at"`
	UpdatedAt              time.Time  `json:"updated_at" db:"updated_at"`
}

// Penalizacao representa a tabela Penalizacao
type Penalizacao struct {
	ID               int       `json:"id_penalizacao" db:"id_penalizacao"`
	Descricao        *string   `json:"descricao" db:"descricao"`
	FinalPenalizacao *time.Time `json:"final_penalizacao" db:"final_penalizacao"`
	Valor            *float64  `json:"valor" db:"valor"`
	IDUsuario        *int      `json:"id_usuario" db:"id_usuario"`
	IDEmprestimo     *int      `json:"id_emprestimo" db:"id_emprestimo"`
	CreatedAt        time.Time `json:"created_at" db:"created_at"`
	UpdatedAt        time.Time `json:"updated_at" db:"updated_at"`
}

// Livro representa a tabela Livros
type Livro struct {
	ID              int        `json:"id_livro" db:"id_livro"`
	Titulo          string     `json:"titulo" db:"titulo"`
	ISBN            *string    `json:"isbn" db:"isbn"`
	NumeroPaginas   *int       `json:"numero_paginas" db:"numero_paginas"`
	Editora         *string    `json:"editora" db:"editora"`
	DataPublicacao  *time.Time `json:"data_publicacao" db:"data_publicacao"`
	CreatedAt       time.Time  `json:"created_at" db:"created_at"`
	UpdatedAt       time.Time  `json:"updated_at" db:"updated_at"`
}

// Revista representa a tabela Revistas
type Revista struct {
	ID              int        `json:"id_revista" db:"id_revista"`
	Titulo          string     `json:"titulo" db:"titulo"`
	ISSN            *string    `json:"issn" db:"issn"`
	Periodicidade   *string    `json:"periodicidade" db:"periodicidade"`
	Editora         *string    `json:"editora" db:"editora"`
	DataPublicacao  *time.Time `json:"data_publicacao" db:"data_publicacao"`
	CreatedAt       time.Time  `json:"created_at" db:"created_at"`
	UpdatedAt       time.Time  `json:"updated_at" db:"updated_at"`
}

// DVD representa a tabela DVDs
type DVD struct {
	ID             int        `json:"id_dvd" db:"id_dvd"`
	Titulo         string     `json:"titulo" db:"titulo"`
	ISAN           *string    `json:"isan" db:"isan"`
	Duracao        *int       `json:"duracao" db:"duracao"`
	Distribuidora  *string    `json:"distribuidora" db:"distribuidora"`
	DataLancamento *time.Time `json:"data_lancamento" db:"data_lancamento"`
	CreatedAt      time.Time  `json:"created_at" db:"created_at"`
	UpdatedAt      time.Time  `json:"updated_at" db:"updated_at"`
}

// Artigo representa a tabela Artigos
type Artigo struct {
	ID              int        `json:"id_artigo" db:"id_artigo"`
	Titulo          string     `json:"titulo" db:"titulo"`
	DOI             *string    `json:"doi" db:"doi"`
	Publicadora     *string    `json:"publicadora" db:"publicadora"`
	DataPublicacao  *time.Time `json:"data_publicacao" db:"data_publicacao"`
	CreatedAt       time.Time  `json:"created_at" db:"created_at"`
	UpdatedAt       time.Time  `json:"updated_at" db:"updated_at"`
}

// Autor representa a tabela Autores
type Autor struct {
	ID               int        `json:"id_autor" db:"id_autor"`
	Nome             string     `json:"nome" db:"nome"`
	DataNascimento   *time.Time `json:"data_nascimento" db:"data_nascimento"`
	DataFalecimento  *time.Time `json:"data_falecimento" db:"data_falecimento"`
	CreatedAt        time.Time  `json:"created_at" db:"created_at"`
	UpdatedAt        time.Time  `json:"updated_at" db:"updated_at"`
}

// Autoria representa a tabela Autorias
type Autoria struct {
	ID        int       `json:"id_autorias" db:"id_autorias"`
	IDAutor   int       `json:"id_autor" db:"id_autor"`
	IDMidia   int       `json:"id_midia" db:"id_midia"`
	CreatedAt time.Time `json:"created_at" db:"created_at"`
}

// DTOs para requests
type CreateUsuarioRequest struct {
	Nome     string  `json:"nome" validate:"required"`
	Email    *string `json:"email"`
	Endereco *string `json:"endereco"`
	Telefone *string `json:"telefone"`
}

type UpdateUsuarioRequest struct {
	Nome     *string `json:"nome"`
	Email    *string `json:"email"`
	Endereco *string `json:"endereco"`
	Telefone *string `json:"telefone"`
}

type CreateBibliotecaRequest struct {
	Nome     string  `json:"nome" validate:"required"`
	Endereco *string `json:"endereco"`
}

type CreateMidiaRequest struct {
	TipoMidia    MidiaTipo `json:"tipo_midia" validate:"required"`
	Condicao     *string   `json:"condicao"`
	IDBiblioteca *int      `json:"id_biblioteca"`
}

type CreateEmprestimoRequest struct {
	DataEmprestimo        time.Time  `json:"data_emprestimo" validate:"required"`
	DataDevolucaoPrevista *time.Time `json:"data_devolucao_prevista"`
	IDMidia               int        `json:"id_midia" validate:"required"`
	IDUsuario             int        `json:"id_usuario" validate:"required"`
}

type CreateLivroRequest struct {
	Titulo         string     `json:"titulo" validate:"required"`
	ISBN           *string    `json:"isbn"`
	NumeroPaginas  *int       `json:"numero_paginas"`
	Editora        *string    `json:"editora"`
	DataPublicacao *time.Time `json:"data_publicacao"`
	TipoMidia      MidiaTipo  `json:"tipo_midia" validate:"required"`
	Condicao       *string    `json:"condicao"`
	IDBiblioteca   *int       `json:"id_biblioteca"`
}

// Response com dados expandidos
type EmprestimoDetalhado struct {
	Emprestimo
	Usuario Usuario `json:"usuario"`
	Midia   Midia   `json:"midia"`
}

type MidiaDetalhada struct {
	Midia
	Biblioteca *Biblioteca `json:"biblioteca,omitempty"`
	Autores    []Autor     `json:"autores,omitempty"`
	Livro      *Livro      `json:"livro,omitempty"`
	Revista    *Revista    `json:"revista,omitempty"`
	DVD        *DVD        `json:"dvd,omitempty"`
	Artigo     *Artigo     `json:"artigo,omitempty"`
}
"""

print("Arquivos base do projeto criados:")
print("✓ main.go")
print("✓ config/config.go")
print("✓ database/database.go")
print("✓ models/models.go")