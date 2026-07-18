import { memo, useCallback, useDeferredValue, useMemo, useState } from "react"
import { PanelLeftClose, PanelLeftOpen, Plus, Search } from "lucide-react"
import { Logo } from "@/components/shared/logo"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { ThemeToggle } from "@/components/shared/theme-toggle"
import { DirectionToggle } from "@/components/shared/direction-toggle"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import { ConversationListItem } from "@/features/chat/conversation-list-item"
import { useChat } from "@/features/chat/chat-context"

interface ChatSidebarProps {
  collapsed?: boolean
  onToggleCollapse?: () => void
  /** Called after New Chat / selecting a conversation — lets the mobile drawer close itself. */
  onNavigate?: () => void
}

export const ChatSidebar = memo(function ChatSidebar({
  collapsed = false,
  onToggleCollapse,
  onNavigate,
}: ChatSidebarProps) {
  const { conversations, activeConversation, newConversation, selectConversation, deleteConversation } =
    useChat()
  const [search, setSearch] = useState("")
  // Keeps keystrokes in the search box instant even as conversation
  // history grows — the (potentially expensive) filter below runs
  // against this lower-priority deferred value instead of `search`
  // directly, so React can keep the input itself responsive.
  const deferredSearch = useDeferredValue(search)

  const filtered = useMemo(() => {
    const query = deferredSearch.trim().toLowerCase()
    if (!query) return conversations
    return conversations.filter(
      (c) =>
        c.title.toLowerCase().includes(query) ||
        c.messages.some((m) => m.content.toLowerCase().includes(query)),
    )
  }, [conversations, deferredSearch])

  // Stable across re-renders regardless of which conversation's row
  // triggered them, so unrelated ConversationListItem rows (memoized
  // below) don't re-render just because one item was selected/deleted.
  const handleSelect = useCallback(
    (id: string) => {
      selectConversation(id)
      onNavigate?.()
    },
    [selectConversation, onNavigate],
  )
  const handleDelete = useCallback((id: string) => deleteConversation(id), [deleteConversation])

  if (collapsed) {
    return (
      <div className="flex h-full w-14 flex-col items-center gap-3 border-r border-border/60 bg-sidebar py-3">
        <Logo />
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => {
                newConversation()
                onNavigate?.()
              }}
              aria-label="New chat"
            >
              <Plus className="size-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent side="right">New chat</TooltipContent>
        </Tooltip>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button variant="ghost" size="icon" onClick={onToggleCollapse} aria-label="Expand sidebar">
              <PanelLeftOpen className="size-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent side="right">Expand sidebar</TooltipContent>
        </Tooltip>
        <div className="mt-auto flex flex-col items-center gap-1">
          <DirectionToggle />
          <ThemeToggle />
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-full w-72 flex-col border-r border-border/60 bg-sidebar">
      <div className="flex items-center justify-between px-3 py-3">
        <Logo withWordmark />
        {onToggleCollapse && (
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" onClick={onToggleCollapse} aria-label="Collapse sidebar">
                <PanelLeftClose className="size-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Collapse sidebar</TooltipContent>
          </Tooltip>
        )}
      </div>

      <div className="px-3">
        <Button
          onClick={() => {
            newConversation()
            onNavigate?.()
          }}
          className="w-full justify-start gap-2"
          variant="outline"
        >
          <Plus className="size-4" />
          New chat
        </Button>
      </div>

      <div className="relative px-3 pt-3">
        <Search className="pointer-events-none absolute left-4 top-1/2 size-3.5 -translate-y-1/2 text-muted-foreground" />
        <Input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search conversations…"
          aria-label="Search conversations"
          className="pl-8"
        />
      </div>

      <ScrollArea className="mt-2 flex-1 px-3">
        <div className="flex flex-col gap-0.5 py-1">
          {conversations.length === 0 && (
            <p className="px-2.5 py-4 text-center text-sm text-muted-foreground">
              No conversations yet
            </p>
          )}

          {conversations.length > 0 && filtered.length === 0 && (
            <p className="px-2.5 py-4 text-center text-sm text-muted-foreground">
              No matches for "{search}"
            </p>
          )}

          {filtered.map((conversation) => (
            <ConversationListItem
              key={conversation.id}
              conversation={conversation}
              isActive={conversation.id === activeConversation?.id}
              onSelect={handleSelect}
              onDelete={handleDelete}
            />
          ))}
        </div>
      </ScrollArea>

      <Separator />
      <div className="flex items-center justify-between px-3 py-2.5">
        <span className="text-xs text-muted-foreground">Preferences</span>
        <div className="flex items-center gap-1">
          <DirectionToggle />
          <ThemeToggle />
        </div>
      </div>
    </div>
  )
})
