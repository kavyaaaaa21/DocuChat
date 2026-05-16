import { motion } from 'framer-motion'
import { CheckCircle, XCircle, RotateCcw, MessageSquare } from 'lucide-react'
import { useNavigate, useParams } from 'react-router-dom'
import clsx from 'clsx'

function ScoreRing({ percentage }) {
  const r = 54
  const circ = 2 * Math.PI * r
  const offset = circ - (percentage / 100) * circ
  const color =
    percentage >= 80 ? '#4ade80' :
    percentage >= 50 ? '#fbbf24' : '#f87171'

  return (
    <svg viewBox="0 0 120 120" className="w-32 h-32 -rotate-90">
      <circle cx="60" cy="60" r={r} fill="none" stroke="#232334" strokeWidth="10" />
      <motion.circle
        cx="60" cy="60" r={r} fill="none"
        stroke={color} strokeWidth="10"
        strokeLinecap="round"
        strokeDasharray={circ}
        initial={{ strokeDashoffset: circ }}
        animate={{ strokeDashoffset: offset }}
        transition={{ duration: 1.2, ease: 'easeOut' }}
      />
      <text
        x="60" y="60"
        textAnchor="middle" dominantBaseline="central"
        className="rotate-90 origin-center"
        transform="rotate(90, 60, 60)"
        fill={color}
        fontSize="22"
        fontFamily="Sora, sans-serif"
        fontWeight="700"
      >
        {percentage}%
      </text>
    </svg>
  )
}

export default function ScoreBoard({ result, onRetry }) {
  const navigate  = useNavigate()
  const { id }    = useParams()

  const { score, total, percentage, feedback } = result
  const label =
    percentage >= 80 ? { text: 'Excellent!',   color: 'text-green' } :
    percentage >= 50 ? { text: 'Good effort',  color: 'text-amber' } :
                       { text: 'Keep going',   color: 'text-red'   }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex flex-col gap-6"
    >
      {/* Score summary */}
      <div className="card flex flex-col items-center gap-3 py-8">
        <ScoreRing percentage={percentage} />
        <p className={clsx('font-display font-bold text-2xl', label.color)}>{label.text}</p>
        <p className="text-dim text-sm">
          You scored <span className="text-text font-semibold">{score}</span> out of{' '}
          <span className="text-text font-semibold">{total}</span>
        </p>

        <div className="flex gap-3 mt-2">
          <button onClick={onRetry} className="btn-primary flex items-center gap-2">
            <RotateCcw className="w-3.5 h-3.5" />
            Retry Quiz
          </button>
          <button
            onClick={() => navigate(`/chat/${id}`)}
            className="btn-ghost flex items-center gap-2"
          >
            <MessageSquare className="w-3.5 h-3.5" />
            Chat Mode
          </button>
        </div>
      </div>

      {/* Per-question feedback */}
      <div className="flex flex-col gap-3">
        <h3 className="font-display font-semibold text-text text-sm px-1">Answer Review</h3>

        {feedback.map((item, i) => (
          <motion.div
            key={item.question_id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            className={clsx(
              'card border-l-4',
              item.is_correct ? 'border-l-green' : 'border-l-red'
            )}
          >
            <div className="flex items-start gap-3">
              <div className="shrink-0 mt-0.5">
                {item.is_correct
                  ? <CheckCircle className="w-4 h-4 text-green" />
                  : <XCircle    className="w-4 h-4 text-red" />
                }
              </div>
              <div className="flex flex-col gap-1.5 flex-1">
                <p className="text-sm text-text font-body leading-snug">{item.question}</p>
                <div className="flex gap-3 text-xs flex-wrap">
                  <span className="text-dim">
                    Your answer:{' '}
                    <span className={clsx('font-semibold', item.is_correct ? 'text-green' : 'text-red')}>
                      {item.user_answer || '(no answer)'}
                    </span>
                  </span>
                  {!item.is_correct && (
                    <span className="text-dim">
                      Correct: <span className="text-green font-semibold">{item.correct_answer}</span>
                    </span>
                  )}
                </div>
                {item.feedback && (
                  <p className="text-dim text-xs leading-relaxed border-t border-border pt-1.5 mt-0.5">
                    {item.feedback}
                  </p>
                )}
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}
