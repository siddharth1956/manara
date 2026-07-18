import { Languages } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import { useDirection } from "@/hooks/use-direction"

export function DirectionToggle() {
  const { direction, toggleDirection } = useDirection()
  const isRtl = direction === "rtl"

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleDirection}
          aria-label={isRtl ? "Switch layout to left-to-right" : "التبديل إلى اتجاه من اليمين لليسار"}
        >
          <Languages className="size-4" />
        </Button>
      </TooltipTrigger>
      <TooltipContent>{isRtl ? "LTR" : "RTL · العربية"}</TooltipContent>
    </Tooltip>
  )
}
