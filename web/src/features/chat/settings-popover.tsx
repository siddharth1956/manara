import { Settings } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"

/**
 * Intentionally inert — settings are not yet implemented, and this
 * says so plainly rather than pretending to be a working panel.
 */
export function SettingsPopover() {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon" aria-label="Settings">
          <Settings className="size-4" />
        </Button>
      </PopoverTrigger>
      <PopoverContent align="end" className="w-72 text-sm">
        <p className="font-medium text-foreground">Settings</p>
        <p className="mt-1 text-muted-foreground">
          Not built yet — this phase covers the chat workspace itself.
          Model info, retrieval preferences, and account settings land in
          a later phase.
        </p>
      </PopoverContent>
    </Popover>
  )
}
