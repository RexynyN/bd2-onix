# 📚 Documentação Completa da API - Sistema de Biblioteca

## 📋 Visão Geral

Esta API oferece funcionalidades completas para gerenciamento de biblioteca, incluindo:
- Gerenciamento de usuários, bibliotecas e acervo
- Sistema de empréstimos e devoluções
- Controle de estoque e disponibilidade
- Relatórios e consultas avançadas

**Base URL**: `http://localhost:8000/api/v1`

## 🔗 Endpoints Disponíveis

### 👥 Usuários (`/usuarios`)

#### `POST /usuarios/` - Criar Usuário
**Request Body:**
```json
{
  "nome": "João Silva",
  "email": "joao@email.com",
  "endereco": "Rua A, 123",
  "telefone": "11999999999"
}
```

**Response (201):**
```json
{
  "id_usuario": 1,
  "nome": "João Silva",
  "email": "joao@email.com",
  "endereco": "Rua A, 123",
  "telefone": "11999999999"
}
```

#### `GET /usuarios/` - Listar Usuários
**Query Parameters:**
- `skip`: número de registros para pular (default: 0)
- `limit`: limite de registros (default: 100, max: 1000)

**Response (200):**
```json
[
  {
    "id_usuario": 1,
    "nome": "João Silva",
    "email": "joao@email.com",
    "endereco": "Rua A, 123",
    "telefone": "11999999999"
  }
]
```

#### `GET /usuarios/{id_usuario}` - Buscar Usuário
**Response (200):**
```json
{
  "id_usuario": 1,
  "nome": "João Silva",
  "email": "joao@email.com",
  "endereco": "Rua A, 123",
  "telefone": "11999999999"
}
```

#### `PUT /usuarios/{id_usuario}` - Atualizar Usuário
**Request Body:** (todos os campos opcionais)
```json
{
  "nome": "João Santos",
  "email": "joao.santos@email.com"
}
```

#### `DELETE /usuarios/{id_usuario}` - Excluir Usuário
**Response (200):**
```json
{
  "message": "Usuário excluído com sucesso"
}
```

#### `GET /usuarios/emprestimos/ativos` - Usuários com Empréstimos Ativos
**Response (200):**
```json
[
  {
    "id_usuario": 1,
    "nome": "João Silva",
    "email": "joao@email.com",
    "endereco": "Rua A, 123",
    "telefone": "11999999999"
  }
]
```

---

### 📖 Empréstimos (`/emprestimos`)

#### `POST /emprestimos/` - Criar Empréstimo
**Request Body:**
```json
{
  "data_emprestimo": "2024-01-15",
  "data_devolucao_prevista": "2024-01-30",
  "id_estoque": 1,
  "id_usuario": 1
}
```

**Response (201):**
```json
{
  "id_emprestimo": 1,
  "data_emprestimo": "2024-01-15",
  "data_devolucao_prevista": "2024-01-30",
  "data_devolucao": null,
  "id_estoque": 1,
  "id_usuario": 1
}
```

#### `GET /emprestimos/` - Listar Empréstimos
**Query Parameters:**
- `skip`: número de registros para pular
- `limit`: limite de registros

#### `GET /emprestimos/{id_emprestimo}` - Buscar Empréstimo

#### `PATCH /emprestimos/{id_emprestimo}/devolver` - Devolver Item
**Query Parameters:**
- `data_devolucao`: data da devolução (opcional, usa data atual se não informada)

**Response (200):**
```json
{
  "id_emprestimo": 1,
  "data_emprestimo": "2024-01-15",
  "data_devolucao_prevista": "2024-01-30",
  "data_devolucao": "2024-01-25",
  "id_estoque": 1,
  "id_usuario": 1
}
```

#### `GET /emprestimos/em-andamento/` - Empréstimos em Andamento
**Response (200):**
```json
[
  {
    "id_emprestimo": 1,
    "data_emprestimo": "2024-01-15",
    "data_devolucao_prevista": "2024-01-30",
    "data_devolucao": null,
    "usuario": {
      "id_usuario": 1,
      "nome": "João Silva",
      "email": "joao@email.com",
      "endereco": "Rua A, 123",
      "telefone": "11999999999"
    },
    "item_titulo": "Dom Casmurro",
    "tipo_midia": "livro",
    "biblioteca": "Biblioteca Central"
  }
]
```

#### `GET /emprestimos/vencidos/` - Empréstimos Vencidos
Retorna empréstimos não devolvidos com data de devolução vencida.

#### `GET /emprestimos/relatorio/` - Relatório de Empréstimos
**Response (200):**
```json
{
  "total_emprestimos": 150,
  "emprestimos_em_andamento": 45,
  "emprestimos_vencidos": 12,
  "emprestimos_devolvidos": 105
}
```

---

### 📦 Estoque (`/estoque`)

#### `POST /estoque/` - Adicionar ao Estoque
**Request Body:**
```json
{
  "condicao": "Novo",
  "id_titulo": 1,
  "id_biblioteca": 1
}
```

**Response (201):**
```json
{
  "id_estoque": 1,
  "condicao": "Novo",
  "id_titulo": 1,
  "id_biblioteca": 1
}
```

#### `GET /estoque/` - Listar Estoque
**Query Parameters:**
- `skip`: número de registros para pular
- `limit`: limite de registros

#### `GET /estoque/{id_estoque}` - Buscar Item do Estoque

#### `GET /estoque/biblioteca/{id_biblioteca}` - Estoque por Biblioteca
Retorna todos os itens do estoque de uma biblioteca específica.

#### `GET /estoque/disponibilidade/{id_titulo}` - Verificar Disponibilidade
**Response (200):**
```json
{
  "id_titulo": 1,
  "titulo": "Dom Casmurro",
  "tipo_midia": "livro",
  "total_exemplares": 3,
  "exemplares_disponiveis": 2,
  "exemplares_emprestados": 1
}
```

#### `PUT /estoque/{id_estoque}` - Atualizar Estoque
**Request Body:** (campos opcionais)
```json
{
  "condicao": "Bom"
}
```

#### `DELETE /estoque/{id_estoque}` - Remover do Estoque

---

## 🔧 Funcionalidades Especiais

### 🔍 Busca de Livros
- **Endpoint**: `GET /api/v1/livros/search/?q={termo}`
- Busca por título, ISBN ou editora
- Busca insensível a maiúsculas/minúsculas

### 📊 Relatórios
- **Empréstimos**: `/api/v1/emprestimos/relatorio/`
- **Disponibilidade**: `/api/v1/estoque/disponibilidade/{id_titulo}`
- **Usuários Ativos**: `/api/v1/usuarios/emprestimos/ativos`

### 🔒 Regras de Negócio

1. **Empréstimos**:
   - Item deve estar disponível (não emprestado)
   - Usuário e item devem existir
   - Data de devolução padrão: 15 dias

2. **Exclusões**:
   - Usuários com empréstimos ativos não podem ser excluídos
   - Bibliotecas com estoque não podem ser excluídas
   - Itens com histórico de empréstimo não podem ser excluídos

3. **Validações**:
   - Email válido para usuários
   - Campos obrigatórios validados
   - Limites de paginação respeitados

---

## 📝 Códigos de Status HTTP

- **200**: OK - Operação realizada com sucesso
- **201**: Created - Recurso criado com sucesso
- **400**: Bad Request - Dados inválidos ou regra de negócio violada
- **404**: Not Found - Recurso não encontrado
- **422**: Unprocessable Entity - Erro de validação
- **500**: Internal Server Error - Erro interno do servidor

---

## 🧪 Exemplos de Uso

### Fluxo Básico de Empréstimo

1. **Criar usuário**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/usuarios/" \
        -H "Content-Type: application/json" \
        -d '{"nome": "Maria Silva", "email": "maria@email.com"}'
   ```

2. **Verificar disponibilidade**:
   ```bash
   curl "http://localhost:8000/api/v1/estoque/disponibilidade/1"
   ```

3. **Criar empréstimo**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/emprestimos/" \
        -H "Content-Type: application/json" \
        -d '{
          "data_emprestimo": "2024-01-15",
          "id_estoque": 1,
          "id_usuario": 1
        }'
   ```

4. **Devolver item**:
   ```bash
   curl -X PATCH "http://localhost:8000/api/v1/emprestimos/1/devolver"
   ```

### Consultas Úteis

- **Listar empréstimos vencidos**:
  ```bash
  curl "http://localhost:8000/api/v1/emprestimos/vencidos/"
  ```

- **Buscar livros por termo**:
  ```bash
  curl "http://localhost:8000/api/v1/livros/search/?q=Machado"
  ```

- **Relatório geral**:
  ```bash
  curl "http://localhost:8000/api/v1/emprestimos/relatorio/"
  ```

---

## 🛠 Ferramentas Recomendadas

- **Swagger UI**: `http://localhost:8000/docs` (interface interativa)
- **ReDoc**: `http://localhost:8000/redoc` (documentação detalhada)
- **Postman**: Para testes manuais da API
- **curl**: Para testes via linha de comando

---

**📞 Suporte**: Para dúvidas ou problemas, consulte o README.md ou abra uma issue no repositório.



## Revistas

### Criar Revista

- **Método:** POST
- **Endpoint:** `/api/v1/revistas/`
- **Descrição:** Cria uma nova revista.
- **Body (JSON):**
{
"titulo": "Revista Ciência Hoje",
"ISSN": "1234-5678",
"periodicidade": "Mensal",
"editora": "Editora X",
"data_publicacao": "2024-01-15"
}


- **Resposta (201):**
{
"id_revista": 1,
"titulo": "Revista Ciência Hoje",
"ISSN": "1234-5678",
"periodicidade": "Mensal",
"editora": "Editora X",
"data_publicacao": "2024-01-15"
}



---

### Listar Revistas

- **Método:** GET
- **Endpoint:** `/api/v1/revistas/`
- **Query Params:**  
- `skip` (int, opcional, padrão: 0): Quantidade de itens a pular  
- `limit` (int, opcional, padrão: 100): Máximo de itens a retornar
- **Resposta (200):**
[
{
"id_revista": 1,
"titulo": "Revista Ciência Hoje",
"ISSN": "1234-5678",
"periodicidade": "Mensal",
"editora": "Editora X",
"data_publicacao": "2024-01-15"
}
]



---

### Buscar Revista por ID

- **Método:** GET
- **Endpoint:** `/api/v1/revistas/{revista_id}`
- **Path Param:**  
- `revista_id` (int): ID da revista
- **Resposta (200):** (igual ao exemplo acima)
- **Resposta (404):**
{"detail": "Revista não encontrada"}



---

### Atualizar Revista

- **Método:** PUT
- **Endpoint:** `/api/v1/revistas/{revista_id}`
- **Path Param:**  
- `revista_id` (int): ID da revista
- **Body (JSON):**
{
"titulo": "Nova Revista",
"ISSN": "8765-4321"
}


- **Resposta (200):** (revista atualizada)
- **Resposta (404):**
{"detail": "Revista não encontrada"}



---

### Excluir Revista

- **Método:** DELETE
- **Endpoint:** `/api/v1/revistas/{revista_id}`
- **Path Param:**  
- `revista_id` (int): ID da revista
- **Resposta (200):**
{"message": "Revista excluída com sucesso"}


- **Resposta (400/404):**  
Mensagem de erro apropriada.

---

### Buscar Revistas (Filtro)

- **Método:** GET
- **Endpoint:** `/api/v1/revistas/search/`
- **Query Param:**  
- `q` (str): termo de busca
- **Resposta (200):**  
Lista de revistas filtradas.

---

### Obter Revista com Autores

- **Método:** GET
- **Endpoint:** `/api/v1/revistas/{revista_id}/autores`
- **Path Param:**  
- `revista_id` (int): ID da revista
- **Resposta (200):**
{
"id_revista": 1,
"titulo": "Revista Ciência Hoje",
"ISSN": "1234-5678",
"periodicidade": "Mensal",
"editora": "Editora X",
"data_publicacao": "2024-01-15",
"autores": [
{"id_autor": 1, "nome": "Autor Exemplo"}
]
}



---

## DVDs

### Criar DVD

- **Método:** POST
- **Endpoint:** `/api/v1/dvds/`
- **Body (JSON):**
{
"titulo": "Filme Exemplo",
"ISAN": "0000-0000-0000-0000-X-0000-0000-0",
"duracao": 120,
"distribuidora": "Distribuidora Y",
"data_lancamento": "2023-12-01"
}


- **Resposta (201):**
{
"id_dvd": 1,
"titulo": "Filme Exemplo",
"ISAN": "0000-0000-0000-0000-X-0000-0000-0",
"duracao": 120,
"distribuidora": "Distribuidora Y",
"data_lancamento": "2023-12-01"
}



---

### Listar DVDs

- **Método:** GET
- **Endpoint:** `/api/v1/dvds/`
- **Query Params:**  
- `skip` (int, opcional, padrão: 0)  
- `limit` (int, opcional, padrão: 100)
- **Resposta (200):**  
Lista de DVDs.

---

### Buscar DVD por ID

- **Método:** GET
- **Endpoint:** `/api/v1/dvds/{dvd_id}`
- **Path Param:**  
- `dvd_id` (int)
- **Resposta (200):**  
Dados do DVD.
- **Resposta (404):**
{"detail": "DVD não encontrado"}



---

### Atualizar DVD

- **Método:** PUT
- **Endpoint:** `/api/v1/dvds/{dvd_id}`
- **Path Param:**  
- `dvd_id` (int)
- **Body (JSON):**  
Campos a serem atualizados.
- **Resposta (200):**  
DVD atualizado.
- **Resposta (404):**
{"detail": "DVD não encontrado"}



---

### Excluir DVD

- **Método:** DELETE
- **Endpoint:** `/api/v1/dvds/{dvd_id}`
- **Path Param:**  
- `dvd_id` (int)
- **Resposta (200):**
{"message": "DVD excluído com sucesso"}



---

### Buscar DVDs (Filtro)

- **Método:** GET
- **Endpoint:** `/api/v1/dvds/search/`
- **Query Param:**  
- `q` (str)
- **Resposta (200):**  
Lista de DVDs filtrados.

---

### Obter DVD com Autores

- **Método:** GET
- **Endpoint:** `/api/v1/dvds/{dvd_id}/autores`
- **Path Param:**  
- `dvd_id` (int)
- **Resposta (200):**
{
"id_dvd": 1,
"titulo": "Filme Exemplo",
"ISAN": "0000-0000-0000-0000-X-0000-0000-0",
"duracao": 120,
"distribuidora": "Distribuidora Y",
"data_lancamento": "2023-12-01",
"autores": [
{"id_autor": 2, "nome": "Diretor Exemplo"}
]
}



---

## Artigos

### Criar Artigo

- **Método:** POST
- **Endpoint:** `/api/v1/artigos/`
- **Body (JSON):**
{
"titulo": "Artigo Científico",
"DOI": "10.1234/exemplo",
"publicadora": "Publicadora Z",
"data_publicacao": "2022-05-10"
}


- **Resposta (201):**
{
"id_artigo": 1,
"titulo": "Artigo Científico",
"DOI": "10.1234/exemplo",
"publicadora": "Publicadora Z",
"data_publicacao": "2022-05-10"
}



---

### Listar Artigos

- **Método:** GET
- **Endpoint:** `/api/v1/artigos/`
- **Query Params:**  
- `skip` (int, opcional, padrão: 0)  
- `limit` (int, opcional, padrão: 100)
- **Resposta (200):**  
Lista de artigos.

---

### Buscar Artigo por ID

- **Método:** GET
- **Endpoint:** `/api/v1/artigos/{artigo_id}`
- **Path Param:**  
- `artigo_id` (int)
- **Resposta (200):**  
Dados do artigo.
- **Resposta (404):**
{"detail": "Artigo não encontrado"}



---

### Atualizar Artigo

- **Método:** PUT
- **Endpoint:** `/api/v1/artigos/{artigo_id}`
- **Path Param:**  
- `artigo_id` (int)
- **Body (JSON):**  
Campos a serem atualizados.
- **Resposta (200):**  
Artigo atualizado.
- **Resposta (404):**
{"detail": "Artigo não encontrado"}


---

### Excluir Artigo

- **Método:** DELETE
- **Endpoint:** `/api/v1/artigos/{artigo_id}`
- **Path Param:**  
- `artigo_id` (int)
- **Resposta (200):**
{"message": "Artigo excluído com sucesso"}



---

### Buscar Artigos (Filtro)

- **Método:** GET
- **Endpoint:** `/api/v1/artigos/search/`
- **Query Param:**  
- `q` (str)
- **Resposta (200):**  
Lista de artigos filtrados.

---

### Obter Artigo com Autores

- **Método:** GET
- **Endpoint:** `/api/v1/artigos/{artigo_id}/autores`
- **Path Param:**  
- `artigo_id` (int)
- **Resposta (200):**
{
"id_artigo": 1,
"titulo": "Artigo Científico",
"DOI": "10.1234/exemplo",
"publicadora": "Publicadora Z",
"data_publicacao": "2022-05-10",
"autores": [
{"id_autor": 3, "nome": "Pesquisador Exemplo"}
]
}

