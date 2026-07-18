import { memo } from "react"
import { Sheet, SheetContent, SheetTitle } from "@/components/ui/sheet"
import { useMediaQuery } from "@/hooks/use-media-query"
import { IntelligencePanelContent } from "@/features/intelligence/intelligence-panel-content"
import type { ChatMessage } from "@/types/chat"

interface IntelligencePanelProps {
  message: ChatMessage | null
  /** Only meaningful below the lg breakpoint, where the panel is a
   * Sheet rather than a persistent column. */
  open: boolean
  onOpenChange: (open: boolean) => void
}

/**
 * Desktop (lg, >=1024px): persistent third column, always visible —
 * "three-column layout" per the brief, not toggleable.
 * Tablet (sm-lg, 640-1023px): collapsible — a right-side Sheet,
 * closed by default, opened via the header's Inspector button.
 * Mobile (<640px): bottom sheet, same trigger.
 */
export const IntelligencePanel = memo(function IntelligencePanel({
  message,
  open,
  onOpenChange,
}: IntelligencePanelProps) {
  const isDesktop = useMediaQuery("(min-width: 1024px)")
  const isTablet = useMediaQuery("(min-width: 640px)")

  if (isDesktop) {
    return (
      <aside className="hidden w-96 shrink-0 border-l border-border/60 lg:block">
        <IntelligencePanelContent message={message} />
      </aside>
    )
  }

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent
        side={isTablet ? "right" : "bottom"}
        className={isTablet ? "w-96 p-0" : "h-[85svh] rounded-t-2xl p-0"}
      >
        <SheetTitle className="sr-only">Retrieval intelligence</SheetTitle>
        <IntelligencePanelContent message={message} />
      </SheetContent>
    </Sheet>
  )
})
