import { lazy, Suspense, useState } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Separator } from "@/components/ui/separator"
import { RetrievalInspector } from "@/features/intelligence/retrieval-inspector"
import { EntityViewer } from "@/features/intelligence/entity-viewer"
import { DocumentList } from "@/features/intelligence/document-list"
import type { ChatMessage } from "@/types/chat"

// Leaflet (~150KB) and its CSS are only worth loading once a user
// actually wants the map — not on every page that renders this panel.
const MapPanel = lazy(() =>
  import("@/features/intelligence/map-panel").then((m) => ({ default: m.MapPanel })),
)

interface IntelligencePanelContentProps {
  message: ChatMessage | null
}

export function IntelligencePanelContent({ message }: IntelligencePanelContentProps) {
  const [activeTab, setActiveTab] = useState("overview")

  if (!message?.meta) {
    return (
      <div className="flex h-full items-center justify-center p-6 text-center">
        <p className="text-sm text-muted-foreground">
          Send a message to see retrieval details here.
        </p>
      </div>
    )
  }

  const { meta } = message

  return (
    <Tabs value={activeTab} onValueChange={setActiveTab} className="flex h-full flex-col gap-0">
      <TabsList className="mx-3 mt-3 w-auto shrink-0">
        <TabsTrigger value="overview">Overview</TabsTrigger>
        <TabsTrigger value="sources">Sources ({meta.sources.length})</TabsTrigger>
        <TabsTrigger value="map">Map</TabsTrigger>
      </TabsList>

      <TabsContent value="overview" className="min-h-0 flex-1 overflow-y-auto">
        <RetrievalInspector message={message} />
        <Separator />
        <EntityViewer entities={meta.entities} />
      </TabsContent>

      <TabsContent value="sources" className="min-h-0 flex-1 overflow-hidden">
        <DocumentList sources={meta.sources} />
      </TabsContent>

      <TabsContent value="map" className="min-h-0 flex-1 overflow-hidden">
        <Suspense
          fallback={
            <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
              Loading map…
            </div>
          }
        >
          <MapPanel
            sources={meta.sources}
            entities={meta.entities}
            isActive={activeTab === "map"}
          />
        </Suspense>
      </TabsContent>
    </Tabs>
  )
}
