import { memo } from "react"
import { motion, useReducedMotion } from "framer-motion"
import { AlertTriangle, Sparkles, User } from "lucide-react"
import type { ChatMessage } from "@/types/chat"
import { MarkdownRenderer } from "@/features/chat/markdown-renderer"
import { formatTimestamp } from "@/utils/format-time"
import { detectLanguage } from "@/utils/detect-language"
import { cn } from "@/lib/utils"

interface MessageBubbleProps {
  message: ChatMessage
}

export const MessageBubble = memo(function MessageBubble({
  message,
}: MessageBubbleProps) {
  const reduceMotion = useReducedMotion()
  const isUser = message.role === "user"

  // Deliberately re-detected from the message's own content rather than
  // trusting `message.language` directly: for assistant messages, that
  // field reflects the QUERY's detected language (mirroring the real
  // backend's QueryResponse.language, which is query-language, not
  // answer-language — see app/main.py). A query and its answer usually
  // match, but nothing guarantees it, and rendering English content
  // right-aligned under dir="rtl" because the question happened to be
  // Arabic reads as broken. Re-detecting from actual content is robust
  // to real backend behavior, not just this phase's mock data.
  const direction = detectLanguage(message.content) === "arabic" ? "rtl" : "ltr"

  return (
    <motion.div
      initial={reduceMotion ? undefined : { opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      dir={direction}
      className={cn(
        // min-w-0 is load-bearing: this row is itself a flex item of
        // MessageList's flex-col container, and flex items default to
        // min-width:auto (their content's intrinsic width) unless
        // overridden — without this, a long unbroken token (e.g. a
        // document ID) forces the whole row wider than the viewport
        // instead of wrapping inside the bubble. Found via testing
        // with a long unbroken string, not assumed.
        "flex w-full min-w-0 gap-3",
        isUser ? "justify-end" : "justify-start",
      )}
    >
      {!isUser && (
        <div
          className="mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary"
          aria-hidden="true"
        >
          <Sparkles className="size-3.5" />
        </div>
      )}

      <div
        className={cn(
          "flex min-w-0 max-w-[85%] flex-col gap-1 sm:max-w-[75%]",
          isUser && "items-end",
        )}
      >
        <div
          className={cn(
            // max-w-full (not just min-w-0) is required here: the parent
            // column uses items-end to right-align user bubbles, and
            // align-items other than the flex default `stretch` makes a
            // flex item revert to content-based (shrink-to-fit) sizing —
            // min-w-0 alone only removes the lower bound, it doesn't cap
            // growth, so an unbroken long token could still force this
            // element wider than its already-capped parent. Found via
            // computed-style inspection, not assumed.
            "min-w-0 max-w-full rounded-2xl px-4 py-2.5 text-[0.9375rem]",
            isUser
              ? "bg-primary text-primary-foreground"
              : message.status === "error"
                ? "border border-destructive/30 bg-destructive/5 text-foreground"
                : "border border-border/60 bg-card text-card-foreground",
          )}
        >
          {message.status === "error" && (
            <div className="mb-1.5 flex items-center gap-1.5 text-xs font-medium text-destructive">
              <AlertTriangle className="size-3.5" />
              Something went wrong
            </div>
          )}
          {isUser ? (
            <p className="whitespace-pre-wrap break-words leading-relaxed">
              {message.content}
            </p>
          ) : (
            <MarkdownRenderer content={message.content} />
          )}
        </div>

        <span className="px-1 text-[11px] text-muted-foreground">
          {formatTimestamp(message.createdAt)}
        </span>
      </div>

      {isUser && (
        <div
          className="mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-full bg-secondary text-secondary-foreground"
          aria-hidden="true"
        >
          <User className="size-3.5" />
        </div>
      )}
    </motion.div>
  )
})
