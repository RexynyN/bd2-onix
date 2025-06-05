"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Plus, Search, Edit, Trash2, PenTool } from "lucide-react"
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

interface Autor {
  id_autor: number
  nome: string
  data_nascimento: string
  data_falecimento?: string
}

export default function AutoresPage() {
  const [autores, setAutores] = useState<Autor[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [editingAutor, setEditingAutor] = useState<Autor | null>(null)
  const [formData, setFormData] = useState({
    nome: "",
    data_nascimento: "",
    data_falecimento: "",
  })
  const { toast } = useToast()

  useEffect(() => {
    // Simular carregamento de dados
    setAutores([
      { id_autor: 1, nome: "Machado de Assis", data_nascimento: "1839-06-21", data_falecimento: "1908-09-29" },
      { id_autor: 2, nome: "Clarice Lispector", data_nascimento: "1920-12-10", data_falecimento: "1977-12-09" },
      { id_autor: 3, nome: "Paulo Coelho", data_nascimento: "1947-08-24" },
      { id_autor: 4, nome: "José Saramago", data_nascimento: "1922-11-16", data_falecimento: "2010-06-18" },
      { id_autor: 5, nome: "Lygia Fagundes Telles", data_nascimento: "1923-04-19", data_falecimento: "2022-04-03" },
    ])
  }, [])

  const filteredAutores = autores.filter((autor) => autor.nome.toLowerCase().includes(searchTerm.toLowerCase()))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (editingAutor) {
      // Atualizar autor
      setAutores(
        autores.map((a) =>
          a.id_autor === editingAutor.id_autor
            ? {
                ...editingAutor,
                ...formData,
                data_falecimento: formData.data_falecimento || undefined,
              }
            : a,
        ),
      )
      toast({
        title: "Autor atualizado",
        description: "Os dados do autor foram atualizados com sucesso.",
      })
    } else {
      // Criar novo autor
      const newAutor: Autor = {
        id_autor: Math.max(...autores.map((a) => a.id_autor)) + 1,
        ...formData,
        data_falecimento: formData.data_falecimento || undefined,
      }
      setAutores([...autores, newAutor])
      toast({
        title: "Autor criado",
        description: "Novo autor foi cadastrado com sucesso.",
      })
    }

    setIsDialogOpen(false)
    setEditingAutor(null)
    setFormData({ nome: "", data_nascimento: "", data_falecimento: "" })
  }

  const handleEdit = (autor: Autor) => {
    setEditingAutor(autor)
    setFormData({
      nome: autor.nome,
      data_nascimento: autor.data_nascimento,
      data_falecimento: autor.data_falecimento || "",
    })
    setIsDialogOpen(true)
  }

  const handleDelete = (id: number) => {
    setAutores(autores.filter((a) => a.id_autor !== id))
    toast({
      title: "Autor removido",
      description: "O autor foi removido do sistema.",
      variant: "destructive",
    })
  }

  const openNewAutorDialog = () => {
    setEditingAutor(null)
    setFormData({ nome: "", data_nascimento: "", data_falecimento: "" })
    setIsDialogOpen(true)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("pt-BR")
  }

  const calculateAge = (nascimento: string, falecimento?: string) => {
    const birthDate = new Date(nascimento)
    const endDate = falecimento ? new Date(falecimento) : new Date()
    const age = endDate.getFullYear() - birthDate.getFullYear()
    return age
  }

  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <SidebarTrigger />
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Autores</h2>
            <p className="text-muted-foreground">Gerencie os autores do acervo</p>
          </div>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={openNewAutorDialog} className="onix-gradient">
              <Plus className="mr-2 h-4 w-4" />
              Novo Autor
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>{editingAutor ? "Editar Autor" : "Novo Autor"}</DialogTitle>
              <DialogDescription>
                {editingAutor ? "Atualize as informações do autor." : "Preencha os dados para cadastrar um novo autor."}
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
                  <Label htmlFor="data_nascimento" className="text-right">
                    Nascimento
                  </Label>
                  <Input
                    id="data_nascimento"
                    type="date"
                    value={formData.data_nascimento}
                    onChange={(e) => setFormData({ ...formData, data_nascimento: e.target.value })}
                    className="col-span-3"
                    required
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="data_falecimento" className="text-right">
                    Falecimento
                  </Label>
                  <Input
                    id="data_falecimento"
                    type="date"
                    value={formData.data_falecimento}
                    onChange={(e) => setFormData({ ...formData, data_falecimento: e.target.value })}
                    className="col-span-3"
                    placeholder="Opcional"
                  />
                </div>
              </div>
              <DialogFooter>
                <Button type="submit" className="onix-gradient">
                  {editingAutor ? "Atualizar" : "Cadastrar"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filteredAutores.map((autor) => (
          <Card key={autor.id_autor} className="hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <div className="flex items-center gap-2">
                <PenTool className="h-5 w-5 text-purple-600" />
                <CardTitle className="text-lg">{autor.nome}</CardTitle>
              </div>
              <div className="flex gap-1">
                <Button variant="outline" size="sm" onClick={() => handleEdit(autor)}>
                  <Edit className="w-4 h-4" />
                </Button>
                <Button variant="outline" size="sm" onClick={() => handleDelete(autor.id_autor)}>
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <p className="text-sm">
                  <span className="font-medium">Nascimento:</span> {formatDate(autor.data_nascimento)}
                </p>
                {autor.data_falecimento && (
                  <p className="text-sm">
                    <span className="font-medium">Falecimento:</span> {formatDate(autor.data_falecimento)}
                  </p>
                )}
                <p className="text-sm">
                  <span className="font-medium">Idade:</span>{" "}
                  {calculateAge(autor.data_nascimento, autor.data_falecimento)} anos
                  {!autor.data_falecimento && " (vivo)"}
                </p>
              </div>
              <div className="mt-4 flex justify-between text-sm">
                <span>ID: {autor.id_autor}</span>
                <span className={`font-medium ${autor.data_falecimento ? "text-gray-600" : "text-green-600"}`}>
                  {autor.data_falecimento ? "Falecido" : "Vivo"}
                </span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Buscar Autores</CardTitle>
          <div className="flex items-center space-x-2">
            <Search className="w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Buscar por nome..."
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
                <TableHead>Nascimento</TableHead>
                <TableHead>Falecimento</TableHead>
                <TableHead>Idade</TableHead>
                <TableHead className="text-right">Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredAutores.map((autor) => (
                <TableRow key={autor.id_autor}>
                  <TableCell className="font-medium">{autor.id_autor}</TableCell>
                  <TableCell className="font-medium">{autor.nome}</TableCell>
                  <TableCell>{formatDate(autor.data_nascimento)}</TableCell>
                  <TableCell>{autor.data_falecimento ? formatDate(autor.data_falecimento) : "Vivo"}</TableCell>
                  <TableCell>{calculateAge(autor.data_nascimento, autor.data_falecimento)} anos</TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button variant="outline" size="sm" onClick={() => handleEdit(autor)}>
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => handleDelete(autor.id_autor)}>
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
