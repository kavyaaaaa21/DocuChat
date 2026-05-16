import { motion } from 'framer-motion'
import { FileText, MessageSquare, BrainCircuit, Zap } from 'lucide-react'
import PDFUploader from '../components/PDFUploader'

const FEATURES = [
  {
    icon: MessageSquare,
    title: 'Chat Mode',
    desc:  'Ask any question about your PDF. Get precise answers grounded in the document with page-level citations.',
  },
  {
    icon: BrainCircuit,
    title: 'Quiz Mode',
    desc:  'Auto-generate MCQs, True/False, and Short Answer questions to test and reinforce your understanding.',
  },
  {
    icon: Zap,
    title: 'RAG-Powered',
    desc:  'Semantic retrieval ensures answers come from your document — not hallucinated from thin air.',
  },
]

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">

      {/* ── Nav ── */}
      <header className="flex items-center justify-between px-8 py-5 border-b border-border/50">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-accent flex items-center justify-center shadow-glow">
            <FileText className="w-4 h-4 text-white" />
          </div>
          <span className="font-display font-bold text-text tracking-tight">DocuChat AI</span>
        </div>
        <span className="tag">RAG · FAISS · GPT-4o</span>
      </header>

      {/* ── Hero ── */}
      <main className="flex-1 flex flex-col items-center justify-center px-6 py-16 gap-14">

        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center max-w-xl"
        >
          <h1 className="font-display font-extrabold text-4xl sm:text-5xl text-text leading-tight tracking-tight">
            Chat with any{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-accent to-glow">
              PDF
            </span>
            {'. '}
            Quiz yourself on it.
          </h1>
          <p className="text-dim text-base mt-4 leading-relaxed max-w-sm mx-auto">
            Upload a document and instantly unlock an AI assistant that cites its sources — plus a quiz engine that tests your retention.
          </p>
        </motion.div>

        {/* Uploader */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15, duration: 0.5 }}
          className="w-full max-w-xl"
        >
          <PDFUploader />
        </motion.div>

        {/* Feature pills */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="grid sm:grid-cols-3 gap-4 w-full max-w-2xl"
        >
          {FEATURES.map(({ icon: Icon, title, desc }, i) => (
            <motion.div
              key={title}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.35 + i * 0.08 }}
              className="card flex flex-col gap-3 hover:border-accent/30 transition-colors duration-300"
            >
              <div className="w-9 h-9 rounded-xl bg-accent/10 flex items-center justify-center">
                <Icon className="w-4 h-4 text-accent" />
              </div>
              <div>
                <p className="font-display font-semibold text-sm text-text">{title}</p>
                <p className="text-dim text-xs mt-1 leading-relaxed">{desc}</p>
              </div>
            </motion.div>
          ))}
        </motion.div>

      </main>

      <footer className="text-center py-5 text-muted text-xs border-t border-border/40">
        DocuChat AI · Built with FastAPI, LangChain, FAISS & React
      </footer>
    </div>
  )
}
