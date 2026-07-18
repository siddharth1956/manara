import type { RetrievedDocument } from "@/types/api"

/**
 * RetrievedDocument has no dedicated "title" field — this derives a
 * human-readable one from the same real fields the document already
 * carries (never fabricated). Road documents' `text` always contains
 * a "Road:\n{name}" line (see scripts/build_search_corpus.py); for
 * satellite documents there's no equivalent human name, so platform +
 * capture date is the most legible real substitute.
 */
export function deriveDocumentTitle(doc: RetrievedDocument): string {
  if (doc.type === "roads") {
    const match = /Road:\s*\n([^\n]+)/.exec(doc.text)
    if (match?.[1]?.trim()) return match[1].trim()
  }

  if (doc.type === "satellite" && doc.datetime) {
    const date = new Date(doc.datetime)
    if (!Number.isNaN(date.getTime())) {
      const formatted = new Intl.DateTimeFormat(undefined, {
        dateStyle: "medium",
      }).format(date)
      return `${doc.platform || "Satellite"} — ${formatted}`
    }
  }

  return doc.id
}
