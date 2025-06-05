# Makefile para o projeto Biblioteca API

.PHONY: help build run test clean docker-up docker-down install dev

# Variáveis
BINARY_NAME=biblioteca-api
DOCKER_COMPOSE_FILE=docker-compose.yml

help: ## Mostra esta ajuda
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\\033[36m%-15s\\033[0m %s\\n", $$1, $$2}'

install: ## Instala as dependências
	go mod download
	go mod tidy

build: ## Compila a aplicação
	go build -o $(BINARY_NAME) .

run: ## Executa a aplicação
	go run .

dev: ## Executa em modo desenvolvimento com reload
	go run . --dev

test: ## Executa os testes
	go test -v ./...

test-coverage: ## Executa testes com cobertura
	go test -v -cover ./...

clean: ## Remove arquivos gerados
	go clean
	rm -f $(BINARY_NAME)

docker-build: ## Constrói a imagem Docker
	docker build -t $(BINARY_NAME) .

docker-up: ## Sobe os containers
	docker-compose -f $(DOCKER_COMPOSE_FILE) up -d

docker-down: ## Para os containers
	docker-compose -f $(DOCKER_COMPOSE_FILE) down

docker-logs: ## Mostra logs dos containers
	docker-compose -f $(DOCKER_COMPOSE_FILE) logs -f

docker-rebuild: ## Reconstrói e sobe os containers
	docker-compose -f $(DOCKER_COMPOSE_FILE) down
	docker-compose -f $(DOCKER_COMPOSE_FILE) up --build -d

setup-db: ## Configura o banco de dados
	@echo "Configurando banco de dados..."
	@echo "Aguarde a inicialização do PostgreSQL..."
	sleep 10
	@echo "Banco configurado!"

format: ## Formata o código
	go fmt ./...

lint: ## Executa linter
	golangci-lint run

security: ## Verifica vulnerabilidades
	gosec ./...

mod-update: ## Atualiza dependências
	go get -u ./...
	go mod tidy

.DEFAULT_GOAL := help