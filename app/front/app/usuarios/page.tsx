"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Plus, Search, Edit, Trash2 } from "lucide-react"
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
import { usuariosAPI, type Usuario, type UsuarioCreate, type UsuarioUpdate } from "@/lib/api"
import { Pagination } from "@/components/pagination"

const ITEMS_PER_PAGE = 10

export default function UsuariosPage() {
  const [usuarios, setUsuarios] = useState<Usuario[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [editingUser, setEditingUser] = useState<Usuario | null>(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalUsers, setTotalUsers] = useState(0)
  const [formData, setFormData] = useState<UsuarioCreate>({
    nome: "",
    email: "",
    endereco: "",
    telefone: "",
  })
  const { toast } = useToast()

  useEffect(() => {
    fetchUsuarios()
  }, [currentPage])

  const fetchUsuarios = async () => {
    try {
      setLoading(true)
      const skip = (currentPage - 1) * ITEMS_PER_PAGE
      const response = await usuariosAPI.getAll(skip, ITEMS_PER_PAGE)
      setUsuarios(response.data)
      // Note: API doesn't return total count, so we estimate based on returned data
      setTotalUsers(
        response.data.length === ITEMS_PER_PAGE
          ? currentPage * ITEMS_PER_PAGE + 1
          : (currentPage - 1) * ITEMS_PER_PAGE + response.data.length,
      )
    } catch (error) {
      console.error("Error fetching usuarios:", error)
      toast({
        title: "Erro ao carregar usuários",
        description: error.response.data.detail || "Não foi possível carregar a lista de usuários.",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const filteredUsuarios = usuarios.filter(
    (usuario) =>
      usuario.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (usuario.email && usuario.email.toLowerCase().includes(searchTerm.toLowerCase())),
  )

  const totalPages = Math.ceil(totalUsers / ITEMS_PER_PAGE)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)

    try {
      if (editingUser) {
        const updateData: UsuarioUpdate = {
          nome: formData.nome,
          email: formData.email || null,
          endereco: formData.endereco || null,
          telefone: formData.telefone || null,
        }
        const response = await usuariosAPI.update(editingUser.id_usuario, updateData)
        setUsuarios(usuarios.map((u) => (u.id_usuario === editingUser.id_usuario ? response.data : u)))
        toast({
          title: "Usuário atualizado",
          description: "Os dados do usuário foram atualizados com sucesso.",
        })
      } else {
        const createData: UsuarioCreate = {
          nome: formData.nome,
          email: formData.email || null,
          endereco: formData.endereco || null,
          telefone: formData.telefone || null,
        }
        const response = await usuariosAPI.create(createData)
        // Refresh the current page to show the new user
        fetchUsuarios()
        toast({
          title: "Usuário criado",
          description: "Novo usuário foi cadastrado com sucesso.",
        })
      }

      setIsDialogOpen(false)
      setEditingUser(null)
      setFormData({ nome: "", email: "", endereco: "", telefone: "" })
    } catch (error) {
      console.error("Error saving usuario:", error)
      toast({
        title: "Erro ao salvar usuário",
        description: error.response.data.detail,
        variant: "destructive",
      })
    } finally {
      setSubmitting(false)
    }
  }

  const handleEdit = (usuario: Usuario) => {
    setEditingUser(usuario)
    setFormData({
      nome: usuario.nome,
      email: usuario.email || "",
      endereco: usuario.endereco || "",
      telefone: usuario.telefone || "",
    })
    setIsDialogOpen(true)
  }

  const handleDelete = async (id: number) => {
    try {
      await usuariosAPI.delete(id)
      fetchUsuarios() // Refresh current page
      toast({
        title: "Usuário removido",
        description: "O usuário foi removido do sistema.",
      })
    } catch (error) {
      console.error("Error deleting usuario:", error)
      toast({
        title: "Erro ao remover usuário",
        description: error.response.data.detail,
        variant: "destructive",
      })
    }
  }

  const openNewUserDialog = () => {
    setEditingUser(null)
    setFormData({ nome: "", email: "", endereco: "", telefone: "" })
    setIsDialogOpen(true)
  }

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
  }

  if (loading) {
    return (
      <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
        <div className="flex items-center gap-4">
          <SidebarTrigger />
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Usuários</h2>
            <p className="text-muted-foreground">Carregando...</p>
          </div>
        </div>
        <Card>
          <CardContent className="p-6">
            <div className="text-center">Carregando usuários...</div>
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
            <h2 className="text-3xl font-bold tracking-tight">Usuários</h2>
            <p className="text-muted-foreground">Gerencie os usuários do sistema</p>
          </div>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={openNewUserDialog} className="onix-gradient">
              <Plus className="mr-2 h-4 w-4" />
              Novo Usuário
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>{editingUser ? "Editar Usuário" : "Novo Usuário"}</DialogTitle>
              <DialogDescription>
                {editingUser
                  ? "Atualize as informações do usuário."
                  : "Preencha os dados para cadastrar um novo usuário."}
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
                  <Label htmlFor="email" className="text-right">
                    Email
                  </Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="col-span-3"
                    disabled={submitting}
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
                    disabled={submitting}
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="telefone" className="text-right">
                    Telefone
                  </Label>
                  <Input
                    id="telefone"
                    value={formData.telefone}
                    onChange={(e) => setFormData({ ...formData, telefone: e.target.value })}
                    className="col-span-3"
                    disabled={submitting}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button type="submit" className="onix-gradient" disabled={submitting}>
                  {submitting ? "Salvando..." : editingUser ? "Atualizar" : "Cadastrar"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Lista de Usuários</CardTitle>
          <CardDescription>
            Página {currentPage} de {totalPages} - {totalUsers} usuários cadastrados
          </CardDescription>
          <div className="flex items-center space-x-2">
            <Search className="w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Buscar usuários..."
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
                <TableHead>Email</TableHead>
                <TableHead>Telefone</TableHead>
                <TableHead>Endereço</TableHead>
                <TableHead className="text-right">Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredUsuarios.map((usuario) => (
                <TableRow key={usuario.id_usuario}>
                  <TableCell className="font-medium">{usuario.id_usuario}</TableCell>
                  <TableCell>{usuario.nome}</TableCell>
                  <TableCell>{usuario.email || "-"}</TableCell>
                  <TableCell>{usuario.telefone || "-"}</TableCell>
                  <TableCell>{usuario.endereco || "-"}</TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button variant="outline" size="sm" onClick={() => handleEdit(usuario)}>
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => handleDelete(usuario.id_usuario)}>
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
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
