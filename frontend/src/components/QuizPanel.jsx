import { useState } from 'react'
import { motion } from 'framer-motion'
import { BrainCircuit, Loader2, ChevronRight } from 'lucide-react'
import QuizQuestion from './QuizQuestion'
import ScoreBoard   from './ScoreBoard'
import { useQuiz }  from '../hooks/useQuiz'
import clsx from 'clsx'

const QUESTION_TYPES = [
  { value: 'mcq',          label: 'MCQ',          desc: 'Multiple choice' },
  { value: 'true_false',   label: 'True / False',  desc: '2-option' },
  { value: 'short_answer', label: 'Short Answer',  desc: 'Open ended' },
]

const COUNTS = [3, 5, 10]

export default function QuizPanel({ documentId, filename }) {
  const {
    questions, answers, result,
    phase, isLoading, error,
    answeredCount, totalQuestions, allAnswered,
    startQuiz, setAnswer, submitAnswers, resetQuiz,
  } = useQuiz(documentId)

  // Config state
  const [qType,  setQType]  = useState('mcq')
  const [qCount, setQCount] = useState(5)
  const [topic,  setTopic]  = useState('')

  return (
    <div className="flex flex-col h-full">

      {/* ── Header ── */}
      <div className="flex items-center gap-3 px-5 py-4 border-b border-border shrink-0">
        <div className="w-8 h-8 rounded-xl bg-accent/10 flex items-center justify-center">
          <BrainCircuit className="w-4 h-4 text-accent" />
        </div>
        <div>
          <p className="font-display font-semibold text-sm text-text">Quiz Mode</p>
          <p className="text-dim text-xs truncate max-w-[200px]">{filename}</p>
        </div>

        {/* Progress badge */}
        {phase === 'attempt' && (
          <span className="ml-auto tag">
            {answeredCount} / {totalQuestions}
          </span>
        )}
      </div>

      {/* ── Body ── */}
      <div className="flex-1 overflow-y-auto px-5 py-5">

        {/* Config phase */}
        {phase === 'config' && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col gap-5"
          >
            {/* Question type */}
            <div className="flex flex-col gap-2">
              <label className="text-xs text-dim font-mono uppercase tracking-widest">Question Type</label>
              <div className="grid grid-cols-3 gap-2">
                {QUESTION_TYPES.map((t) => (
                  <button
                    key={t.value}
                    onClick={() => setQType(t.value)}
                    className={clsx(
                      'flex flex-col items-center py-3 rounded-xl border text-center transition-all',
                      qType === t.value
                        ? 'border-accent bg-accent/10 shadow-glow'
                        : 'border-border bg-surface hover:border-accent/40'
                    )}
                  >
                    <span className="font-display font-semibold text-xs text-text">{t.label}</span>
                    <span className="text-dim text-xs mt-0.5">{t.desc}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Question count */}
            <div className="flex flex-col gap-2">
              <label className="text-xs text-dim font-mono uppercase tracking-widest">Number of Questions</label>
              <div className="flex gap-2">
                {COUNTS.map((c) => (
                  <button
                    key={c}
                    onClick={() => setQCount(c)}
                    className={clsx(
                      'flex-1 py-2.5 rounded-lg border font-display font-semibold text-sm transition-all',
                      qCount === c
                        ? 'border-accent bg-accent/10 text-glow shadow-glow'
                        : 'border-border bg-surface text-dim hover:border-accent/40'
                    )}
                  >
                    {c}
                  </button>
                ))}
              </div>
            </div>

            {/* Topic focus (optional) */}
            <div className="flex flex-col gap-2">
              <label className="text-xs text-dim font-mono uppercase tracking-widest">
                Topic Focus <span className="normal-case">(optional)</span>
              </label>
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g. technical architecture, week 3 tasks…"
                className="input-field"
              />
            </div>

            {error && (
              <p className="text-red text-xs text-center">{error}</p>
            )}

            <button
              disabled={isLoading}
              onClick={() => startQuiz({ question_type: qType, num_questions: qCount, topic_focus: topic })}
              className="btn-primary flex items-center justify-center gap-2 py-3"
            >
              {isLoading
                ? <><Loader2 className="w-4 h-4 animate-spin" /> Generating…</>
                : <><BrainCircuit className="w-4 h-4" /> Generate Quiz</>
              }
            </button>
          </motion.div>
        )}

        {/* Attempt phase */}
        {phase === 'attempt' && (
          <div className="flex flex-col gap-4">
            {questions.map((q, i) => (
              <QuizQuestion
                key={q.question_id}
                question={q}
                index={i}
                selected={answers[q.question_id]}
                onSelect={setAnswer}
              />
            ))}

            {error && <p className="text-red text-xs text-center">{error}</p>}

            <div className="flex gap-3 mt-2 pb-2">
              <button onClick={resetQuiz} className="btn-ghost flex-1">Back</button>
              <button
                disabled={!allAnswered || isLoading}
                onClick={submitAnswers}
                className="btn-primary flex-1 flex items-center justify-center gap-2"
              >
                {isLoading
                  ? <><Loader2 className="w-4 h-4 animate-spin" /> Evaluating…</>
                  : <><ChevronRight className="w-4 h-4" /> Submit Answers</>
                }
              </button>
            </div>
          </div>
        )}

        {/* Result phase */}
        {phase === 'result' && result && (
          <ScoreBoard result={result} onRetry={resetQuiz} />
        )}
      </div>
    </div>
  )
}
