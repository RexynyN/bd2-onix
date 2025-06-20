import axios from "axios"

// Configure axios base URL - adjust this to your API URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8765"

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
})

// API Types based on the updated OpenAPI specification

// Usuario types
export interface Usuario {
  id_usuario: number
  nome: string
  email?: string | null
  endereco?: string | null
  telefone?: string | null
}

export interface UsuarioCreate {
  nome: string
  email?: string | null
  endereco?: string | null
  telefone?: string | null
}

export interface UsuarioUpdate {
  nome?: string | null
  email?: string | null
  endereco?: string | null
  telefone?: string | null
}

// Emprestimo types
export interface Emprestimo {
  id_emprestimo: number
  data_emprestimo: string
  data_devolucao_prevista?: string | null
  data_devolucao?: string | null
  id_estoque: number
  id_usuario: number
}

export interface EmprestimoCreate {
  data_emprestimo: string
  data_devolucao_prevista?: string | null
  id_estoque: number
  id_usuario: number
}

export interface EmprestimoCompleto {
  id_emprestimo: number
  data_emprestimo: string
  data_devolucao_prevista: string | null
  data_devolucao: string | null
  usuario: Usuario
  item_titulo: string
  tipo_midia: string
  biblioteca: string
}

export interface RelatorioEmprestimos {
  total_emprestimos: number
  emprestimos_em_andamento: number
  emprestimos_vencidos: number
  emprestimos_devolvidos: number
}

// Estoque types
export interface Estoque {
  id_estoque: number
  condicao?: string | null
  id_titulo: number
  id_biblioteca: number
}

export interface EstoqueCreate {
  condicao?: string | null
  id_titulo: number
  id_biblioteca: number
}

export interface EstoqueUpdate {
  condicao?: string | null
  id_titulo?: number | null
  id_biblioteca?: number | null
}

export interface DisponibilidadeItem {
  id_titulo: number
  titulo: string
  tipo_midia: string
  total_exemplares: number
  exemplares_disponiveis: number
  exemplares_emprestados: number
}

// Revista types
export interface RevistaResponse {
  id_revista: number
  titulo: string
  ISSN?: string | null
  periodicidade?: string | null
  editora?: string | null
  data_publicacao?: string | null
}

export interface RevistaCreate {
  titulo: string
  ISSN?: string | null
  periodicidade?: string | null
  editora?: string | null
  data_publicacao?: string | null
}

export interface RevistaUpdate {
  titulo?: string | null
  ISSN?: string | null
  periodicidade?: string | null
  editora?: string | null
  data_publicacao?: string | null
}

export interface RevistaWithAuthors extends RevistaResponse {
  autores: any[]
}

// DVD types
export interface DVDResponse {
  id_dvd: number
  titulo: string
  ISAN?: string | null
  duracao?: number | null
  distribuidora?: string | null
  data_lancamento?: string | null
}

export interface DVDCreate {
  titulo: string
  ISAN?: string | null
  duracao?: number | null
  distribuidora?: string | null
  data_lancamento?: string | null
}

export interface DVDUpdate {
  titulo?: string | null
  ISAN?: string | null
  duracao?: number | null
  distribuidora?: string | null
  data_lancamento?: string | null
}

export interface DVDWithAuthors extends DVDResponse {
  autores: any[]
}

// Artigo types
export interface ArtigoResponse {
  id_artigo: number
  titulo: string
  DOI?: string | null
  publicadora?: string | null
  data_publicacao?: string | null
}

export interface ArtigoCreate {
  titulo: string
  DOI?: string | null
  publicadora?: string | null
  data_publicacao?: string | null
}

export interface ArtigoUpdate {
  titulo?: string | null
  DOI?: string | null
  publicadora?: string | null
  data_publicacao?: string | null
}

export interface ArtigoWithAuthors extends ArtigoResponse {
  autores: any[]
}

// Livro types (placeholder - not in API yet)
export interface LivroResponse {
  id_livro: number
  titulo: string
  ISBN?: string | null
  editora?: string | null
  data_publicacao?: string | null
  numero_paginas?: number | null
}

export interface LivroCreate {
  titulo: string
  ISBN?: string | null
  editora?: string | null
  data_publicacao?: string | null
  numero_paginas?: number | null
}

export interface LivroUpdate {
  titulo?: string | null
  ISBN?: string | null
  editora?: string | null
  data_publicacao?: string | null
  numero_paginas?: string | null
}

export interface LivroWithAuthors extends LivroResponse {
  autores: any[]
}

// Biblioteca types
export interface BibliotecaResponse {
  id_biblioteca: number
  nome: string
  endereco?: string | null
}

export interface BibliotecaCreate {
  nome: string
  endereco?: string | null
}

export interface BibliotecaUpdate {
  nome?: string | null
  endereco?: string | null
}

export interface BibliotecaListResponse {
  success: boolean
  message: string
  data: BibliotecaResponse[]
  total: number
}

export interface BaseResponse {
  success: boolean
  message: string
}

// Updated Autor types based on new API
export interface AutorResponse {
  id_autor: number
  nome: string
  data_nascimento?: string | null
  data_falecimento?: string | null
}

export interface AutorCreate {
  nome: string
  data_nascimento?: string | null
  data_falecimento?: string | null
}

export interface AutorUpdate {
  nome?: string | null
  data_nascimento?: string | null
  data_falecimento?: string | null
}

export interface AutorListResponse {
  success: boolean
  message: string
  data: AutorResponse[]
  total: number
}

// Autorias types
export interface AutoriasResponse {
  id_autorias: number
  id_autor: number
  id_titulo: number
}

export interface AutoriasCreate {
  id_autor: number
  id_titulo: number
}

export interface AutoriasListResponse {
  success: boolean
  message: string
  data: AutoriasResponse[]
  total: number
}

// Enhanced Estoque with names
export interface EstoqueWithNames extends Estoque {
  titulo_nome?: string
  biblioteca_nome?: string
}

// API Functions

// Usuarios API
export const usuariosAPI = {
  getAll: (skip = 0, limit = 100) => api.get<Usuario[]>("/api/v1/usuarios/", { params: { skip, limit } }),
  getById: (id: number) => api.get<Usuario>(`/api/v1/usuarios/${id}`),
  create: (data: UsuarioCreate) => api.post<Usuario>("/api/v1/usuarios/", data),
  update: (id: number, data: UsuarioUpdate) => api.put<Usuario>(`/api/v1/usuarios/${id}`, data),
  delete: (id: number) => api.delete(`/api/v1/usuarios/${id}`),
  getComEmprestimosAtivos: (skip = 0, limit = 100) =>
    api.get<Usuario[]>("/api/v1/usuarios/emprestimos/ativos", { params: { skip, limit } }),
}

// Emprestimos API
export const emprestimosAPI = {
  getAll: (skip = 0, limit = 100) => api.get<Emprestimo[]>("/api/v1/emprestimos/", { params: { skip, limit } }),
  getById: (id: number) => api.get<Emprestimo>(`/api/v1/emprestimos/${id}`),
  create: (data: EmprestimoCreate) => api.post<Emprestimo>("/api/v1/emprestimos/", data),
  devolver: (id: number, data_devolucao?: string) =>
    api.patch<Emprestimo>(`/api/v1/emprestimos/${id}/devolver`, null, {
      params: data_devolucao ? { data_devolucao } : {},
    }),
  getEmAndamento: (skip = 0, limit = 100) =>
    api.get<EmprestimoCompleto[]>("/api/v1/emprestimos/em-andamento/", { params: { skip, limit } }),
  getVencidos: (skip = 0, limit = 100) =>
    api.get<EmprestimoCompleto[]>("/api/v1/emprestimos/vencidos/", { params: { skip, limit } }),
  getRelatorio: () => api.get<RelatorioEmprestimos>("/api/v1/emprestimos/relatorio/"),
}

// Estoque API
export const estoqueAPI = {
  getAll: (skip = 0, limit = 100) => api.get<Estoque[]>("/api/v1/estoque/", { params: { skip, limit } }),
  getById: (id: number) => api.get<Estoque>(`/api/v1/estoque/${id}`),
  create: (data: EstoqueCreate) => api.post<Estoque>("/api/v1/estoque/", data),
  update: (id: number, data: EstoqueUpdate) => api.put<Estoque>(`/api/v1/estoque/${id}`, data),
  delete: (id: number) => api.delete(`/api/v1/estoque/${id}`),
  getByBiblioteca: (id_biblioteca: number, skip = 0, limit = 100) =>
    api.get<Estoque[]>(`/api/v1/estoque/biblioteca/${id_biblioteca}`, { params: { skip, limit } }),
  getDisponibilidade: (id_titulo: number) =>
    api.get<DisponibilidadeItem>(`/api/v1/estoque/disponibilidade/${id_titulo}`),
}

// Revistas API
export const revistasAPI = {
  getAll: (skip = 0, limit = 100) => api.get<RevistaResponse[]>("/api/v1/revistas/", { params: { skip, limit } }),
  getById: (id: number) => api.get<RevistaResponse>(`/api/v1/revistas/${id}`),
  create: (data: RevistaCreate) => api.post<RevistaResponse>("/api/v1/revistas/", data),
  update: (id: number, data: RevistaUpdate) => api.put<RevistaResponse>(`/api/v1/revistas/${id}`, data),
  delete: (id: number) => api.delete(`/api/v1/revistas/${id}`),
  search: (q: string) => api.get<RevistaResponse[]>("/api/v1/revistas/search/", { params: { q } }),
  getWithAuthors: (id: number) => api.get<RevistaWithAuthors>(`/api/v1/revistas/${id}/autores`),
}

// DVDs API
export const dvdsAPI = {
  getAll: (skip = 0, limit = 100) => api.get<DVDResponse[]>("/api/v1/dvds/", { params: { skip, limit } }),
  getById: (id: number) => api.get<DVDResponse>(`/api/v1/dvds/${id}`),
  create: (data: DVDCreate) => api.post<DVDResponse>("/api/v1/dvds/", data),
  update: (id: number, data: DVDUpdate) => api.put<DVDResponse>(`/api/v1/dvds/${id}`, data),
  delete: (id: number) => api.delete(`/api/v1/dvds/${id}`),
  search: (q: string) => api.get<DVDResponse[]>("/api/v1/dvds/search/", { params: { q } }),
  getWithAuthors: (id: number) => api.get<DVDWithAuthors>(`/api/v1/dvds/${id}/autores`),
}

// Artigos API
export const artigosAPI = {
  getAll: (skip = 0, limit = 100) => api.get<ArtigoResponse[]>("/api/v1/artigos/", { params: { skip, limit } }),
  getById: (id: number) => api.get<ArtigoResponse>(`/api/v1/artigos/${id}`),
  create: (data: ArtigoCreate) => api.post<ArtigoResponse>("/api/v1/artigos/", data),
  update: (id: number, data: ArtigoUpdate) => api.put<ArtigoResponse>(`/api/v1/artigos/${id}`, data),
  delete: (id: number) => api.delete(`/api/v1/artigos/${id}`),
  search: (q: string) => api.get<ArtigoResponse[]>("/api/v1/artigos/search/", { params: { q } }),
  getWithAuthors: (id: number) => api.get<ArtigoWithAuthors>(`/api/v1/artigos/${id}/autores`),
}

// Livros API (placeholder - not implemented in backend yet)
export const livrosAPI = {
  getAll: (skip = 0, limit = 100) => {
    // For now, return a proper empty response structure until backend implements livros
    return Promise.resolve({
      data: [] as LivroResponse[],
      total: 0,
      success: true,
    })
  },
  getById: (id: number) => {
    return Promise.reject(new Error(`Livro with ID ${id} not found`))
  },
  create: (data: LivroCreate) => {
    // Simulate creation with a temporary ID
    const newLivro: LivroResponse = {
      id_livro: Math.floor(Math.random() * 1000) + 1000,
      titulo: data.titulo,
      ISBN: data.ISBN || null,
      editora: data.editora || null,
      data_publicacao: data.data_publicacao || null,
      numero_paginas: data.numero_paginas || null,
    }
    return Promise.resolve({ data: newLivro })
  },
  update: (id: number, data: LivroUpdate) => {
    return Promise.reject(new Error("Livros update not implemented yet"))
  },
  delete: (id: number) => {
    return Promise.resolve({ data: {} })
  },
  search: (q: string) => {
    return Promise.resolve({ data: [] as LivroResponse[] })
  },
  getWithAuthors: (id: number) => {
    return Promise.reject(new Error("Livros with authors not implemented yet"))
  },
}

// Bibliotecas API
export const bibliotecasAPI = {
  getAll: (page = 1, size = 100) => api.get<BibliotecaListResponse>("/api/v1/bibliotecas/", { params: { page, size } }),
  getById: (id: number) => api.get<BibliotecaResponse>(`/api/v1/bibliotecas/${id}`),
  create: (data: BibliotecaCreate) => api.post<BibliotecaResponse>("/api/v1/bibliotecas/", data),
  update: (id: number, data: BibliotecaUpdate) => api.put<BibliotecaResponse>(`/api/v1/bibliotecas/${id}`, data),
  delete: (id: number) => api.delete<BaseResponse>(`/api/v1/bibliotecas/${id}`),
  getEstoque: (id: number, page = 1, size = 10) =>
    api.get(`/api/v1/bibliotecas/${id}/estoque`, { params: { page, size } }),
  getItensDisponiveis: (id: number) => api.get(`/api/v1/bibliotecas/${id}/itens-disponiveis`),
}

// Updated Autores API
export const autoresAPI = {
  getAll: (page = 1, size = 10) => api.get<AutorListResponse>("/api/v1/autores/", { params: { page, size } }),
  getById: (id: number) => api.get<AutorResponse>(`/api/v1/autores/${id}`),
  create: (data: AutorCreate) => api.post<AutorResponse>("/api/v1/autores/", data),
  update: (id: number, data: AutorUpdate) => api.put<AutorResponse>(`/api/v1/autores/${id}`, data),
  delete: (id: number) => api.delete<BaseResponse>(`/api/v1/autores/${id}`),
}

// Autorias API
export const autoriasAPI = {
  getAll: (page = 1, size = 10, id_autor?: number, id_titulo?: number) =>
    api.get<AutoriasListResponse>("/api/v1/autores/autorias", {
      params: { page, size, ...(id_autor && { id_autor }), ...(id_titulo && { id_titulo }) },
    }),
  create: (data: AutoriasCreate) => api.post<AutoriasResponse>("/api/v1/autores/autorias", data),
}

export default api
