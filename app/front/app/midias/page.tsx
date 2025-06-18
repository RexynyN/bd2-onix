"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Users, Building2, BookOpen, Calendar, TrendingUp, AlertTriangle } from "lucide-react"
import { usuariosAPI, bibliotecasAPI, livrosAPI, revistasAPI, dvdsAPI, artigosAPI, emprestimosAPI } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"

interface DashboardStats {
  totalUsuarios: number
  totalBibliotecas: number
  totalLivros: number
  totalRevistas: number
  totalDvds: number
  totalArtigos: number
  emprestimosAtivos: number
  emprestimosVencidos: number
  emprestimosDevolvidos: number
  totalEmprestimos: number
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats>({
    totalUsuarios: 0,
    totalBibliotecas: 0,
    totalLivros: 0,
    totalRevistas: 0,
    totalDvds: 0,
    totalArtigos: 0,
    emprestimosAtivos: 0,
    emprestimosVencidos: 0,
    emprestimosDevolvidos: 0,
    totalEmprestimos: 0,
  })
  const [loading, setLoading] = useState(true)
  const { toast } = useToast()

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [usuariosRes, bibliotecasRes, livrosRes, revistasRes, dvdsRes, artigosRes, relatorioRes] =
          await Promise.all([
            usuariosAPI.getAll(0, 1000),
            bibliotecasAPI.getAll(0, 1000),
            livrosAPI.getAll(0, 1000),
            revistasAPI.getAll(0, 1000),
            dvdsAPI.getAll(0, 1000),
            artigosAPI.getAll(0, 1000),
            emprestimosAPI.getRelatorio(),
          ])

        setStats({
          totalUsuarios: usuariosRes.data.length,
          totalBibliotecas: bibliotecasRes.data.length,
          totalLivros: livrosRes.data.length,
          totalRevistas: revistasRes.data.length,
          totalDvds: dvdsRes.data.length,
          totalArtigos: artigosRes.data.length,
          emprestimosAtivos: relatorioRes.data.emprestimos_em_andamento,
          emprestimosVencidos: relatorioRes.data.emprestimos_vencidos,
          emprestimosDevolvidos: relatorioRes.data.emprestimos_devolvidos,
          totalEmprestimos: relatorioRes.data.total_emprestimos,
        })
      } catch (error) {
        console.error("Error fetching dashboard data:", error)
        toast({
          title: "Erro ao carregar dados",
          description: "Não foi possível carregar os dados do dashboard.",
          variant: "destructive",
        })
      } finally {
        setLoading(false)
      }
    }

    fetchDashboardData()
  }, [toast])

  const totalTitulos = stats.totalLivros + stats.totalRevistas + stats.totalDvds + stats.totalArtigos

  const cards = [
    {
      title: "Total de Usuários",
      value: loading ? "..." : stats.totalUsuarios.toLocaleString(),
      description: "Usuários cadastrados no sistema",
      icon: Users,
      color: "text-blue-600",
    },
    {
      title: "Bibliotecas",
      value: loading ? "..." : stats.totalBibliotecas.toString(),
      description: "Unidades ativas",
      icon: Building2,
      color: "text-green-600",
    },
    {
      title: "Títulos Cadastrados",
      value: loading ? "..." : totalTitulos.toLocaleString(),
      description: "Títulos no sistema",
      icon: BookOpen,
      color: "text-purple-600",
    },
    {
      title: "Empréstimos Ativos",
      value: loading ? "..." : stats.emprestimosAtivos.toString(),
      description: "Em andamento",
      icon: Calendar,
      color: "text-orange-600",
    },
    {
      title: "Total de Empréstimos",
      value: loading ? "..." : stats.totalEmprestimos.toLocaleString(),
      description: "Histórico completo",
      icon: TrendingUp,
      color: "text-emerald-600",
    },
    {
      title: "Empréstimos Vencidos",
      value: loading ? "..." : stats.emprestimosVencidos.toString(),
      description: "Requer atenção",
      icon: AlertTriangle,
      color: "text-red-600",
    },
  ]

  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <div className="flex items-center gap-4">
          <SidebarTrigger />
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
            <p className="text-muted-foreground">Visão geral do sistema Onix Biblioteca</p>
          </div>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {cards.map((card, index) => (
          <Card key={index} className="hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{card.title}</CardTitle>
              <card.icon className={`h-4 w-4 ${card.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{card.value}</div>
              <p className="text-xs text-muted-foreground">{card.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Distribuição do Acervo</CardTitle>
            <CardDescription>Tipos de mídia cadastradas</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center space-x-4">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm font-medium">Livros</p>
                <p className="text-xs text-muted-foreground">{stats.totalLivros} títulos</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm font-medium">Revistas</p>
                <p className="text-xs text-muted-foreground">{stats.totalRevistas} títulos</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm font-medium">DVDs</p>
                <p className="text-xs text-muted-foreground">{stats.totalDvds} títulos</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm font-medium">Artigos</p>
                <p className="text-xs text-muted-foreground">{stats.totalArtigos} títulos</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Resumo de Empréstimos</CardTitle>
            <CardDescription>Estatísticas em tempo real</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm">Em Andamento</span>
              <span className="text-sm font-bold text-blue-600">{stats.emprestimosAtivos}</span>
            </div>
            <div className="w-full bg-secondary rounded-full h-2">
              <div
                className="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full"
                style={{
                  width:
                    stats.totalEmprestimos > 0 ? `${(stats.emprestimosAtivos / stats.totalEmprestimos) * 100}%` : "0%",
                }}
              ></div>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-sm">Vencidos</span>
              <span className="text-sm font-bold text-red-600">{stats.emprestimosVencidos}</span>
            </div>
            <div className="w-full bg-secondary rounded-full h-2">
              <div
                className="bg-gradient-to-r from-red-500 to-red-600 h-2 rounded-full"
                style={{
                  width:
                    stats.totalEmprestimos > 0
                      ? `${(stats.emprestimosVencidos / stats.totalEmprestimos) * 100}%`
                      : "0%",
                }}
              ></div>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-sm">Devolvidos</span>
              <span className="text-sm font-bold text-green-600">{stats.emprestimosDevolvidos}</span>
            </div>
            <div className="w-full bg-secondary rounded-full h-2">
              <div
                className="bg-gradient-to-r from-green-500 to-green-600 h-2 rounded-full"
                style={{
                  width:
                    stats.totalEmprestimos > 0
                      ? `${(stats.emprestimosDevolvidos / stats.totalEmprestimos) * 100}%`
                      : "0%",
                }}
              ></div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
