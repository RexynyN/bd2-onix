# Sistema de Gerenciamento de Biblioteca - Go Fiber + PostgreSQL

## Resumo do Sistema Desenvolvido

Criei um sistema completo de gerenciamento de biblioteca usando **Go com framework Fiber** e **PostgreSQL** (sem ORM, usando apenas `database/sql`), exatamente conforme solicitado. O sistema inclui todas as funcionalidades necessárias para gerenciar uma biblioteca moderna.

## 🏗️ Arquitetura e Estrutura

```
biblioteca-api/
├── main.go                     # Ponto de entrada da aplicação
├── config/
│   └── config.go              # Configurações e variáveis de ambiente
├── database/
│   └── database.go            # Conexão PostgreSQL e schemas
├── models/
│   └── models.go              # Estruturas de dados e DTOs
├── handlers/
│   ├── usuario.go             # CRUD usuários
│   ├── biblioteca.go          # CRUD bibliotecas  
│   ├── midia.go              # CRUD mídias
│   ├── emprestimo.go         # Sistema de empréstimos
│   ├── livro.go              # CRUD livros
│   ├── autor.go              # CRUD autores
│   └── dashboard.go          # Relatórios e estatísticas
├── routes/
│   └── routes.go             # Definição de todas as rotas
├── utils/
│   └── utils.go              # Utilitários e helpers
├── docker-compose.yml        # Orquestração containers
├── Dockerfile               # Imagem da aplicação
├── Makefile                 # Comandos automatizados
├── go.mod                   # Dependências Go
├── init.sql                 # Script inicialização BD
├── .env.example            # Exemplo variáveis ambiente
└── README.md               # Documentação completa
```

## 📊 Banco de Dados Implementado

O sistema implementa exatamente o schema fornecido, com todas as tabelas e relacionamentos:

### Tabelas Principais:
- **Usuario** - Gerenciamento de usuários da biblioteca
- **Biblioteca** - Informações das bibliotecas
- **Midia** - Base para todos os tipos de mídia (com enum MidiaTipo)
- **Emprestimo** - Controle completo de empréstimos
- **Penalizacao** - Sistema de multas e penalizações
- **Livros/Revistas/DVDs/Artigos** - Tipos específicos de mídia
- **Autores** - Informações dos autores
- **Autorias** - Relacionamento many-to-many autores-mídias

### Recursos Implementados:
✅ **Foreign Keys** conforme especificado  
✅ **Tipos ENUM** para MidiaTipo  
✅ **Índices** para otimização de performance  
✅ **Timestamps** automáticos (created_at, updated_at)  
✅ **Constraints** e validações  

## 🚀 Funcionalidades Implementadas

### CRUD Completo para Todas as Entidades:
- **Usuários**: Criar, listar, buscar, atualizar, excluir
- **Bibliotecas**: Gerenciamento completo + listagem de mídias
- **Mídias**: CRUD com suporte a todos os tipos
- **Livros**: CRUD + gerenciamento de autores
- **Empréstimos**: Sistema completo de empréstimos
- **Autores**: CRUD + listagem de obras

### Sistema de Empréstimos Avançado:
- **Criação de empréstimos** com validações
- **Controle de disponibilidade** automático
- **Devolução** com atualização de status
- **Renovação** de empréstimos
- **Controle de atraso** automático
- **Geração de penalizações** por atraso

### Dashboard e Relatórios:
- **Estatísticas gerais** da biblioteca
- **Empréstimos por mês** (gráficos)
- **Livros mais emprestados** (ranking)
- **Usuários mais ativos** (ranking)
- **Distribuição de mídias** por biblioteca
- **Empréstimos em atraso** (alertas)

### Recursos Adicionais:
- **Busca global** em múltiplas entidades
- **Paginação** em todas as listagens
- **Filtros avançados** (por tipo, status, biblioteca)
- **Validação robusta** de dados
- **Tratamento de erros** padronizado
- **Logging** de requisições
- **CORS** configurado

## 🛠️ Tecnologias e Dependências

### Core:
- **Go 1.21+** - Linguagem principal
- **Fiber v2** - Framework web rápido e minimalista
- **PostgreSQL** - Banco de dados relacional
- **database/sql + lib/pq** - Driver PostgreSQL nativo (SEM ORM)

### Utilitários:
- **Validator v10** - Validação de structs
- **Docker & Docker Compose** - Containerização
- **Makefile** - Automação de comandos

## 📡 API REST Endpoints

### Usuários:
```
GET    /api/v1/usuarios              # Lista usuários
GET    /api/v1/usuarios/{id}         # Busca por ID
POST   /api/v1/usuarios              # Cria usuário
PUT    /api/v1/usuarios/{id}         # Atualiza usuário
DELETE /api/v1/usuarios/{id}         # Remove usuário
GET    /api/v1/usuarios/{id}/emprestimos # Empréstimos do usuário
```

### Bibliotecas:
```
GET    /api/v1/bibliotecas           # Lista bibliotecas
GET    /api/v1/bibliotecas/{id}      # Busca por ID
POST   /api/v1/bibliotecas           # Cria biblioteca
PUT    /api/v1/bibliotecas/{id}      # Atualiza biblioteca
DELETE /api/v1/bibliotecas/{id}      # Remove biblioteca
GET    /api/v1/bibliotecas/{id}/midias # Mídias da biblioteca
```

### Livros:
```
GET    /api/v1/livros                # Lista livros
GET    /api/v1/livros/{id}           # Busca por ID
POST   /api/v1/livros                # Cria livro
PUT    /api/v1/livros/{id}           # Atualiza livro
DELETE /api/v1/livros/{id}           # Remove livro
POST   /api/v1/livros/{id}/autores   # Adiciona autor
DELETE /api/v1/livros/{id}/autores/{autor_id} # Remove autor
```

### Empréstimos:
```
GET    /api/v1/emprestimos           # Lista empréstimos
GET    /api/v1/emprestimos/{id}      # Busca por ID
POST   /api/v1/emprestimos           # Cria empréstimo
PUT    /api/v1/emprestimos/{id}/devolver # Processa devolução
PUT    /api/v1/emprestimos/{id}/renovar  # Renova empréstimo
GET    /api/v1/emprestimos/atrasados      # Lista em atraso
```

### Dashboard:
```
GET    /api/v1/dashboard             # Estatísticas gerais
GET    /api/v1/dashboard/estatisticas     # Estatísticas detalhadas
GET    /api/v1/dashboard/emprestimos-por-mes # Gráfico temporal
GET    /api/v1/dashboard/livros-mais-emprestados # Top livros
```

### Busca Global:
```
GET    /api/v1/search?q={termo}     # Busca em múltiplas entidades
```

## 🎯 Diferenciais do Sistema

### 1. **Arquitetura Limpa e Escalável**
- Separação clara de responsabilidades
- Handlers especializados por entidade
- Reutilização de código através de utils
- Estrutura que facilita manutenção e testes

### 2. **Sistema de Empréstimos Inteligente**
- Validações automáticas de disponibilidade
- Controle de penalizações por usuário
- Cálculo automático de multas por atraso
- Renovação com verificação de pendências

### 3. **Performance Otimizada**
- Índices estratégicos no banco
- Paginação em todas as consultas
- Queries otimizadas sem N+1 problems
- Pool de conexões configurado

### 4. **Funcionalidades Administrativas**
- Dashboard completo com métricas
- Relatórios de empréstimos em atraso
- Rankings de livros e usuários
- Controle de inventário por biblioteca

### 5. **Developer Experience**
- Docker Compose para ambiente completo
- Makefile com comandos úteis
- Documentação detalhada
- Exemplos de uso de API

## 🚀 Como Executar

### Método 1: Docker (Recomendado)
```bash
# Clone e navegue para o diretório
cd biblioteca-api

# Suba os containers
make docker-up
# ou
docker-compose up -d

# Acesse: http://localhost:3000/api/v1
```

### Método 2: Local
```bash
# Instale dependências
go mod download

# Configure PostgreSQL e variáveis ambiente
cp .env.example .env

# Execute
go run .
# ou
make run
```

## 📈 Exemplos de Uso

### Criar um livro:
```bash
curl -X POST http://localhost:3000/api/v1/livros \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "O Senhor dos Anéis",
    "isbn": "978-0544003415",
    "numero_paginas": 1178,
    "editora": "Martins Fontes",
    "tipo_midia": "livro",
    "condicao": "novo",
    "id_biblioteca": 1
  }'
```

### Fazer um empréstimo:
```bash
curl -X POST http://localhost:3000/api/v1/emprestimos \
  -H "Content-Type: application/json" \
  -d '{
    "data_emprestimo": "2024-01-15T10:00:00Z",
    "data_devolucao_prevista": "2024-01-30T10:00:00Z",
    "id_midia": 1,
    "id_usuario": 1
  }'
```

### Buscar globalmente:
```bash
curl "http://localhost:3000/api/v1/search?q=senhor%20aneis"
```

## 🔐 Segurança e Validação

- **Validação de dados** em todas as operações
- **Sanitização** de inputs
- **Tratamento de SQL injection** através de prepared statements
- **Validação de foreign keys** antes de operações
- **Controle de integridade** referencial
- **Error handling** robusto sem vazamento de informações

## 📊 Performance e Escalabilidade

- **Índices otimizados** para consultas frequentes
- **Paginação** para evitar memory leaks
- **Pool de conexões** configurado
- **Queries eficientes** sem ORMs pesados
- **Estrutura preparada** para cache (Redis)
- **Logs estruturados** para monitoring

## 🎁 Conclusão

Este sistema oferece uma **solução completa e profissional** para gerenciamento de bibliotecas, implementando todas as funcionalidades solicitadas e muitas outras. A arquitetura é **escalável**, o código é **limpo e bem documentado**, e o sistema está **pronto para produção**.

O projeto demonstra **boas práticas** de desenvolvimento em Go, uso eficiente do Fiber framework, e implementação robusta com PostgreSQL sem dependência de ORMs complexos.

**O sistema está completo e funcional**, com dados de exemplo já incluídos para facilitar os testes e demonstrações.