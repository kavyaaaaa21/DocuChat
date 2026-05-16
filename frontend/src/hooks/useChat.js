import { useState, useCallback } from 'react'
import { sendChatMessage } from '../services/api'

/**
 * useChat — manages chat state and API interaction for Chat Mode.
 *
 * @param {string} documentId
 * @returns {{ messages, isLoading, error, sendMessage, clearChat }}
 */
export function useChat(documentId) {
  const [messages, setMessages]   = useState([])   // { role, content, citations? }[]
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError]         = useState(null)

  /**
   * Sends a user message and appends the AI response.
   * @param {string} query
   */
  const sendMessage = useCallback(async (query) => {
    if (!query.trim() || isLoading) return

    const userMsg = { role: 'user', content: query }
    setMessages((prev) => [...prev, userMsg])
    setIsLoading(true)
    setError(null)

    // Build history excluding the message we just pushed
    const history = messages.map(({ role, content }) => ({ role, content }))

    try {
      const { answer, citations } = await sendChatMessage({
        document_id: documentId,
        query,
        chat_history: history,
      })

      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: answer, citations },
      ])
    } catch (err) {
      setError(err.message)
      // Remove the optimistic user message on failure
      setMessages((prev) => prev.slice(0, -1))
    } finally {
      setIsLoading(false)
    }
  }, [documentId, messages, isLoading])

  const clearChat = useCallback(() => {
    setMessages([])
    setError(null)
  }, [])

  return { messages, isLoading, error, sendMessage, clearChat }
}
