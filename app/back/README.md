# Sistema de Gerenciamento de Biblioteca - API

Este é um backend desenvolvido em Python com FastAPI para gerenciamento de biblioteca e empréstimo de livros. A API conecta-se com um banco de dados PostgreSQL local e não utiliza ORM, trabalhando diretamente com SQL.

## 🚀 Características

- **FastAPI**: Framework moderno e rápido para APIs
- **PostgreSQL**: Banco de dados relacional robusto
- **Sem ORM**: Consultas SQL diretas usando psycopg2
- **Connection Pool**: Pool de conexões para melhor performance
- **Validação**: Validação de dados com Pydantic
- **Documentação**: Documentação automática com Swagger/OpenAPI
- **Estrutura Modular**: Organização clara em routers, services e schemas

## 📋 Pré-requisitos

- Python 3.8+
- PostgreSQL 12+
- pip (gerenciador de pacotes Python)

## 🛠️ Instalação

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd library_api
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure o banco de dados

#### Crie o banco de dados PostgreSQL:
```sql
CREATE DATABASE biblioteca;
CREATE USER usuario WITH PASSWORD 'senha';
GRANT ALL PRIVILEGES ON DATABASE biblioteca TO usuario;
```

#### Execute o schema:
```bash
psql -U usuario -d biblioteca -f schema.sql
```

### 5. Configure as variáveis de ambiente

Copie o arquivo `.env.example` para `.env` e ajuste as configurações:
```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:
```env
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USER=usuario
DATABASE_PASSWORD=senha
DATABASE_NAME=biblioteca

MIN_CONNECTIONS=5
MAX_CONNECTIONS=20

API_V1_PREFIX=/api/v1
PROJECT_NAME=Sistema de Gerenciamento de Biblioteca
```

## 🚀 Executando a aplicação

### Desenvolvimento
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Produção
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

A API estará disponível em: http://localhost:8000

## 📚 Documentação da API

Após iniciar a aplicação, acesse:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🏗️ Estrutura do Projeto

```
library_api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Aplicação principal
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py          # Configurações
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py        # Gerenciamento do banco
│   ├── models/
│   │   └── __init__.py
│   ├── schemas/               # Modelos Pydantic
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── usuario.py
│   │   ├── biblioteca.py
│   │   ├── emprestimo.py
│   │   ├── livro.py
│   │   ├── revista.py
│   │   ├── dvd.py
│   │   ├── artigo.py
│   │   ├── estoque.py
│   │   ├── autor.py
│   │   └── penalizacao.py
│   ├── services/              # Lógica de negócio
│   │   ├── __init__.py
│   │   ├── base_service.py
│   │   ├── usuario_service.py
│   │   ├── biblioteca_service.py
│   │   ├── emprestimo_service.py
│   │   └── media_service.py
│   └── routers/               # Endpoints da API
│       ├── __init__.py
│       ├── usuario.py
│       ├── biblioteca.py
│       ├── emprestimo.py
│       ├── media.py
│       ├── estoque.py
│       ├── autor.py
│       └── penalizacao.py
├── .env.example
├── requirements.txt
├── schema.sql
└── README.md
```

## 🎯 Endpoints Principais

### Usuários
- `POST /api/v1/usuarios` - Criar usuário
- `GET /api/v1/usuarios` - Listar usuários
- `GET /api/v1/usuarios/{id}` - Obter usuário por ID
- `PUT /api/v1/usuarios/{id}` - Atualizar usuário
- `DELETE /api/v1/usuarios/{id}` - Deletar usuário

### Bibliotecas
- `POST /api/v1/bibliotecas` - Criar biblioteca
- `GET /api/v1/bibliotecas` - Listar bibliotecas
- `GET /api/v1/bibliotecas/{id}/estoque` - Ver estoque da biblioteca

### Empréstimos
- `POST /api/v1/emprestimos/emprestar` - Criar empréstimo
- `POST /api/v1/emprestimos/{id}/devolver` - Devolver item
- `GET /api/v1/emprestimos/ativos` - Empréstimos ativos
- `GET /api/v1/emprestimos/atrasados` - Empréstimos atrasados

### Mídias
- `POST /api/v1/midias/livros` - Cadastrar livro
- `POST /api/v1/midias/revistas` - Cadastrar revista
- `POST /api/v1/midias/dvds` - Cadastrar DVD
- `POST /api/v1/midias/artigos` - Cadastrar artigo
- `GET /api/v1/midias/buscar` - Buscar mídias

### Estoque
- `POST /api/v1/estoque` - Adicionar item ao estoque
- `GET /api/v1/estoque` - Listar estoque

### Autores
- `POST /api/v1/autores` - Cadastrar autor
- `POST /api/v1/autores/autorias` - Vincular autor a título

### Penalizações
- `GET /api/v1/penalizacoes` - Listar penalizações
- `GET /api/v1/penalizacoes?ativas=true` - Penalizações ativas

## 🔧 Funcionalidades Especiais

### Gestão de Empréstimos
- Validação automática de disponibilidade
- Verificação de penalizações ativas
- Criação automática de penalizações por atraso
- Relatórios de empréstimos ativos e atrasados

### Busca de Mídias
- Busca unificada em todos os tipos de mídia
- Filtros por tipo de mídia
- Paginação de resultados

### Pool de Conexões
- Gerenciamento eficiente de conexões com PostgreSQL
- Configuração automática de pool
- Tratamento de erros de conexão

## 🧪 Testando a API

### Health Check
```bash
curl http://localhost:8000/health
```

### Criar um usuário
```bash
curl -X POST "http://localhost:8000/api/v1/usuarios" \
     -H "Content-Type: application/json" \
     -d '{
       "nome": "João Silva",
       "email": "joao@email.com",
       "endereco": "Rua das Flores, 123",
       "telefone": "(11) 99999-9999"
     }'
```

### Buscar mídias
```bash
curl "http://localhost:8000/api/v1/midias/buscar?termo=python&page=1&size=10"
```

## ⚠️ Importante

- Configure adequadamente as variáveis de ambiente antes de executar
- Certifique-se de que o PostgreSQL está rodando e acessível
- Para produção, ajuste as configurações de CORS no `main.py`
- Monitore os logs para debugging e monitoramento

## 📝 Licença

Este projeto está sob a licença MIT.
