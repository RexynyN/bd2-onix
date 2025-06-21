"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Plus, Search, Edit, Trash2, FileText, Disc, Newspaper, BookOpen } from "lucide-react"
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
import { useToast } from "@/hooks/use-toast"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  revistasAPI,
  dvdsAPI,
  artigosAPI,
  livrosAPI,
  type RevistaResponse,
  type DVDResponse,
  type ArtigoResponse,
  type LivroResponse,
  type RevistaCreate,
  type DVDCreate,
  type ArtigoCreate,
  type LivroCreate,
} from "@/lib/api"
import { Pagination } from "@/components/pagination"
import { AdvancedFilters, type FilterConfig, type FilterValues } from "@/components/advanced-filters"

type MediaType = "revista" | "dvd" | "artigo" | "livro"
type MediaItem = RevistaResponse | DVDResponse | ArtigoResponse | LivroResponse

const ITEMS_PER_PAGE = 10

const tipoMidiaIcons = {
  revista: Newspaper,
  dvd: Disc,
  artigo: FileText,
  livro: BookOpen,
}

const tipoMidiaColors = {
  revista: "bg-green-100 text-green-800",
  dvd: "bg-purple-100 text-purple-800",
  artigo: "bg-orange-100 text-orange-800",
  livro: "bg-blue-100 text-blue-800",
}

export default function MidiasPage() {
  const [revistas, setRevistas] = useState<RevistaResponse[]>([])
  const [dvds, setDvds] = useState<DVDResponse[]>([])
  const [artigos, setArtigos] = useState<ArtigoResponse[]>([])
  const [livros, setLivros] = useState<LivroResponse[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [activeTab, setActiveTab] = useState<MediaType>("revista")
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [filterValues, setFilterValues] = useState<FilterValues>({})
  const [formData, setFormData] = useState<any>({})
  const { toast } = useToast()

  const filterConfig: FilterConfig[] = [
    {
      key: "data_publicacao",
      label: "Data de Publicação",
      type: "dateRange",
    },
    {
      key: "editora_publicadora",
      label: "Editora/Publicadora",
      type: "text",
      placeholder: "Nome da editora ou publicadora",
    },
  ]

  useEffect(() => {
    fetchMediaByType()
  }, [currentPage, activeTab])

  const fetchMediaByType = async () => {
    try {
      setLoading(true)
      const skip = (currentPage - 1) * ITEMS_PER_PAGE

      let response
      switch (activeTab) {
        case "revista":
          response = await revistasAPI.getAll(skip, ITEMS_PER_PAGE)
          setRevistas(response.data)
          break
        case "dvd":
          response = await dvdsAPI.getAll(skip, ITEMS_PER_PAGE)
          setDvds(response.data)
          break
        case "artigo":
          response = await artigosAPI.getAll(skip, ITEMS_PER_PAGE)
          setArtigos(response.data)
          break
        case "livro":
          response = await livrosAPI.getAll(skip, ITEMS_PER_PAGE)
          setLivros(response.data)
          break
      }

      // Calculate total pages based on returned data
      setTotalPages(
        response.data.length === ITEMS_PER_PAGE
          ? currentPage + 1
          : Math.max(1, Math.ceil(((currentPage - 1) * ITEMS_PER_PAGE + response.data.length) / ITEMS_PER_PAGE)),
      )
    } catch (error) {
      console.error("Error fetching media:", error)
      toast({
        title: "Erro ao carregar mídias",
        description: "Não foi possível carregar a lista de mídias.",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const searchMedia = async (query: string) => {
    if (!query.trim()) {
      fetchMediaByType()
      return
    }

    try {
      setLoading(true)
      let response
      switch (activeTab) {
        case "revista":
          response = await revistasAPI.search(query)
          setRevistas(response.data)
          break
        case "dvd":
          response = await dvdsAPI.search(query)
          setDvds(response.data)
          break
        case "artigo":
          response = await artigosAPI.search(query)
          setArtigos(response.data)
          break
        case "livro":
          response = await livrosAPI.search(query)
          setLivros(response.data)
          break
      }
      setTotalPages(1) // Search results are typically on one page
      setCurrentPage(1)
    } catch (error) {
      console.error("Error searching media:", error)
      toast({
        title: "Erro na busca",
        description: error.response.data.detail,
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    searchMedia(searchTerm)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)

    try {
      let response
      switch (activeTab) {
        case "revista":
          const revistaData: RevistaCreate = {
            titulo: formData.titulo,
            ISSN: formData.ISSN || null,
            periodicidade: formData.periodicidade || null,
            editora: formData.editora || null,
            data_publicacao: formData.data_publicacao || null,
          }
          response = await revistasAPI.create(revistaData)
          setRevistas([...revistas, response.data])
          break
        case "dvd":
          const dvdData: DVDCreate = {
            titulo: formData.titulo,
            ISAN: formData.ISAN || null,
            duracao: formData.duracao || null,
            distribuidora: formData.distribuidora || null,
            data_lancamento: formData.data_lancamento || null,
          }
          response = await dvdsAPI.create(dvdData)
          setDvds([...dvds, response.data])
          break
        case "artigo":
          const artigoData: ArtigoCreate = {
            titulo: formData.titulo,
            DOI: formData.DOI || null,
            publicadora: formData.publicadora || null,
            data_publicacao: formData.data_publicacao || null,
          }
          response = await artigosAPI.create(artigoData)
          setArtigos([...artigos, response.data])
          break
        case "livro":
          const livroData: LivroCreate = {
            titulo: formData.titulo,
            ISBN: formData.ISBN || null,
            editora: formData.editora || null,
            data_publicacao: formData.data_publicacao || null,
            numero_paginas: formData.numero_paginas || null,
          }
          response = await livrosAPI.create(livroData)
          setLivros([...livros, response.data])
          break
      }

      toast({
        title: "Mídia criada",
        description: "Nova mídia foi cadastrada com sucesso.",
      })

      setIsDialogOpen(false)
      setFormData({})
    } catch (error) {
      console.error("Error saving media:", error)
      toast({
        title: "Erro ao salvar mídia",
        description: error.response.data.detail,
        variant: "destructive",
      })
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (id: number, type: MediaType) => {
    try {
      switch (type) {
        case "revista":
          await revistasAPI.delete(id)
          setRevistas(revistas.filter((r) => r.id_revista !== id))
          break
        case "dvd":
          await dvdsAPI.delete(id)
          setDvds(dvds.filter((d) => d.id_dvd !== id))
          break
        case "artigo":
          await artigosAPI.delete(id)
          setArtigos(artigos.filter((a) => a.id_artigo !== id))
          break
        case "livro":
          await livrosAPI.delete(id)
          setLivros(livros.filter((l) => l.id_livro !== id))
          break
      }

      toast({
        title: "Mídia removida",
        description: "A mídia foi removida com sucesso.",
      })
    } catch (error) {
      console.error("Error deleting media:", error)
      toast({
        title: "Erro ao remover mídia",
        description: error.response.data.detail ,
        variant: "destructive",
      })
    }
  }

  const renderMediaForm = () => {
    switch (activeTab) {
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
              <Label htmlFor="ISSN" className="text-right">
                ISSN
              </Label>
              <Input
                id="ISSN"
                value={formData.ISSN || ""}
                onChange={(e) => setFormData({ ...formData, ISSN: e.target.value })}
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
              <Label htmlFor="ISAN" className="text-right">
                ISAN
              </Label>
              <Input
                id="ISAN"
                value={formData.ISAN || ""}
                onChange={(e) => setFormData({ ...formData, ISAN: e.target.value })}
                className="col-span-3"
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
              <Label htmlFor="distribuidora" className="text-right">
                Distribuidora
              </Label>
              <Input
                id="distribuidora"
                value={formData.distribuidora || ""}
                onChange={(e) => setFormData({ ...formData, distribuidora: e.target.value })}
                className="col-span-3"
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
              <Label htmlFor="DOI" className="text-right">
                DOI
              </Label>
              <Input
                id="DOI"
                value={formData.DOI || ""}
                onChange={(e) => setFormData({ ...formData, DOI: e.target.value })}
                className="col-span-3"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="publicadora" className="text-right">
                Publicadora
              </Label>
              <Input
                id="publicadora"
                value={formData.publicadora || ""}
                onChange={(e) => setFormData({ ...formData, publicadora: e.target.value })}
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
              <Label htmlFor="numero_paginas" className="text-right">
                Nº Páginas
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
    }
  }

  const renderMediaTable = (items: MediaItem[], type: MediaType) => {
    const Icon = tipoMidiaIcons[type]

    return (
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>ID</TableHead>
            <TableHead>Título</TableHead>
            <TableHead>Detalhes</TableHead>
            <TableHead>Data</TableHead>
            <TableHead className="text-right">Ações</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {items.map((item) => {
            let id: number
            let details = ""
            let date = ""

            if ("id_revista" in item) {
              id = item.id_revista
              details = item.editora || ""
              date = item.data_publicacao || ""
            } else if ("id_dvd" in item) {
              id = item.id_dvd
              details = item.distribuidora || ""
              date = item.data_lancamento || ""
            } else if ("id_artigo" in item) {
              id = item.id_artigo
              details = item.publicadora || ""
              date = item.data_publicacao || ""
            } else {
              id = item.id_livro
              details = item.editora || ""
              date = item.data_publicacao || ""
            }

            return (
              <TableRow key={id}>
                <TableCell className="font-medium">{id}</TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <Badge className={tipoMidiaColors[type]}>
                      <Icon className="w-3 h-3 mr-1" />
                      {type}
                    </Badge>
                    {item.titulo}
                  </div>
                </TableCell>
                <TableCell>{details}</TableCell>
                <TableCell>{date ? new Date(date).toLocaleDateString("pt-BR") : "-"}</TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-2">
                    <Button variant="outline" size="sm">
                      <Edit className="w-4 h-4" />
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => handleDelete(id, type)}>
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            )
          })}
        </TableBody>
      </Table>
    )
  }

  const getCurrentItems = () => {
    switch (activeTab) {
      case "revista":
        return revistas
      case "dvd":
        return dvds
      case "artigo":
        return artigos
      case "livro":
        return livros
      default:
        return []
    }
  }

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
  }

  const handleApplyFilters = () => {
    setCurrentPage(1)
    fetchMediaByType()
  }

  const handleClearFilters = () => {
    setFilterValues({})
    setCurrentPage(1)
    fetchMediaByType()
  }

  const handleTabChange = (value: string) => {
    setActiveTab(value as MediaType)
    setCurrentPage(1)
    setSearchTerm("")
  }

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
        <div className="flex gap-2">
          <AdvancedFilters
            filters={filterConfig}
            values={filterValues}
            onValuesChange={setFilterValues}
            onApply={handleApplyFilters}
            onClear={handleClearFilters}
          />
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button className="onix-gradient">
                <Plus className="mr-2 h-4 w-4" />
                Nova Mídia
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[500px] max-h-[80vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Nova {activeTab}</DialogTitle>
                <DialogDescription>Preencha os dados para cadastrar uma nova {activeTab}.</DialogDescription>
              </DialogHeader>
              <form onSubmit={handleSubmit}>
                <div className="grid gap-4 py-4">{renderMediaForm()}</div>
                <DialogFooter>
                  <Button type="submit" className="onix-gradient" disabled={submitting}>
                    {submitting ? "Salvando..." : "Cadastrar"}
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Revistas</CardTitle>
            <Newspaper className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{revistas.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">DVDs</CardTitle>
            <Disc className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dvds.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Artigos</CardTitle>
            <FileText className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{artigos.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Livros</CardTitle>
            <BookOpen className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{livros.length}</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Acervo de Mídias</CardTitle>
          <CardDescription>
            Página {currentPage} de {totalPages} - {getCurrentItems().length} mídias na página atual
          </CardDescription>
          <form onSubmit={handleSearch} className="flex items-center space-x-2">
            <Search className="w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Buscar mídias..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="max-w-sm"
            />
            <Button type="submit" variant="outline" size="sm">
              Buscar
            </Button>
            {searchTerm && (
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => {
                  setSearchTerm("")
                  fetchMediaByType()
                }}
              >
                Limpar
              </Button>
            )}
          </form>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={handleTabChange}>
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="revista">Revistas</TabsTrigger>
              <TabsTrigger value="dvd">DVDs</TabsTrigger>
              <TabsTrigger value="artigo">Artigos</TabsTrigger>
              <TabsTrigger value="livro">Livros</TabsTrigger>
            </TabsList>
            <TabsContent value="revista" className="mt-4">
              {renderMediaTable(revistas, "revista")}
            </TabsContent>
            <TabsContent value="dvd" className="mt-4">
              {renderMediaTable(dvds, "dvd")}
            </TabsContent>
            <TabsContent value="artigo" className="mt-4">
              {renderMediaTable(artigos, "artigo")}
            </TabsContent>
            <TabsContent value="livro" className="mt-4">
              {renderMediaTable(livros, "livro")}
            </TabsContent>
          </Tabs>

          <div className="mt-4">
            <Pagination currentPage={currentPage} totalPages={totalPages} onPageChange={handlePageChange} />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
