import { useState, useCallback } from 'react'
import { generateQuiz, submitQuiz } from '../services/api'

/**
 * useQuiz — manages quiz generation, answer tracking, and submission.
 *
 * @param {string} documentId
 * @returns quiz state + actions
 */
export function useQuiz(documentId) {
  const [quizId,    setQuizId]    = useState(null)
  const [questions, setQuestions] = useState([])
  const [answers,   setAnswers]   = useState({})   // { question_id: answer }
  const [result,    setResult]    = useState(null)  // QuizSubmitResponse
  const [phase,     setPhase]     = useState('config')  // config | attempt | result
  const [isLoading, setIsLoading] = useState(false)
  const [error,     setError]     = useState(null)

  /**
   * Generates a new quiz.
   * @param {{ question_type, num_questions, topic_focus }} opts
   */
  const startQuiz = useCallback(async (opts) => {
    setIsLoading(true)
    setError(null)
    setResult(null)
    setAnswers({})

    try {
      const { quiz_id, questions: qs } = await generateQuiz({
        document_id:   documentId,
        question_type: opts.question_type,
        num_questions: opts.num_questions,
        topic_focus:   opts.topic_focus || undefined,
      })
      setQuizId(quiz_id)
      setQuestions(qs)
      setPhase('attempt')
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }, [documentId])

  /**
   * Records the user's answer for a question.
   * @param {string} questionId
   * @param {string} answer
   */
  const setAnswer = useCallback((questionId, answer) => {
    setAnswers((prev) => ({ ...prev, [questionId]: answer }))
  }, [])

  /**
   * Submits all answers and fetches results.
   */
  const submitAnswers = useCallback(async () => {
    if (!quizId) return
    setIsLoading(true)
    setError(null)

    try {
      const res = await submitQuiz({ quiz_id: quizId, user_answers: answers })
      setResult(res)
      setPhase('result')
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }, [quizId, answers])

  /** Resets to configuration phase. */
  const resetQuiz = useCallback(() => {
    setQuizId(null)
    setQuestions([])
    setAnswers({})
    setResult(null)
    setPhase('config')
    setError(null)
  }, [])

  const answeredCount  = Object.keys(answers).length
  const totalQuestions = questions.length
  const allAnswered    = totalQuestions > 0 && answeredCount === totalQuestions

  return {
    quizId, questions, answers, result,
    phase, isLoading, error,
    answeredCount, totalQuestions, allAnswered,
    startQuiz, setAnswer, submitAnswers, resetQuiz,
  }
}
