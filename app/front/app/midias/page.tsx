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
import { titulosAPI, livrosAPI, revistasAPI, dvdsAPI, artigosAPI, type Titulo } from "@/lib/api"

interface MidiaExtended extends Titulo {
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
  data_lancamento?: string
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
  const [midias, setMidias] = useState<MidiaExtended[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [editingMidia, setEditingMidia] = useState<MidiaExtended | null>(null)
  const [selectedTipo, setSelectedTipo] = useState<string>("")
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [formData, setFormData] = useState<Partial<MidiaExtended>>({})
  const { toast } = useToast()

  useEffect(() => {
    fetchTitulos()
  }, [])

  const fetchTitulos = async () => {
    try {
      setLoading(true)
      const response = await titulosAPI.getAll()
      // For now, we'll just show the titles. In a real app, you'd need to fetch
      // additional data for each title based on its type
      setMidias(
        response.data.map((titulo) => ({
          ...titulo,
          titulo: `Título ${titulo.id_titulo}`, // Placeholder - would come from related tables
        })),
      )
    } catch (error) {
      console.error("Error fetching titulos:", error)
      toast({
        title: "Erro ao carregar mídias",
        description: "Não foi possível carregar a lista de mídias.",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

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
    setSubmitting(true)

    try {
      if (editingMidia) {
        // For editing, we would need separate endpoints for each media type
        toast({
          title: "Funcionalidade em desenvolvimento",
          description: "A edição de mídias será implementada em breve.",
          variant: "destructive",
        })
      } else {
        // Create new title first
        const tituloResponse = await titulosAPI.create({ tipo_midia: selectedTipo })

        // Create the specific media type record
        let mediaResponse
        switch (selectedTipo) {
          case "livro":
            if (formData.titulo) {
              mediaResponse = await livrosAPI.create({
                titulo: formData.titulo,
                ISBN: formData.ISBN || "",
                numero_paginas: formData.numero_paginas || 0,
                editora: formData.editora || "",
                data_publicacao: formData.data_publicacao || "",
                id_titulo: tituloResponse.data.id_titulo,
              })
            }
            break
          case "revista":
            if (formData.titulo) {
              mediaResponse = await revistasAPI.create({
                titulo: formData.titulo,
                edicao: formData.edicao || "",
                periodicidade: formData.periodicidade || "",
                editora: formData.editora || "",
                data_publicacao: formData.data_publicacao || "",
                id_titulo: tituloResponse.data.id_titulo,
              })
            }
            break
          case "dvd":
            if (formData.titulo) {
              mediaResponse = await dvdsAPI.create({
                titulo: formData.titulo,
                duracao: formData.duracao || 0,
                diretor: formData.diretor || "",
                genero: formData.genero || "",
                data_lancamento: formData.data_lancamento || "",
                id_titulo: tituloResponse.data.id_titulo,
              })
            }
            break
          case "artigo":
            if (formData.titulo) {
              mediaResponse = await artigosAPI.create({
                titulo: formData.titulo,
                resumo: formData.resumo || "",
                palavras_chave: formData.palavras_chave || "",
                data_publicacao: formData.data_publicacao || "",
                id_titulo: tituloResponse.data.id_titulo,
              })
            }
            break
        }

        // Add the new title to our list
        const newMidia: MidiaExtended = {
          ...tituloResponse.data,
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
    } catch (error) {
      console.error("Error saving midia:", error)
      toast({
        title: "Erro ao salvar mídia",
        description: "Não foi possível salvar a mídia. Tente novamente.",
        variant: "destructive",
      })
    } finally {
      setSubmitting(false)
    }
  }

  const handleEdit = (midia: MidiaExtended) => {
    setEditingMidia(midia)
    setSelectedTipo(midia.tipo_midia)
    setFormData(midia)
    setIsDialogOpen(true)
  }

  const handleDelete = (id: number) => {
    // Note: The API doesn't provide a delete endpoint for titles
    toast({
      title: "Funcionalidade não disponível",
      description: "A API não fornece endpoint para deletar títulos.",
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
                disabled={submitting}
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
                disabled={submitting}
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
                disabled={submitting}
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
                disabled={submitting}
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
                disabled={submitting}
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
                disabled={submitting}
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
                disabled={submitting}
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
                disabled={submitting}
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
                disabled={submitting}
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
                disabled={submitting}
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
                disabled={submitting}
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
                disabled={submitting}
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
                disabled={submitting}
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
                disabled={submitting}
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="data_lancamento" className="text-right">
                Data Lançamento
              </Label>
              <Input
                id="data_lancamento"
                type="date"
                value={formData.data_lancamento || ""}
                onChange={(e) => setFormData({ ...formData, data_lancamento: e.target.value })}
                className="col-span-3"
                disabled={submitting}
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
                disabled={submitting}
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
                disabled={submitting}
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
                disabled={submitting}
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
                disabled={submitting}
              />
            </div>
          </>
        )
      default:
        return null
    }
  }

  // Rest of the component remains the same...
  if (loading) {
    return (
      <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
        <div className="flex items-center gap-4">
          <SidebarTrigger />
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Mídias</h2>
            <p className="text-muted-foreground">Carregando...</p>
          </div>
        </div>
        <Card>
          <CardContent className="p-6">
            <div className="text-center">Carregando mídias...</div>
          </CardContent>
        </Card>
      </div>
    )
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
                  <Select value={selectedTipo} onValueChange={setSelectedTipo} required disabled={submitting}>
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
                <Button type="submit" className="onix-gradient" disabled={!selectedTipo || submitting}>
                  {submitting ? "Salvando..." : editingMidia ? "Atualizar" : "Cadastrar"}
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
