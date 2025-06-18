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
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

A API estará disponível em: http://localhost:8000

## 📚 Documentação da API

Após iniciar a aplicação, acesse:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🛠 Estrutura do Projeto

```

├── app/
│   ├── api/               # Rotas da API
│   │   ├── usuarios.py
│   │   ├── emprestimos.py
│   │   └── estoque.py
│   ├── core/              # Configurações
│   │   └── config.py
│   ├── database/          # Conexão com banco
│   │   └── connection.py
│   ├── schemas/           # Modelos Pydantic
│   │   └── schemas.py
│   ├── services/          # Lógica de negócio
│   │   ├── usuario_service.py
│   │   ├── emprestimo_service.py
│   │   └── estoque_service.py
│   └── main.py           # Aplicação principal
├── database_setup.sql    # Script de criação do BD
├── requirements.txt      # Dependências
├── run.py               # Script para executar
└── .env.example         # Exemplo de configuração
```

## 📖 Principais Endpoints

### Usuários
- `GET /api/v1/usuarios/` - Listar usuários
- `POST /api/v1/usuarios/` - Criar usuário
- `GET /api/v1/usuarios/{id}` - Buscar usuário
- `PUT /api/v1/usuarios/{id}` - Atualizar usuário
- `DELETE /api/v1/usuarios/{id}` - Excluir usuário

### Empréstimos
- `GET /api/v1/emprestimos/` - Listar empréstimos
- `POST /api/v1/emprestimos/` - Criar empréstimo
- `PATCH /api/v1/emprestimos/{id}/devolver` - Devolver item
- `GET /api/v1/emprestimos/em-andamento/` - Empréstimos ativos
- `GET /api/v1/emprestimos/vencidos/` - Empréstimos vencidos
- `GET /api/v1/emprestimos/relatorio/` - Relatório de empréstimos

### Estoque
- `GET /api/v1/estoque/` - Listar estoque
- `POST /api/v1/estoque/` - Adicionar ao estoque
- `GET /api/v1/estoque/disponibilidade/{id_titulo}` - Verificar disponibilidade
- `GET /api/v1/estoque/biblioteca/{id}` - Estoque por biblioteca

## 🔒 Regras de Negócio Implementadas

1. **Empréstimos**:
   - Não é possível emprestar um item já emprestado
   - Data de devolução padrão: 15 dias após empréstimo
   - Controle de itens vencidos

2. **Exclusões**:
   - Usuários com empréstimos não podem ser excluídos
   - Bibliotecas com estoque não podem ser excluídas
   - Livros com exemplares no estoque não podem ser excluídos

3. **Validações**:
   - Campos obrigatórios validados via Pydantic
   - Verificação de existência de relacionamentos

## 🐛 Resolução de Problemas

### Erro de conexão com banco
- Verifique se o PostgreSQL está rodando
- Confirme as credenciais no arquivo `.env`
- Teste a conexão: `psql -h localhost -U postgres -d biblioteca`

### Erro ao instalar psycopg2
No Windows, pode ser necessário instalar:
```bash
pip install psycopg2-binary
```

## 📄 Licença

Este projeto é de uso educacional e pode ser livremente modificado e distribuído.

## 🤝 Contribuições

1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

---

**Desenvolvido para demonstrar um sistema completo de gerenciamento de biblioteca usando FastAPI e PostgreSQL sem ORM.**
