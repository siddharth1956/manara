import { memo, useEffect, useRef } from "react"
import type { ChatMessage } from "@/types/chat"
import { MessageBubble } from "@/features/chat/message-bubble"
import { AssistantMessage } from "@/features/chat/assistant-message"
import { ChatEmptyState } from "@/features/chat/chat-empty-state"

interface MessageListProps {
  messages: ChatMessage[]
  onExampleSelect: (text: string) => void
}

export const MessageList = memo(function MessageList({ messages, onExampleSelect }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" })
  }, [messages])

  if (messages.length === 0) {
    return <ChatEmptyState onExampleSelect={onExampleSelect} />
  }

  return (
    <div
      role="log"
      aria-live="polite"
      aria-relevant="additions"
      aria-label="Conversation"
      className="mx-auto flex w-full max-w-3xl flex-col gap-6 px-4 py-6 sm:px-6"
    >
      {messages.map((message) =>
        message.role === "user" ? (
          <MessageBubble key={message.id} message={message} />
        ) : (
          <AssistantMessage key={message.id} message={message} />
        ),
      )}
      <div ref={bottomRef} aria-hidden="true" />
    </div>
  )
})
