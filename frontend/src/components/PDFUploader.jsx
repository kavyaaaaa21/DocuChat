import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { FileText, Upload, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import { uploadPDF } from '../services/api'
import clsx from 'clsx'

const PHASE = { IDLE: 'idle', UPLOADING: 'uploading', SUCCESS: 'success', ERROR: 'error' }

export default function PDFUploader() {
  const navigate = useNavigate()
  const [phase,    setPhase]    = useState(PHASE.IDLE)
  const [progress, setProgress] = useState(0)
  const [fileName, setFileName] = useState('')
  const [errorMsg, setErrorMsg] = useState('')
  const [docInfo,  setDocInfo]  = useState(null)

  const handleFile = useCallback(async (file) => {
    setFileName(file.name)
    setPhase(PHASE.UPLOADING)
    setProgress(0)
    setErrorMsg('')

    try {
      const data = await uploadPDF(file, setProgress)
      setDocInfo(data)
      setPhase(PHASE.SUCCESS)
    } catch (err) {
      setErrorMsg(err.message)
      setPhase(PHASE.ERROR)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024, // 50 MB
    disabled: phase === PHASE.UPLOADING,
    onDropAccepted: ([file]) => handleFile(file),
    onDropRejected: ([{ errors }]) => {
      setErrorMsg(errors[0]?.message || 'Invalid file.')
      setPhase(PHASE.ERROR)
    },
  })

  return (
    <div className="w-full max-w-xl mx-auto">
      <AnimatePresence mode="wait">

        {/* ── Drop Zone ── */}
        {(phase === PHASE.IDLE || phase === PHASE.ERROR) && (
          <motion.div
            key="dropzone"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            {...getRootProps()}
            className={clsx(
              'relative flex flex-col items-center justify-center gap-4',
              'border-2 border-dashed rounded-2xl p-14 cursor-pointer',
              'transition-all duration-300 group',
              isDragActive
                ? 'border-accent bg-accent/10 shadow-glow'
                : 'border-border hover:border-accent/50 hover:bg-panel/60'
            )}
          >
            <input {...getInputProps()} />

            <div className={clsx(
              'flex items-center justify-center w-16 h-16 rounded-2xl transition-all duration-300',
              isDragActive ? 'bg-accent/20' : 'bg-surface group-hover:bg-accent/10'
            )}>
              <Upload className={clsx(
                'w-7 h-7 transition-colors duration-300',
                isDragActive ? 'text-accent' : 'text-muted group-hover:text-accent'
              )} />
            </div>

            <div className="text-center">
              <p className="font-display font-semibold text-text text-base">
                {isDragActive ? 'Drop your PDF here' : 'Upload a PDF'}
              </p>
              <p className="text-dim text-sm mt-1">
                Drag & drop or <span className="text-accent underline underline-offset-2">browse</span> — up to 50 MB
              </p>
            </div>

            {phase === PHASE.ERROR && (
              <div className="flex items-center gap-2 text-red text-sm mt-1">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}
          </motion.div>
        )}

        {/* ── Uploading ── */}
        {phase === PHASE.UPLOADING && (
          <motion.div
            key="uploading"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="card flex flex-col items-center gap-5 py-12"
          >
            <div className="relative">
              <div className="w-16 h-16 rounded-2xl bg-accent/10 flex items-center justify-center">
                <FileText className="w-7 h-7 text-accent" />
              </div>
              <Loader2 className="w-5 h-5 text-glow absolute -top-1 -right-1 animate-spin" />
            </div>

            <div className="w-full max-w-xs text-center">
              <p className="font-display font-semibold text-sm text-text mb-1 truncate">{fileName}</p>
              <p className="text-dim text-xs mb-3">Processing your document…</p>

              <div className="w-full bg-surface rounded-full h-1.5 overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-accent to-glow rounded-full"
                  initial={{ width: '0%' }}
                  animate={{ width: `${progress}%` }}
                  transition={{ duration: 0.3 }}
                />
              </div>
              <p className="text-dim text-xs mt-1.5">{progress}%</p>
            </div>
          </motion.div>
        )}

        {/* ── Success ── */}
        {phase === PHASE.SUCCESS && docInfo && (
          <motion.div
            key="success"
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            className="card flex flex-col items-center gap-5 py-10"
          >
            <div className="w-16 h-16 rounded-2xl bg-green/10 flex items-center justify-center">
              <CheckCircle className="w-8 h-8 text-green" />
            </div>

            <div className="text-center">
              <p className="font-display font-semibold text-text">{docInfo.filename}</p>
              <p className="text-dim text-sm mt-1">
                {docInfo.total_chunks} chunks indexed — ready to explore
              </p>
            </div>

            <div className="flex gap-3 w-full max-w-xs">
              <button
                onClick={() => navigate(`/chat/${docInfo.document_id}`)}
                className="btn-primary flex-1"
              >
                Chat Mode
              </button>
              <button
                onClick={() => navigate(`/quiz/${docInfo.document_id}`)}
                className="btn-ghost flex-1"
              >
                Quiz Mode
              </button>
            </div>
          </motion.div>
        )}

      </AnimatePresence>
    </div>
  )
}
