"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Users, Building2, BookOpen, Calendar, TrendingUp, AlertTriangle } from "lucide-react"

interface DashboardStats {
  totalUsuarios: number
  totalBibliotecas: number
  totalMidias: number
  emprestimosAtivos: number
  emprestimosVencidos: number
  itensDisponiveis: number
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats>({
    totalUsuarios: 0,
    totalBibliotecas: 0,
    totalMidias: 0,
    emprestimosAtivos: 0,
    emprestimosVencidos: 0,
    itensDisponiveis: 0,
  })

  useEffect(() => {
    // Simular carregamento de dados da API
    setStats({
      totalUsuarios: 1250,
      totalBibliotecas: 5,
      totalMidias: 15420,
      emprestimosAtivos: 342,
      emprestimosVencidos: 23,
      itensDisponiveis: 12890,
    })
  }, [])

  const cards = [
    {
      title: "Total de Usuários",
      value: stats.totalUsuarios.toLocaleString(),
      description: "Usuários cadastrados no sistema",
      icon: Users,
      color: "text-blue-600",
    },
    {
      title: "Bibliotecas",
      value: stats.totalBibliotecas.toString(),
      description: "Unidades ativas",
      icon: Building2,
      color: "text-green-600",
    },
    {
      title: "Acervo Total",
      value: stats.totalMidias.toLocaleString(),
      description: "Mídias cadastradas",
      icon: BookOpen,
      color: "text-purple-600",
    },
    {
      title: "Empréstimos Ativos",
      value: stats.emprestimosAtivos.toString(),
      description: "Em andamento",
      icon: Calendar,
      color: "text-orange-600",
    },
    {
      title: "Itens Disponíveis",
      value: stats.itensDisponiveis.toLocaleString(),
      description: "Para empréstimo",
      icon: TrendingUp,
      color: "text-emerald-600",
    },
    {
      title: "Empréstimos Vencidos",
      value: stats.emprestimosVencidos.toString(),
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
            <CardTitle>Atividade Recente</CardTitle>
            <CardDescription>Últimas movimentações do sistema</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center space-x-4">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm font-medium">Novo usuário cadastrado</p>
                <p className="text-xs text-muted-foreground">Maria Silva - há 2 minutos</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm font-medium">Empréstimo realizado</p>
                <p className="text-xs text-muted-foreground">"Dom Casmurro" - há 15 minutos</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm font-medium">Devolução em atraso</p>
                <p className="text-xs text-muted-foreground">João Santos - há 1 hora</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm font-medium">Nova mídia cadastrada</p>
                <p className="text-xs text-muted-foreground">"O Alquimista" - há 2 horas</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Estatísticas Rápidas</CardTitle>
            <CardDescription>Métricas importantes</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm">Taxa de Ocupação</span>
              <span className="text-sm font-bold onix-accent">73%</span>
            </div>
            <div className="w-full bg-secondary rounded-full h-2">
              <div
                className="bg-gradient-to-r from-green-500 to-emerald-600 h-2 rounded-full"
                style={{ width: "73%" }}
              ></div>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-sm">Empréstimos/Mês</span>
              <span className="text-sm font-bold onix-accent">+12%</span>
            </div>
            <div className="w-full bg-secondary rounded-full h-2">
              <div
                className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full"
                style={{ width: "85%" }}
              ></div>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-sm">Satisfação</span>
              <span className="text-sm font-bold onix-accent">4.8/5</span>
            </div>
            <div className="w-full bg-secondary rounded-full h-2">
              <div
                className="bg-gradient-to-r from-yellow-500 to-orange-600 h-2 rounded-full"
                style={{ width: "96%" }}
              ></div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
