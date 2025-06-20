"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command"
import { Check, ChevronsUpDown } from "lucide-react"
import { cn } from "@/lib/utils"
import { revistasAPI, dvdsAPI, artigosAPI, livrosAPI } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"

interface TitleOption {
  value: string
  label: string
  subtitle: string
  type: string
  originalId: number
}

interface SearchableSelectProps {
  value?: string
  onValueChange: (value: string) => void
  placeholder?: string
  searchPlaceholder?: string
  className?: string
  type?: "titles" | "custom"
  options?: Array<{ value: string; label: string; subtitle?: string }>
  loading?: boolean
  onSearch?: (query: string) => void
}

export function SearchableSelect({
  value,
  onValueChange,
  placeholder = "Selecione uma opção...",
  searchPlaceholder = "Buscar...",
  className,
  type = "custom",
  options = [],
  loading = false,
  onSearch,
}: SearchableSelectProps) {
  const [open, setOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")
  const [titleOptions, setTitleOptions] = useState<TitleOption[]>([])
  const [loadingTitles, setLoadingTitles] = useState(false)
  const { toast } = useToast()

  const selectedOption =
    type === "titles"
      ? titleOptions.find((option) => option.value === value)
      : options.find((option) => option.value === value)

  // useEffect(() => {
  //   if (type === "titles" && open) {
  //     fetchAllTitles()
  //   }
  // }, [open, type])

  const fetchAllTitles = async () => {
    try {
      setLoadingTitles(true)
      const [revistas, dvds, artigos, livros] = await Promise.all([
        revistasAPI.getAll(0, 1000),
        dvdsAPI.getAll(0, 1000),
        artigosAPI.getAll(0, 1000),
        livrosAPI.getAll(0, 1000),
      ])

      const allOptions: TitleOption[] = [
        ...revistas.data.map((r) => ({
          value: r.id_revista.toString(),
          label: r.titulo,
          subtitle: `Revista - ${r.editora || "Sem editora"}`,
          type: "revista",
          originalId: r.id_revista,
        })),
        ...dvds.data.map((d) => ({
          value: d.id_dvd.toString(),
          label: d.titulo,
          subtitle: `DVD - ${d.distribuidora || "Sem distribuidora"}`,
          type: "dvd",
          originalId: d.id_dvd,
        })),
        ...artigos.data.map((a) => ({
          value: a.id_artigo.toString(),
          label: a.titulo,
          subtitle: `Artigo - ${a.publicadora || "Sem publicadora"}`,
          type: "artigo",
          originalId: a.id_artigo,
        })),
        ...livros.data.map((l) => ({
          value: l.id_livro.toString(),
          label: l.titulo,
          subtitle: `Livro - ${l.editora || "Sem editora"}`,
          type: "livro",
          originalId: l.id_livro,
        })),
      ]

      setTitleOptions(allOptions)
    } catch (error) {
      console.error("Error fetching titles:", error)
      toast({
        title: "Erro ao carregar títulos",
        description: "Não foi possível carregar a lista de títulos.",
        variant: "destructive",
      })
    } finally {
      setLoadingTitles(false)
    }
  }

  const searchTitles = async (query: string) => {
    // if (!query.trim()) {
    //   fetchAllTitles()
    //   return
    // }

    if(!query.trim())
        return

    try {
      setLoadingTitles(true)
      const [revistas, dvds, artigos, livros] = await Promise.all([
        revistasAPI.search(query).catch(() => ({ data: [] })),
        dvdsAPI.search(query).catch(() => ({ data: [] })),
        artigosAPI.search(query).catch(() => ({ data: [] })),
        livrosAPI.search(query).catch(() => ({ data: [] })),
      ])

      const searchResults: TitleOption[] = [
        ...revistas.data.map((r) => ({
          value: r.id_revista.toString(),
          label: r.titulo,
          subtitle: `Revista - ${r.editora || "Sem editora"}`,
          type: "revista",
          originalId: r.id_revista,
        })),
        ...dvds.data.map((d) => ({
          value: d.id_dvd.toString(),
          label: d.titulo,
          subtitle: `DVD - ${d.distribuidora || "Sem distribuidora"}`,
          type: "dvd",
          originalId: d.id_dvd,
        })),
        ...artigos.data.map((a) => ({
          value: a.id_artigo.toString(),
          label: a.titulo,
          subtitle: `Artigo - ${a.publicadora || "Sem publicadora"}`,
          type: "artigo",
          originalId: a.id_artigo,
        })),
        ...livros.data.map((l) => ({
          value: l.id_livro.toString(),
          label: l.titulo,
          subtitle: `Livro - ${l.editora || "Sem editora"}`,
          type: "livro",
          originalId: l.id_livro,
        })),
      ]

      setTitleOptions(searchResults)
    } catch (error) {
      console.error("Error searching titles:", error)
    } finally {
      setLoadingTitles(false)
    }
  }

  const handleSearch = (query: string) => {
    setSearchQuery(query)
    if (type === "titles") {
      searchTitles(query)
    } else if (onSearch) {
      onSearch(query)
    }
  }

  const currentOptions = type === "titles" ? titleOptions : options
  const isLoading = type === "titles" ? loadingTitles : loading

  const filteredOptions =
    type === "titles" || onSearch
      ? currentOptions
      : currentOptions.filter((option) => option.label.toLowerCase().includes(searchQuery.toLowerCase()))

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button variant="outline" role="combobox" aria-expanded={open} className={cn("justify-between", className)}>
          {selectedOption ? (
            <div className="flex flex-col items-start">
              <span>{selectedOption.label}</span>
              {selectedOption.subtitle && (
                <span className="text-xs text-muted-foreground">{selectedOption.subtitle}</span>
              )}
            </div>
          ) : (
            placeholder
          )}
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[400px] p-0">
        <Command>
          <CommandInput
            placeholder={searchPlaceholder}
            value={searchQuery}
            onValueChange={handleSearch}
            className="h-9"
          />
          <CommandList>
            <CommandEmpty>{isLoading ? "Carregando..." : "Nenhum resultado encontrado."}</CommandEmpty>
            <CommandGroup>
              {filteredOptions.map((option) => (
                <CommandItem
                  key={option.value}
                  value={option.value}
                  onSelect={(currentValue) => {
                    onValueChange(currentValue === value ? "" : currentValue)
                    setOpen(false)
                  }}
                >
                  <Check className={cn("mr-2 h-4 w-4", value === option.value ? "opacity-100" : "opacity-0")} />
                  <div className="flex flex-col">
                    <span>{option.label}</span>
                    {option.subtitle && <span className="text-xs text-muted-foreground">{option.subtitle}</span>}
                  </div>
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}
