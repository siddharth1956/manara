import { useCallback, useEffect, useMemo, useRef, useState } from "react"
import { useLocation } from "react-router-dom"
import { toast } from "sonner"
import { Sheet, SheetContent, SheetTitle } from "@/components/ui/sheet"
import { ChatSidebar } from "@/features/chat/chat-sidebar"
import { ChatHeader } from "@/features/chat/chat-header"
import { MessageList } from "@/features/chat/message-list"
import { ChatInput } from "@/features/chat/chat-input"
import { ChatProvider, useChat } from "@/features/chat/chat-context"
import { IntelligencePanel } from "@/features/intelligence/intelligence-panel"
import { queryManara, ApiError } from "@/services/api"
import { detectLanguage } from "@/utils/detect-language"
import type { ChatMessage, Conversation } from "@/types/chat"
import type { QueryContext } from "@/types/api"

const SIDEBAR_COLLAPSED_KEY = "manara-sidebar-collapsed"

// Lets a follow-up ("What about Abu Dhabi?") inherit the previous
// turn's topic instead of the backend treating it as a fresh,
// unrelated "general" query — see app/services/conversation_router.py.
function lastTurnContext(conversation: Conversation | null): QueryContext | undefined {
  const messages = conversation?.messages ?? []
  for (let i = messages.length - 1; i >= 0; i--) {
    const message = messages[i]
    if (message.role === "assistant" && message.meta) {
      return { intent: message.meta.intent, entities: message.meta.entities }
    }
  }
  return undefined
}

// Stable reference so an inactive conversation doesn't hand MessageList
// a freshly-allocated empty array on every render — matters once
// MessageList is memoized below.
const EMPTY_MESSAGES: ChatMessage[] = []

function ChatWorkspace({ initialInputValue }: { initialInputValue: string }) {
  const { activeConversation, newConversation, addMessage, updateMessage } = useChat()

  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(
    () => window.localStorage.getItem(SIDEBAR_COLLAPSED_KEY) === "true",
  )
  const [isBusy, setIsBusy] = useState(false)
  const [inputValue, setInputValue] = useState(initialInputValue)
  const [inspectorOpen, setInspectorOpen] = useState(false)
  const abortControllerRef = useRef<AbortController | null>(null)

  useEffect(() => {
    window.localStorage.setItem(SIDEBAR_COLLAPSED_KEY, String(sidebarCollapsed))
  }, [sidebarCollapsed])

  // The Inspector always reflects the most recently completed
  // assistant response in the active conversation — the natural
  // "what did that last answer actually retrieve" reading, rather
  // than requiring the user to pick a message to inspect.
  const latestInspectableMessage = useMemo(() => {
    const messages = activeConversation?.messages ?? []
    for (let i = messages.length - 1; i >= 0; i--) {
      if (messages[i].role === "assistant" && messages[i].meta) return messages[i]
    }
    return null
  }, [activeConversation])

  const handleSend = useCallback(
    async (text: string) => {
      // isBusy already disables the input while a request is in
      // flight (see ChatInput), but guard here too — this is the
      // single place a submission can actually be triggered from
      // (Enter key, Send click, or an example chip), so it's the
      // right place to make "no duplicate submissions" unconditional.
      if (isBusy) return

      const conversationId = activeConversation?.id ?? newConversation()

      const userMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content: text,
        language: detectLanguage(text),
        status: "complete",
        createdAt: Date.now(),
      }
      addMessage(conversationId, userMessage)

      const assistantId = crypto.randomUUID()
      addMessage(conversationId, {
        id: assistantId,
        role: "assistant",
        content: "",
        language: "english",
        status: "pending",
        createdAt: Date.now(),
      })

      const controller = new AbortController()
      abortControllerRef.current = controller
      setIsBusy(true)

      try {
        const context = lastTurnContext(activeConversation)
        const { data, latencyMs } = await queryManara(text, controller.signal, context)

        if (!data.answer.trim()) {
          updateMessage(conversationId, assistantId, {
            content:
              "MANARA didn't return an answer for this question. Try rephrasing it.",
            status: "error",
          })
          return
        }

        updateMessage(conversationId, assistantId, {
          content: data.answer,
          language: data.language,
          status: "complete",
          meta: {
            question: data.question,
            intent: data.intent,
            entities: data.entities,
            sources: data.sources,
            latencyMs,
          },
        })
      } catch (error) {
        if (error instanceof DOMException && error.name === "AbortError") {
          updateMessage(conversationId, assistantId, {
            content: "_Generation stopped._",
            status: "complete",
          })
          return
        }

        const message =
          error instanceof ApiError
            ? error.message
            : "Something went wrong while generating a response. Please try again."

        updateMessage(conversationId, assistantId, {
          content: message,
          status: "error",
        })
        toast.error(message)
      } finally {
        setIsBusy(false)
        abortControllerRef.current = null
      }
    },
    [isBusy, activeConversation, newConversation, addMessage, updateMessage],
  )

  const handleStop = useCallback(() => {
    abortControllerRef.current?.abort()
  }, [])

  const handleToggleCollapse = useCallback(() => setSidebarCollapsed((v) => !v), [])
  const handleCloseMobileSidebar = useCallback(() => setMobileSidebarOpen(false), [])
  const handleOpenMobileSidebar = useCallback(() => setMobileSidebarOpen(true), [])
  const handleOpenInspector = useCallback(() => setInspectorOpen(true), [])
  const handleExampleSelect = useCallback((text: string) => setInputValue(text), [])

  return (
    <div className="flex h-svh overflow-hidden bg-background">
      {/* Desktop sidebar — persistent, collapsible */}
      <aside className="hidden lg:block">
        <ChatSidebar collapsed={sidebarCollapsed} onToggleCollapse={handleToggleCollapse} />
      </aside>

      {/* Mobile sidebar — drawer */}
      <Sheet open={mobileSidebarOpen} onOpenChange={setMobileSidebarOpen}>
        <SheetContent side="left" className="w-72 p-0">
          <SheetTitle className="sr-only">Conversations</SheetTitle>
          <ChatSidebar onNavigate={handleCloseMobileSidebar} />
        </SheetContent>
      </Sheet>

      <div className="flex min-w-0 flex-1 flex-col">
        <ChatHeader
          conversation={activeConversation}
          onOpenMobileSidebar={handleOpenMobileSidebar}
          onOpenInspector={handleOpenInspector}
        />

        <div className="min-h-0 flex-1 overflow-y-auto">
          <MessageList
            messages={activeConversation?.messages ?? EMPTY_MESSAGES}
            onExampleSelect={handleExampleSelect}
          />
        </div>

        <ChatInput
          value={inputValue}
          onChange={setInputValue}
          onSend={handleSend}
          onStop={handleStop}
          isBusy={isBusy}
        />
      </div>

      <IntelligencePanel
        message={latestInspectableMessage}
        open={inspectorOpen}
        onOpenChange={setInspectorOpen}
      />
    </div>
  )
}

export function ChatPage() {
  const location = useLocation()
  const prefill = (location.state as { prefill?: string } | null)?.prefill ?? ""

  // Consume the landing page's prefill exactly once, then clear it from
  // history so a later refresh/back-navigation doesn't re-populate it.
  useEffect(() => {
    if (prefill) window.history.replaceState({}, "")
  }, [prefill])

  return (
    <ChatProvider>
      <ChatWorkspace initialInputValue={prefill} />
    </ChatProvider>
  )
}
