import { motion } from "framer-motion"
import { useNavigate } from "react-router-dom"
import { ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { AnimatedBackground } from "@/features/landing/animated-background"
import { QuickExamples } from "@/features/landing/quick-examples"

export function HeroSection() {
  const navigate = useNavigate()

  return (
    <section className="relative flex flex-col items-center px-4 pt-20 pb-16 text-center sm:pt-28 sm:pb-24">
      <AnimatedBackground />

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Badge
          variant="outline"
          className="mb-6 border-primary/30 bg-primary/5 text-primary"
        >
          Arabic + English · Hybrid Retrieval · UAE Geospatial Data
        </Badge>
      </motion.div>

      <motion.h1
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.08 }}
        className="max-w-3xl text-balance font-heading text-4xl font-semibold tracking-tight text-foreground sm:text-6xl"
      >
        Geospatial intelligence,{" "}
        <span className="bg-gradient-to-r from-cyan-500 to-violet-500 bg-clip-text text-transparent">
          in your language
        </span>
      </motion.h1>

      <motion.p
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.16 }}
        className="mt-5 max-w-xl text-pretty text-base text-muted-foreground sm:text-lg"
      >
        Ask MANARA about satellite imagery, road networks, and analytics
        across the UAE — in Arabic or English — and see exactly which
        documents and confidence scores it drew from.
      </motion.p>

      <motion.div
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.24 }}
        className="mt-8"
      >
        <Button
          size="lg"
          onClick={() => navigate("/chat")}
          className="group gap-2"
        >
          Start Chat
          <ArrowRight className="size-4 transition-transform group-hover:translate-x-0.5" />
        </Button>
      </motion.div>

      <div className="mt-12 w-full max-w-2xl">
        <QuickExamples />
      </div>
    </section>
  )
}
