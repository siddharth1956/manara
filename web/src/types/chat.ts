import type { Language, RetrievedDocument, QueryEntities, Intent } from "@/types/api"

export type MessageRole = "user" | "assistant"
export type MessageStatus = "pending" | "complete" | "error"

export interface ChatMessage {
  id: string
  role: MessageRole
  content: string
  language: Language
  status: MessageStatus
  createdAt: number
  /** Populated on assistant messages once resolved — mirrors the real
   * QueryResponse shape (including the backend's own echoed
   * `question`, used by the Retrieval Inspector so it doesn't need to
   * re-derive the query text from conversation order). */
  meta?: {
    question: string
    intent: Intent
    entities: QueryEntities
    sources: RetrievedDocument[]
    latencyMs: number
  }
}

export interface Conversation {
  id: string
  title: string
  messages: ChatMessage[]
  createdAt: number
  updatedAt: number
}
