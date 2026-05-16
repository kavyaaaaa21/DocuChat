import { useParams, useNavigate, Link } from 'react-router-dom'
import { FileText, ArrowLeft, MessageSquare } from 'lucide-react'
import QuizPanel from '../components/QuizPanel'

export default function QuizPage() {
  const { id }   = useParams()
  const navigate = useNavigate()

  const displayName = `Document · ${id?.slice(0, 8)}…`

  return (
    <div className="min-h-screen flex flex-col">

      {/* ── Top bar ── */}
      <header className="flex items-center justify-between px-5 py-4 border-b border-border shrink-0">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/')}
            className="btn-ghost p-2 !px-2"
            aria-label="Back"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>

          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-accent/10 flex items-center justify-center">
              <FileText className="w-3.5 h-3.5 text-accent" />
            </div>
            <span className="font-display font-semibold text-sm text-text">{displayName}</span>
          </div>
        </div>

        <Link
          to={`/chat/${id}`}
          className="btn-ghost flex items-center gap-1.5 text-xs"
        >
          <MessageSquare className="w-3.5 h-3.5" />
          Switch to Chat
        </Link>
      </header>

      {/* ── Quiz ── */}
      <main className="flex-1 flex flex-col overflow-hidden max-w-2xl w-full mx-auto">
        <QuizPanel documentId={id} filename={displayName} />
      </main>

    </div>
  )
}
