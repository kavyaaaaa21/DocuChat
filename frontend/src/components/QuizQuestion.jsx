import { motion } from 'framer-motion'
import clsx from 'clsx'

const LABELS = ['A', 'B', 'C', 'D']

export default function QuizQuestion({ question, index, selected, onSelect, disabled = false }) {
  const isTrueFalse  = question.question_type === 'true_false'
  const isShortAnswer = question.question_type === 'short_answer'

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06 }}
      className="card flex flex-col gap-4"
    >
      {/* Question header */}
      <div className="flex items-start gap-3">
        <span className="tag shrink-0">Q{index + 1}</span>
        <p className="text-sm font-body text-text leading-relaxed">{question.question}</p>
      </div>

      {/* MCQ options */}
      {!isShortAnswer && question.options && (
        <div className={clsx('grid gap-2', isTrueFalse ? 'grid-cols-2' : 'grid-cols-1')}>
          {question.options.map((opt, i) => {
            const value   = isTrueFalse ? opt : LABELS[i]
            const isChosen = selected === value

            return (
              <button
                key={i}
                disabled={disabled}
                onClick={() => onSelect(question.question_id, value)}
                className={clsx(
                  'flex items-center gap-3 px-4 py-3 rounded-lg border text-left',
                  'transition-all duration-200 text-sm group',
                  disabled && 'cursor-not-allowed',
                  isChosen
                    ? 'border-accent bg-accent/10 text-text shadow-glow'
                    : 'border-border bg-surface text-dim hover:border-accent/40 hover:text-text'
                )}
              >
                <span className={clsx(
                  'w-6 h-6 rounded-md flex items-center justify-center shrink-0',
                  'text-xs font-mono font-semibold transition-colors',
                  isChosen ? 'bg-accent text-white' : 'bg-muted/20 text-muted'
                )}>
                  {isTrueFalse ? (opt === 'True' ? 'T' : 'F') : LABELS[i]}
                </span>
                <span className="leading-snug">{isTrueFalse ? opt : opt.replace(/^[A-D]\.\s*/, '')}</span>
              </button>
            )
          })}
        </div>
      )}

      {/* Short answer textarea */}
      {isShortAnswer && (
        <textarea
          rows={3}
          disabled={disabled}
          value={selected || ''}
          onChange={(e) => onSelect(question.question_id, e.target.value)}
          placeholder="Type your answer here…"
          className="input-field resize-none font-body text-sm leading-relaxed
                     disabled:opacity-50 disabled:cursor-not-allowed"
        />
      )}
    </motion.div>
  )
}
