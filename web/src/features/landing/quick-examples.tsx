import { motion } from "framer-motion"
import { useNavigate } from "react-router-dom"
import { Badge } from "@/components/ui/badge"
import { EXAMPLE_QUERIES } from "@/features/landing/example-queries"

export function QuickExamples() {
  const navigate = useNavigate()

  return (
    <div className="flex flex-wrap items-center justify-center gap-2">
      {EXAMPLE_QUERIES.map((example, i) => (
        <motion.button
          key={example.text}
          type="button"
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 + i * 0.08, duration: 0.4 }}
          onClick={() =>
            navigate("/chat", { state: { prefill: example.text } })
          }
          dir={example.language === "arabic" ? "rtl" : "ltr"}
          className="group flex items-center gap-2 rounded-full border border-border bg-card/60 px-4 py-2 text-sm text-foreground/80 backdrop-blur transition-colors hover:border-primary/40 hover:bg-card hover:text-foreground"
        >
          <span>{example.text}</span>
          <Badge
            variant="secondary"
            className="hidden text-[10px] font-normal sm:inline-flex"
          >
            {example.description}
          </Badge>
        </motion.button>
      ))}
    </div>
  )
}
