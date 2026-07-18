import { Sparkles } from "lucide-react"
import { Skeleton } from "@/components/ui/skeleton"

/** Shown briefly after the thinking indicator, just before real content
 * fades in — signals "content is materializing" rather than "still working". */
export function MessageSkeleton() {
  return (
    <div className="flex w-full gap-3" aria-hidden="true">
      <div className="mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
        <Sparkles className="size-3.5" />
      </div>
      <div className="flex max-w-[75%] flex-1 flex-col gap-2 rounded-2xl border border-border/60 bg-card px-4 py-3">
        <Skeleton className="h-3.5 w-4/5" />
        <Skeleton className="h-3.5 w-full" />
        <Skeleton className="h-3.5 w-3/5" />
      </div>
    </div>
  )
}
