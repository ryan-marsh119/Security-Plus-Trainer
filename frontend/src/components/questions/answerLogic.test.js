import { describe, it, expect } from 'vitest'
import {
  SUPPORTED_TYPES,
  buildAnswer,
  hasSelection,
  initialSelection,
  computeDisplayChoices,
  sameOrder,
} from './answerLogic'

const choices = [
  { id: 10, text: 'A', order: 1 },
  { id: 20, text: 'B', order: 2 },
  { id: 30, text: 'C', order: 3 },
]

describe('buildAnswer — CROSS-STACK CONTRACT with Question.check_answer', () => {
  it('multiple_choice → {selected_id}', () => {
    expect(buildAnswer({ question_type: 'multiple_choice' }, 20)).toEqual({ selected_id: 20 })
  })
  it('true_false → {selected_id}', () => {
    expect(buildAnswer({ question_type: 'true_false' }, 10)).toEqual({ selected_id: 10 })
  })
  it('multi_select → {selected_ids}', () => {
    expect(buildAnswer({ question_type: 'multi_select' }, [10, 30])).toEqual({ selected_ids: [10, 30] })
  })
  it('ordering → {ordered_ids}', () => {
    expect(buildAnswer({ question_type: 'ordering' }, [30, 10, 20])).toEqual({ ordered_ids: [30, 10, 20] })
  })
  it('throws on an unsupported type instead of emitting a bad shape', () => {
    expect(() => buildAnswer({ question_type: 'drag_drop' }, {})).toThrow()
  })
})

describe('hasSelection', () => {
  it('multiple_choice requires a non-null id', () => {
    expect(hasSelection({ question_type: 'multiple_choice' }, null)).toBe(false)
    expect(hasSelection({ question_type: 'multiple_choice' }, 10)).toBe(true)
  })
  it('multi_select requires at least one id', () => {
    expect(hasSelection({ question_type: 'multi_select' }, [])).toBe(false)
    expect(hasSelection({ question_type: 'multi_select' }, [10])).toBe(true)
  })
  it('ordering is submittable once populated', () => {
    expect(hasSelection({ question_type: 'ordering' }, [10, 20, 30])).toBe(true)
  })
})

describe('initialSelection', () => {
  it('multi_select starts empty', () => {
    expect(initialSelection({ question_type: 'multi_select' }, choices)).toEqual([])
  })
  it('ordering starts as the display-order ids', () => {
    expect(initialSelection({ question_type: 'ordering' }, choices)).toEqual([10, 20, 30])
  })
  it('choice types start null', () => {
    expect(initialSelection({ question_type: 'multiple_choice' }, choices)).toBeNull()
  })
})

describe('computeDisplayChoices', () => {
  it('keeps true_false in natural order', () => {
    const q = { question_type: 'true_false', answer_choices: choices }
    expect(computeDisplayChoices(q)).toEqual(choices)
  })
  it('returns a same-length set for multiple_choice', () => {
    const q = { question_type: 'multiple_choice', answer_choices: choices }
    const out = computeDisplayChoices(q)
    expect(out).toHaveLength(3)
    expect(new Set(out.map((c) => c.id))).toEqual(new Set([10, 20, 30]))
  })
  it('does not crash when answer_choices is missing', () => {
    expect(computeDisplayChoices({ question_type: 'drag_drop' })).toEqual([])
  })
  it('ordering returns a permutation of the same ids', () => {
    const q = { question_type: 'ordering', answer_choices: choices }
    const out = computeDisplayChoices(q)
    expect(out).toHaveLength(3)
    expect(new Set(out.map((c) => c.id))).toEqual(new Set([10, 20, 30]))
  })
})

describe('sameOrder', () => {
  it('true only when ids match positionally', () => {
    expect(sameOrder(choices, choices)).toBe(true)
    expect(sameOrder(choices, [...choices].reverse())).toBe(false)
  })
})

describe('SUPPORTED_TYPES', () => {
  it('contains the four wired types and not the unwired ones', () => {
    expect(SUPPORTED_TYPES.has('multiple_choice')).toBe(true)
    expect(SUPPORTED_TYPES.has('ordering')).toBe(true)
    expect(SUPPORTED_TYPES.has('drag_drop')).toBe(false)
    expect(SUPPORTED_TYPES.has('pbq_simulation')).toBe(false)
  })
})
