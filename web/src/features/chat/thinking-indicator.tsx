import { motion, useReducedMotion } from "framer-motion"
import { Sparkles } from "lucide-react"

/**
 * Premium "thinking" indicator — three dots with a staggered pulse.
 * No fake streaming text, per the agreed loading UX: this only ever
 * signals "working", it never simulates partial output.
 */
export function ThinkingIndicator() {
  const reduceMotion = useReducedMotion()

  return (
    <div
      className="flex items-center gap-3"
      role="status"
      aria-label="MANARA is thinking"
    >
      <div className="flex size-7 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
        <Sparkles className="size-3.5" />
      </div>
      <div className="flex items-center gap-1.5 rounded-2xl border border-border/60 bg-card px-4 py-3">
        {[0, 1, 2].map((i) => (
          <motion.span
            key={i}
            className="size-1.5 rounded-full bg-muted-foreground/60"
            animate={
              reduceMotion
                ? { opacity: [0.4, 1, 0.4] }
                : { y: [0, -4, 0], opacity: [0.4, 1, 0.4] }
            }
            transition={{
              duration: 1.1,
              repeat: Infinity,
              delay: i * 0.15,
              ease: "easeInOut",
            }}
          />
        ))}
      </div>
    </div>
  )
}
