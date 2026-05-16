import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 60_000,
})

// ─── Request interceptor ────────────────────
api.interceptors.request.use((config) => {
  return config
})

// ─── Response interceptor ───────────────────
api.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const message =
      err.response?.data?.detail || err.message || 'Something went wrong'
    return Promise.reject(new Error(message))
  }
)

// ─── Upload ─────────────────────────────────

/**
 * Upload a PDF file.
 * @param {File} file
 * @param {(pct: number) => void} onProgress
 * @returns {{ document_id, filename, total_chunks, message }}
 */
export const uploadPDF = (file, onProgress) => {
  const form = new FormData()
  form.append('file', file)

  return api.post('/upload/', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (onProgress && e.total) {
        onProgress(Math.round((e.loaded / e.total) * 100))
      }
    },
  })
}

// ─── Chat ────────────────────────────────────

/**
 * Send a chat message.
 * @param {{ document_id, query, chat_history }} payload
 * @returns {{ answer, citations }}
 */
export const sendChatMessage = (payload) =>
  api.post('/chat/', payload)

// ─── Quiz ────────────────────────────────────

/**
 * Generate a quiz.
 * @param {{ document_id, question_type, num_questions, topic_focus }} payload
 * @returns {{ quiz_id, questions }}
 */
export const generateQuiz = (payload) =>
  api.post('/quiz/generate', payload)

/**
 * Submit quiz answers.
 * @param {{ quiz_id, user_answers }} payload
 * @returns {{ quiz_id, score, total, percentage, feedback }}
 */
export const submitQuiz = (payload) =>
  api.post('/quiz/submit', payload)
