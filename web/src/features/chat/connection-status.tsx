import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import { cn } from "@/lib/utils"

export type ConnectionState = "connected" | "disconnected" | "checking"

const CONFIG: Record<ConnectionState, { label: string; dotClass: string }> = {
  connected: { label: "Connected", dotClass: "bg-emerald-500" },
  disconnected: { label: "Not connected", dotClass: "bg-muted-foreground/50" },
  checking: { label: "Checking…", dotClass: "bg-amber-500 animate-pulse" },
}

interface ConnectionStatusProps {
  state: ConnectionState
  detail?: string
}

export function ConnectionStatus({ state, detail }: ConnectionStatusProps) {
  const config = CONFIG[state]

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <div className="flex items-center gap-1.5" role="status" aria-label={config.label}>
          <span
            className={cn("size-2 rounded-full", config.dotClass)}
            aria-hidden="true"
          />
          <span className="hidden text-xs text-muted-foreground sm:inline" aria-hidden="true">
            {config.label}
          </span>
        </div>
      </TooltipTrigger>
      <TooltipContent>{detail ?? config.label}</TooltipContent>
    </Tooltip>
  )
}
