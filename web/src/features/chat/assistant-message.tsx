import { useEffect, useRef, useState } from "react"
import { motion, AnimatePresence, useReducedMotion } from "framer-motion"
import type { ChatMessage } from "@/types/chat"
import { ThinkingIndicator } from "@/features/chat/thinking-indicator"
import { MessageSkeleton } from "@/features/chat/message-skeleton"
import { MessageBubble } from "@/features/chat/message-bubble"

const REVEAL_HOLD_MS = 260 // within the agreed 150-300ms fade-in window

/**
 * Renders one assistant message through its full lifecycle:
 * pending -> (brief skeleton hold) -> fade-in real content.
 *
 * The skeleton hold only plays when a message transitions from
 * pending to complete *within this component's lifetime* (tracked via
 * a ref, not global state) — a message loaded from localStorage that
 * mounts already-complete renders immediately, with no replayed
 * animation on every page load.
 */
export function AssistantMessage({ message }: { message: ChatMessage }) {
  const reduceMotion = useReducedMotion()
  const previousStatus = useRef(message.status)
  const [phase, setPhase] = useState<"pending" | "revealing" | "settled">(
    message.status === "pending" ? "pending" : "settled",
  )

  useEffect(() => {
    const wasPending = previousStatus.current === "pending"
    previousStatus.current = message.status

    if (!wasPending || message.status === "pending") return

    // A pending -> error transition must also clear `phase` out of
    // "pending", not just pending -> complete — the render check below
    // tests `phase === "pending"` first, so otherwise an error response
    // would get stuck showing the thinking indicator forever even
    // though `message.status` had correctly become "error". Errors
    // settle immediately (no reveal-hold flourish in front of a
    // failure); only a genuine "complete" gets the hold.
    if (message.status === "error") {
      setPhase("settled")
      return
    }

    setPhase("revealing")
    const timer = setTimeout(() => setPhase("settled"), REVEAL_HOLD_MS)
    return () => clearTimeout(timer)
  }, [message.status])

  if (message.status === "pending" || phase === "pending") {
    return <ThinkingIndicator />
  }

  // Errors render immediately — a fake "materializing" delay in front
  // of a failure message reads as broken, not premium.
  if (message.status === "error") {
    return <MessageBubble message={message} />
  }

  if (phase === "revealing") {
    return <MessageSkeleton />
  }

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={message.id}
        initial={reduceMotion ? undefined : { opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.2 }}
      >
        <MessageBubble message={message} />
      </motion.div>
    </AnimatePresence>
  )
}
