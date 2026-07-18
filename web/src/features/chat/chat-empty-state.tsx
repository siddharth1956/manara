import { motion } from "framer-motion"
import { Logo } from "@/components/shared/logo"
import { EXAMPLE_QUERIES } from "@/features/landing/example-queries"

interface ChatEmptyStateProps {
  onExampleSelect: (text: string) => void
}

export function ChatEmptyState({ onExampleSelect }: ChatEmptyStateProps) {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-6 px-4 text-center">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
      >
        <Logo className="scale-150" />
      </motion.div>

      <div className="space-y-1.5">
        <h2 className="text-lg font-semibold text-foreground">
          Ask MANARA anything
        </h2>
        <p className="max-w-sm text-sm text-muted-foreground">
          Satellite imagery, road networks, and analytics across the UAE —
          in Arabic or English.
        </p>
      </div>

      <div className="flex max-w-md flex-wrap items-center justify-center gap-2">
        {EXAMPLE_QUERIES.map((example) => (
          <button
            key={example.text}
            type="button"
            dir={example.language === "arabic" ? "rtl" : "ltr"}
            onClick={() => onExampleSelect(example.text)}
            className="rounded-full border border-border bg-card/60 px-3.5 py-1.5 text-sm text-foreground/80 transition-colors hover:border-primary/40 hover:bg-card hover:text-foreground"
          >
            {example.text}
          </button>
        ))}
      </div>
    </div>
  )
}
