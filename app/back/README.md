# Sistema de Gerenciamento de Biblioteca

Backend em Python com FastAPI para gerenciamento de biblioteca e empréstimos de livros.

## 🚀 Funcionalidades

- **Gerenciamento de Usuários**: CRUD completo de usuários
- **Gerenciamento de Bibliotecas**: CRUD de bibliotecas
- **Catálogo de Mídia**: Gerenciamento de livros, revistas, DVDs e artigos
- **Controle de Estoque**: Gestão de exemplares por biblioteca
- **Sistema de Empréstimos**: Controle completo de empréstimos e devoluções
- **Relatórios**: Relatórios de empréstimos, disponibilidade e usuários

## 📋 Pré-requisitos

- Python 3.8+
- PostgreSQL 12+
- pip ou poetry

## 🔧 Instalação

### 1. Clone ou baixe o projeto

### 2. Configure o ambiente virtual

```bash
python -m venv venv

# No Windows
venv\Scripts\activate

# No Linux/Mac
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure o banco de dados

#### Instale e configure o PostgreSQL:
- Crie um banco de dados chamado `biblioteca`
- Execute o script `database_setup.sql` no PostgreSQL

```sql
CREATE DATABASE biblioteca;
\c biblioteca;
\i database_setup.sql
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
DATABASE_NAME=biblioteca
DATABASE_USER=seu_usuario
DATABASE_PASSWORD=sua_senha
```

## 🚀 Executando a aplicação

```bash
# Opção 1: Usando o script run.py
python run.py

# Opção 2: Usando uvicorn diretamente
uvicorn app.main:app --reload --host 0.0.0.0 --port 8765
```

A API estará disponível em: http://localhost:8765

## 📚 Documentação da API

Após iniciar a aplicação, acesse:

- **Swagger UI**: http://localhost:8765/docs
- **ReDoc**: http://localhost:8765/redoc

