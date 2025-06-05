"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Plus, Search, Edit, Trash2, BookOpen, FileText, Disc, Newspaper } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useToast } from "@/hooks/use-toast"
import { Badge } from "@/components/ui/badge"

interface Midia {
  id_titulo: number
  tipo_midia: "livro" | "revista" | "dvd" | "artigo"
  titulo?: string
  ISBN?: string
  numero_paginas?: number
  editora?: string
  data_publicacao?: string
  edicao?: string
  periodicidade?: string
  duracao?: number
  diretor?: string
  genero?: string
  resumo?: string
  palavras_chave?: string
}

const tipoMidiaIcons = {
  livro: BookOpen,
  revista: Newspaper,
  dvd: Disc,
  artigo: FileText,
}

const tipoMidiaColors = {
  livro: "bg-blue-100 text-blue-800",
  revista: "bg-green-100 text-green-800",
  dvd: "bg-purple-100 text-purple-800",
  artigo: "bg-orange-100 text-orange-800",
}

export default function MidiasPage() {
  const [midias, setMidias] = useState<Midia[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [editingMidia, setEditingMidia] = useState<Midia | null>(null)
  const [selectedTipo, setSelectedTipo] = useState<string>("")
  const [formData, setFormData] = useState<Partial<Midia>>({})
  const { toast } = useToast()

  useEffect(() => {
    // Simular carregamento de dados
    setMidias([
      {
        id_titulo: 1,
        tipo_midia: "livro",
        titulo: "Dom Casmurro",
        ISBN: "978-85-359-0277-5",
        numero_paginas: 256,
        editora: "Companhia das Letras",
        data_publicacao: "2008-01-15",
      },
      {
        id_titulo: 2,
        tipo_midia: "revista",
        titulo: "National Geographic Brasil",
        edicao: "Janeiro 2024",
        periodicidade: "Mensal",
        editora: "Editora Abril",
      },
      {
        id_titulo: 3,
        tipo_midia: "dvd",
        titulo: "Cidade de Deus",
        duracao: 130,
        diretor: "Fernando Meirelles",
        genero: "Drama",
      },
      {
        id_titulo: 4,
        tipo_midia: "artigo",
        titulo: "Inteligência Artificial na Educação",
        resumo: "Análise do impacto da IA no ensino",
        palavras_chave: "IA, educação, tecnologia",
      },
    ])
  }, [])

  const filteredMidias = midias.filter(
    (midia) =>
      midia.titulo?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      midia.tipo_midia.toLowerCase().includes(searchTerm.toLowerCase()),
  )

  const resetForm = () => {
    setFormData({})
    setSelectedTipo("")
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (editingMidia) {
      // Atualizar mídia
      setMidias(
        midias.map((m) =>
          m.id_titulo === editingMidia.id_titulo
            ? { ...editingMidia, ...formData, tipo_midia: selectedTipo as any }
            : m,
        ),
      )
      toast({
        title: "Mídia atualizada",
        description: "Os dados da mídia foram atualizados com sucesso.",
      })
    } else {
      // Criar nova mídia
      const newMidia: Midia = {
        id_titulo: Math.max(...midias.map((m) => m.id_titulo)) + 1,
        tipo_midia: selectedTipo as any,
        ...formData,
      }
      setMidias([...midias, newMidia])
      toast({
        title: "Mídia criada",
        description: "Nova mídia foi cadastrada com sucesso.",
      })
    }

    setIsDialogOpen(false)
    setEditingMidia(null)
    resetForm()
  }

  const handleEdit = (midia: Midia) => {
    setEditingMidia(midia)
    setSelectedTipo(midia.tipo_midia)
    setFormData(midia)
    setIsDialogOpen(true)
  }

  const handleDelete = (id: number) => {
    setMidias(midias.filter((m) => m.id_titulo !== id))
    toast({
      title: "Mídia removida",
      description: "A mídia foi removida do sistema.",
      variant: "destructive",
    })
  }

  const openNewMidiaDialog = () => {
    setEditingMidia(null)
    resetForm()
    setIsDialogOpen(true)
  }

  const renderSpecificFields = () => {
    switch (selectedTipo) {
      case "livro":
        return (
          <>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="titulo" className="text-right">
                Título
              </Label>
              <Input
                id="titulo"
                value={formData.titulo || ""}
                onChange={(e) => setFormData({ ...formData, titulo: e.target.value })}
                className="col-span-3"
                required
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="ISBN" className="text-right">
                ISBN
              </Label>
              <Input
                id="ISBN"
                value={formData.ISBN || ""}
                onChange={(e) => setFormData({ ...formData, ISBN: e.target.value })}
                className="col-span-3"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="numero_paginas" className="text-right">
                Páginas
              </Label>
              <Input
                id="numero_paginas"
                type="number"
                value={formData.numero_paginas || ""}
                onChange={(e) => setFormData({ ...formData, numero_paginas: Number.parseInt(e.target.value) })}
                className="col-span-3"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="editora" className="text-right">
                Editora
              </Label>
              <Input
                id="editora"
                value={formData.editora || ""}
                onChange={(e) => setFormData({ ...formData, editora: e.target.value })}
                className="col-span-3"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="data_publicacao" className="text-right">
                Data Publicação
              </Label>
              <Input
                id="data_publicacao"
                type="date"
                value={formData.data_publicacao || ""}
                onChange={(e) => setFormData({ ...formData, data_publicacao: e.target.value })}
                className="col-span-3"
              />
            </div>
          </>
        )
      case "revista":
        return (
          <>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="titulo" className="text-right">
                Título
              </Label>
              <Input
                id="titulo"
                value={formData.titulo || ""}
                onChange={(e) => setFormData({ ...formData, titulo: e.target.value })}
                className="col-span-3"
                required
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="edicao" className="text-right">
                Edição
              </Label>
              <Input
                id="edicao"
                value={formData.edicao || ""}
                onChange={(e) => setFormData({ ...formData, edicao: e.target.value })}
                className="col-span-3"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="periodicidade" className="text-right">
                Periodicidade
              </Label>
              <Input
                id="periodicidade"
                value={formData.periodicidade || ""}
                onChange={(e) => setFormData({ ...formData, periodicidade: e.target.value })}
                className="col-span-3"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="editora" className="text-right">
                Editora
              </Label>
              <Input
                id="editora"
                value={formData.editora || ""}
                onChange={(e) => setFormData({ ...formData, editora: e.target.value })}
                className="col-span-3"
              />
            </div>
          </>
        )
      case "dvd":
        return (
          <>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="titulo" className="text-right">
                Título
              </Label>
              <Input
                id="titulo"
                value={formData.titulo || ""}
                onChange={(e) => setFormData({ ...formData, titulo: e.target.value })}
                className="col-span-3"
                required
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="duracao" className="text-right">
                Duração (min)
              </Label>
              <Input
                id="duracao"
                type="number"
                value={formData.duracao || ""}
                onChange={(e) => setFormData({ ...formData, duracao: Number.parseInt(e.target.value) })}
                className="col-span-3"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="diretor" className="text-right">
                Diretor
              </Label>
              <Input
                id="diretor"
                value={formData.diretor || ""}
                onChange={(e) => setFormData({ ...formData, diretor: e.target.value })}
                className="col-span-3"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="genero" className="text-right">
                Gênero
              </Label>
              <Input
                id="genero"
                value={formData.genero || ""}
                onChange={(e) => setFormData({ ...formData, genero: e.target.value })}
                className="col-span-3"
              />
            </div>
          </>
        )
      case "artigo":
        return (
          <>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="titulo" className="text-right">
                Título
              </Label>
              <Input
                id="titulo"
                value={formData.titulo || ""}
                onChange={(e) => setFormData({ ...formData, titulo: e.target.value })}
                className="col-span-3"
                required
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="resumo" className="text-right">
                Resumo
              </Label>
              <Input
                id="resumo"
                value={formData.resumo || ""}
                onChange={(e) => setFormData({ ...formData, resumo: e.target.value })}
                className="col-span-3"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="palavras_chave" className="text-right">
                Palavras-chave
              </Label>
              <Input
                id="palavras_chave"
                value={formData.palavras_chave || ""}
                onChange={(e) => setFormData({ ...formData, palavras_chave: e.target.value })}
                className="col-span-3"
                placeholder="Separadas por vírgula"
              />
            </div>
          </>
        )
      default:
        return null
    }
  }

  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <SidebarTrigger />
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Mídias</h2>
            <p className="text-muted-foreground">Gerencie o acervo de mídias da biblioteca</p>
          </div>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={openNewMidiaDialog} className="onix-gradient">
              <Plus className="mr-2 h-4 w-4" />
              Nova Mídia
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[500px] max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>{editingMidia ? "Editar Mídia" : "Nova Mídia"}</DialogTitle>
              <DialogDescription>
                {editingMidia
                  ? "Atualize as informações da mídia."
                  : "Selecione o tipo de mídia e preencha os dados específicos."}
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit}>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="tipo_midia" className="text-right">
                    Tipo de Mídia
                  </Label>
                  <Select value={selectedTipo} onValueChange={setSelectedTipo} required>
                    <SelectTrigger className="col-span-3">
                      <SelectValue placeholder="Selecione o tipo" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="livro">📚 Livro</SelectItem>
                      <SelectItem value="revista">📰 Revista</SelectItem>
                      <SelectItem value="dvd">💿 DVD</SelectItem>
                      <SelectItem value="artigo">📄 Artigo</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {renderSpecificFields()}
              </div>
              <DialogFooter>
                <Button type="submit" className="onix-gradient" disabled={!selectedTipo}>
                  {editingMidia ? "Atualizar" : "Cadastrar"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Acervo de Mídias</CardTitle>
          <CardDescription>{midias.length} mídias cadastradas</CardDescription>
          <div className="flex items-center space-x-2">
            <Search className="w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Buscar mídias..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="max-w-sm"
            />
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Título</TableHead>
                <TableHead>Detalhes</TableHead>
                <TableHead className="text-right">Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredMidias.map((midia) => {
                const Icon = tipoMidiaIcons[midia.tipo_midia]
                return (
                  <TableRow key={midia.id_titulo}>
                    <TableCell className="font-medium">{midia.id_titulo}</TableCell>
                    <TableCell>
                      <Badge className={tipoMidiaColors[midia.tipo_midia]}>
                        <Icon className="w-3 h-3 mr-1" />
                        {midia.tipo_midia}
                      </Badge>
                    </TableCell>
                    <TableCell className="font-medium">{midia.titulo || "Sem título"}</TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {midia.tipo_midia === "livro" && midia.editora && `${midia.editora}`}
                      {midia.tipo_midia === "revista" && midia.edicao && `${midia.edicao}`}
                      {midia.tipo_midia === "dvd" && midia.diretor && `Dir: ${midia.diretor}`}
                      {midia.tipo_midia === "artigo" && midia.palavras_chave && `${midia.palavras_chave}`}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button variant="outline" size="sm" onClick={() => handleEdit(midia)}>
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button variant="outline" size="sm" onClick={() => handleDelete(midia.id_titulo)}>
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
