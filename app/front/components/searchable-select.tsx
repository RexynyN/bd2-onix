"use client"

import * as React from "react"
import { Check, ChevronsUpDown, Search } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { estoqueAPI, type TituloSearch } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"

interface SearchableSelectProps {
  type: "titles"
  value?: string
  onValueChange?: (value: string) => void
  placeholder?: string
  searchPlaceholder?: string
  className?: string
}

export function SearchableSelect({
  type,
  value,
  onValueChange,
  placeholder = "Selecione uma opção...",
  searchPlaceholder = "Buscar...",
  className,
}: SearchableSelectProps) {
  const [open, setOpen] = React.useState(false)
  const [searchTerm, setSearchTerm] = React.useState("")
  const [options, setOptions] = React.useState<TituloSearch[]>([])
  const [loading, setLoading] = React.useState(false)
  const [selectedOption, setSelectedOption] = React.useState<TituloSearch | null>(null)
  const { toast } = useToast()

  // Search for titles when search term changes
  React.useEffect(() => {
    if (searchTerm.trim() && type === "titles") {
      searchTitles(searchTerm)
    } else {
      setOptions([])
    }
  }, [searchTerm, type])

  // Find selected option when value changes
  React.useEffect(() => {
    if (value && options.length > 0) {
      const found = options.find((option) => option.id_titulo.toString() === value)
      setSelectedOption(found || null)
    } else {
      setSelectedOption(null)
    }
  }, [value, options])

  const searchTitles = async (query: string) => {
    try {
      setLoading(true)
      const response = await estoqueAPI.searchTitles(query)
      setOptions(response.data)
    } catch (error) {
      console.error("Error searching titles:", error)
      toast({
        title: "Erro na busca",
        description: "Não foi possível buscar os títulos.",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleSelect = (option: TituloSearch) => {
    setSelectedOption(option)
    onValueChange?.(option.id_titulo.toString())
    setOpen(false)
  }

  const getDisplayValue = () => {
    if (selectedOption) {
      return `${selectedOption.titulo} (${selectedOption.tipo_midia})`
    }
    return placeholder
  }

  const getMediaTypeColor = (tipo: string) => {
    switch (tipo) {
      case "livro":
        return "bg-blue-100 text-blue-800"
      case "revista":
        return "bg-green-100 text-green-800"
      case "dvd":
        return "bg-purple-100 text-purple-800"
      case "artigo":
        return "bg-orange-100 text-orange-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className={cn("w-full justify-between", className)}
        >
          <span className="truncate">{getDisplayValue()}</span>
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-full p-0" align="start">
        <Command>
          <div className="flex items-center border-b px-3">
            <Search className="mr-2 h-4 w-4 shrink-0 opacity-50" />
            <CommandInput
              placeholder={searchPlaceholder}
              value={searchTerm}
              onValueChange={setSearchTerm}
              className="flex h-11 w-full rounded-md bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50"
            />
          </div>
          <CommandList>
            {loading && <div className="py-6 text-center text-sm">Buscando títulos...</div>}
            {!loading && searchTerm && options.length === 0 && <CommandEmpty>Nenhum título encontrado.</CommandEmpty>}
            {!loading && !searchTerm && (
              <div className="py-6 text-center text-sm text-muted-foreground">Digite para buscar títulos...</div>
            )}
            {!loading && options.length > 0 && (
              <CommandGroup>
                {options.map((option) => (
                  <CommandItem
                    key={option.id_titulo}
                    value={option.id_titulo.toString()}
                    onSelect={() => handleSelect(option)}
                    className="flex items-center justify-between"
                  >
                    <div className="flex items-center gap-2">
                      <Check
                        className={cn(
                          "mr-2 h-4 w-4",
                          value === option.id_titulo.toString() ? "opacity-100" : "opacity-0",
                        )}
                      />
                      <div>
                        <div className="font-medium">{option.titulo}</div>
                        <div className="text-sm text-muted-foreground">ID: {option.id_titulo}</div>
                      </div>
                    </div>
                    <span
                      className={cn("px-2 py-1 rounded-full text-xs font-medium", getMediaTypeColor(option.tipo_midia))}
                    >
                      {option.tipo_midia}
                    </span>
                  </CommandItem>
                ))}
              </CommandGroup>
            )}
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}
