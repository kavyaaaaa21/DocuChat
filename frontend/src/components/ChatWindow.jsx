import { useEffect, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Trash2, MessageSquare } from 'lucide-react'
import ChatMessage from './ChatMessage'
import { useChat } from '../hooks/useChat'
import clsx from 'clsx'

export default function ChatWindow({ documentId, filename }) {
  const { messages, isLoading, error, sendMessage, clearChat } = useChat(documentId)
  const [input, setInput] = useState('')
  const bottomRef = useRef(null)
  const textareaRef = useRef(null)

  // Auto-scroll to latest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  const handleSend = () => {
    const q = input.trim()
    if (!q) return
    setInput('')
    sendMessage(q)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // Auto-resize textarea
  const handleInput = (e) => {
    setInput(e.target.value)
    const el = textareaRef.current
    if (el) {
      el.style.height = 'auto'
      el.style.height = Math.min(el.scrollHeight, 160) + 'px'
    }
  }

  return (
    <div className="flex flex-col h-full">

      {/* ── Header ── */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-border shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-accent/10 flex items-center justify-center">
            <MessageSquare className="w-4 h-4 text-accent" />
          </div>
          <div>
            <p className="font-display font-semibold text-sm text-text">Chat Mode</p>
            <p className="text-dim text-xs truncate max-w-[200px]">{filename}</p>
          </div>
        </div>

        {messages.length > 0 && (
          <button onClick={clearChat} className="btn-ghost flex items-center gap-1.5 text-xs">
            <Trash2 className="w-3.5 h-3.5" />
            Clear
          </button>
        )}
      </div>

      {/* ── Messages ── */}
      <div className="flex-1 overflow-y-auto px-5 py-5 flex flex-col gap-5">
        {messages.length === 0 && !isLoading && (
          <div className="flex flex-col items-center justify-center h-full gap-3 text-center">
            <div className="w-14 h-14 rounded-2xl bg-accent/10 flex items-center justify-center">
              <MessageSquare className="w-6 h-6 text-accent/60" />
            </div>
            <div>
              <p className="font-display font-semibold text-text text-sm">Ask anything about your document</p>
              <p className="text-dim text-xs mt-1">Answers come with source citations</p>
            </div>
            <div className="flex flex-wrap gap-2 justify-center mt-2">
              {['Summarize this document', 'What are the key findings?', 'List the main topics'].map((q) => (
                <button
                  key={q}
                  onClick={() => { setInput(q); textareaRef.current?.focus() }}
                  className="text-xs px-3 py-1.5 rounded-lg border border-border
                             text-dim hover:border-accent/40 hover:text-text transition-all"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <ChatMessage key={i} {...msg} />
        ))}

        {/* Thinking indicator */}
        <AnimatePresence>
          {isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="flex items-center gap-2 pl-11"
            >
              {[0, 0.15, 0.3].map((delay, i) => (
                <span
                  key={i}
                  className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse-dot"
                  style={{ animationDelay: `${delay}s` }}
                />
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        {error && (
          <p className="text-red text-xs text-center py-2">{error}</p>
        )}

        <div ref={bottomRef} />
      </div>

      {/* ── Input ── */}
      <div className="shrink-0 border-t border-border px-4 py-3">
        <div className={clsx(
          'flex items-end gap-2 rounded-xl border bg-panel px-3 py-2 transition-all duration-200',
          input ? 'border-accent/40' : 'border-border'
        )}>
          <textarea
            ref={textareaRef}
            value={input}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question…"
            rows={1}
            disabled={isLoading}
            className="flex-1 resize-none bg-transparent text-sm text-text
                       placeholder:text-muted focus:outline-none font-body
                       leading-relaxed py-1 disabled:opacity-50"
            style={{ minHeight: '24px', maxHeight: '160px' }}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="shrink-0 w-8 h-8 rounded-lg bg-accent flex items-center justify-center
                       hover:bg-glow transition-colors duration-200
                       disabled:opacity-30 disabled:cursor-not-allowed mb-0.5"
          >
            <Send className="w-3.5 h-3.5 text-white" />
          </button>
        </div>
        <p className="text-muted text-xs mt-1.5 text-center">
          Enter to send · Shift+Enter for new line
        </p>
      </div>

    </div>
  )
}