import { Badge } from "@/components/ui/badge"
import type { ChatMessage } from "@/types/chat"

interface RetrievalInspectorProps {
  message: ChatMessage
}

function formatLatency(ms: number): string {
  return ms < 1000 ? `${Math.round(ms)} ms` : `${(ms / 1000).toFixed(1)} s`
}

const INTENT_LABELS: Record<string, string> = {
  analytics: "Analytics",
  satellite_search: "Satellite search",
  road_search: "Road search",
  comparison: "Comparison",
  map: "Map",
  general: "General",
}

export function RetrievalInspector({ message }: RetrievalInspectorProps) {
  const meta = message.meta

  if (!meta) {
    return (
      <p className="p-4 text-sm text-muted-foreground">
        No retrieval data available for this message.
      </p>
    )
  }

  // The backend has no overall "confidence" field — only each
  // retrieved document has one. Documents are already returned
  // sorted by confidence (app/services/retriever.py), so the top
  // source's real confidence is the most honest stand-in for "how
  // confident was the best match", labeled unambiguously below
  // rather than presented as some separate AI-confidence figure.
  const topConfidence = meta.sources[0]?.confidence

  const stats: { label: string; value: string }[] = [
    { label: "Intent", value: INTENT_LABELS[meta.intent] ?? meta.intent },
    { label: "Language", value: message.language === "arabic" ? "العربية" : "English" },
    { label: "Latency", value: formatLatency(meta.latencyMs) },
    {
      label: "Top match confidence",
      value: topConfidence !== undefined ? `${topConfidence.toFixed(1)}%` : "N/A",
    },
    { label: "Sources retrieved", value: String(meta.sources.length) },
  ]

  return (
    <div className="space-y-4 p-4">
      <div className="grid grid-cols-2 gap-3">
        {stats.map((stat) => (
          <div key={stat.label} className="rounded-lg border border-border/60 bg-card/50 p-3">
            <p className="text-[11px] text-muted-foreground">{stat.label}</p>
            <p className="mt-0.5 text-sm font-medium text-foreground">{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="rounded-lg border border-border/60 bg-card/50 p-3">
        <p className="mb-1.5 text-[11px] text-muted-foreground">Query</p>
        <p dir="auto" className="text-sm text-foreground/90">
          {meta.question || "—"}
        </p>
      </div>

      <div className="flex flex-wrap gap-1.5">
        <Badge variant="outline" className="text-[11px]">
          {new Date(message.createdAt).toLocaleString()}
        </Badge>
      </div>
    </div>
  )
}
