import { useEffect, useRef, type KeyboardEvent } from "react"
import { ArrowUp, Square } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import { detectLanguage } from "@/utils/detect-language"

const MAX_LENGTH = 2000
const MAX_TEXTAREA_HEIGHT_PX = 200

interface ChatInputProps {
  value: string
  onChange: (value: string) => void
  onSend: (text: string) => void
  onStop: () => void
  isBusy: boolean
}

export function ChatInput({ value, onChange, onSend, onStop, isBusy }: ChatInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Auto-grow, capped at MAX_TEXTAREA_HEIGHT_PX with internal scroll beyond that.
  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = "auto"
    el.style.height = `${Math.min(el.scrollHeight, MAX_TEXTAREA_HEIGHT_PX)}px`
  }, [value])

  const submit = () => {
    const trimmed = value.trim()
    if (!trimmed || isBusy) return
    onSend(trimmed)
    onChange("")
  }

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault()
      submit()
    }
  }

  const direction = value.trim() ? (detectLanguage(value) === "arabic" ? "rtl" : "ltr") : "ltr"

  return (
    <div className="mx-auto w-full max-w-3xl px-4 pb-4 sm:px-6">
      <div className="flex items-end gap-2 rounded-2xl border border-border bg-card p-2 shadow-sm focus-within:border-primary/50 focus-within:ring-2 focus-within:ring-ring/30">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => onChange(e.target.value.slice(0, MAX_LENGTH))}
          onKeyDown={handleKeyDown}
          dir={direction}
          rows={1}
          disabled={isBusy}
          placeholder="Ask about roads, satellite imagery, or analytics… · اسأل عن الطرق أو الصور الفضائية"
          aria-label="Message MANARA"
          className="max-h-[200px] flex-1 resize-none bg-transparent px-2 py-2 text-[0.9375rem] leading-relaxed outline-none placeholder:text-muted-foreground disabled:opacity-60"
        />

        <div className="flex shrink-0 items-center gap-2 pb-1">
          {value.length > MAX_LENGTH * 0.8 && (
            <span
              className="text-xs tabular-nums text-muted-foreground"
              aria-live="polite"
            >
              {value.length}/{MAX_LENGTH}
            </span>
          )}

          {isBusy ? (
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  size="icon"
                  variant="secondary"
                  onClick={onStop}
                  aria-label="Stop generating"
                  className="size-9 rounded-xl"
                >
                  <Square className="size-3.5 fill-current" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Stop generating</TooltipContent>
            </Tooltip>
          ) : (
            <Button
              size="icon"
              onClick={submit}
              disabled={!value.trim()}
              aria-label="Send message"
              className="size-9 rounded-xl"
            >
              <ArrowUp className="size-4" />
            </Button>
          )}
        </div>
      </div>
      <p className="mt-2 text-center text-xs text-muted-foreground">
        MANARA can make mistakes. Verify important geospatial information.
      </p>
    </div>
  )
}
