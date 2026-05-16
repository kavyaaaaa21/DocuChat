import { motion } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import { Bot, User } from 'lucide-react'
import SourceCitation from './SourceCitation'
import clsx from 'clsx'

export default function ChatMessage({ role, content, citations = [] }) {
  const isUser = role === 'user'

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={clsx('flex gap-3', isUser ? 'flex-row-reverse' : 'flex-row')}
    >
      {/* Avatar */}
      <div className={clsx(
        'shrink-0 w-8 h-8 rounded-xl flex items-center justify-center',
        isUser ? 'bg-accent/20' : 'bg-surface border border-border'
      )}>
        {isUser
          ? <User className="w-4 h-4 text-glow" />
          : <Bot  className="w-4 h-4 text-accent" />
        }
      </div>

      {/* Bubble */}
      <div className={clsx('flex flex-col gap-2 max-w-[75%]', isUser && 'items-end')}>
        <div className={clsx(
          'px-4 py-3 rounded-2xl text-sm leading-relaxed',
          isUser
            ? 'bg-accent/15 border border-accent/20 text-text rounded-tr-sm'
            : 'bg-panel border border-border text-text rounded-tl-sm'
        )}>
          {isUser
            ? <p>{content}</p>
            : (
              <ReactMarkdown
                components={{
                  p:      ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                  strong: ({ children }) => <strong className="text-glow font-semibold">{children}</strong>,
                  code:   ({ children }) => (
                    <code className="font-mono text-xs bg-surface px-1.5 py-0.5 rounded text-accent">{children}</code>
                  ),
                  ul: ({ children }) => <ul className="list-disc list-inside space-y-1 mb-2">{children}</ul>,
                  ol: ({ children }) => <ol className="list-decimal list-inside space-y-1 mb-2">{children}</ol>,
                }}
              >
                {content}
              </ReactMarkdown>
            )
          }
        </div>

        {/* Citations */}
        {!isUser && citations.length > 0 && (
          <div className="flex flex-col gap-1.5 w-full">
            {citations.map((c, i) => (
              <SourceCitation key={i} citation={c} index={i + 1} />
            ))}
          </div>
        )}
      </div>
    </motion.div>
  )
}
