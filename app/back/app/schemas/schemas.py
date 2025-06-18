from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date
from enum import Enum

# Enum para tipo de mídia
class MidiaTipo(str, Enum):
    livro = "livro"
    revista = "revista"
    dvd = "dvd"
    artigo = "artigo"

# Schemas para Usuario
class UsuarioBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    endereco: Optional[str] = None
    telefone: Optional[str] = None

class UsuarioCreate(UsuarioBase):
    pass

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    endereco: Optional[str] = None
    telefone: Optional[str] = None

class Usuario(UsuarioBase):
    id_usuario: int
    
    class Config:
        from_attributes = True

# Schemas para Biblioteca
class BibliotecaBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=255)
    endereco: Optional[str] = None

class BibliotecaCreate(BibliotecaBase):
    pass

class BibliotecaUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    endereco: Optional[str] = None

class Biblioteca(BibliotecaBase):
    id_biblioteca: int
    
    class Config:
        from_attributes = True

# Schemas para Titulo
class TituloBase(BaseModel):
    tipo_midia: MidiaTipo

class TituloCreate(TituloBase):
    pass

class TituloUpdate(BaseModel):
    tipo_midia: Optional[MidiaTipo] = None

class Titulo(TituloBase):
    id_titulo: int
    
    class Config:
        from_attributes = True

# Schemas para Estoque
class EstoqueBase(BaseModel):
    condicao: Optional[str] = None
    id_titulo: int
    id_biblioteca: int

class EstoqueCreate(EstoqueBase):
    pass

class EstoqueUpdate(BaseModel):
    condicao: Optional[str] = None
    id_titulo: Optional[int] = None
    id_biblioteca: Optional[int] = None

class Estoque(EstoqueBase):
    id_estoque: int
    
    class Config:
        from_attributes = True

# Schemas para Emprestimo
class EmprestimoBase(BaseModel):
    data_emprestimo: date
    data_devolucao_prevista: Optional[date] = None
    id_estoque: int
    id_usuario: int

class EmprestimoCreate(EmprestimoBase):
    pass

class EmprestimoUpdate(BaseModel):
    data_emprestimo: Optional[date] = None
    data_devolucao_prevista: Optional[date] = None
    data_devolucao: Optional[date] = None
    id_estoque: Optional[int] = None
    id_usuario: Optional[int] = None

class Emprestimo(EmprestimoBase):
    id_emprestimo: int
    data_devolucao: Optional[date] = None
    
    class Config:
        from_attributes = True

# Schemas para Penalizacao
class PenalizacaoBase(BaseModel):
    descricao: Optional[str] = None
    final_penalizacao: Optional[date] = None
    id_usuario: int
    id_emprestimo: int

class PenalizacaoCreate(PenalizacaoBase):
    pass

class PenalizacaoUpdate(BaseModel):
    descricao: Optional[str] = None
    final_penalizacao: Optional[date] = None
    id_usuario: Optional[int] = None
    id_emprestimo: Optional[int] = None

class Penalizacao(PenalizacaoBase):
    id_penalizacao: int
    
    class Config:
        from_attributes = True

# Schemas para Livros
class LivroBase(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=255)
    isbn: Optional[str] = None
    numero_paginas: Optional[int] = None
    editora: Optional[str] = None
    data_publicacao: Optional[date] = None

class LivroCreate(LivroBase):
    pass

class LivroUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=1, max_length=255)
    isbn: Optional[str] = None
    numero_paginas: Optional[int] = None
    editora: Optional[str] = None
    data_publicacao: Optional[date] = None

class Livro(LivroBase):
    id_livro: int
    
    class Config:
        from_attributes = True

# Schemas para Revistas
class RevistaBase(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=255)
    issn: Optional[str] = None
    periodicidade: Optional[str] = None
    editora: Optional[str] = None
    data_publicacao: Optional[date] = None

class RevistaCreate(RevistaBase):
    pass

class RevistaUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=1, max_length=255)
    issn: Optional[str] = None
    periodicidade: Optional[str] = None
    editora: Optional[str] = None
    data_publicacao: Optional[date] = None

class Revista(RevistaBase):
    id_revista: int
    
    class Config:
        from_attributes = True

# Schemas para DVDs
class DVDBase(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=255)
    isan: Optional[str] = None
    duracao: Optional[int] = None
    distribuidora: Optional[str] = None
    data_lancamento: Optional[date] = None

class DVDCreate(DVDBase):
    pass

class DVDUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=1, max_length=255)
    isan: Optional[str] = None
    duracao: Optional[int] = None
    distribuidora: Optional[str] = None
    data_lancamento: Optional[date] = None

class DVD(DVDBase):
    id_dvd: int
    
    class Config:
        from_attributes = True

# Schemas para Artigos
class ArtigoBase(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=255)
    doi: Optional[str] = None
    publicadora: Optional[str] = None
    data_publicacao: Optional[date] = None

class ArtigoCreate(ArtigoBase):
    pass

class ArtigoUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=1, max_length=255)
    doi: Optional[str] = None
    publicadora: Optional[str] = None
    data_publicacao: Optional[date] = None

class Artigo(ArtigoBase):
    id_artigo: int
    
    class Config:
        from_attributes = True

# Schemas para Autores
class AutorBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=255)
    data_nascimento: Optional[date] = None
    data_falecimento: Optional[date] = None

class AutorCreate(AutorBase):
    pass

class AutorUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    data_nascimento: Optional[date] = None
    data_falecimento: Optional[date] = None

class Autor(AutorBase):
    id_autor: int
    
    class Config:
        from_attributes = True

# Schemas para Autorias
class AutoriasBase(BaseModel):
    id_autor: int
    id_titulo: int

class AutoriasCreate(AutoriasBase):
    pass

class AutoriasUpdate(BaseModel):
    id_autor: Optional[int] = None
    id_titulo: Optional[int] = None

class Autorias(AutoriasBase):
    id_autorias: int
    
    class Config:
        from_attributes = True

# Schemas para respostas com informações adicionais
class EmprestimoCompleto(BaseModel):
    id_emprestimo: int
    data_emprestimo: date
    data_devolucao_prevista: Optional[date]
    data_devolucao: Optional[date]
    usuario: Usuario
    item_titulo: str
    tipo_midia: str
    biblioteca: str

class RelatorioEmprestimos(BaseModel):
    total_emprestimos: int
    emprestimos_em_andamento: int
    emprestimos_vencidos: int
    emprestimos_devolvidos: int

class DisponibilidadeItem(BaseModel):
    id_titulo: int
    titulo: str
    tipo_midia: str
    total_exemplares: int
    exemplares_disponiveis: int
    exemplares_emprestados: int
