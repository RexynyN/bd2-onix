"use client"

import { Calendar } from "@/components/ui/calendar"

import type React from "react"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Plus, Search, CheckCircle, AlertTriangle, Clock } from "lucide-react"
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
import {
  emprestimosAPI,
  usuariosAPI,
  estoqueAPI,
  type EmprestimoDetalhado,
  type Usuario,
  type Estoque,
} from "@/lib/api"

const statusColors = {
  ativo: "bg-blue-100 text-blue-800",
  devolvido: "bg-green-100 text-green-800",
  vencido: "bg-red-100 text-red-800",
}

const statusIcons = {
  ativo: Clock,
  devolvido: CheckCircle,
  vencido: AlertTriangle,
}

export default function EmprestimosPage() {
  const [emprestimos, setEmprestimos] = useState<EmprestimoDetalhado[]>([])
  const [usuarios, setUsuarios] = useState<Usuario[]>([])
  const [estoque, setEstoque] = useState<Estoque[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState<string>("todos")
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [isDevolucaoDialogOpen, setIsDevolucaoDialogOpen] = useState(false)
  const [selectedEmprestimo, setSelectedEmprestimo] = useState<EmprestimoDetalhado | null>(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [stats, setStats] = useState({
    total: 0,
    ativos: 0,
    vencidos: 0,
    devolvidos: 0,
  })
  const [formData, setFormData] = useState({
    id_usuario: "",
    id_estoque: "",
    data_emprestimo: "",
    data_devolucao_prevista: "",
  })
  const { toast } = useToast()

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [emprestimosRes, usuariosRes, estoqueRes, relatorioRes] = await Promise.all([
        emprestimosAPI.getEmAndamento(),
        usuariosAPI.getAll(0, 1000),
        estoqueAPI.getAll(0, 1000),
        emprestimosAPI.getRelatorio(),
      ])

      setEmprestimos(emprestimosRes.data)
      setUsuarios(usuariosRes.data)
      setEstoque(estoqueRes.data)
      setStats({
        total: relatorioRes.data.total_emprestimos,
        ativos: relatorioRes.data.emprestimos_em_andamento,
        vencidos: relatorioRes.data.emprestimos_vencidos,
        devolvidos: relatorioRes.data.emprestimos_devolvidos,
      })
    } catch (error) {
      console.error("Error fetching data:", error)
      toast({
        title: "Erro ao carregar dados",
        description: "Não foi possível carregar os dados dos empréstimos.",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const getEmprestimoStatus = (emprestimo: EmprestimoDetalhado): "ativo" | "devolvido" | "vencido" => {
    if (emprestimo.data_devolucao) {
      return "devolvido"
    }

    const hoje = new Date()
    const dataPrevista = new Date(emprestimo.data_devolucao_prevista)

    if (hoje > dataPrevista) {
      return "vencido"
    }

    return "ativo"
  }

  const filteredEmprestimos = emprestimos.filter((emprestimo) => {
    const status = getEmprestimoStatus(emprestimo)
    const matchesSearch =
      emprestimo.usuario.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
      emprestimo.item_titulo.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === "todos" || status === statusFilter
    return matchesSearch && matchesStatus
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)

    try {
      const emprestimoData = {
        data_emprestimo: formData.data_emprestimo,
        data_devolucao_prevista: formData.data_devolucao_prevista,
        id_estoque: Number.parseInt(formData.id_estoque),
        id_usuario: Number.parseInt(formData.id_usuario),
      }

      await emprestimosAPI.create(emprestimoData)

      toast({
        title: "Empréstimo criado",
        description: "Novo empréstimo foi registrado com sucesso.",
      })

      setIsDialogOpen(false)
      setFormData({ id_usuario: "", id_estoque: "", data_emprestimo: "", data_devolucao_prevista: "" })

      // Refresh data
      fetchData()
    } catch (error) {
      console.error("Error creating emprestimo:", error)
      toast({
        title: "Erro ao criar empréstimo",
        description: "Não foi possível criar o empréstimo. Verifique se o item está disponível.",
        variant: "destructive",
      })
    } finally {
      setSubmitting(false)
    }
  }

  const handleDevolucao = async () => {
    if (!selectedEmprestimo) return

    try {
      await emprestimosAPI.devolver(selectedEmprestimo.id_emprestimo)

      toast({
        title: "Devolução registrada",
        description: "A devolução foi registrada com sucesso.",
      })

      setIsDevolucaoDialogOpen(false)
      setSelectedEmprestimo(null)

      // Refresh data
      fetchData()
    } catch (error) {
      console.error("Error returning emprestimo:", error)
      toast({
        title: "Erro ao registrar devolução",
        description: "Não foi possível registrar a devolução. Tente novamente.",
        variant: "destructive",
      })
    }
  }

  const openDevolucaoDialog = (emprestimo: EmprestimoDetalhado) => {
    setSelectedEmprestimo(emprestimo)
    setIsDevolucaoDialogOpen(true)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("pt-BR")
  }

  const getDaysOverdue = (dataPrevista: string) => {
    const hoje = new Date()
    const prevista = new Date(dataPrevista)
    const diffTime = hoje.getTime() - prevista.getTime()
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return diffDays > 0 ? diffDays : 0
  }

  if (loading) {
    return (
      <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
        <div className="flex items-center gap-4">
          <SidebarTrigger />
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Empréstimos</h2>
            <p className="text-muted-foreground">Carregando...</p>
          </div>
        </div>
        <Card>
          <CardContent className="p-6">
            <div className="text-center">Carregando empréstimos...</div>
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
            <h2 className="text-3xl font-bold tracking-tight">Empréstimos</h2>
            <p className="text-muted-foreground">Gerencie os empréstimos da biblioteca</p>
          </div>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button className="onix-gradient">
              <Plus className="mr-2 h-4 w-4" />
              Novo Empréstimo
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>Novo Empréstimo</DialogTitle>
              <DialogDescription>Preencha os dados para registrar um novo empréstimo.</DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit}>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="id_usuario" className="text-right">
                    Usuário
                  </Label>
                  <Select
                    value={formData.id_usuario}
                    onValueChange={(value) => setFormData({ ...formData, id_usuario: value })}
                    required
                    disabled={submitting}
                  >
                    <SelectTrigger className="col-span-3">
                      <SelectValue placeholder="Selecione o usuário" />
                    </SelectTrigger>
                    <SelectContent>
                      {usuarios.map((usuario) => (
                        <SelectItem key={usuario.id_usuario} value={usuario.id_usuario.toString()}>
                          {usuario.nome}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="id_estoque" className="text-right">
                    Item do Estoque
                  </Label>
                  <Select
                    value={formData.id_estoque}
                    onValueChange={(value) => setFormData({ ...formData, id_estoque: value })}
                    required
                    disabled={submitting}
                  >
                    <SelectTrigger className="col-span-3">
                      <SelectValue placeholder="Selecione o item" />
                    </SelectTrigger>
                    <SelectContent>
                      {estoque.map((item) => (
                        <SelectItem key={item.id_estoque} value={item.id_estoque.toString()}>
                          ID: {item.id_estoque} - Título: {item.id_titulo} ({item.condicao})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="data_emprestimo" className="text-right">
                    Data Empréstimo
                  </Label>
                  <Input
                    id="data_emprestimo"
                    type="date"
                    value={formData.data_emprestimo}
                    onChange={(e) => setFormData({ ...formData, data_emprestimo: e.target.value })}
                    className="col-span-3"
                    required
                    disabled={submitting}
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="data_devolucao_prevista" className="text-right">
                    Devolução Prevista
                  </Label>
                  <Input
                    id="data_devolucao_prevista"
                    type="date"
                    value={formData.data_devolucao_prevista}
                    onChange={(e) => setFormData({ ...formData, data_devolucao_prevista: e.target.value })}
                    className="col-span-3"
                    required
                    disabled={submitting}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button type="submit" className="onix-gradient" disabled={submitting}>
                  {submitting ? "Registrando..." : "Registrar Empréstimo"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Estatísticas rápidas */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Empréstimos</CardTitle>
            <Calendar className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Empréstimos Ativos</CardTitle>
            <Clock className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.ativos}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Empréstimos Vencidos</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats.vencidos}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Devoluções</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.devolvidos}</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Lista de Empréstimos</CardTitle>
          <CardDescription>{emprestimos.length} empréstimos em andamento</CardDescription>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Search className="w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Buscar empréstimos..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="max-w-sm"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Filtrar por status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="todos">Todos</SelectItem>
                <SelectItem value="ativo">Ativos</SelectItem>
                <SelectItem value="vencido">Vencidos</SelectItem>
                <SelectItem value="devolvido">Devolvidos</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent>
          {emprestimos.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Clock className="mx-auto h-12 w-12 mb-4 opacity-50" />
              <p>Nenhum empréstimo em andamento.</p>
              <p className="text-sm">Clique em "Novo Empréstimo" para começar.</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Usuário</TableHead>
                  <TableHead>Item</TableHead>
                  <TableHead>Biblioteca</TableHead>
                  <TableHead>Empréstimo</TableHead>
                  <TableHead>Devolução Prevista</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredEmprestimos.map((emprestimo) => {
                  const status = getEmprestimoStatus(emprestimo)
                  const StatusIcon = statusIcons[status]
                  const diasAtraso = status === "vencido" ? getDaysOverdue(emprestimo.data_devolucao_prevista) : 0

                  return (
                    <TableRow key={emprestimo.id_emprestimo}>
                      <TableCell className="font-medium">{emprestimo.id_emprestimo}</TableCell>
                      <TableCell>{emprestimo.usuario.nome}</TableCell>
                      <TableCell>
                        <div>
                          <div className="font-medium">{emprestimo.item_titulo}</div>
                          <div className="text-sm text-muted-foreground capitalize">{emprestimo.tipo_midia}</div>
                        </div>
                      </TableCell>
                      <TableCell>{emprestimo.biblioteca}</TableCell>
                      <TableCell>{formatDate(emprestimo.data_emprestimo)}</TableCell>
                      <TableCell>
                        <div>
                          {formatDate(emprestimo.data_devolucao_prevista)}
                          {diasAtraso > 0 && (
                            <div className="text-xs text-red-600 font-medium">{diasAtraso} dia(s) de atraso</div>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge className={statusColors[status]}>
                          <StatusIcon className="w-3 h-3 mr-1" />
                          {status}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        {status === "ativo" || status === "vencido" ? (
                          <Button variant="outline" size="sm" onClick={() => openDevolucaoDialog(emprestimo)}>
                            <CheckCircle className="w-4 h-4 mr-1" />
                            Devolver
                          </Button>
                        ) : (
                          <span className="text-sm text-muted-foreground">
                            Devolvido em {emprestimo.data_devolucao && formatDate(emprestimo.data_devolucao)}
                          </span>
                        )}
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Dialog de Devolução */}
      <Dialog open={isDevolucaoDialogOpen} onOpenChange={setIsDevolucaoDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirmar Devolução</DialogTitle>
            <DialogDescription>Tem certeza que deseja registrar a devolução desta mídia?</DialogDescription>
          </DialogHeader>
          {selectedEmprestimo && (
            <div className="py-4">
              <div className="space-y-2">
                <p>
                  <strong>Usuário:</strong> {selectedEmprestimo.usuario.nome}
                </p>
                <p>
                  <strong>Item:</strong> {selectedEmprestimo.item_titulo}
                </p>
                <p>
                  <strong>Biblioteca:</strong> {selectedEmprestimo.biblioteca}
                </p>
                <p>
                  <strong>Data do Empréstimo:</strong> {formatDate(selectedEmprestimo.data_emprestimo)}
                </p>
                <p>
                  <strong>Devolução Prevista:</strong> {formatDate(selectedEmprestimo.data_devolucao_prevista)}
                </p>
                {getEmprestimoStatus(selectedEmprestimo) === "vencido" && (
                  <p className="text-red-600 font-medium">
                    <strong>Atraso:</strong> {getDaysOverdue(selectedEmprestimo.data_devolucao_prevista)} dia(s)
                  </p>
                )}
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDevolucaoDialogOpen(false)}>
              Cancelar
            </Button>
            <Button onClick={handleDevolucao} className="onix-gradient">
              Confirmar Devolução
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
