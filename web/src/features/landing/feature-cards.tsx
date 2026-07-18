import { motion } from "framer-motion"
import { Languages, Network, Satellite, Gauge } from "lucide-react"
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card"

/**
 * Describes capabilities this system actually implements — not
 * aspirational marketing copy. See app/services/arabic/ (bilingual
 * NLU), app/services/retriever.py (hybrid RRF retrieval),
 * scripts/build_search_corpus.py (the satellite + road corpus), and
 * the confidence field on every retrieved document.
 */
const FEATURES = [
  {
    icon: Languages,
    title: "Bilingual by design",
    description:
      "A dedicated Arabic NLP pipeline — normalization, tokenization, entity extraction, and intent classification — alongside English, not a translation layer bolted on top.",
  },
  {
    icon: Network,
    title: "Hybrid retrieval",
    description:
      "Dense semantic search (FAISS) and lexical search (BM25) fused with Reciprocal Rank Fusion, so exact names and conceptual queries both get a fair shot.",
  },
  {
    icon: Satellite,
    title: "Real geospatial data",
    description:
      "1,920 indexed documents spanning Sentinel-2 satellite imagery and the Dubai OpenStreetMap road network — down to individually named roads.",
  },
  {
    icon: Gauge,
    title: "Transparent confidence",
    description:
      "Every answer is grounded in retrieved sources, each with its own confidence score and intent/entity match — inspectable, not a black box.",
  },
]

export function FeatureCards() {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {FEATURES.map((feature, i) => (
        <motion.div
          key={feature.title}
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-40px" }}
          transition={{ delay: i * 0.08, duration: 0.45 }}
        >
          <Card className="h-full border-border/60 bg-card/50 backdrop-blur transition-colors hover:border-primary/30">
            <CardHeader>
              <div className="mb-2 flex size-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <feature.icon className="size-5" strokeWidth={1.75} />
              </div>
              <CardTitle className="text-base">{feature.title}</CardTitle>
              <CardDescription className="leading-relaxed">
                {feature.description}
              </CardDescription>
            </CardHeader>
          </Card>
        </motion.div>
      ))}
    </div>
  )
}
