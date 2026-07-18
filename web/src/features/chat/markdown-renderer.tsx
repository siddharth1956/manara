import { memo } from "react"
import ReactMarkdown, { type Components } from "react-markdown"
import remarkGfm from "remark-gfm"
import { PrismLight as SyntaxHighlighter } from "react-syntax-highlighter"
import json from "react-syntax-highlighter/dist/esm/languages/prism/json"
import python from "react-syntax-highlighter/dist/esm/languages/prism/python"
import bash from "react-syntax-highlighter/dist/esm/languages/prism/bash"
import sql from "react-syntax-highlighter/dist/esm/languages/prism/sql"
import typescript from "react-syntax-highlighter/dist/esm/languages/prism/typescript"
import javascript from "react-syntax-highlighter/dist/esm/languages/prism/javascript"
import { oneDark, oneLight } from "react-syntax-highlighter/dist/esm/styles/prism"
import { Check, Copy } from "lucide-react"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { useTheme } from "@/hooks/use-theme"

// Register only the languages MANARA's answers realistically produce
// (geospatial data snippets, coordinates, occasional shell/query
// examples) — the full `react-syntax-highlighter` import pulls in
// every Prism grammar and bloated the chat route to ~870KB; this
// keeps only what's actually used.
SyntaxHighlighter.registerLanguage("json", json)
SyntaxHighlighter.registerLanguage("python", python)
SyntaxHighlighter.registerLanguage("bash", bash)
SyntaxHighlighter.registerLanguage("sql", sql)
SyntaxHighlighter.registerLanguage("typescript", typescript)
SyntaxHighlighter.registerLanguage("javascript", javascript)

const REGISTERED_LANGUAGES = new Set([
  "json",
  "python",
  "bash",
  "sql",
  "typescript",
  "javascript",
])

function CodeBlock({ language, code }: { language: string; code: string }) {
  const { theme } = useTheme()
  const [copied, setCopied] = useState(false)
  const isHighlightable = REGISTERED_LANGUAGES.has(language)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }

  return (
    <div className="group relative my-3 overflow-hidden rounded-lg border border-border/60">
      <div className="flex items-center justify-between border-b border-border/60 bg-muted/50 px-3 py-1.5">
        <span className="font-mono text-xs text-muted-foreground">
          {language || "text"}
        </span>
        <Button
          variant="ghost"
          size="icon"
          className="size-6"
          onClick={handleCopy}
          aria-label="Copy code"
        >
          {copied ? (
            <Check className="size-3.5 text-emerald-500" />
          ) : (
            <Copy className="size-3.5" />
          )}
        </Button>
      </div>
      {isHighlightable ? (
        <SyntaxHighlighter
          language={language}
          style={theme === "dark" ? oneDark : oneLight}
          customStyle={{
            margin: 0,
            borderRadius: 0,
            fontSize: "0.8125rem",
            padding: "0.75rem 1rem",
          }}
        >
          {code}
        </SyntaxHighlighter>
      ) : (
        // Unregistered language (or plain text) — render unhighlighted
        // rather than risk PrismLight erroring on an unknown grammar.
        <pre className="overflow-x-auto bg-transparent px-4 py-3 font-mono text-[0.8125rem]">
          <code>{code}</code>
        </pre>
      )}
    </div>
  )
}

const components: Components = {
  code({ className, children, ...props }) {
    const match = /language-(\w+)/.exec(className ?? "")
    const isInline = !match && !String(children).includes("\n")

    if (isInline) {
      return (
        <code
          className="rounded bg-muted px-1.5 py-0.5 font-mono text-[0.85em]"
          {...props}
        >
          {children}
        </code>
      )
    }

    return (
      <CodeBlock
        language={match?.[1] ?? ""}
        code={String(children).replace(/\n$/, "")}
      />
    )
  },
  table({ children }) {
    return (
      <div className="my-3 overflow-x-auto rounded-lg border border-border/60">
        <table className="w-full text-sm">{children}</table>
      </div>
    )
  },
}

interface MarkdownRendererProps {
  content: string
}

/** Memoized — chat messages don't change once rendered, and re-parsing
 * markdown on every parent re-render (e.g. a sibling message streaming
 * in) is pure waste. */
export const MarkdownRenderer = memo(function MarkdownRenderer({
  content,
}: MarkdownRendererProps) {
  return (
    <div className="prose prose-sm dark:prose-invert max-w-none prose-p:leading-relaxed prose-pre:p-0 prose-pre:bg-transparent">
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {content}
      </ReactMarkdown>
    </div>
  )
})
