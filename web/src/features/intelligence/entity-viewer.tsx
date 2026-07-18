import { MapPin, Calendar, Satellite, Gauge, Layers } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import type { QueryEntities } from "@/types/api"

interface EntityRow {
  key: keyof QueryEntities | "platform"
  label: string
  icon: typeof MapPin
  value: string | null | undefined
}

interface EntityViewerProps {
  entities: QueryEntities | undefined
}

export function EntityViewer({ entities }: EntityViewerProps) {
  const rows: EntityRow[] = [
    { key: "location", label: "Location", icon: MapPin, value: entities?.location },
    { key: "date", label: "Date", icon: Calendar, value: entities?.date },
    { key: "satellite", label: "Satellite", icon: Satellite, value: entities?.satellite },
    { key: "metric", label: "Metric", icon: Gauge, value: entities?.metric },
    // The backend's retrieval boost logic checks entities.platform, but
    // neither NLU pipeline (English or Arabic) ever populates it — a
    // pre-existing gap in the backend, not something to fake here.
    // Shown for completeness; will always read "None detected" today.
    { key: "platform", label: "Platform", icon: Layers, value: undefined },
  ]

  const anyDetected = rows.some((r) => r.value)

  return (
    <div className="space-y-3 p-4">
      {!anyDetected && (
        <p className="text-sm text-muted-foreground">
          No entities were detected for this query.
        </p>
      )}

      {rows.map((row) => (
        <div key={row.key} className="flex items-center justify-between gap-3">
          <span className="flex items-center gap-2 text-sm text-muted-foreground">
            <row.icon className="size-4" />
            {row.label}
          </span>
          {row.value ? (
            <Badge variant="secondary" className="max-w-[60%] truncate">
              {row.value}
            </Badge>
          ) : (
            <span className="text-xs text-muted-foreground/60">None detected</span>
          )}
        </div>
      ))}
    </div>
  )
}
