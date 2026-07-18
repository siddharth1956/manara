/**
 * Representative queries actually verified against this system during
 * development (see project history) — not illustrative copy. Each one
 * exercises a distinct real capability: English/Arabic NLU, hybrid
 * FAISS+BM25 retrieval, intent classification, and entity extraction.
 */
export interface ExampleQuery {
  text: string
  language: "english" | "arabic"
  description: string
}

export const EXAMPLE_QUERIES: ExampleQuery[] = [
  {
    text: "Show Dubai roads",
    language: "english",
    description: "Road network retrieval",
  },
  {
    text: "ما هو متوسط الغطاء السحابي؟",
    language: "arabic",
    description: "Arabic analytics query",
  },
  {
    text: "Show satellite images of Dubai",
    language: "english",
    description: "Satellite imagery search",
  },
  {
    text: "قارن بين Sentinel-2A و Sentinel-2B",
    language: "arabic",
    description: "Arabic comparison query",
  },
]
