const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8765"

// Base API client
class APIClient {
  private baseURL: string

  constructor(baseURL: string) {
    this.baseURL = baseURL
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<{ data: T }> {
    const url = `${this.baseURL}${endpoint}`
    const config: RequestInit = {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    }

    const response = await fetch(url, config)

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    return { data }
  }

  async get<T>(endpoint: string): Promise<{ data: T }> {
    return this.request<T>(endpoint, { method: "GET" })
  }

  async post<T>(endpoint: string, data: any): Promise<{ data: T }> {
    return this.request<T>(endpoint, {
      method: "POST",
      body: JSON.stringify(data),
    })
  }

  async put<T>(endpoint: string, data: any): Promise<{ data: T }> {
    return this.request<T>(endpoint, {
      method: "PUT",
      body: JSON.stringify(data),
    })
  }

  async delete<T>(endpoint: string): Promise<{ data: T }> {
    return this.request<T>(endpoint, { method: "DELETE" })
  }
}

const apiClient = new APIClient(API_BASE_URL)

// Types
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

export interface RelatorioEmprestimos {
    total_emprestimos: number
    emprestimos_em_andamento: number
    emprestimos_vencidos: number
    emprestimos_devolvidos: number
}

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

export interface Estoque {
  id_estoque: number
  condicao?: string | null
  id_titulo: number
  id_biblioteca: number
}

export interface EstoqueWithNames extends Estoque {
  titulo_nome?: string
  biblioteca_nome?: string
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

export interface TituloSearch {
  id_titulo: number
  titulo: string
  tipo_midia: "livro" | "revista" | "dvd" | "artigo"
}

export interface Emprestimo {
  id_emprestimo: number
  data_emprestimo: string
  data_devolucao_prevista?: string | null
  data_devolucao?: string | null
  id_estoque: number
  id_usuario: number
}

export interface EmprestimoCompleto {
  id_emprestimo: number
  data_emprestimo: string
  data_devolucao_prevista: string
  data_devolucao?: string | null
  id_estoque: number
  id_usuario: number
  usuario?: Usuario
  item_titulo: string
  tipo_midia: string
  biblioteca: string
}

export interface EmprestimoCreate {
  data_emprestimo: string
  data_devolucao_prevista?: string | null
  id_estoque: number
  id_usuario: number
}

// API functions
export const usuariosAPI = {
  getAll: (skip = 0, limit = 100) => apiClient.get<Usuario[]>(`/api/v1/usuarios/?skip=${skip}&limit=${limit}`),
  getById: (id: number) => apiClient.get<Usuario>(`/api/v1/usuarios/${id}`),
  create: (data: UsuarioCreate) => apiClient.post<Usuario>("/api/v1/usuarios/", data),
  update: (id: number, data: UsuarioUpdate) => apiClient.put<Usuario>(`/api/v1/usuarios/${id}`, data),
  delete: (id: number) => apiClient.delete(`/api/v1/usuarios/${id}`),
  search: (name: string) =>
    apiClient.get<Usuario[]>(`/api/v1/usuarios/pesquisar/usuarios?name=${encodeURIComponent(name)}`),
}

export const bibliotecasAPI = {
  getAll: (page = 0, size = 100) =>
    apiClient.get<{ data: BibliotecaResponse[]; total: number }>(`/api/v1/bibliotecas/?page=${page}&size=${size}`),
  getById: (id: number) => apiClient.get<BibliotecaResponse>(`/api/v1/bibliotecas/${id}`),
  create: (data: BibliotecaCreate) => apiClient.post<BibliotecaResponse>("/api/v1/bibliotecas/", data),
  update: (id: number, data: BibliotecaUpdate) => apiClient.put<BibliotecaResponse>(`/api/v1/bibliotecas/${id}`, data),
  delete: (id: number) => apiClient.delete(`/api/v1/bibliotecas/${id}`),
  search: (name: string) =>
    apiClient.get<BibliotecaResponse[]>(`/api/v1/bibliotecas/pesquisar/bibliotecas?name=${encodeURIComponent(name)}`),
}

export const autoresAPI = {
  getAll: (page = 1, size = 10) =>
    apiClient.get<{ data: AutorResponse[]; total: number }>(`/api/v1/autores/?page=${page}&size=${size}`),
  getById: (id: number) => apiClient.get<AutorResponse>(`/api/v1/autores/${id}`),
  create: (data: AutorCreate) => apiClient.post<AutorResponse>("/api/v1/autores/", data),
  update: (id: number, data: AutorUpdate) => apiClient.put<AutorResponse>(`/api/v1/autores/${id}`, data),
  delete: (id: number) => apiClient.delete(`/api/v1/autores/${id}`),
  search: (name: string) =>
    apiClient.get<AutorResponse[]>(`/api/v1/autores/pesquisar/bibliotecas?name=${encodeURIComponent(name)}`),
}

export const revistasAPI = {
  getAll: (skip = 0, limit = 100) => apiClient.get<RevistaResponse[]>(`/api/v1/revistas/?skip=${skip}&limit=${limit}`),
  getById: (id: number) => apiClient.get<RevistaResponse>(`/api/v1/revistas/${id}`),
  create: (data: RevistaCreate) => apiClient.post<RevistaResponse>("/api/v1/revistas/", data),
  update: (id: number, data: any) => apiClient.put<RevistaResponse>(`/api/v1/revistas/${id}`, data),
  delete: (id: number) => apiClient.delete(`/api/v1/revistas/${id}`),
  search: (query: string) =>
    apiClient.get<RevistaResponse[]>(`/api/v1/revistas/search/?q=${encodeURIComponent(query)}`),
  searchByTitle: (title: string) =>
    apiClient.get<RevistaResponse[]>(`/api/v1/revistas/pesquisar/revistas?title=${encodeURIComponent(title)}`),
}

export const dvdsAPI = {
  getAll: (skip = 0, limit = 100) => apiClient.get<DVDResponse[]>(`/api/v1/dvds/?skip=${skip}&limit=${limit}`),
  getById: (id: number) => apiClient.get<DVDResponse>(`/api/v1/dvds/${id}`),
  create: (data: DVDCreate) => apiClient.post<DVDResponse>("/api/v1/dvds/", data),
  update: (id: number, data: any) => apiClient.put<DVDResponse>(`/api/v1/dvds/${id}`, data),
  delete: (id: number) => apiClient.delete(`/api/v1/dvds/${id}`),
  search: (query: string) => apiClient.get<DVDResponse[]>(`/api/v1/dvds/search/?q=${encodeURIComponent(query)}`),
  searchByTitle: (title: string) =>
    apiClient.get<DVDResponse[]>(`/api/v1/dvds/pesquisar/dvds?title=${encodeURIComponent(title)}`),
}

export const artigosAPI = {
  getAll: (skip = 0, limit = 100) => apiClient.get<ArtigoResponse[]>(`/api/v1/artigos/?skip=${skip}&limit=${limit}`),
  getById: (id: number) => apiClient.get<ArtigoResponse>(`/api/v1/artigos/${id}`),
  create: (data: ArtigoCreate) => apiClient.post<ArtigoResponse>("/api/v1/artigos/", data),
  update: (id: number, data: any) => apiClient.put<ArtigoResponse>(`/api/v1/artigos/${id}`, data),
  delete: (id: number) => apiClient.delete(`/api/v1/artigos/${id}`),
  search: (query: string) => apiClient.get<ArtigoResponse[]>(`/api/v1/artigos/search/?q=${encodeURIComponent(query)}`),
  searchByTitle: (title: string) =>
    apiClient.get<ArtigoResponse[]>(`/api/v1/artigos/pesquisar/artigos?title=${encodeURIComponent(title)}`),
}

export const livrosAPI = {
  getAll: (skip = 0, limit = 100) => apiClient.get<LivroResponse[]>(`/api/v1/livros/?skip=${skip}&limit=${limit}`),
  getById: (id: number) => apiClient.get<LivroResponse>(`/api/v1/livros/${id}`),
  create: (data: LivroCreate) => apiClient.post<LivroResponse>("/api/v1/livros/", data),
  update: (id: number, data: any) => apiClient.put<LivroResponse>(`/api/v1/livros/${id}`, data),
  delete: (id: number) => apiClient.delete(`/api/v1/livros/${id}`),
  search: (query: string) => apiClient.get<LivroResponse[]>(`/api/v1/livros/search/?q=${encodeURIComponent(query)}`),
  searchByTitle: (title: string) =>
    apiClient.get<LivroResponse[]>(`/api/v1/livros/pesquisar/livros?title=${encodeURIComponent(title)}`),
}

export const estoqueAPI = {
  getAll: (skip = 0, limit = 100) => apiClient.get<Estoque[]>(`/api/v1/estoque/?skip=${skip}&limit=${limit}`),
  getById: (id: number) => apiClient.get<Estoque>(`/api/v1/estoque/${id}`),
  create: (data: EstoqueCreate) => apiClient.post<Estoque>("/api/v1/estoque/", data),
  update: (id: number, data: EstoqueUpdate) => apiClient.put<Estoque>(`/api/v1/estoque/${id}`, data),
  delete: (id: number) => apiClient.delete(`/api/v1/estoque/${id}`),
  searchTitles: (title: string) =>
    apiClient.get<TituloSearch[]>(`/api/v1/estoque/pesquisar/titulo?title=${encodeURIComponent(title)}`),
  searchEstoque: (title: string) =>
    apiClient.get<Estoque[]>(`/api/v1/estoque/pesquisar/estoque?title=${encodeURIComponent(title)}`),
}

export const emprestimosAPI = {
  getAll: (skip = 0, limit = 100) => apiClient.get<Emprestimo[]>(`/api/v1/emprestimos/?skip=${skip}&limit=${limit}`),
  getById: (id: number) => apiClient.get<Emprestimo>(`/api/v1/emprestimos/${id}`),
  create: (data: EmprestimoCreate) => apiClient.post<Emprestimo>("/api/v1/emprestimos/", data),
  devolver: (id: number, dataDevolucao?: string) => {
    const params = dataDevolucao ? `?data_devolucao=${dataDevolucao}` : ""
    return apiClient.request<Emprestimo>(`/api/v1/emprestimos/${id}/devolver${params}`, { method: "PATCH" })
  },
  getRelatorio: () => apiClient.get<RelatorioEmprestimos>("/api/v1/emprestimos/relatorio/"),
  getEmAndamento: (skip = 0, limit = 100) =>
    apiClient.get<EmprestimoCompleto[]>(`/api/v1/emprestimos/em-andamento/?skip=${skip}&limit=${limit}`),
  getVencidos: (skip = 0, limit = 100) =>
    apiClient.get<EmprestimoCompleto[]>(`/api/v1/emprestimos/vencidos/?skip=${skip}&limit=${limit}`),
  search: (query: string) =>
    apiClient.get<Emprestimo[]>(`/api/v1/emprestimos/pesquisar/emprestimos?query=${encodeURIComponent(query)}`),
}
