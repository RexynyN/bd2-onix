"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Calendar } from "@/components/ui/calendar"
import { CalendarIcon, Filter, X } from "lucide-react"
import { format } from "date-fns"
import { ptBR } from "date-fns/locale"
import { cn } from "@/lib/utils"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export interface FilterConfig {
  key: string
  label: string
  type: "text" | "select" | "date" | "dateRange"
  options?: Array<{ value: string; label: string }>
  placeholder?: string
}

export interface FilterValues {
  [key: string]: any
}

interface AdvancedFiltersProps {
  filters: FilterConfig[]
  values: FilterValues
  onValuesChange: (values: FilterValues) => void
  onApply: () => void
  onClear: () => void
  className?: string
}

export function AdvancedFilters({
  filters,
  values,
  onValuesChange,
  onApply,
  onClear,
  className,
}: AdvancedFiltersProps) {
  const [isOpen, setIsOpen] = useState(false)

  const updateValue = (key: string, value: any) => {
    onValuesChange({ ...values, [key]: value })
  }

  const hasActiveFilters = Object.values(values).some((value) => {
    if (Array.isArray(value)) return value.length > 0
    return value !== "" && value !== null && value !== undefined
  })

  const renderFilterInput = (filter: FilterConfig) => {
    const value = values[filter.key]

    switch (filter.type) {
      case "text":
        return (
          <Input
            placeholder={filter.placeholder}
            value={value || ""}
            onChange={(e) => updateValue(filter.key, e.target.value)}
          />
        )

      case "select":
        return (
          <Select value={value || ""} onValueChange={(newValue) => updateValue(filter.key, newValue)}>
            <SelectTrigger>
              <SelectValue placeholder={filter.placeholder} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos</SelectItem>
              {filter.options?.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )

      case "date":
        return (
          <Popover>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                className={cn("justify-start text-left font-normal", !value && "text-muted-foreground")}
              >
                <CalendarIcon className="mr-2 h-4 w-4" />
                {value ? format(new Date(value), "PPP", { locale: ptBR }) : filter.placeholder}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0">
              <Calendar
                mode="single"
                selected={value ? new Date(value) : undefined}
                onSelect={(date) => updateValue(filter.key, date?.toISOString().split("T")[0])}
                initialFocus
              />
            </PopoverContent>
          </Popover>
        )

      case "dateRange":
        return (
          <div className="grid grid-cols-2 gap-2">
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className={cn("justify-start text-left font-normal", !value?.from && "text-muted-foreground")}
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {value?.from ? format(new Date(value.from), "PPP", { locale: ptBR }) : "Data inicial"}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0">
                <Calendar
                  mode="single"
                  selected={value?.from ? new Date(value.from) : undefined}
                  onSelect={(date) => updateValue(filter.key, { ...value, from: date?.toISOString().split("T")[0] })}
                  initialFocus
                />
              </PopoverContent>
            </Popover>
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className={cn("justify-start text-left font-normal", !value?.to && "text-muted-foreground")}
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {value?.to ? format(new Date(value.to), "PPP", { locale: ptBR }) : "Data final"}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0">
                <Calendar
                  mode="single"
                  selected={value?.to ? new Date(value.to) : undefined}
                  onSelect={(date) => updateValue(filter.key, { ...value, to: date?.toISOString().split("T")[0] })}
                  initialFocus
                />
              </PopoverContent>
            </Popover>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className={className}>
      <Popover open={isOpen} onOpenChange={setIsOpen}>
        <PopoverTrigger asChild>
          <Button variant="outline" className="relative">
            <Filter className="mr-2 h-4 w-4" />
            Filtros Avançados
            {hasActiveFilters && (
              <span className="absolute -top-1 -right-1 h-3 w-3 bg-primary rounded-full text-xs flex items-center justify-center text-primary-foreground">
                {Object.values(values).filter((v) => v && v !== "").length}
              </span>
            )}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-96 p-0" align="start">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Filtros Avançados</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {filters.map((filter) => (
                <div key={filter.key} className="space-y-2">
                  <Label htmlFor={filter.key} className="text-sm font-medium">
                    {filter.label}
                  </Label>
                  {renderFilterInput(filter)}
                </div>
              ))}
              <div className="flex gap-2 pt-4">
                <Button onClick={onApply} size="sm" className="flex-1">
                  Aplicar
                </Button>
                <Button onClick={onClear} variant="outline" size="sm" className="flex-1">
                  <X className="mr-2 h-4 w-4" />
                  Limpar
                </Button>
              </div>
            </CardContent>
          </Card>
        </PopoverContent>
      </Popover>
    </div>
  )
}
