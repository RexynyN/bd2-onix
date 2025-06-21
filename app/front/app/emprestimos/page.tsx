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
import { emprestimosAPI, usuariosAPI, type EmprestimoCompleto, type Usuario, type EmprestimoCreate } from "@/lib/api"
import { Pagination } from "@/components/pagination"
import { AdvancedFilters, type FilterConfig, type FilterValues } from "@/components/advanced-filters"

interface EmprestimoExtended extends EmprestimoCompleto {
  status: "ativo" | "devolvido" | "vencido"
}

const ITEMS_PER_PAGE = 10

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
  const [emprestimos, setEmprestimos] = useState<EmprestimoCompleto[]>([])
  const [usuarios, setUsuarios] = useState<Usuario[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState<string>("todos")
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [isDevolucaoDialogOpen, setIsDevolucaoDialogOpen] = useState(false)
  const [selectedEmprestimo, setSelectedEmprestimo] = useState<EmprestimoExtended | null>(null)
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalEmprestimos, setTotalEmprestimos] = useState(0)
  const [filterValues, setFilterValues] = useState<FilterValues>({})
  const [formData, setFormData] = useState({
    id_usuario: "",
    id_estoque: "",
    data_emprestimo: "",
    data_devolucao_prevista: "",
  })
  const { toast } = useToast()

  const filterConfig: FilterConfig[] = [
    {
      key: "status",
      label: "Status",
      type: "select",
      options: [
        { value: "ativo", label: "Ativo" },
        { value: "vencido", label: "Vencido" },
        { value: "devolvido", label: "Devolvido" },
      ],
      placeholder: "Todos os status",
    },
    {
      key: "usuario",
      label: "Usuário",
      type: "text",
      placeholder: "Nome do usuário",
    },
    {
      key: "data_emprestimo",
      label: "Data do Empréstimo",
      type: "dateRange",
    },
    {
      key: "data_devolucao_prevista",
      label: "Data de Devolução Prevista",
      type: "dateRange",
    },
    {
      key: "biblioteca",
      label: "Biblioteca",
      type: "text",
      placeholder: "Nome da biblioteca",
    },
  ]

  useEffect(() => {
    fetchUsuarios()
    fetchEmprestimos()
  }, [currentPage])

  const fetchUsuarios = async () => {
    try {
      const response = await usuariosAPI.getAll()
      setUsuarios(response.data)
    } catch (error) {
      console.error("Error fetching usuarios:", error)
    }
  }

  const fetchEmprestimos = async () => {
    try {
      setLoading(true)
      const skip = (currentPage - 1) * ITEMS_PER_PAGE
      const response = await emprestimosAPI.getEmAndamento(skip, ITEMS_PER_PAGE)

      let filteredEmprestimos = response.data.map((emp) => ({
        ...emp,
        status: getEmprestimoStatus(emp),
      }))

      // Apply filters
      if (filterValues.status) {
        filteredEmprestimos = filteredEmprestimos.filter((e) => e.status === filterValues.status)
      }
      if (filterValues.usuario) {
        filteredEmprestimos = filteredEmprestimos.filter((e) =>
          e.usuario?.nome?.toLowerCase().includes(filterValues.usuario.toLowerCase()),
        )
      }
      if (filterValues.biblioteca) {
        filteredEmprestimos = filteredEmprestimos.filter((e) =>
          e.biblioteca?.toLowerCase().includes(filterValues.biblioteca.toLowerCase()),
        )
      }
      if (filterValues.data_emprestimo?.from) {
        filteredEmprestimos = filteredEmprestimos.filter(
          (e) => new Date(e.data_emprestimo) >= new Date(filterValues.data_emprestimo.from),
        )
      }
      if (filterValues.data_emprestimo?.to) {
        filteredEmprestimos = filteredEmprestimos.filter(
          (e) => new Date(e.data_emprestimo) <= new Date(filterValues.data_emprestimo.to),
        )
      }

      setEmprestimos(filteredEmprestimos)
      setTotalEmprestimos(
        response.data.length === ITEMS_PER_PAGE
          ? currentPage * ITEMS_PER_PAGE + 1
          : (currentPage - 1) * ITEMS_PER_PAGE + response.data.length,
      )
    } catch (error) {
      console.error("Error fetching emprestimos:", error)
    } finally {
      setLoading(false)
    }
  }

  const getEmprestimoStatus = (emprestimo: EmprestimoCompleto): "ativo" | "devolvido" | "vencido" => {
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
    const matchesSearch = emprestimo.usuario?.nome?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === "todos" || emprestimo.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)

    try {
      const emprestimoData: EmprestimoCreate = {
        data_emprestimo: formData.data_emprestimo,
        data_devolucao_prevista: formData.data_devolucao_prevista || null,
        id_estoque: Number.parseInt(formData.id_estoque),
        id_usuario: Number.parseInt(formData.id_usuario),
      }

      await emprestimosAPI.create(emprestimoData)
      fetchEmprestimos()

      toast({
        title: "Empréstimo criado",
        description: "Novo empréstimo foi registrado com sucesso.",
      })

      setIsDialogOpen(false)
      setFormData({ id_usuario: "", id_estoque: "", data_emprestimo: "", data_devolucao_prevista: "" })
    } catch (error) {
      console.error("Error creating emprestimo:", error)
      toast({
        title: "Erro ao criar empréstimo",
        description: error.response.data.detail,
        variant: "destructive",
      })
    } finally {
      setSubmitting(false)
    }
  }

  const handleDevolucao = async () => {
    if (!selectedEmprestimo) return

    try {
      const hoje = new Date().toISOString().split("T")[0]
      await emprestimosAPI.devolver(selectedEmprestimo.id_emprestimo, hoje)
      fetchEmprestimos()

      toast({
        title: "Devolução registrada",
        description: "A devolução foi registrada com sucesso.",
      })

      setIsDevolucaoDialogOpen(false)
      setSelectedEmprestimo(null)
    } catch (error) {
      console.error("Error returning emprestimo:", error)
      toast({
        title: "Erro ao registrar devolução",
        description: error.response.data.detail,
        variant: "destructive",
      })
    }
  }

  const openDevolucaoDialog = (emprestimo: EmprestimoExtended) => {
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

  const handleApplyFilters = () => {
    setCurrentPage(1)
    fetchEmprestimos()
  }

  const handleClearFilters = () => {
    setFilterValues({})
    setCurrentPage(1)
    fetchEmprestimos()
  }

  const totalPages = Math.ceil(totalEmprestimos / ITEMS_PER_PAGE)

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
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
                      Estoque ID
                    </Label>
                    <Input
                      id="id_estoque"
                      type="number"
                      value={formData.id_estoque}
                      onChange={(e) => setFormData({ ...formData, id_estoque: e.target.value })}
                      className="col-span-3"
                      required
                      disabled={submitting}
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
            <CardTitle className="text-sm font-medium">Devoluções</CardTitle>
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
          <CardDescription>
            Página {currentPage} de {totalPages} - {totalEmprestimos} empréstimos registrados
          </CardDescription>
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
              <p>Nenhum empréstimo registrado ainda.</p>
              <p className="text-sm">Clique em "Novo Empréstimo" para começar.</p>
            </div>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Usuário</TableHead>
                    <TableHead>Estoque ID</TableHead>
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
                        <TableCell>{emprestimo.usuario?.nome || `ID: ${emprestimo.id_usuario}`}</TableCell>
                        <TableCell>{emprestimo.id_estoque}</TableCell>
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

              <div className="mt-4">
                <Pagination currentPage={currentPage} totalPages={totalPages} onPageChange={handlePageChange} />
              </div>
            </>
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
                  <strong>Usuário:</strong> {selectedEmprestimo.usuario?.nome}
                </p>
                <p>
                  <strong>Estoque ID:</strong> {selectedEmprestimo.id_estoque}
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
