import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import QuestionWrapper from './QuestionWrapper'

// Controllable mock of the Zustand session store. vi.hoisted lets the factory
// below reference it despite vi.mock hoisting.
const { mockStore } = vi.hoisted(() => ({
  mockStore: { submitAnswer: vi.fn(), fetchNextQuestion: vi.fn() },
}))
vi.mock('../../store/sessionStore', () => ({ default: () => mockStore }))

const mcQuestion = {
  id: 1,
  question_type: 'multiple_choice',
  difficulty: 'easy',
  question_text: 'What is 2+2?',
  answer_choices: [
    { id: 1, text: 'three', order: 1 },
    { id: 2, text: 'four', order: 2 },
  ],
}

beforeEach(() => {
  mockStore.submitAnswer.mockReset()
  mockStore.fetchNextQuestion.mockReset()
})

describe('QuestionWrapper', () => {
  it('submits the contract-shaped answer for the selected choice', async () => {
    mockStore.submitAnswer.mockResolvedValue({ correct: true, attempt_number: 1, correct_ids: [2] })
    render(<QuestionWrapper question={mcQuestion} />)

    fireEvent.click(screen.getByText('four'))
    fireEvent.click(screen.getByText('Submit Answer'))

    await waitFor(() => expect(mockStore.submitAnswer).toHaveBeenCalledWith({ selected_id: 2 }))
  })

  it('reveals the correct answer green only when correct_ids is present (Contract B)', async () => {
    // 2nd wrong attempt → resolved → server includes correct_ids.
    mockStore.submitAnswer.mockResolvedValue({
      correct: false,
      attempt_number: 2,
      explanation: 'four is correct',
      correct_ids: [2],
    })
    render(<QuestionWrapper question={mcQuestion} />)
    fireEvent.click(screen.getByText('three'))
    fireEvent.click(screen.getByText('Submit Answer'))

    await waitFor(() => expect(screen.getByText('Incorrect')).toBeInTheDocument())
    expect(screen.getByLabelText('correct answer')).toBeInTheDocument()
  })

  it('does NOT reveal on the 1st wrong attempt (correct_ids absent)', async () => {
    mockStore.submitAnswer.mockResolvedValue({
      correct: false,
      attempt_number: 1,
      hint: 'think harder',
      // no correct_ids — gate keeps it hidden
    })
    render(<QuestionWrapper question={mcQuestion} />)
    fireEvent.click(screen.getByText('three'))
    fireEvent.click(screen.getByText('Submit Answer'))

    await waitFor(() => expect(screen.getByText('Try Again')).toBeInTheDocument())
    expect(screen.queryByLabelText('correct answer')).not.toBeInTheDocument()
  })

  it('renders a Skip affordance (not a dead Submit) for unsupported types', () => {
    const dragQuestion = { ...mcQuestion, id: 9, question_type: 'drag_drop', answer_choices: [] }
    render(<QuestionWrapper question={dragQuestion} />)

    expect(screen.queryByText('Submit Answer')).not.toBeInTheDocument()
    fireEvent.click(screen.getByText('Skip Question'))
    expect(mockStore.fetchNextQuestion).toHaveBeenCalled()
  })

  it('resets state when the question changes (no stale submitted UI)', async () => {
    mockStore.submitAnswer.mockResolvedValue({ correct: true, attempt_number: 1, correct_ids: [2] })
    const { rerender } = render(<QuestionWrapper question={mcQuestion} />)
    fireEvent.click(screen.getByText('four'))
    fireEvent.click(screen.getByText('Submit Answer'))
    await waitFor(() => expect(screen.getByText('Correct!')).toBeInTheDocument())

    // New question (different id) → feedback cleared, Submit available again.
    const next = { ...mcQuestion, id: 2, question_text: 'Pick one' }
    rerender(<QuestionWrapper question={next} />)
    expect(screen.queryByText('Correct!')).not.toBeInTheDocument()
    expect(screen.getByText('Submit Answer')).toBeInTheDocument()
  })
})
