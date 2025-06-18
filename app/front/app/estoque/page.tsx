"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Plus, Search, Edit, Trash2, Package, Building2 } from "lucide-react"
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
import { estoqueAPI, bibliotecasAPI, type Estoque, type Biblioteca } from "@/lib/api"

const condicaoColors = {
  Novo: "bg-green-100 text-green-800",
  Bom: "bg-blue-100 text-blue-800",
  Regular: "bg-yellow-100 text-yellow-800",
  Ruim: "bg-red-100 text-red-800",
}

export default function EstoquePage() {
  const [estoque, setEstoque] = useState<Estoque[]>([])
  const [bibliotecas, setBibliotecas] = useState<Biblioteca[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [bibliotecaFilter, setBibliotecaFilter] = useState<string>("todas")
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [editingItem, setEditingItem] = useState<Estoque | null>(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [formData, setFormData] = useState({
    condicao: "",
    id_titulo: "",
    id_biblioteca: "",
  })
  const { toast } = useToast()

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [estoqueRes, bibliotecasRes] = await Promise.all([
        estoqueAPI.getAll(0, 1000),
        bibliotecasAPI.getAll(0, 1000),
      ])

      setEstoque(estoqueRes.data)
      setBibliotecas(bibliotecasRes.data)
    } catch (error) {
      console.error("Error fetching data:", error)
      toast({
        title: "Erro ao carregar dados",
        description: "Não foi possível carregar os dados do estoque.",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const getBibliotecaNome = (id_biblioteca: number) => {
    const biblioteca = bibliotecas.find((b) => b.id_biblioteca === id_biblioteca)
    return biblioteca?.nome || `Biblioteca ${id_biblioteca}`
  }

  const filteredEstoque = estoque.filter((item) => {
    const matchesSearch =
      item.id_estoque.toString().includes(searchTerm) ||
      item.id_titulo.toString().includes(searchTerm) ||
      item.condicao.toLowerCase().includes(searchTerm.toLowerCase())

    const matchesBiblioteca = bibliotecaFilter === "todas" || item.id_biblioteca.toString() === bibliotecaFilter

    return matchesSearch && matchesBiblioteca
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)

    try {
      const itemData = {
        condicao: formData.condicao,
        id_titulo: Number.parseInt(formData.id_titulo),
        id_biblioteca: Number.parseInt(formData.id_biblioteca),
      }

      if (editingItem) {
        const response = await estoqueAPI.update(editingItem.id_estoque, itemData)
        setEstoque(estoque.map((item) => (item.id_estoque === editingItem.id_estoque ? response.data : item)))
        toast({
          title: "Item atualizado",
          description: "O item do estoque foi atualizado com sucesso.",
        })
      } else {
        const response = await estoqueAPI.create(itemData)
        setEstoque([...estoque, response.data])
        toast({
          title: "Item adicionado",
          description: "Novo item foi adicionado ao estoque.",
        })
      }

      setIsDialogOpen(false)
      setEditingItem(null)
      setFormData({ condicao: "", id_titulo: "", id_biblioteca: "" })
    } catch (error) {
      console.error("Error saving item:", error)
      toast({
        title: "Erro ao salvar item",
        description: "Não foi possível salvar o item. Tente novamente.",
        variant: "destructive",
      })
    } finally {
      setSubmitting(false)
    }
  }

  const handleEdit = (item: Estoque) => {
    setEditingItem(item)
    setFormData({
      condicao: item.condicao,
      id_titulo: item.id_titulo.toString(),
      id_biblioteca: item.id_biblioteca.toString(),
    })
    setIsDialogOpen(true)
  }

  const handleDelete = async (id: number) => {
    try {
      await estoqueAPI.delete(id)
      setEstoque(estoque.filter((item) => item.id_estoque !== id))
      toast({
        title: "Item removido",
        description: "O item foi removido do estoque.",
      })
    } catch (error) {
      console.error("Error deleting item:", error)
      toast({
        title: "Erro ao remover item",
        description: "Não foi possível remover o item. Verifique se não há empréstimos ativos.",
        variant: "destructive",
      })
    }
  }

  const openNewItemDialog = () => {
    setEditingItem(null)
    setFormData({ condicao: "", id_titulo: "", id_biblioteca: "" })
    setIsDialogOpen(true)
  }

  const getEstoquePorBiblioteca = () => {
    const stats = bibliotecas.map((biblioteca) => {
      const itens = estoque.filter((item) => item.id_biblioteca === biblioteca.id_biblioteca)
      return {
        biblioteca: biblioteca.nome,
        total: itens.length,
        novo: itens.filter((item) => item.condicao === "Novo").length,
        bom: itens.filter((item) => item.condicao === "Bom").length,
        regular: itens.filter((item) => item.condicao === "Regular").length,
        ruim: itens.filter((item) => item.condicao === "Ruim").length,
      }
    })
    return stats
  }

  if (loading) {
    return (
      <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
        <div className="flex items-center gap-4">
          <SidebarTrigger />
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Estoque</h2>
            <p className="text-muted-foreground">Carregando...</p>
          </div>
        </div>
        <Card>
          <CardContent className="p-6">
            <div className="text-center">Carregando estoque...</div>
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
            <h2 className="text-3xl font-bold tracking-tight">Estoque</h2>
            <p className="text-muted-foreground">Gerencie o estoque das bibliotecas</p>
          </div>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={openNewItemDialog} className="onix-gradient">
              <Plus className="mr-2 h-4 w-4" />
              Adicionar Item
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>{editingItem ? "Editar Item" : "Adicionar Item ao Estoque"}</DialogTitle>
              <DialogDescription>
                {editingItem
                  ? "Atualize as informações do item."
                  : "Preencha os dados para adicionar um novo item ao estoque."}
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit}>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="id_titulo" className="text-right">
                    ID do Título
                  </Label>
                  <Input
                    id="id_titulo"
                    type="number"
                    value={formData.id_titulo}
                    onChange={(e) => setFormData({ ...formData, id_titulo: e.target.value })}
                    className="col-span-3"
                    required
                    disabled={submitting}
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="id_biblioteca" className="text-right">
                    Biblioteca
                  </Label>
                  <Select
                    value={formData.id_biblioteca}
                    onValueChange={(value) => setFormData({ ...formData, id_biblioteca: value })}
                    required
                    disabled={submitting}
                  >
                    <SelectTrigger className="col-span-3">
                      <SelectValue placeholder="Selecione a biblioteca" />
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
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="condicao" className="text-right">
                    Condição
                  </Label>
                  <Select
                    value={formData.condicao}
                    onValueChange={(value) => setFormData({ ...formData, condicao: value })}
                    required
                    disabled={submitting}
                  >
                    <SelectTrigger className="col-span-3">
                      <SelectValue placeholder="Selecione a condição" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Novo">Novo</SelectItem>
                      <SelectItem value="Bom">Bom</SelectItem>
                      <SelectItem value="Regular">Regular</SelectItem>
                      <SelectItem value="Ruim">Ruim</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <DialogFooter>
                <Button type="submit" className="onix-gradient" disabled={submitting}>
                  {submitting ? "Salvando..." : editingItem ? "Atualizar" : "Adicionar"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Estatísticas por biblioteca */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {getEstoquePorBiblioteca().map((stat, index) => (
          <Card key={index} className="hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <div className="flex items-center gap-2">
                <Building2 className="h-5 w-5 text-blue-600" />
                <CardTitle className="text-lg">{stat.biblioteca}</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold mb-2">{stat.total} itens</div>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div className="flex justify-between">
                  <span>Novo:</span>
                  <span className="font-medium text-green-600">{stat.novo}</span>
                </div>
                <div className="flex justify-between">
                  <span>Bom:</span>
                  <span className="font-medium text-blue-600">{stat.bom}</span>
                </div>
                <div className="flex justify-between">
                  <span>Regular:</span>
                  <span className="font-medium text-yellow-600">{stat.regular}</span>
                </div>
                <div className="flex justify-between">
                  <span>Ruim:</span>
                  <span className="font-medium text-red-600">{stat.ruim}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Itens do Estoque</CardTitle>
          <CardDescription>{estoque.length} itens cadastrados</CardDescription>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Search className="w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Buscar itens..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="max-w-sm"
              />
            </div>
            <Select value={bibliotecaFilter} onValueChange={setBibliotecaFilter}>
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="Filtrar por biblioteca" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="todas">Todas as bibliotecas</SelectItem>
                {bibliotecas.map((biblioteca) => (
                  <SelectItem key={biblioteca.id_biblioteca} value={biblioteca.id_biblioteca.toString()}>
                    {biblioteca.nome}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent>
          {estoque.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Package className="mx-auto h-12 w-12 mb-4 opacity-50" />
              <p>Nenhum item no estoque ainda.</p>
              <p className="text-sm">Clique em "Adicionar Item" para começar.</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID Estoque</TableHead>
                  <TableHead>ID Título</TableHead>
                  <TableHead>Biblioteca</TableHead>
                  <TableHead>Condição</TableHead>
                  <TableHead className="text-right">Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredEstoque.map((item) => (
                  <TableRow key={item.id_estoque}>
                    <TableCell className="font-medium">{item.id_estoque}</TableCell>
                    <TableCell>{item.id_titulo}</TableCell>
                    <TableCell>{getBibliotecaNome(item.id_biblioteca)}</TableCell>
                    <TableCell>
                      <Badge
                        className={
                          condicaoColors[item.condicao as keyof typeof condicaoColors] || "bg-gray-100 text-gray-800"
                        }
                      >
                        {item.condicao}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button variant="outline" size="sm" onClick={() => handleEdit(item)}>
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button variant="outline" size="sm" onClick={() => handleDelete(item.id_estoque)}>
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
