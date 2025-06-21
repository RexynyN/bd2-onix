"use client"

import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { useEffect, useState } from "react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useToast } from "@/hooks/use-toast"
import { Search } from "lucide-react"
import {
  estoqueAPI,
  bibliotecasAPI,
  revistasAPI,
  dvdsAPI,
  artigosAPI,
  livrosAPI,
  type Estoque,
  type EstoqueCreate,
  type EstoqueUpdate,
  type BibliotecaResponse,
  type EstoqueWithNames,
} from "@/lib/api"
import { Pagination } from "@/components/pagination"
import { SearchableSelect } from "@/components/searchable-select"
import { AdvancedFilters, type FilterConfig, type FilterValues } from "@/components/advanced-filters"

const ITEMS_PER_PAGE = 10

export default function EstoquePage() {
  const [estoques, setEstoques] = useState<EstoqueWithNames[]>([])
  const [allEstoques, setAllEstoques] = useState<EstoqueWithNames[]>([])
  const [bibliotecas, setBibliotecas] = useState<BibliotecaResponse[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [formData, setFormData] = useState({
    condicao: "",
    id_titulo: "",
    id_biblioteca: "",
  })
  const [editingEstoque, setEditingEstoque] = useState<Estoque | null>(null)
  const [loading, setLoading] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalEstoques, setTotalEstoques] = useState(0)
  const [filterValues, setFilterValues] = useState<FilterValues>({})
  const { toast } = useToast()

  const filterConfig: FilterConfig[] = [
    {
      key: "condicao",
      label: "Condição",
      type: "select",
      options: [
        { value: "novo", label: "Novo" },
        { value: "usado", label: "Usado" },
        { value: "danificado", label: "Danificado" },
        { value: "perdido", label: "Perdido" },
      ],
      placeholder: "Todas as condições",
    },
    {
      key: "biblioteca",
      label: "Biblioteca",
      type: "select",
      options: bibliotecas.map((bib) => ({ value: bib.id_biblioteca.toString(), label: bib.nome })),
      placeholder: "Todas as bibliotecas",
    },
    {
      key: "tipo_midia",
      label: "Tipo de Mídia",
      type: "select",
      options: [
        { value: "revista", label: "Revista" },
        { value: "dvd", label: "DVD" },
        { value: "artigo", label: "Artigo" },
        { value: "livro", label: "Livro" },
      ],
      placeholder: "Todos os tipos",
    },
  ]

  useEffect(() => {
    fetchEstoques()
    fetchBibliotecas()
  }, [currentPage])

  useEffect(() => {
    applySearchAndFilters()
  }, [searchTerm, allEstoques, filterValues])

  const fetchEstoques = async () => {
    try {
      setLoading(true)
      const skip = (currentPage - 1) * ITEMS_PER_PAGE
      const response = await estoqueAPI.getAll(skip, ITEMS_PER_PAGE)

      // Enhance estoque data with names
      const enhancedEstoques = await Promise.all(
        response.data.map(async (estoque) => {
          const enhanced: EstoqueWithNames = { ...estoque }

          // Try to get title name from different media types
          try {
            const revista = await revistasAPI.getById(estoque.id_titulo)
            enhanced.titulo_nome = revista.data.titulo
          } catch {
            try {
              const dvd = await dvdsAPI.getById(estoque.id_titulo)
              enhanced.titulo_nome = dvd.data.titulo
            } catch {
              try {
                const artigo = await artigosAPI.getById(estoque.id_titulo)
                enhanced.titulo_nome = artigo.data.titulo
              } catch {
                try {
                  const livro = await livrosAPI.getById(estoque.id_titulo)
                  enhanced.titulo_nome = livro.data.titulo
                } catch {
                  enhanced.titulo_nome = `Título ID: ${estoque.id_titulo}`
                }
              }
            }
          }

          // Get biblioteca name
          try {
            const biblioteca = await bibliotecasAPI.getById(estoque.id_biblioteca)
            enhanced.biblioteca_nome = biblioteca.data.nome
          } catch {
            enhanced.biblioteca_nome = `Biblioteca ID: ${estoque.id_biblioteca}`
          }

          return enhanced
        }),
      )

      setAllEstoques(enhancedEstoques)
      setTotalEstoques(
        response.data.length === ITEMS_PER_PAGE
          ? currentPage * ITEMS_PER_PAGE + 1
          : (currentPage - 1) * ITEMS_PER_PAGE + response.data.length,
      )
    } catch (error) {
      console.error("Error fetching estoques:", error)
      toast({
        title: "Erro ao carregar estoque",
        description: error.response.data.detail,
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const applySearchAndFilters = () => {
    let filteredEstoques = [...allEstoques]

    // Apply search filter
    if (searchTerm) {
      filteredEstoques = filteredEstoques.filter(
        (estoque) =>
          estoque.titulo_nome?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          estoque.biblioteca_nome?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          estoque.condicao?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          estoque.id_estoque.toString().includes(searchTerm),
      )
    }

    // Apply advanced filters
    if (filterValues.condicao && filterValues.condicao !== "all") {
      filteredEstoques = filteredEstoques.filter((e) =>
        e.condicao?.toLowerCase().includes(filterValues.condicao.toLowerCase()),
      )
    }
    if (filterValues.biblioteca && filterValues.biblioteca !== "all") {
      filteredEstoques = filteredEstoques.filter((e) => e.id_biblioteca.toString() === filterValues.biblioteca)
    }

    setEstoques(filteredEstoques)
  }

  const fetchBibliotecas = async () => {
    try {
      const response = await bibliotecasAPI.getAll()
      setBibliotecas(response.data.data)
    } catch (error) {
      console.error("Error fetching bibliotecas:", error)
    }
  }

  const handleChange = (e: any) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e: any) => {
    e.preventDefault()

    try {
      if (editingEstoque) {
        const estoqueData: EstoqueUpdate = {
          condicao: formData.condicao || null,
          id_titulo: Number.parseInt(formData.id_titulo) || null,
          id_biblioteca: Number.parseInt(formData.id_biblioteca) || null,
        }
        await estoqueAPI.update(editingEstoque.id_estoque, estoqueData)
      } else {
        const estoqueData: EstoqueCreate = {
          condicao: formData.condicao || null,
          id_titulo: Number.parseInt(formData.id_titulo),
          id_biblioteca: Number.parseInt(formData.id_biblioteca),
        }
        await estoqueAPI.create(estoqueData)
      }

      setFormData({ condicao: "", id_titulo: "", id_biblioteca: "" })
      setEditingEstoque(null)
      fetchEstoques()

      toast({
        title: editingEstoque ? "Estoque atualizado" : "Estoque criado",
        description: editingEstoque ? "Item do estoque atualizado com sucesso." : "Novo item adicionado ao estoque.",
      })
    } catch (error) {
      console.error("Error saving estoque:", error)
      toast({
        title: "Erro ao salvar estoque",
        description: error.response.data.detail,
        variant: "destructive",
      })
    }
  }

  const handleEdit = (estoque: Estoque) => {
    setFormData({
      condicao: estoque.condicao || "",
      id_titulo: estoque.id_titulo.toString(),
      id_biblioteca: estoque.id_biblioteca.toString(),
    })
    setEditingEstoque(estoque)
  }

  const handleDelete = async (id: number) => {
    try {
      await estoqueAPI.delete(id)
      fetchEstoques()
      toast({
        title: "Item removido",
        description: "O item foi removido do estoque.",
      })
    } catch (error) {
      console.error("Error deleting estoque:", error)
      toast({
        title: "Erro ao remover item",
        description: error.response.data.detail,
        variant: "destructive",
      })
    }
  }

  const handleApplyFilters = () => {
    setCurrentPage(1)
    applySearchAndFilters()
  }

  const handleClearFilters = () => {
    setFilterValues({})
    setSearchTerm("")
    setCurrentPage(1)
    applySearchAndFilters()
  }

  const totalPages = Math.ceil(totalEstoques / ITEMS_PER_PAGE)

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
  }

  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <SidebarTrigger />
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Estoque</h2>
            <p className="text-muted-foreground">Gerencie o estoque da biblioteca</p>
          </div>
        </div>
        <AdvancedFilters
          filters={filterConfig}
          values={filterValues}
          onValuesChange={setFilterValues}
          onApply={handleApplyFilters}
          onClear={handleClearFilters}
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{editingEstoque ? "Editar Item do Estoque" : "Adicionar Item ao Estoque"}</CardTitle>
          <CardDescription>
            {editingEstoque ? "Atualize as informações do item." : "Preencha os dados para adicionar um novo item."}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="condicao">Condição</Label>
                <Input
                  type="text"
                  id="condicao"
                  name="condicao"
                  value={formData.condicao}
                  onChange={handleChange}
                  placeholder="Ex: Novo, Usado, Danificado"
                />
              </div>
              <div>
                <Label htmlFor="id_titulo">Título</Label>
                <SearchableSelect
                  type="titles"
                  value={formData.id_titulo}
                  onValueChange={(value) => setFormData({ ...formData, id_titulo: value })}
                  placeholder="Selecione um título..."
                  searchPlaceholder="Buscar por título..."
                  className="w-full"
                />
              </div>
              <div>
                <Label htmlFor="id_biblioteca">Biblioteca</Label>
                <Select
                  value={formData.id_biblioteca}
                  onValueChange={(value) => setFormData({ ...formData, id_biblioteca: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione a Biblioteca" />
                  </SelectTrigger>
                  <SelectContent>
                    {bibliotecas.map((biblioteca) => (
                      <SelectItem key={biblioteca.id_biblioteca} value={biblioteca.id_biblioteca.toString()}>
                        {biblioteca.nome}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="flex gap-2">
              <Button type="submit">{editingEstoque ? "Atualizar Estoque" : "Adicionar Estoque"}</Button>
              {editingEstoque && (
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => {
                    setEditingEstoque(null)
                    setFormData({ condicao: "", id_titulo: "", id_biblioteca: "" })
                  }}
                >
                  Cancelar Edição
                </Button>
              )}
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Itens do Estoque</CardTitle>
          <CardDescription>
            Página {currentPage} de {totalPages} - {estoques.length} itens exibidos de {totalEstoques} total
          </CardDescription>
          <div className="flex items-center space-x-2">
            <Search className="w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Buscar por título, biblioteca, condição ou ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="max-w-sm"
            />
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableCaption>Lista de itens no estoque da biblioteca.</TableCaption>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[100px]">ID</TableHead>
                <TableHead>Condição</TableHead>
                <TableHead>Título</TableHead>
                <TableHead>Biblioteca</TableHead>
                <TableHead className="text-right">Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center">
                    Carregando...
                  </TableCell>
                </TableRow>
              ) : estoques.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center">
                    {searchTerm || Object.values(filterValues).some((v) => v && v !== "all")
                      ? "Nenhum item encontrado com os filtros aplicados."
                      : "Nenhum item no estoque."}
                  </TableCell>
                </TableRow>
              ) : (
                estoques.map((estoque) => (
                  <TableRow key={estoque.id_estoque}>
                    <TableCell className="font-medium">{estoque.id_estoque}</TableCell>
                    <TableCell>{estoque.condicao || "-"}</TableCell>
                    <TableCell>
                      <div>
                        <div className="font-medium">{estoque.titulo_nome}</div>
                        <div className="text-sm text-muted-foreground">ID: {estoque.id_titulo}</div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div>
                        <div className="font-medium">{estoque.biblioteca_nome}</div>
                        <div className="text-sm text-muted-foreground">ID: {estoque.id_biblioteca}</div>
                      </div>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button variant="secondary" size="sm" onClick={() => handleEdit(estoque)}>
                          Editar
                        </Button>
                        <Button variant="destructive" size="sm" onClick={() => handleDelete(estoque.id_estoque)}>
                          Excluir
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>

          <div className="mt-4">
            <Pagination currentPage={currentPage} totalPages={totalPages} onPageChange={handlePageChange} />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
