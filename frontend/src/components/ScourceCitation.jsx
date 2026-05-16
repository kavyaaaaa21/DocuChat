import { useState } from 'react'
import { ChevronDown, BookOpen } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import clsx from 'clsx'

export default function SourceCitation({ citation, index }) {
  const [open, setOpen] = useState(false)

  return (
    <div className="border border-border rounded-lg overflow-hidden text-xs">
      {/* Header */}
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between gap-2 px-3 py-2
                   bg-surface hover:bg-panel transition-colors duration-150"
      >
        <div className="flex items-center gap-2 text-dim">
          <BookOpen className="w-3.5 h-3.5 text-accent/70" />
          <span className="font-mono font-medium text-accent/80">Source {index}</span>
          <span className="text-muted">·</span>
          <span>Page {citation.page}</span>
        </div>
        <ChevronDown className={clsx(
          'w-3.5 h-3.5 text-muted transition-transform duration-200',
          open && 'rotate-180'
        )} />
      </button>

      {/* Snippet */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <p className="px-3 py-2.5 text-dim leading-relaxed border-t border-border font-mono">
              "{citation.snippet}"
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

