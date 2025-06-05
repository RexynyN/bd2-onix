"use client"

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

interface Emprestimo {
  id_emprestimo: number
  data_emprestimo: string
  data_devolucao_prevista: string
  data_devolucao?: string
  id_estoque: number
  id_usuario: number
  usuario_nome: string
  titulo_midia: string
  tipo_midia: string
  status: "ativo" | "devolvido" | "vencido"
}

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
  const [emprestimos, setEmprestimos] = useState<Emprestimo[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState<string>("todos")
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [isDevolucaoDialogOpen, setIsDevolucaoDialogOpen] = useState(false)
  const [selectedEmprestimo, setSelectedEmprestimo] = useState<Emprestimo | null>(null)
  const [formData, setFormData] = useState({
    id_usuario: "",
    id_estoque: "",
    data_emprestimo: "",
    data_devolucao_prevista: "",
  })
  const { toast } = useToast()

  useEffect(() => {
    // Simular carregamento de dados
    const hoje = new Date()
    const ontem = new Date(hoje)
    ontem.setDate(hoje.getDate() - 1)
    const semanaPassada = new Date(hoje)
    semanaPassada.setDate(hoje.getDate() - 7)
    const proximaSemana = new Date(hoje)
    proximaSemana.setDate(hoje.getDate() + 7)

    setEmprestimos([
      {
        id_emprestimo: 1,
        data_emprestimo: semanaPassada.toISOString().split("T")[0],
        data_devolucao_prevista: ontem.toISOString().split("T")[0],
        id_estoque: 1,
        id_usuario: 1,
        usuario_nome: "João Silva",
        titulo_midia: "Dom Casmurro",
        tipo_midia: "livro",
        status: "vencido",
      },
      {
        id_emprestimo: 2,
        data_emprestimo: hoje.toISOString().split("T")[0],
        data_devolucao_prevista: proximaSemana.toISOString().split("T")[0],
        id_estoque: 2,
        id_usuario: 2,
        usuario_nome: "Maria Santos",
        titulo_midia: "National Geographic Brasil",
        tipo_midia: "revista",
        status: "ativo",
      },
      {
        id_emprestimo: 3,
        data_emprestimo: "2024-01-10",
        data_devolucao_prevista: "2024-01-17",
        data_devolucao: "2024-01-16",
        id_estoque: 3,
        id_usuario: 3,
        usuario_nome: "Pedro Oliveira",
        titulo_midia: "Cidade de Deus",
        tipo_midia: "dvd",
        status: "devolvido",
      },
    ])
  }, [])

  const filteredEmprestimos = emprestimos.filter((emprestimo) => {
    const matchesSearch =
      emprestimo.usuario_nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
      emprestimo.titulo_midia.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === "todos" || emprestimo.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    const newEmprestimo: Emprestimo = {
      id_emprestimo: Math.max(...emprestimos.map((e) => e.id_emprestimo)) + 1,
      data_emprestimo: formData.data_emprestimo,
      data_devolucao_prevista: formData.data_devolucao_prevista,
      id_estoque: Number.parseInt(formData.id_estoque),
      id_usuario: Number.parseInt(formData.id_usuario),
      usuario_nome: "Usuário " + formData.id_usuario, // Simulado
      titulo_midia: "Mídia " + formData.id_estoque, // Simulado
      tipo_midia: "livro", // Simulado
      status: "ativo",
    }

    setEmprestimos([...emprestimos, newEmprestimo])
    toast({
      title: "Empréstimo criado",
      description: "Novo empréstimo foi registrado com sucesso.",
    })

    setIsDialogOpen(false)
    setFormData({ id_usuario: "", id_estoque: "", data_emprestimo: "", data_devolucao_prevista: "" })
  }

  const handleDevolucao = () => {
    if (!selectedEmprestimo) return

    const hoje = new Date().toISOString().split("T")[0]
    setEmprestimos(
      emprestimos.map((e) =>
        e.id_emprestimo === selectedEmprestimo.id_emprestimo
          ? { ...e, data_devolucao: hoje, status: "devolvido" as const }
          : e,
      ),
    )

    toast({
      title: "Devolução registrada",
      description: "A devolução foi registrada com sucesso.",
    })

    setIsDevolucaoDialogOpen(false)
    setSelectedEmprestimo(null)
  }

  const openDevolucaoDialog = (emprestimo: Emprestimo) => {
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
                    Usuário ID
                  </Label>
                  <Input
                    id="id_usuario"
                    type="number"
                    value={formData.id_usuario}
                    onChange={(e) => setFormData({ ...formData, id_usuario: e.target.value })}
                    className="col-span-3"
                    required
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="id_estoque" className="text-right">
                    Estoque ID
                  </Label>
                  <Input
                    id="id_estoque"
                    type="number"
                    value={formData.id_estoque}
                    onChange={(e) => setFormData({ ...formData, id_estoque: e.target.value })}
                    className="col-span-3"
                    required
                  />
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
                  />
                </div>
              </div>
              <DialogFooter>
                <Button type="submit" className="onix-gradient">
                  Registrar Empréstimo
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Estatísticas rápidas */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Empréstimos Ativos</CardTitle>
            <Clock className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{emprestimos.filter((e) => e.status === "ativo").length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Empréstimos Vencidos</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {emprestimos.filter((e) => e.status === "vencido").length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Devoluções do Mês</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {emprestimos.filter((e) => e.status === "devolvido").length}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Lista de Empréstimos</CardTitle>
          <CardDescription>{emprestimos.length} empréstimos registrados</CardDescription>
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
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Usuário</TableHead>
                <TableHead>Mídia</TableHead>
                <TableHead>Empréstimo</TableHead>
                <TableHead>Devolução Prevista</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredEmprestimos.map((emprestimo) => {
                const StatusIcon = statusIcons[emprestimo.status]
                const diasAtraso =
                  emprestimo.status === "vencido" ? getDaysOverdue(emprestimo.data_devolucao_prevista) : 0

                return (
                  <TableRow key={emprestimo.id_emprestimo}>
                    <TableCell className="font-medium">{emprestimo.id_emprestimo}</TableCell>
                    <TableCell>{emprestimo.usuario_nome}</TableCell>
                    <TableCell>
                      <div>
                        <div className="font-medium">{emprestimo.titulo_midia}</div>
                        <div className="text-sm text-muted-foreground">{emprestimo.tipo_midia}</div>
                      </div>
                    </TableCell>
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
                      <Badge className={statusColors[emprestimo.status]}>
                        <StatusIcon className="w-3 h-3 mr-1" />
                        {emprestimo.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      {emprestimo.status === "ativo" || emprestimo.status === "vencido" ? (
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
                  <strong>Usuário:</strong> {selectedEmprestimo.usuario_nome}
                </p>
                <p>
                  <strong>Mídia:</strong> {selectedEmprestimo.titulo_midia}
                </p>
                <p>
                  <strong>Data do Empréstimo:</strong> {formatDate(selectedEmprestimo.data_emprestimo)}
                </p>
                <p>
                  <strong>Devolução Prevista:</strong> {formatDate(selectedEmprestimo.data_devolucao_prevista)}
                </p>
                {selectedEmprestimo.status === "vencido" && (
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
