"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Plus, Search, Package, AlertCircle, CheckCircle } from "lucide-react"
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

interface ItemEstoque {
  id_estoque: number
  condicao: "novo" | "bom" | "regular" | "ruim"
  id_titulo: number
  id_biblioteca: number
  titulo_midia: string
  tipo_midia: string
  biblioteca_nome: string
  disponivel: boolean
}

const condicaoColors = {
  novo: "bg-green-100 text-green-800",
  bom: "bg-blue-100 text-blue-800",
  regular: "bg-yellow-100 text-yellow-800",
  ruim: "bg-red-100 text-red-800",
}

export default function EstoquePage() {
  const [estoque, setEstoque] = useState<ItemEstoque[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [bibliotecaFilter, setBibliotecaFilter] = useState<string>("todas")
  const [condicaoFilter, setCondicaoFilter] = useState<string>("todas")
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [formData, setFormData] = useState({
    condicao: "",
    id_titulo: "",
    id_biblioteca: "",
  })
  const { toast } = useToast()

  useEffect(() => {
    // Simular carregamento de dados
    setEstoque([
      {
        id_estoque: 1,
        condicao: "novo",
        id_titulo: 1,
        id_biblioteca: 1,
        titulo_midia: "Dom Casmurro",
        tipo_midia: "livro",
        biblioteca_nome: "Biblioteca Central",
        disponivel: true,
      },
      {
        id_estoque: 2,
        condicao: "bom",
        id_titulo: 2,
        id_biblioteca: 1,
        titulo_midia: "National Geographic Brasil",
        tipo_midia: "revista",
        biblioteca_nome: "Biblioteca Central",
        disponivel: false,
      },
      {
        id_estoque: 3,
        condicao: "regular",
        id_titulo: 3,
        id_biblioteca: 2,
        titulo_midia: "Cidade de Deus",
        tipo_midia: "dvd",
        biblioteca_nome: "Biblioteca Norte",
        disponivel: true,
      },
      {
        id_estoque: 4,
        condicao: "novo",
        id_titulo: 1,
        id_biblioteca: 2,
        titulo_midia: "Dom Casmurro",
        tipo_midia: "livro",
        biblioteca_nome: "Biblioteca Norte",
        disponivel: true,
      },
      {
        id_estoque: 5,
        condicao: "ruim",
        id_titulo: 4,
        id_biblioteca: 3,
        titulo_midia: "Artigo IA na Educação",
        tipo_midia: "artigo",
        biblioteca_nome: "Biblioteca Sul",
        disponivel: true,
      },
    ])
  }, [])

  const filteredEstoque = estoque.filter((item) => {
    const matchesSearch =
      item.titulo_midia.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.biblioteca_nome.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesBiblioteca = bibliotecaFilter === "todas" || item.biblioteca_nome === bibliotecaFilter
    const matchesCondicao = condicaoFilter === "todas" || item.condicao === condicaoFilter
    return matchesSearch && matchesBiblioteca && matchesCondicao
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    const newItem: ItemEstoque = {
      id_estoque: Math.max(...estoque.map((e) => e.id_estoque)) + 1,
      condicao: formData.condicao as any,
      id_titulo: Number.parseInt(formData.id_titulo),
      id_biblioteca: Number.parseInt(formData.id_biblioteca),
      titulo_midia: "Mídia " + formData.id_titulo, // Simulado
      tipo_midia: "livro", // Simulado
      biblioteca_nome: "Biblioteca " + formData.id_biblioteca, // Simulado
      disponivel: true,
    }

    setEstoque([...estoque, newItem])
    toast({
      title: "Item adicionado ao estoque",
      description: "Novo item foi adicionado com sucesso.",
    })

    setIsDialogOpen(false)
    setFormData({ condicao: "", id_titulo: "", id_biblioteca: "" })
  }

  const bibliotecas = Array.from(new Set(estoque.map((item) => item.biblioteca_nome)))

  const estatisticas = {
    total: estoque.length,
    disponiveis: estoque.filter((item) => item.disponivel).length,
    emprestados: estoque.filter((item) => !item.disponivel).length,
    novosBons: estoque.filter((item) => item.condicao === "novo" || item.condicao === "bom").length,
  }

  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <SidebarTrigger />
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Estoque</h2>
            <p className="text-muted-foreground">Gerencie o estoque de mídias das bibliotecas</p>
          </div>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button className="onix-gradient">
              <Plus className="mr-2 h-4 w-4" />
              Adicionar ao Estoque
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>Adicionar Item ao Estoque</DialogTitle>
              <DialogDescription>Preencha os dados para adicionar um novo item ao estoque.</DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit}>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="condicao" className="text-right">
                    Condição
                  </Label>
                  <Select
                    value={formData.condicao}
                    onValueChange={(value) => setFormData({ ...formData, condicao: value })}
                    required
                  >
                    <SelectTrigger className="col-span-3">
                      <SelectValue placeholder="Selecione a condição" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="novo">Novo</SelectItem>
                      <SelectItem value="bom">Bom</SelectItem>
                      <SelectItem value="regular">Regular</SelectItem>
                      <SelectItem value="ruim">Ruim</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="id_titulo" className="text-right">
                    Título ID
                  </Label>
                  <Input
                    id="id_titulo"
                    type="number"
                    value={formData.id_titulo}
                    onChange={(e) => setFormData({ ...formData, id_titulo: e.target.value })}
                    className="col-span-3"
                    required
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="id_biblioteca" className="text-right">
                    Biblioteca ID
                  </Label>
                  <Input
                    id="id_biblioteca"
                    type="number"
                    value={formData.id_biblioteca}
                    onChange={(e) => setFormData({ ...formData, id_biblioteca: e.target.value })}
                    className="col-span-3"
                    required
                  />
                </div>
              </div>
              <DialogFooter>
                <Button type="submit" className="onix-gradient">
                  Adicionar ao Estoque
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Estatísticas do Estoque */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Itens</CardTitle>
            <Package className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{estatisticas.total}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Disponíveis</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{estatisticas.disponiveis}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Emprestados</CardTitle>
            <AlertCircle className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{estatisticas.emprestados}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Bom Estado</CardTitle>
            <Package className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">{estatisticas.novosBons}</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Itens do Estoque</CardTitle>
          <CardDescription>{estoque.length} itens no estoque total</CardDescription>
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
                <SelectItem value="todas">Todas as Bibliotecas</SelectItem>
                {bibliotecas.map((biblioteca) => (
                  <SelectItem key={biblioteca} value={biblioteca}>
                    {biblioteca}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={condicaoFilter} onValueChange={setCondicaoFilter}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Filtrar por condição" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="todas">Todas</SelectItem>
                <SelectItem value="novo">Novo</SelectItem>
                <SelectItem value="bom">Bom</SelectItem>
                <SelectItem value="regular">Regular</SelectItem>
                <SelectItem value="ruim">Ruim</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Mídia</TableHead>
                <TableHead>Biblioteca</TableHead>
                <TableHead>Condição</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Tipo</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredEstoque.map((item) => (
                <TableRow key={item.id_estoque}>
                  <TableCell className="font-medium">{item.id_estoque}</TableCell>
                  <TableCell>
                    <div>
                      <div className="font-medium">{item.titulo_midia}</div>
                      <div className="text-sm text-muted-foreground">ID Título: {item.id_titulo}</div>
                    </div>
                  </TableCell>
                  <TableCell>{item.biblioteca_nome}</TableCell>
                  <TableCell>
                    <Badge className={condicaoColors[item.condicao]}>{item.condicao}</Badge>
                  </TableCell>
                  <TableCell>
                    <Badge className={item.disponivel ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}>
                      {item.disponivel ? "Disponível" : "Emprestado"}
                    </Badge>
                  </TableCell>
                  <TableCell className="capitalize">{item.tipo_midia}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
