import { memo } from "react"
import { Menu, Telescope } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import { ThemeToggle } from "@/components/shared/theme-toggle"
import { SettingsPopover } from "@/features/chat/settings-popover"
import { ConnectionStatus } from "@/features/chat/connection-status"
import { useConnectionStatus } from "@/hooks/use-connection-status"
import type { Conversation } from "@/types/chat"

const STATUS_DETAIL: Record<string, string> = {
  connected: "Connected to the MANARA backend",
  disconnected: "Can't reach the MANARA backend — check that it's running",
  checking: "Checking connection to the MANARA backend…",
}

interface ChatHeaderProps {
  conversation: Conversation | null
  onOpenMobileSidebar: () => void
  onOpenInspector: () => void
}

export const ChatHeader = memo(function ChatHeader({
  conversation,
  onOpenMobileSidebar,
  onOpenInspector,
}: ChatHeaderProps) {
  const lastLanguage = [...(conversation?.messages ?? [])]
    .reverse()
    .find((m) => m.role === "user")?.language
  const connectionState = useConnectionStatus()

  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b border-border/60 px-3 sm:px-4">
      <div className="flex min-w-0 items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          className="lg:hidden"
          onClick={onOpenMobileSidebar}
          aria-label="Open sidebar"
        >
          <Menu className="size-4" />
        </Button>
        <h1 className="truncate text-sm font-medium text-foreground">
          {conversation?.title ?? "New chat"}
        </h1>
        {lastLanguage && (
          <Badge variant="secondary" className="hidden shrink-0 text-[11px] sm:inline-flex">
            {lastLanguage === "arabic" ? "العربية" : "English"}
          </Badge>
        )}
      </div>

      <div className="flex items-center gap-1">
        <ConnectionStatus
          state={connectionState}
          detail={STATUS_DETAIL[connectionState]}
        />
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden"
              onClick={onOpenInspector}
              aria-label="Open retrieval intelligence panel"
            >
              <Telescope className="size-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>Retrieval intelligence</TooltipContent>
        </Tooltip>
        <SettingsPopover />
        <ThemeToggle />
      </div>
    </header>
  )
})
