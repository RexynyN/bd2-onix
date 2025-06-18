import axios from "axios"

// Configure axios base URL - adjust this to your API URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
})

// API Types based on the exact API specification
export interface Usuario {
  id_usuario: number
  nome: string
  email: string
  endereco: string
  telefone: string
}

export interface Biblioteca {
  id_biblioteca: number
  nome: string
  endereco: string
}

export interface Livro {
  id_livro: number
  titulo: string
  ISBN: string
  numero_paginas: number
  editora: string
  data_publicacao: string
}

export interface Revista {
  id_revista: number
  titulo: string
  ISSN: string
  periodicidade: string
  editora: string
  data_publicacao: string
}

export interface DVD {
  id_dvd: number
  titulo: string
  ISAN: string
  duracao: number
  distribuidora: string
  data_lancamento: string
}

export interface Artigo {
  id_artigo: number
  titulo: string
  DOI: string
  publicadora: string
  data_publicacao: string
}

export interface Autor {
  id_autor: number
  nome: string
  data_nascimento: string
  data_falecimento?: string
}

export interface Estoque {
  id_estoque: number
  condicao: string
  id_titulo: number
  id_biblioteca: number
}

export interface Emprestimo {
  id_emprestimo: number
  data_emprestimo: string
  data_devolucao_prevista: string
  data_devolucao?: string | null
  id_estoque: number
  id_usuario: number
}

export interface EmprestimoDetalhado {
  id_emprestimo: number
  data_emprestimo: string
  data_devolucao_prevista: string
  data_devolucao?: string | null
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

export interface DisponibilidadeItem {
  id_titulo: number
  titulo: string
  tipo_midia: string
  total_exemplares: number
  exemplares_disponiveis: number
  exemplares_emprestados: number
}

// API Functions
export const usuariosAPI = {
  getAll: (skip = 0, limit = 100) => api.get<Usuario[]>(`/usuarios/?skip=${skip}&limit=${limit}`),
  getById: (id: number) => api.get<Usuario>(`/usuarios/${id}`),
  create: (data: Omit<Usuario, "id_usuario">) => api.post<Usuario>("/usuarios/", data),
  update: (id: number, data: Partial<Omit<Usuario, "id_usuario">>) => api.put<Usuario>(`/usuarios/${id}`, data),
  delete: (id: number) => api.delete<{ message: string }>(`/usuarios/${id}`),
  getAtivos: () => api.get<Usuario[]>("/usuarios/emprestimos/ativos"),
}

export const bibliotecasAPI = {
  getAll: (skip = 0, limit = 100) => api.get<Biblioteca[]>(`/bibliotecas/?skip=${skip}&limit=${limit}`),
  getById: (id: number) => api.get<Biblioteca>(`/bibliotecas/${id}`),
  create: (data: Omit<Biblioteca, "id_biblioteca">) => api.post<Biblioteca>("/bibliotecas/", data),
  update: (id: number, data: Partial<Omit<Biblioteca, "id_biblioteca">>) =>
    api.put<Biblioteca>(`/bibliotecas/${id}`, data),
  delete: (id: number) => api.delete<{ message: string }>(`/bibliotecas/${id}`),
}

export const livrosAPI = {
  getAll: (skip = 0, limit = 100) => api.get<Livro[]>(`/livros/?skip=${skip}&limit=${limit}`),
  getById: (id: number) => api.get<Livro>(`/livros/${id}`),
  create: (data: Omit<Livro, "id_livro">) => api.post<Livro>("/livros/", data),
  update: (id: number, data: Partial<Omit<Livro, "id_livro">>) => api.put<Livro>(`/livros/${id}`, data),
  delete: (id: number) => api.delete<{ message: string }>(`/livros/${id}`),
  search: (q: string) => api.get<Livro[]>(`/livros/search/?q=${encodeURIComponent(q)}`),
  getWithAuthors: (id: number) => api.get<Livro & { autores: Autor[] }>(`/livros/${id}/autores`),
}

export const revistasAPI = {
  getAll: (skip = 0, limit = 100) => api.get<Revista[]>(`/revistas/?skip=${skip}&limit=${limit}`),
  getById: (id: number) => api.get<Revista>(`/revistas/${id}`),
  create: (data: Omit<Revista, "id_revista">) => api.post<Revista>("/revistas/", data),
  update: (id: number, data: Partial<Omit<Revista, "id_revista">>) => api.put<Revista>(`/revistas/${id}`, data),
  delete: (id: number) => api.delete<{ message: string }>(`/revistas/${id}`),
  search: (q: string) => api.get<Revista[]>(`/revistas/search/?q=${encodeURIComponent(q)}`),
  getWithAuthors: (id: number) => api.get<Revista & { autores: Autor[] }>(`/revistas/${id}/autores`),
}

export const dvdsAPI = {
  getAll: (skip = 0, limit = 100) => api.get<DVD[]>(`/dvds/?skip=${skip}&limit=${limit}`),
  getById: (id: number) => api.get<DVD>(`/dvds/${id}`),
  create: (data: Omit<DVD, "id_dvd">) => api.post<DVD>("/dvds/", data),
  update: (id: number, data: Partial<Omit<DVD, "id_dvd">>) => api.put<DVD>(`/dvds/${id}`, data),
  delete: (id: number) => api.delete<{ message: string }>(`/dvds/${id}`),
  search: (q: string) => api.get<DVD[]>(`/dvds/search/?q=${encodeURIComponent(q)}`),
  getWithAuthors: (id: number) => api.get<DVD & { autores: Autor[] }>(`/dvds/${id}/autores`),
}

export const artigosAPI = {
  getAll: (skip = 0, limit = 100) => api.get<Artigo[]>(`/artigos/?skip=${skip}&limit=${limit}`),
  getById: (id: number) => api.get<Artigo>(`/artigos/${id}`),
  create: (data: Omit<Artigo, "id_artigo">) => api.post<Artigo>("/artigos/", data),
  update: (id: number, data: Partial<Omit<Artigo, "id_artigo">>) => api.put<Artigo>(`/artigos/${id}`, data),
  delete: (id: number) => api.delete<{ message: string }>(`/artigos/${id}`),
  search: (q: string) => api.get<Artigo[]>(`/artigos/search/?q=${encodeURIComponent(q)}`),
  getWithAuthors: (id: number) => api.get<Artigo & { autores: Autor[] }>(`/artigos/${id}/autores`),
}

export const autoresAPI = {
  getAll: (skip = 0, limit = 100) => api.get<Autor[]>(`/autores/?skip=${skip}&limit=${limit}`),
  getById: (id: number) => api.get<Autor>(`/autores/${id}`),
  create: (data: Omit<Autor, "id_autor">) => api.post<Autor>("/autores/", data),
  update: (id: number, data: Partial<Omit<Autor, "id_autor">>) => api.put<Autor>(`/autores/${id}`, data),
  delete: (id: number) => api.delete<{ message: string }>(`/autores/${id}`),
  search: (q: string) => api.get<Autor[]>(`/autores/search/?q=${encodeURIComponent(q)}`),
}

export const estoqueAPI = {
  getAll: (skip = 0, limit = 100) => api.get<Estoque[]>(`/estoque/?skip=${skip}&limit=${limit}`),
  getById: (id: number) => api.get<Estoque>(`/estoque/${id}`),
  create: (data: Omit<Estoque, "id_estoque">) => api.post<Estoque>("/estoque/", data),
  update: (id: number, data: Partial<Omit<Estoque, "id_estoque">>) => api.put<Estoque>(`/estoque/${id}`, data),
  delete: (id: number) => api.delete<{ message: string }>(`/estoque/${id}`),
  getByBiblioteca: (id_biblioteca: number) => api.get<Estoque[]>(`/estoque/biblioteca/${id_biblioteca}`),
  getDisponibilidade: (id_titulo: number) => api.get<DisponibilidadeItem>(`/estoque/disponibilidade/${id_titulo}`),
}

export const emprestimosAPI = {
  getAll: (skip = 0, limit = 100) => api.get<Emprestimo[]>(`/emprestimos/?skip=${skip}&limit=${limit}`),
  getById: (id: number) => api.get<Emprestimo>(`/emprestimos/${id}`),
  create: (data: Omit<Emprestimo, "id_emprestimo">) => api.post<Emprestimo>("/emprestimos/", data),
  devolver: (id: number, data_devolucao?: string) => {
    const params = data_devolucao ? `?data_devolucao=${data_devolucao}` : ""
    return api.patch<Emprestimo>(`/emprestimos/${id}/devolver${params}`)
  },
  getEmAndamento: () => api.get<EmprestimoDetalhado[]>("/emprestimos/em-andamento/"),
  getVencidos: () => api.get<EmprestimoDetalhado[]>("/emprestimos/vencidos/"),
  getRelatorio: () => api.get<RelatorioEmprestimos>("/emprestimos/relatorio/"),
}

export default api
