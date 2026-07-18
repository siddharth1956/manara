/**
 * Types mirroring MANARA's FastAPI contract exactly, as implemented in
 * app/main.py and app/services/retriever.py. Do not add fields the
 * backend doesn't actually return — see CLAUDE.md / project history
 * for why (e.g. `entities.platform` is checked by the retriever's
 * boost logic but no NLU pipeline currently ever populates it).
 */

export type Language = "english" | "arabic"

export type Intent =
  | "analytics"
  | "satellite_search"
  | "road_search"
  | "comparison"
  | "map"
  | "general"

/** Sparse — English NLU only includes keys it actually found; Arabic NER
 * always includes location/metric but may set them to null. */
export interface QueryEntities {
  location?: string | null
  satellite?: string | null
  metric?: string | null
  date?: string | null
}

export interface RetrievedDocument {
  id: string
  type: "satellite" | "roads" | string
  platform: string
  constellation: string
  datetime: string
  cloud_cover: number | null
  /** Stringified list, e.g. "[54.9, 24.8, 55.5, 25.3]" — parse with parseBbox(). */
  bbox: string
  confidence: number
  distance: number
  text: string
}

/** Previous turn's intent/entities — lets the backend resolve a
 * follow-up like "What about Abu Dhabi?" without repeating the topic.
 * Optional; omitted entirely for a conversation's first message. */
export interface QueryContext {
  intent: Intent
  entities: QueryEntities
}

export interface QueryRequest {
  question: string
  context?: QueryContext
}

export interface QueryResponse {
  question: string
  language: Language
  intent: Intent
  entities: QueryEntities
  answer: string
  sources: RetrievedDocument[]
}

export interface ApiErrorBody {
  detail: string
}
