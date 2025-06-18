"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Plus, Search, PenTool, Edit, Trash2 } from "lucide-react"
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
import { autoresAPI, type Autor } from "@/lib/api"

export default function AutoresPage() {
  const [autores, setAutores] = useState<Autor[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [editingAutor, setEditingAutor] = useState<Autor | null>(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [formData, setFormData] = useState({
    nome: "",
    data_nascimento: "",
    data_falecimento: "",
  })
  const { toast } = useToast()

  useEffect(() => {
    fetchAutores()
  }, [])

  const fetchAutores = async () => {
    try {
      setLoading(true)
      const response = await autoresAPI.getAll(0, 1000)
      setAutores(response.data)
    } catch (error) {
      console.error("Error fetching autores:", error)
      toast({
        title: "Erro ao carregar autores",
        description: "Não foi possível carregar a lista de autores.",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const filteredAutores = autores.filter((autor) => autor.nome.toLowerCase().includes(searchTerm.toLowerCase()))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)

    try {
      const authorData = {
        nome: formData.nome,
        data_nascimento: formData.data_nascimento,
        ...(formData.data_falecimento && { data_falecimento: formData.data_falecimento }),
      }

      if (editingAutor) {
        const response = await autoresAPI.update(editingAutor.id_autor, authorData)
        setAutores(autores.map((a) => (a.id_autor === editingAutor.id_autor ? response.data : a)))
        toast({
          title: "Autor atualizado",
          description: "Os dados do autor foram atualizados com sucesso.",
        })
      } else {
        const response = await autoresAPI.create(authorData)
        setAutores([...autores, response.data])
        toast({
          title: "Autor criado",
          description: "Novo autor foi cadastrado com sucesso.",
        })
      }

      setIsDialogOpen(false)
      setEditingAutor(null)
      setFormData({ nome: "", data_nascimento: "", data_falecimento: "" })
    } catch (error) {
      console.error("Error saving autor:", error)
      toast({
        title: "Erro ao salvar autor",
        description: "Não foi possível salvar o autor. Tente novamente.",
        variant: "destructive",
      })
    } finally {
      setSubmitting(false)
    }
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

  const handleDelete = async (id: number) => {
    try {
      await autoresAPI.delete(id)
      setAutores(autores.filter((a) => a.id_autor !== id))
      toast({
        title: "Autor removido",
        description: "O autor foi removido do sistema.",
      })
    } catch (error) {
      console.error("Error deleting autor:", error)
      toast({
        title: "Erro ao remover autor",
        description: "Não foi possível remover o autor. Tente novamente.",
        variant: "destructive",
      })
    }
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

  if (loading) {
    return (
      <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
        <div className="flex items-center gap-4">
          <SidebarTrigger />
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Autores</h2>
            <p className="text-muted-foreground">Carregando...</p>
          </div>
        </div>
        <Card>
          <CardContent className="p-6">
            <div className="text-center">Carregando autores...</div>
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
                    disabled={submitting}
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
                    disabled={submitting}
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
                    disabled={submitting}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button type="submit" className="onix-gradient" disabled={submitting}>
                  {submitting ? "Salvando..." : editingAutor ? "Atualizar" : "Cadastrar"}
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
          {autores.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <PenTool className="mx-auto h-12 w-12 mb-4 opacity-50" />
              <p>Nenhum autor cadastrado ainda.</p>
              <p className="text-sm">Clique em "Novo Autor" para começar.</p>
            </div>
          ) : (
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
          )}
        </CardContent>
      </Card>
    </div>
  )
}
