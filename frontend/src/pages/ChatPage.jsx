import { useParams, useNavigate, Link } from 'react-router-dom'
import { FileText, ArrowLeft, BrainCircuit } from 'lucide-react'
import ChatWindow from '../components/ChatWindow'

export default function ChatPage() {
  const { id }    = useParams()
  const navigate  = useNavigate()

  // In a real app, filename would be fetched or passed via state.
  // For now we display the document_id truncated.
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
          to={`/quiz/${id}`}
          className="btn-ghost flex items-center gap-1.5 text-xs"
        >
          <BrainCircuit className="w-3.5 h-3.5" />
          Switch to Quiz
        </Link>
      </header>

      {/* ── Chat ── */}
      <main className="flex-1 flex flex-col overflow-hidden max-w-3xl w-full mx-auto">
        <ChatWindow documentId={id} filename={displayName} />
      </main>

    </div>
  )
}
