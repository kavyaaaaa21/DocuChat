import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Home     from './pages/Home.jsx'
import ChatPage from './pages/ChatPage.jsx'
import QuizPage from './pages/QuizPage.jsx'
 
export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/"         element={<Home />} />
        <Route path="/chat/:id" element={<ChatPage />} />
        <Route path="/quiz/:id" element={<QuizPage />} />
        <Route path="*"         element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}