/**
 * components/questions/inputs/Ordering.jsx
 *
 * Drag-and-drop sortable list for ordering questions (@dnd-kit). The current
 * order is held by the parent as an array of choice ids; dragging a row
 * reorders that array. When `correctOrder` is present (question resolved), the
 * sortable list is replaced by a static green list showing the correct sequence.
 *
 * Props:
 *   choices      {object[]} -- AnswerChoiceSerializer array [{id, text, order}]
 *   order        {number[]} -- choice ids in the user's current order
 *   onChange     {function} -- called with the reordered id array after a drag
 *   disabled     {boolean}  -- true after submission; disables dragging
 *   correctOrder {number[]|undefined} -- the correct id sequence; when present,
 *                 renders the green correct-order reveal instead of the list.
 */
import {
  DndContext,
  closestCenter,
  PointerSensor,
  KeyboardSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core'
import {
  SortableContext,
  verticalListSortingStrategy,
  arrayMove,
  useSortable,
  sortableKeyboardCoordinates,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'

export default function Ordering({ choices, order, onChange, disabled, correctOrder }) {
  // useSensors must be called unconditionally (rules of hooks) — before the
  // correctOrder early-return below.
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  )
  const list = Array.isArray(choices) ? choices : []
  const byId = Object.fromEntries(list.map((c) => [c.id, c]))
  // Guard: fall back to the served choice order if `order` is ever null/non-array
  // (defensive backstop against a stale value mid-question-transition).
  const ids = Array.isArray(order) ? order : list.map((c) => c.id)

  // Reveal: show the canonical correct sequence in green.
  if (Array.isArray(correctOrder)) {
    return (
      <div className="space-y-3">
        <p className="text-xs font-medium text-green-700">Correct order:</p>
        {correctOrder.map((id, index) => (
          <div
            key={id}
            className="flex items-center gap-3 rounded-xl border border-green-500 bg-green-50 px-4 py-3"
          >
            <span className="text-green-600 text-sm w-5 select-none">{index + 1}.</span>
            <span className="text-gray-800">{byId[id]?.text ?? ''}</span>
          </div>
        ))}
      </div>
    )
  }

  const handleDragEnd = (event) => {
    const { active, over } = event
    if (!over || active.id === over.id) return
    const oldIndex = ids.indexOf(active.id)
    const newIndex = ids.indexOf(over.id)
    onChange(arrayMove(ids, oldIndex, newIndex))
  }

  return (
    <div>
      <p className="text-xs text-gray-400 mb-2">Drag the rows into the correct order (or focus a row and use the arrow keys).</p>
      <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
        <SortableContext items={ids} strategy={verticalListSortingStrategy}>
          <div className="space-y-3">
            {ids.map((id, index) => (
              <SortableItem
                key={id}
                id={id}
                index={index}
                text={byId[id]?.text ?? ''}
                disabled={disabled}
              />
            ))}
          </div>
        </SortableContext>
      </DndContext>
    </div>
  )
}

/**
 * A single draggable row within the Ordering list.
 */
function SortableItem({ id, index, text, disabled }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } =
    useSortable({ id, disabled })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.6 : 1,
  }

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      aria-roledescription="sortable"
      aria-label={`Position ${index + 1}: ${text}`}
      className={`flex items-center gap-3 rounded-xl border border-gray-200 bg-white px-4 py-3
        ${disabled ? 'cursor-default' : 'cursor-grab active:cursor-grabbing hover:border-gray-300'}`}
    >
      <span className="text-gray-400 select-none" aria-hidden="true">☰</span>
      <span className="text-gray-400 text-sm w-5 select-none" aria-hidden="true">{index + 1}.</span>
      <span className="text-gray-800">{text}</span>
    </div>
  )
}
