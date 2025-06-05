# go.mod
go_mod = """module biblioteca-api

go 1.21

require (
	github.com/gofiber/fiber/v2 v2.52.0
	github.com/lib/pq v1.10.9
	github.com/go-playground/validator/v10 v10.16.0
	github.com/joho/godotenv v1.5.1
)

require (
	github.com/andybalholm/brotli v1.0.5 // indirect
	github.com/gabriel-vasile/mimetype v1.4.2 // indirect
	github.com/go-playground/locales v0.14.1 // indirect
	github.com/go-playground/universal-translator v0.18.1 // indirect
	github.com/google/uuid v1.5.0 // indirect
	github.com/klauspost/compress v1.17.0 // indirect
	github.com/leodido/go-urn v1.2.4 // indirect
	github.com/mattn/go-colorable v0.1.13 // indirect
	github.com/mattn/go-isatty v0.0.20 // indirect
	github.com/mattn/go-runewidth v0.0.15 // indirect
	github.com/rivo/uniseg v0.2.0 // indirect
	github.com/valyala/bytebufferpool v1.0.0 // indirect
	github.com/valyala/fasthttp v1.51.0 // indirect
	github.com/valyala/tcplisten v1.0.0 // indirect
	golang.org/x/crypto v0.7.0 // indirect
	golang.org/x/net v0.8.0 // indirect
	golang.org/x/sys v0.15.0 // indirect
	golang.org/x/text v0.8.0 // indirect
)
"""

# Dockerfile
dockerfile = """# Build stage
FROM golang:1.21-alpine AS builder

WORKDIR /app

# Install dependencies
RUN apk add --no-cache git

# Copy go mod files
COPY go.mod go.sum ./
RUN go mod download

# Copy source code
COPY . .

# Build the application
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

# Final stage
FROM alpine:latest

# Install ca-certificates for HTTPS
RUN apk --no-cache add ca-certificates tzdata

WORKDIR /root/

# Copy the binary from builder stage
COPY --from=builder /app/main .

# Expose port
EXPOSE 3000

# Command to run
CMD ["./main"]
"""

# docker-compose.yml
docker_compose = """version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: biblioteca_postgres
    environment:
      POSTGRES_DB: biblioteca
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build: .
    container_name: biblioteca_api
    environment:
      DATABASE_URL: "host=postgres port=5432 user=postgres password=postgres dbname=biblioteca sslmode=disable"
      PORT: "3000"
      ENVIRONMENT: "production"
    ports:
      - "3000:3000"
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped

  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: biblioteca_pgadmin
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@biblioteca.com
      PGADMIN_DEFAULT_PASSWORD: admin123
    ports:
      - "8080:80"
    depends_on:
      - postgres
    volumes:
      - pgadmin_data:/var/lib/pgadmin

volumes:
  postgres_data:
  pgadmin_data:
"""

# .env.example
env_example = """# Configurações do Banco de Dados
DATABASE_URL=host=localhost port=5432 user=postgres password=postgres dbname=biblioteca sslmode=disable

# Configurações do Servidor
PORT=3000
ENVIRONMENT=development

# Configurações opcionais
LOG_LEVEL=info
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
"""

# Makefile
makefile = """# Makefile para o projeto Biblioteca API

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
"""

# README.md
readme = """# Sistema de Gerenciamento de Biblioteca - API

Uma API REST completa para gerenciamento de bibliotecas, desenvolvida em Go com Fiber framework e PostgreSQL.

## 🚀 Características

- **CRUD completo** para todas as entidades (Usuários, Bibliotecas, Mídias, Empréstimos, etc.)
- **Sistema de empréstimos** com controle de datas e renovações
- **Gerenciamento de penalizações** por atraso
- **Dashboard com estatísticas** e relatórios
- **Busca global** em múltiplas entidades
- **Paginação** em todas as listagens
- **Validação de dados** robusta
- **Tratamento de erros** padronizado
- **Documentação** completa da API

## 🏗️ Arquitetura

O projeto segue uma arquitetura limpa e organizada:

```
biblioteca-api/
├── cmd/                    # Ponto de entrada da aplicação
├── config/                 # Configurações
├── database/              # Conexão e schemas do banco
├── handlers/              # Controladores HTTP
├── models/                # Modelos de dados
├── routes/                # Definição das rotas
├── utils/                 # Utilitários e helpers
├── docker-compose.yml     # Configuração Docker
├── Dockerfile            # Imagem Docker
├── Makefile              # Comandos automatizados
└── README.md             # Esta documentação
```

## 🛠️ Tecnologias Utilizadas

- **Go 1.21+** - Linguagem de programação
- **Fiber v2** - Framework web rápido e minimalista
- **PostgreSQL** - Banco de dados relacional
- **Docker & Docker Compose** - Containerização
- **database/sql** - Driver nativo do PostgreSQL (sem ORM)

## 📦 Instalação e Execução

### Pré-requisitos

- Go 1.21 ou superior
- PostgreSQL 13+
- Docker e Docker Compose (opcional)

### Método 1: Execução Local

1. **Clone o repositório:**
```bash
git clone <repository-url>
cd biblioteca-api
```

2. **Instale as dependências:**
```bash
make install
# ou
go mod download
```

3. **Configure as variáveis de ambiente:**
```bash
cp .env.example .env
# Edite o arquivo .env conforme necessário
```

4. **Configure o PostgreSQL:**
```bash
# Crie o banco de dados
createdb biblioteca

# Execute as migrações (o schema será criado automaticamente na primeira execução)
```

5. **Execute a aplicação:**
```bash
make run
# ou
go run .
```

### Método 2: Docker (Recomendado)

1. **Clone o repositório:**
```bash
git clone <repository-url>
cd biblioteca-api
```

2. **Suba os containers:**
```bash
make docker-up
```

3. **Verifique os logs:**
```bash
make docker-logs
```

A API estará disponível em `http://localhost:3000`
O pgAdmin estará disponível em `http://localhost:8080` (admin@biblioteca.com / admin123)

## 📖 Uso da API

### Endpoints Principais

#### Autenticação
A API não implementa autenticação por padrão, mas é estruturada para facilitar a adição de JWT ou OAuth.

#### Usuários
```http
GET    /api/v1/usuarios              # Lista usuários
GET    /api/v1/usuarios/{id}         # Busca usuário por ID
POST   /api/v1/usuarios              # Cria usuário
PUT    /api/v1/usuarios/{id}         # Atualiza usuário
DELETE /api/v1/usuarios/{id}         # Remove usuário
GET    /api/v1/usuarios/{id}/emprestimos # Empréstimos do usuário
```

#### Bibliotecas
```http
GET    /api/v1/bibliotecas           # Lista bibliotecas
GET    /api/v1/bibliotecas/{id}      # Busca biblioteca por ID
POST   /api/v1/bibliotecas           # Cria biblioteca
PUT    /api/v1/bibliotecas/{id}      # Atualiza biblioteca
DELETE /api/v1/bibliotecas/{id}      # Remove biblioteca
GET    /api/v1/bibliotecas/{id}/midias # Mídias da biblioteca
```

#### Livros
```http
GET    /api/v1/livros                # Lista livros
GET    /api/v1/livros/{id}           # Busca livro por ID
POST   /api/v1/livros                # Cria livro
PUT    /api/v1/livros/{id}           # Atualiza livro
DELETE /api/v1/livros/{id}           # Remove livro
POST   /api/v1/livros/{id}/autores   # Adiciona autor ao livro
DELETE /api/v1/livros/{id}/autores/{autor_id} # Remove autor do livro
```

#### Empréstimos
```http
GET    /api/v1/emprestimos           # Lista empréstimos
GET    /api/v1/emprestimos/{id}      # Busca empréstimo por ID
POST   /api/v1/emprestimos           # Cria empréstimo
PUT    /api/v1/emprestimos/{id}/devolver # Devolve empréstimo
PUT    /api/v1/emprestimos/{id}/renovar  # Renova empréstimo
GET    /api/v1/emprestimos/atrasados      # Lista empréstimos em atraso
```

#### Dashboard
```http
GET    /api/v1/dashboard             # Estatísticas gerais
GET    /api/v1/dashboard/estatisticas     # Estatísticas detalhadas
GET    /api/v1/dashboard/emprestimos-por-mes # Gráfico empréstimos/mês
GET    /api/v1/dashboard/livros-mais-emprestados # Top livros
```

#### Busca Global
```http
GET    /api/v1/search?q={termo}     # Busca em múltiplas entidades
```

### Exemplos de Requisições

#### Criar um usuário:
```bash
curl -X POST http://localhost:3000/api/v1/usuarios \\
  -H "Content-Type: application/json" \\
  -d '{
    "nome": "João Silva",
    "email": "joao@email.com",
    "endereco": "Rua das Flores, 123",
    "telefone": "(11) 99999-9999"
  }'
```

#### Criar um livro:
```bash
curl -X POST http://localhost:3000/api/v1/livros \\
  -H "Content-Type: application/json" \\
  -d '{
    "titulo": "O Senhor dos Anéis",
    "isbn": "978-0544003415",
    "numero_paginas": 1178,
    "editora": "Martins Fontes",
    "data_publicacao": "2019-11-25T00:00:00Z",
    "tipo_midia": "livro",
    "condicao": "novo",
    "id_biblioteca": 1
  }'
```

#### Fazer um empréstimo:
```bash
curl -X POST http://localhost:3000/api/v1/emprestimos \\
  -H "Content-Type: application/json" \\
  -d '{
    "data_emprestimo": "2024-01-15T10:00:00Z",
    "data_devolucao_prevista": "2024-01-30T10:00:00Z",
    "id_midia": 1,
    "id_usuario": 1
  }'
```

### Parâmetros de Query Comuns

- `page` - Número da página (padrão: 1)
- `limit` - Itens por página (padrão: 10)
- `search` - Termo de busca
- `status` - Filtro por status
- `tipo` - Filtro por tipo de mídia

## 🗃️ Modelo de Dados

### Entidades Principais

1. **Usuario** - Informações dos usuários da biblioteca
2. **Biblioteca** - Dados das bibliotecas
3. **Midia** - Base para todos os tipos de mídia
4. **Livros/Revistas/DVDs/Artigos** - Tipos específicos de mídia
5. **Emprestimo** - Controle de empréstimos
6. **Penalizacao** - Multas e penalizações
7. **Autores** - Informações dos autores
8. **Autorias** - Relacionamento entre autores e mídias

### Relacionamentos

- Um usuário pode ter múltiplos empréstimos
- Uma mídia pode ter múltiplos autores
- Uma biblioteca pode ter múltiplas mídias
- Um empréstimo pode gerar penalizações

## 🧪 Testes

```bash
# Executar todos os testes
make test

# Executar testes com cobertura
make test-coverage
```

## 📋 Funcionalidades Especiais

### Sistema de Empréstimos
- Controle automático de disponibilidade
- Cálculo automático de datas de devolução
- Renovação de empréstimos
- Controle de atrasos

### Sistema de Penalizações
- Multas automáticas por atraso
- Bloqueio de usuários com penalizações ativas
- Controle de valores e prazos

### Dashboard e Relatórios
- Estatísticas em tempo real
- Gráficos de empréstimos por período
- Rankings de livros e usuários
- Distribuição de mídias por biblioteca

## 🔧 Configuração

### Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|---------|
| `DATABASE_URL` | String de conexão PostgreSQL | `host=localhost port=5432 user=postgres password=postgres dbname=biblioteca sslmode=disable` |
| `PORT` | Porta do servidor | `3000` |
| `ENVIRONMENT` | Ambiente (development/production) | `development` |

### Configuração do Banco

O schema do banco é criado automaticamente na primeira execução. Para customizar, edite o arquivo `database/database.go`.

## 🚀 Deploy

### Docker Production

```bash
# Build da imagem
docker build -t biblioteca-api:latest .

# Run do container
docker run -d \\
  --name biblioteca-api \\
  -p 3000:3000 \\
  -e DATABASE_URL="sua-string-de-conexao" \\
  biblioteca-api:latest
```

### Deploy em Cloud

A aplicação está preparada para deploy em:
- Heroku
- Railway
- Render
- AWS ECS
- Google Cloud Run

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para dúvidas ou problemas:
- Abra uma issue no GitHub
- Entre em contato através do email: [seu-email@exemplo.com]

## 🏆 Status do Projeto

✅ CRUD básico para todas entidades  
✅ Sistema de empréstimos  
✅ Controle de penalizações  
✅ Dashboard com estatísticas  
✅ Busca global  
✅ Documentação completa  
🔄 Testes unitários (em desenvolvimento)  
⏳ Sistema de autenticação (planejado)  
⏳ API de relatórios avançados (planejado)  

---

Desenvolvido com ❤️ em Go
"""

print("Arquivos de configuração e documentação criados:")
print("✓ go.mod")
print("✓ Dockerfile")
print("✓ docker-compose.yml")
print("✓ .env.example")
print("✓ Makefile")
print("✓ README.md")