"use client"

import { BookOpen, Building2, Users, Package, Calendar, Home, PenTool } from "lucide-react"
import Link from "next/link"
import { usePathname } from "next/navigation"

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"

const menuItems = [
  {
    title: "Dashboard",
    url: "/",
    icon: Home,
  },
  {
    title: "Usuários",
    url: "/usuarios",
    icon: Users,
  },
  {
    title: "Bibliotecas",
    url: "/bibliotecas",
    icon: Building2,
  },
  {
    title: "Mídias",
    url: "/midias",
    icon: BookOpen,
  },
  {
    title: "Autores",
    url: "/autores",
    icon: PenTool,
  },
  {
    title: "Empréstimos",
    url: "/emprestimos",
    icon: Calendar,
  },
  {
    title: "Estoque",
    url: "/estoque",
    icon: Package,
  },
]

export function AppSidebar() {
  const pathname = usePathname()

  return (
    <Sidebar className="border-r border-border/40">
      <SidebarHeader className="border-b border-border/40 p-6">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg onix-gradient flex items-center justify-center">
            <BookOpen className="w-4 h-4 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-bold">Onix Biblioteca</h2>
            <p className="text-sm text-muted-foreground">Sistema de Gerenciamento</p>
          </div>
        </div>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Menu Principal</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {menuItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild isActive={pathname === item.url}>
                    <Link href={item.url}>
                      <item.icon className="w-4 h-4" />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t border-border/40 p-4">
        <div className="text-xs text-muted-foreground text-center">© 2024 Onix Biblioteca</div>
      </SidebarFooter>
    </Sidebar>
  )
}
