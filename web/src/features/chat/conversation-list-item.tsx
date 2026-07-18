import { memo } from "react"
import { MessageSquare, Trash2 } from "lucide-react"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import type { Conversation } from "@/types/chat"

interface ConversationListItemProps {
  conversation: Conversation
  isActive: boolean
  onSelect: (id: string) => void
  onDelete: (id: string) => void
}

export const ConversationListItem = memo(function ConversationListItem({
  conversation,
  isActive,
  onSelect,
  onDelete,
}: ConversationListItemProps) {
  return (
    <div
      className={cn(
        "group relative flex items-center gap-2 rounded-lg px-2.5 py-2 text-sm transition-colors",
        isActive
          ? "bg-accent text-accent-foreground"
          : "text-foreground/80 hover:bg-accent/60",
      )}
    >
      <button
        type="button"
        onClick={() => onSelect(conversation.id)}
        aria-current={isActive ? "true" : undefined}
        className="flex min-w-0 flex-1 items-center gap-2 text-left"
      >
        <MessageSquare className="size-4 shrink-0 text-muted-foreground" />
        <span className="truncate">{conversation.title}</span>
      </button>

      <AlertDialog>
        <AlertDialogTrigger asChild>
          <Button
            variant="ghost"
            size="icon"
            aria-label={`Delete conversation "${conversation.title}"`}
            className="size-6 shrink-0 opacity-0 focus-visible:opacity-100 group-hover:opacity-100 group-focus-within:opacity-100 data-[state=open]:opacity-100"
            onClick={(e) => e.stopPropagation()}
          >
            <Trash2 className="size-3.5" />
          </Button>
        </AlertDialogTrigger>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete this conversation?</AlertDialogTitle>
            <AlertDialogDescription>
              "{conversation.title}" and all its messages will be permanently
              removed. This can't be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => onDelete(conversation.id)}
              className="bg-destructive text-white hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
})
