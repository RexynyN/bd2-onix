"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Plus, Search, Edit, Trash2, Building2 } from "lucide-react"
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

interface Biblioteca {
  id_biblioteca: number
  nome: string
  endereco: string
}

export default function BibliotecasPage() {
  const [bibliotecas, setBibliotecas] = useState<Biblioteca[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [editingBiblioteca, setEditingBiblioteca] = useState<Biblioteca | null>(null)
  const [formData, setFormData] = useState({
    nome: "",
    endereco: "",
  })
  const { toast } = useToast()

  useEffect(() => {
    // Simular carregamento de dados
    setBibliotecas([
      { id_biblioteca: 1, nome: "Biblioteca Central", endereco: "Av. Principal, 1000" },
      { id_biblioteca: 2, nome: "Biblioteca Norte", endereco: "Rua Norte, 500" },
      { id_biblioteca: 3, nome: "Biblioteca Sul", endereco: "Rua Sul, 300" },
      { id_biblioteca: 4, nome: "Biblioteca Infantil", endereco: "Praça das Crianças, 100" },
      { id_biblioteca: 5, nome: "Biblioteca Universitária", endereco: "Campus Universitário, s/n" },
    ])
  }, [])

  const filteredBibliotecas = bibliotecas.filter(
    (biblioteca) =>
      biblioteca.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
      biblioteca.endereco.toLowerCase().includes(searchTerm.toLowerCase()),
  )

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (editingBiblioteca) {
      // Atualizar biblioteca
      setBibliotecas(
        bibliotecas.map((b) =>
          b.id_biblioteca === editingBiblioteca.id_biblioteca ? { ...editingBiblioteca, ...formData } : b,
        ),
      )
      toast({
        title: "Biblioteca atualizada",
        description: "Os dados da biblioteca foram atualizados com sucesso.",
      })
    } else {
      // Criar nova biblioteca
      const newBiblioteca: Biblioteca = {
        id_biblioteca: Math.max(...bibliotecas.map((b) => b.id_biblioteca)) + 1,
        ...formData,
      }
      setBibliotecas([...bibliotecas, newBiblioteca])
      toast({
        title: "Biblioteca criada",
        description: "Nova biblioteca foi cadastrada com sucesso.",
      })
    }

    setIsDialogOpen(false)
    setEditingBiblioteca(null)
    setFormData({ nome: "", endereco: "" })
  }

  const handleEdit = (biblioteca: Biblioteca) => {
    setEditingBiblioteca(biblioteca)
    setFormData({
      nome: biblioteca.nome,
      endereco: biblioteca.endereco,
    })
    setIsDialogOpen(true)
  }

  const handleDelete = (id: number) => {
    setBibliotecas(bibliotecas.filter((b) => b.id_biblioteca !== id))
    toast({
      title: "Biblioteca removida",
      description: "A biblioteca foi removida do sistema.",
      variant: "destructive",
    })
  }

  const openNewBibliotecaDialog = () => {
    setEditingBiblioteca(null)
    setFormData({ nome: "", endereco: "" })
    setIsDialogOpen(true)
  }

  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <SidebarTrigger />
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Bibliotecas</h2>
            <p className="text-muted-foreground">Gerencie as unidades do sistema</p>
          </div>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={openNewBibliotecaDialog} className="onix-gradient">
              <Plus className="mr-2 h-4 w-4" />
              Nova Biblioteca
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>{editingBiblioteca ? "Editar Biblioteca" : "Nova Biblioteca"}</DialogTitle>
              <DialogDescription>
                {editingBiblioteca
                  ? "Atualize as informações da biblioteca."
                  : "Preencha os dados para cadastrar uma nova biblioteca."}
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit}>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="nome" className="text-right">
                    Nome
                  </Label>
                  <Input
                    id="nome"
                    value={formData.nome}
                    onChange={(e) => setFormData({ ...formData, nome: e.target.value })}
                    className="col-span-3"
                    required
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="endereco" className="text-right">
                    Endereço
                  </Label>
                  <Input
                    id="endereco"
                    value={formData.endereco}
                    onChange={(e) => setFormData({ ...formData, endereco: e.target.value })}
                    className="col-span-3"
                    required
                  />
                </div>
              </div>
              <DialogFooter>
                <Button type="submit" className="onix-gradient">
                  {editingBiblioteca ? "Atualizar" : "Cadastrar"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filteredBibliotecas.map((biblioteca) => (
          <Card key={biblioteca.id_biblioteca} className="hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <div className="flex items-center gap-2">
                <Building2 className="h-5 w-5 text-blue-600" />
                <CardTitle className="text-lg">{biblioteca.nome}</CardTitle>
              </div>
              <div className="flex gap-1">
                <Button variant="outline" size="sm" onClick={() => handleEdit(biblioteca)}>
                  <Edit className="w-4 h-4" />
                </Button>
                <Button variant="outline" size="sm" onClick={() => handleDelete(biblioteca.id_biblioteca)}>
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">{biblioteca.endereco}</p>
              <div className="mt-4 flex justify-between text-sm">
                <span>ID: {biblioteca.id_biblioteca}</span>
                <span className="text-green-600 font-medium">Ativa</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Buscar Bibliotecas</CardTitle>
          <div className="flex items-center space-x-2">
            <Search className="w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Buscar por nome ou endereço..."
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
                <TableHead>Nome</TableHead>
                <TableHead>Endereço</TableHead>
                <TableHead className="text-right">Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredBibliotecas.map((biblioteca) => (
                <TableRow key={biblioteca.id_biblioteca}>
                  <TableCell className="font-medium">{biblioteca.id_biblioteca}</TableCell>
                  <TableCell>{biblioteca.nome}</TableCell>
                  <TableCell>{biblioteca.endereco}</TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button variant="outline" size="sm" onClick={() => handleEdit(biblioteca)}>
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => handleDelete(biblioteca.id_biblioteca)}>
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
