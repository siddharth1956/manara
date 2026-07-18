import { memo } from "react"
import { Satellite, Route } from "lucide-react"
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import type { RetrievedDocument } from "@/types/api"
import { deriveDocumentTitle } from "@/utils/document-title"

interface DocumentListProps {
  sources: RetrievedDocument[]
}

function ConfidenceBar({ value }: { value: number }) {
  const clamped = Math.max(0, Math.min(100, value))
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-16 overflow-hidden rounded-full bg-muted">
        <div
          className="h-full rounded-full bg-primary"
          style={{ width: `${clamped}%` }}
        />
      </div>
      <span className="text-xs tabular-nums text-muted-foreground">
        {value.toFixed(1)}%
      </span>
    </div>
  )
}

const DocumentRow = memo(function DocumentRow({ doc }: { doc: RetrievedDocument }) {
  const Icon = doc.type === "satellite" ? Satellite : Route

  return (
    <AccordionItem value={doc.id} className="border-border/60 px-3">
      <AccordionTrigger className="gap-3 py-3 text-sm hover:no-underline">
        <div className="flex min-w-0 flex-1 items-center gap-2.5">
          <Icon className="size-4 shrink-0 text-muted-foreground" />
          <span className="min-w-0 flex-1 truncate text-left font-medium">
            {deriveDocumentTitle(doc)}
          </span>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          <Badge variant="secondary" className="text-[10px] capitalize">
            {doc.type}
          </Badge>
        </div>
      </AccordionTrigger>
      <AccordionContent className="space-y-2.5 pb-3 text-xs">
        <div className="flex items-center justify-between">
          <span className="text-muted-foreground">Confidence</span>
          <ConfidenceBar value={doc.confidence} />
        </div>
        <dl className="grid grid-cols-2 gap-x-3 gap-y-1.5">
          <dt className="text-muted-foreground">Platform</dt>
          <dd className="truncate text-right">{doc.platform || "—"}</dd>
          <dt className="text-muted-foreground">Constellation</dt>
          <dd className="truncate text-right">{doc.constellation || "—"}</dd>
          <dt className="text-muted-foreground">Captured</dt>
          <dd className="truncate text-right">{doc.datetime || "—"}</dd>
          <dt className="text-muted-foreground">Cloud cover</dt>
          <dd className="truncate text-right">
            {doc.cloud_cover !== null ? `${doc.cloud_cover}%` : "—"}
          </dd>
          <dt className="text-muted-foreground">Distance</dt>
          <dd className="truncate text-right">{doc.distance.toFixed(2)}</dd>
          <dt className="text-muted-foreground">Bounding box</dt>
          <dd className="truncate text-right font-mono">{doc.bbox || "—"}</dd>
        </dl>
        <p className="rounded-md bg-muted/50 p-2 whitespace-pre-wrap text-muted-foreground">
          {doc.text.trim()}
        </p>
      </AccordionContent>
    </AccordionItem>
  )
})

export function DocumentList({ sources }: DocumentListProps) {
  if (sources.length === 0) {
    return (
      <p className="p-4 text-sm text-muted-foreground">
        No documents were retrieved for this query.
      </p>
    )
  }

  return (
    <ScrollArea className="h-full">
      <Accordion type="multiple" className="w-full pt-2">
        {sources.map((doc) => (
          <DocumentRow key={doc.id} doc={doc} />
        ))}
      </Accordion>
    </ScrollArea>
  )
}
