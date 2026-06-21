# Frontend Code Review — Security+ Trainer (React/Vite)

**Reviewer:** Senior Frontend Engineer (read-only review)
**Date:** 2026-06-04
**Scope:** `frontend/src/**`, `vite.config.js`, `package.json`, `eslint.config.js`
**Stack:** Vite 8 + React 19 (StrictMode) + React Router v7 + Zustand 5 + Axios + Tailwind v4 + @dnd-kit. Session-based auth (Django sessions + CSRF). No TypeScript, no tests.

## Summary

The frontend is small, readable, and unusually well-commented for a hobby project; the recent answer-UX work (shuffle seeding, render-time state reset, server-gated green reveal) is thoughtfully done and the cross-stack answer contracts (`buildAnswer` payloads and the `correct_ids`/`correct_order` reveal fields) currently **match the Django backend exactly** — verified against `backend/questions/models.py` and `backend/progress/views.py`. The real weaknesses are structural and operational rather than functional: `QuestionWrapper.jsx` is a 498-line monolith mixing five concerns; there is **zero error handling** anywhere (no error boundary, stores have no error state, several `.catch(()=>{})` swallow failures silently, and an unhandled rejection in `App`'s mount effect or any store action surfaces as a blank screen or a hung spinner); there is **no test infrastructure** despite delicate state logic (render-time reset, shuffle-seeding, two-strike gating) that is exactly the kind of thing that regresses silently; three declared question types (`drag_drop`, `fill_blank`, `pbq_simulation`) render **nothing** with no fallback; and the cross-stack contracts, while correct today, are duplicated as prose comments on both sides with no shared schema or test to keep them honest. Accessibility is basic-to-poor (icon-only DnD handles, no live regions for feedback, no focus management). None of these are release blockers for a personal study tool, but the error-handling and missing-type-fallback gaps are the two most likely to bite a real user.

---

## Findings

### FE-01 — `QuestionWrapper.jsx` is a 498-line monolith mixing 5 concerns
- **Severity:** High
- **File:** `frontend/src/components/questions/QuestionWrapper.jsx:1-498`
- **What's wrong:** One file holds the container component, three input renderers (`MultipleChoice` 222-250, `MultiSelect` 264-313, `Ordering` 331-386, `SortableItem` 391-415), and six pure helpers (`computeDisplayChoices`, `sameOrder`, `initialSelection`, `hasSelection`, `buildAnswer` 427-498). The type-dispatch logic, the network/feedback lifecycle, the shuffle/reveal logic, and three independent UI widgets all live together. This hurts testability (helpers can't be imported without the component), reuse (a future PBQ renderer can't reuse `MultipleChoice`), and review surface.
- **Proposed fix:** Extract into a folder:
  - `questions/inputs/MultipleChoice.jsx`, `MultiSelect.jsx`, `Ordering.jsx` (+ `SortableItem` colocated in `Ordering.jsx`).
  - `questions/answerLogic.js` — the pure helpers (`computeDisplayChoices`, `sameOrder`, `initialSelection`, `hasSelection`, `buildAnswer`). These become directly unit-testable (see Tests section).
  - `questions/QuestionFeedback.jsx` — the feedback panel (lines 174-206).
  - `QuestionWrapper.jsx` keeps only state + dispatch (~120 lines). Pure mechanical move; no behavior change.
- **Cross-stack:** no
- **Effort:** M

### FE-02 — No error handling anywhere; failures surface as blank screens or stuck spinners
- **Severity:** High
- **Files:** `frontend/src/store/sessionStore.js:34-93`, `frontend/src/store/userStore.js:35-92`, `frontend/src/api/client.js` (no response interceptor), `frontend/src/App.jsx` (no error boundary)
- **What's wrong:** `sessionStore` actions (`startSession`, `fetchNextQuestion`, `submitAnswer`, `completeSession`) have no try/catch and no error state. If `/sessions/.../next/` 500s or the network drops, the promise rejects unhandled and the page sits on "Loading question…" forever (`StudySession.jsx:16`, `PracticeExam.jsx:40`, `PBQSession.jsx:16`). `handleSubmit` in `QuestionWrapper` (line 91) `await`s `submitAnswer` with no catch — a failed submit throws an unhandled rejection and the UI never advances. There is no React error boundary, so any render-time throw (e.g. a malformed question, see FE-07) white-screens the whole app.
- **Proposed fix:**
  1. Add an `<ErrorBoundary>` component wrapping `<Routes>` in `App.jsx` with a fallback ("Something went wrong — reload").
  2. Add an Axios **response** interceptor in `client.js` to normalize errors (and optionally redirect to `/login` on 401 so an expired session doesn't strand the user mid-session).
  3. Give `sessionStore` an `error` field; wrap each action's body in try/catch, set `error`, and have session pages render a retry affordance instead of an infinite spinner. Same for the `QuestionWrapper.handleSubmit` await.
- **Cross-stack:** no
- **Effort:** M

### FE-03 — Cross-stack answer contracts are correct but unguarded (duplicated prose, no shared schema/test)
- **Severity:** Medium
- **Files:** `frontend/src/components/questions/QuestionWrapper.jsx:487-498` (`buildAnswer`) and `:138,148,158` (consumes `result.correct_ids` / `result.correct_order`); backend `backend/questions/models.py:149-173` (`check_answer`), `backend/progress/views.py:120-144`.
- **What's wrong / verified:** The contract is **currently correct** — verified both directions:

  | question_type | `buildAnswer` emits (FE) | `check_answer` reads (BE) | match |
  |---|---|---|---|
  | multiple_choice / true_false | `{ selected_id }` (line 489) | `submitted.get('selected_id')` (models.py:169) | ✓ |
  | multi_select | `{ selected_ids }` (line 492) | `submitted.get('selected_ids')` (models.py:171) | ✓ |
  | ordering | `{ ordered_ids }` (line 495) | `submitted.get('ordered_ids')` (models.py:173) | ✓ |

  Reveal fields consumed by the component: `correct_ids` (int[]) for choice types, `correct_order` (int[]) for ordering — these match `views.py:142,144` exactly, and the server gates their presence on `resolved` (views.py:138), which the component relies on (presence = reveal). The risk is purely that **both sides are kept in sync only by hand-written comments**; there is no shared constant, no schema, and no test. The fallback branch `buildAnswer` returns `{ answer: selected }` (line 497) for any unhandled type, which `check_answer` would silently treat as wrong (no `selected_id`/etc.), so a new type fails closed but invisibly.
- **Proposed fix:** Add a unit test that asserts the exact emitted shape per type (cheapest guard — see Tests). Longer term, a single shared `QUESTION_TYPES`/payload-shape module referenced by docs on both sides, or generate one from the other. At minimum, replace the silent `{ answer }` fallback with a thrown error so an unmapped type is loud in dev.
- **Cross-stack:** **YES** — answer-submission payload + reveal-response contract with `check_answer`/`SessionAnswerView`.
- **Effort:** S (test) / M (shared schema)

### FE-04 — Three declared question types render nothing, with no fallback UI
- **Severity:** High
- **File:** `frontend/src/components/questions/QuestionWrapper.jsx:132-160`
- **What's wrong:** The type switch handles `multiple_choice`, `true_false`, `multi_select`, `ordering`. The schema/CLAUDE.md declares `drag_drop`, `fill_blank`, and `pbq_simulation` as valid `question_type` values, and `check_answer` (models.py:174-178) implements `drag_drop` and `fill_blank`. If the server ever serves one (the PBQ flow is literally named for performance-based questions), the component renders **only the stem and a permanently-disabled Submit button** (`hasSelection` returns `selected !== null`, and `selected` starts `null` → button stays disabled forever). The user is stuck with no way to answer or skip.
- **Proposed fix:** Add an explicit `else` branch rendering an "Unsupported question type — Skip" panel with a button that calls `fetchNextQuestion()`, so the session can never dead-end. Then implement `fill_blank` (text inputs → `{ answers: [...] }`) and `drag_drop` (`{ matches: {...} }`) since the backend already scores them. `pbq_simulation` has no `check_answer` branch on the backend either — note that as a paired gap.
- **Cross-stack:** **YES** (partial) — implementing the missing inputs requires emitting `{ answers }` / `{ matches }` to match `check_answer`; `pbq_simulation` needs a backend branch first.
- **Effort:** S (fallback) / L (full implementations)

### FE-05 — `PracticeExam` timer effect calls a stale `handleComplete`; double-completion possible
- **Severity:** Medium
- **File:** `frontend/src/pages/PracticeExam.jsx:17-35`
- **What's wrong:** The interval effect depends on `[session]` and calls `handleComplete`, which is recreated every render but captured once at effect setup (stale closure — works here only because it just calls store actions + `navigate`). More importantly, there is **no guard against double completion**: the timer's `handleComplete` and the manual "Submit Exam" button (line 58) can both fire. `completeSession` (sessionStore:86) is a no-op-safe on the second call only because it nulls `session` first, but the second call still `POST`s `/complete/` and `GET`s `/results/` against a now-null `session` → `session.id` throws (unhandled, FE-02). Also the effect cleanup clears the interval correctly, but on auto-complete the `setSecondsLeft` updater calls `handleComplete` **inside a state setter** (line 24) — a side effect in a reducer, which React StrictMode double-invokes in dev.
- **Proposed fix:** Move completion out of the setter: track `secondsLeft` and trigger completion from a separate effect when it hits 0. Add a `completing` ref/flag so manual+timer can't both run. Pull completion into a `useCallback` or read store actions via `getState()` to avoid the stale closure. Guard `completeSession` against a null session (also helps FE-02).
- **Cross-stack:** no
- **Effort:** M

### FE-06 — `Results` page relies solely on router `location.state`; breaks on refresh/direct-nav
- **Severity:** Medium
- **File:** `frontend/src/pages/Results.jsx:4-16`; written by `PracticeExam.jsx:34`
- **What's wrong:** Results come only from `useLocation().state.results`. A refresh, a bookmark, a browser back→forward, or any direct navigation to `/results` loses the state and shows "No results to display." The data exists server-side (`GET /sessions/<id>/results/`), so this is recoverable. `StudySession` and `PBQSession` never navigate to `/results` at all (they only "End Session" back to the dashboard), so study/PBQ scores are never shown — only exams reach this page.
- **Proposed fix:** Pass the completed `sessionId` in the navigation state (or a query param) and have `Results` fetch `/sessions/:id/results/` on mount if `location.state.results` is absent. Keep the passed-in results as a fast path. This also lets study/PBQ sessions show results.
- **Cross-stack:** no (uses existing endpoint)
- **Effort:** M

### FE-07 — Render-time reset pattern is correct but fragile; reset logic duplicated and unguarded against bad data
- **Severity:** Medium
- **File:** `frontend/src/components/questions/QuestionWrapper.jsx:78-85`, `103-118`
- **What's wrong:** The "reset state during render when `activeId !== question.id`" pattern (78-85) is the documented React idiom for derived-state-on-prop-change and is implemented correctly (calls setState during render of the same component, which React bails-and-reruns). Two concerns: (1) the same reset shape (`setSelected(initialSelection(...))`, `setSubmitted(false)`, `setResult(null)`) is **repeated** in three places (the render block, `handleNext` 103-108, `handleRetry` 114-118) — `handleNext` even resets state for the *outgoing* question right before `fetchNextQuestion` swaps it, which is redundant with the render-time reset. (2) `computeDisplayChoices` (427) does `question.answer_choices` with no guard; if the API ever returns a question without `answer_choices` (or null), `shuffle([...undefined])` throws during render → white screen (no error boundary, FE-02). The leading `question.question_type.replace('_',' ')` (line 124) and `question.difficulty` (126) are likewise unguarded.
- **Proposed fix:** Extract a `resetForQuestion(q)` helper to remove the triplication; drop the redundant reset in `handleNext`. Add a defensive default `const choices = question.answer_choices ?? []` in `computeDisplayChoices`. Pairs naturally with the FE-01 extraction.
- **Cross-stack:** no
- **Effort:** S

### FE-08 — `Domains` effect has an unmount/race gap; `client` calls can set state after unmount
- **Severity:** Low
- **File:** `frontend/src/pages/Domains.jsx:13-26`
- **What's wrong:** `Promise.all([...]).then(...).finally(setLoading(false))` calls `setDomains`/`setProgress`/`setLoading` after the await with no `cancelled` guard. If the user navigates away before both requests resolve, React 18/19 warns about state updates on an unmounted component (benign but noisy), and in StrictMode the effect runs twice in dev → two in-flight request pairs. The inner `.catch(() => ({ data: [] }))` on the progress call (line 16) is fine, but the outer chain has **no `.catch`** — if `/domains/` rejects, `loading` is cleared (finally) but `domains` stays `[]` with no error message; the user sees an empty grid silently.
- **Proposed fix:** Standard `let cancelled = false` cleanup, guard setState calls, and a cleanup that sets `cancelled = true`. Add a `.catch` that sets an error state for the domains call. (Same silent-empty pattern in `Dashboard.jsx:12` and `PBQHub.jsx:9` with `.catch(() => {})` — those also swallow failure silently.)
- **Cross-stack:** no
- **Effort:** S

### FE-09 — CSRF cookie parsing is brittle to value contents
- **Severity:** Low
- **File:** `frontend/src/api/client.js:30-41`
- **What's wrong:** `document.cookie.split('; ').find(row => row.startsWith('csrftoken=')).split('=')[1]` takes only `[1]` after splitting on `=`. Django's CSRF token is alphanumeric so this works today, but the pattern silently truncates if a value ever contains `=`, and `split('; ')` assumes exactly `"; "` separators. It's also re-parsed on every mutating request. Minor robustness issue, not a current bug.
- **Proposed fix:** Use `.slice(('csrftoken=').length)` instead of `.split('=')[1]`, or a small `getCookie(name)` regex helper. Optionally let Axios do it natively via `xsrfCookieName: 'csrftoken'` / `xsrfHeaderName: 'X-CSRFToken'` in the `axios.create` config and drop the interceptor entirely (Axios reads the cookie and sets the header for same-origin requests — works in the combined-image prod topology; in dev the Vite proxy is same-origin too).
- **Cross-stack:** minor — header name `X-CSRFToken` must match Django's `CSRF_HEADER_NAME`.
- **Effort:** S

### FE-10 — Accessibility gaps: DnD keyboard support is wired but undiscoverable; feedback not announced; icon-only handles
- **Severity:** Medium
- **File:** `frontend/src/components/questions/QuestionWrapper.jsx:334-337` (KeyboardSensor), `391-415` (SortableItem), `174-206` (feedback panel)
- **What's wrong:**
  - `KeyboardSensor` + `sortableKeyboardCoordinates` are correctly registered, so keyboard reordering technically works — but there is no visible "press space to pick up" instruction and no `aria-label`/`aria-roledescription` on the sortable rows, so a keyboard/SR user can't discover it. The drag handle is a bare `☰` glyph (line 410) with no accessible name.
  - The feedback panel (Correct/Incorrect + hint + explanation) is injected without `role="status"`/`aria-live`, so screen readers don't announce the result after submit.
  - After "Try Again" / "Next Question" there is no focus management — focus is lost to `<body>`.
  - Choice buttons are real `<button>`s (good) but convey selection only via color (blue border), with no `aria-pressed`; correct-answer reveal is green-only (color-only signal — fails for color-blind users; the `✓` in MultiSelect helps, MultipleChoice has none).
- **Proposed fix:** Add `role="status" aria-live="polite"` to the feedback panel; `aria-pressed={isSelected}` on choice buttons and a non-color correct marker (e.g. a "✓ Correct" text label) in `MultipleChoice`; `aria-label`/`aria-roledescription="sortable"` + a visible hint on sortable rows; focus the feedback panel or the Next button after submit. Reuse @dnd-kit's `announcements` API for screen-reader drag feedback.
- **Cross-stack:** no
- **Effort:** M

### FE-11 — No test infrastructure at all
- **Severity:** High
- **Files:** `frontend/package.json` (no test deps/scripts), absent `vitest.config`, no `*.test.jsx`
- **What's wrong:** There is delicate logic — render-time reset, shuffle seeding with the ordering "reshuffle if pre-solved" rule, two-strike gating, per-type answer payloads, the auth route guard — and **nothing tests any of it**. The cross-stack payload shapes (FE-03) and the reveal gating are exactly the contracts that break silently on a refactor.
- **Proposed fix:** Add `vitest` + `@testing-library/react` + `@testing-library/jest-dom` + `jsdom`, a `test` script, and `vitest.config.js` (`environment: 'jsdom'`). The FE-01 extraction makes the pure helpers trivially testable. See the Critical Missing Tests section for the prioritized first set.
- **Cross-stack:** no
- **Effort:** M

### FE-12 — Dead code: `App.css` (Vite template leftover) and four empty directories
- **Severity:** Nit
- **Files:** `frontend/src/App.css` (185 lines, unimported — Vite starter CSS for `.hero`/`#next-steps`/etc.), empty `frontend/src/hooks/`, `frontend/src/components/common/`, `frontend/src/components/feedback/`, `frontend/src/components/progress/`. Also `src/assets/react.svg`, `vite.svg`, possibly `hero.png` are template leftovers.
- **What's wrong:** `App.css` is never imported (confirmed — only `index.css` is imported, in `main.jsx:3`) and references CSS variables that don't exist in this project. The empty dirs are scaffolding that git doesn't track (no `.gitkeep`) and add noise. Pure clutter.
- **Proposed fix:** Delete `App.css` and the four empty dirs; audit `src/assets/` for unused starter SVGs (`react.svg`/`vite.svg`). Note the FE-01 extraction will populate `components/questions/` — but `common`/`feedback`/`progress` should either be used or removed.
- **Cross-stack:** no
- **Effort:** S

### FE-13 — `App` mount effect: missing deps, unhandled rejection on the CSRF/fetchMe chain
- **Severity:** Low
- **File:** `frontend/src/App.jsx:61-63`
- **What's wrong:** `useEffect(() => { client.get('/auth/csrf/').finally(fetchMe) }, [])` has an empty dep array while using `fetchMe` (eslint `react-hooks/exhaustive-deps` would flag it; the rule is enabled in `eslint.config.js`). It's fine in practice because `fetchMe` is a stable Zustand action, but it's an inconsistency the linter should be catching — worth confirming lint passes. The `client.get('/auth/csrf/')` has no `.catch`; if CSRF seeding 500s, `.finally(fetchMe)` still runs (good), but a `fetchMe` rejection is caught internally (userStore:39) so this is benign — still, the bare `client.get` rejection on the csrf call itself is technically unhandled.
- **Proposed fix:** Either add `fetchMe` to deps (it's stable) or pull it via `useUserStore.getState().fetchMe()` to make the no-deps intent explicit. Run `npm run lint` and fix any `exhaustive-deps` warnings across the session pages (`StudySession:14`, `PracticeExam:15`, `PBQSession:14` all have the same empty-array-with-action pattern).
- **Cross-stack:** no
- **Effort:** S

### FE-14 — `userStore.logout` has no try/catch; a failed logout strands the local session
- **Severity:** Low
- **File:** `frontend/src/store/userStore.js:70-73`; caller `Dashboard.jsx:15-18`
- **What's wrong:** `logout` `await`s `/auth/logout/` then clears `user`. If the POST fails (network/CSRF), it throws, `user` is never cleared, and `Dashboard.handleLogout` (which has no catch) leaves the user "logged in" locally with a dangling navigate. Minor, but inconsistent with the careful try/finally added to `login`/`register`.
- **Proposed fix:** Clear `user` in a `finally` (or before the request) so logout always succeeds locally; let the cookie expire server-side. Add the matching catch in `handleLogout`.
- **Cross-stack:** no
- **Effort:** S

### FE-15 — Minor UX/state nits
- **Severity:** Nit
- **Files:** various
- **What's wrong:**
  - `sessionStore.submitAnswer` (sessionStore:68) dereferences `session.id`/`currentQuestion.id` with no null check — if called with no active session it throws (related to FE-02/FE-05).
  - `question.question_type.replace('_', ' ')` (QuestionWrapper:124) replaces only the **first** underscore, so `multi_select` → "multi select" (ok) but a hypothetical `pbq_simulation` badge is fine; just use `replaceAll`/regex `/_/g` for consistency.
  - `PracticeExam` is wired to a "90 questions, 90 minutes" exam (Dashboard:56) but there is no question counter / progress indicator — the user can't see how many remain.
  - `Results` "Study Again" links to `/study` but a stale `sessionStore.session` may still be set from the just-completed exam... actually `completeSession` nulls it, so this is fine — noting it as verified-OK.
- **Proposed fix:** Small guards + a question counter in exam mode (the session/results endpoints already have totals).
- **Cross-stack:** no
- **Effort:** S

---

## Proposed Change Plan (ordered work items)

**WI-1 — Stop silent failures (highest user impact).** FE-02 (error boundary + Axios response interceptor + store error states), FE-04 (unsupported-type fallback so sessions can't dead-end), FE-07 (defensive `answer_choices ?? []`), FE-14 (logout always clears locally), FE-08 (`.catch` on Domains/Dashboard/PBQHub fetches). These together eliminate every white-screen / infinite-spinner / stuck-state path.

**WI-2 — Decompose `QuestionWrapper`.** FE-01 (extract inputs + `answerLogic.js` + feedback panel), folding in FE-07's `resetForQuestion` helper and FE-15's `replaceAll`. Mechanical, unlocks WI-4 testing.

**WI-3 — Fix the exam + results flows.** FE-05 (timer: move completion out of the setter, add a completing guard, fix stale closure) and FE-06 (Results fetches `/sessions/:id/results/` on refresh; wire study/PBQ to show results). FE-15 question counter.

**WI-4 — Add tests.** FE-11 (vitest + RTL scaffold) then the Critical Missing Tests below. Do this right after WI-2 so the extracted helpers are import-testable, and it locks the FE-03 cross-stack contract.

**WI-5 — Accessibility pass.** FE-10 (aria-live feedback, aria-pressed, non-color correct marker, DnD announcements + handle labels, focus management).

**WI-6 — Cleanup & robustness.** FE-09 (CSRF parsing / native Axios xsrf), FE-13 (lint deps + run `npm run lint`), FE-12 (delete `App.css` + empty dirs + unused assets), FE-03 shared-schema (optional, after the test guard exists).

---

## Critical Missing Tests (highest value first)

1. **`buildAnswer` per question_type** (`answerLogic.js`) — asserts exact shapes `{selected_id}` / `{selected_ids}` / `{ordered_ids}`. This is the **cross-stack contract guard** (FE-03); cheapest, highest-leverage test. Add a paired note/test that the backend `check_answer` keys match.
2. **`shuffle`** (`utils/shuffle.js`) — returns a new array (no mutation), same length, same elements (set equality); for ordering, the `computeDisplayChoices` "reshuffle once if it reproduces served order" rule is honored (mock `Math.random`).
3. **`QuestionWrapper` resets on question change** — render with question A, select an answer, rerender with question B (different id), assert `selected`/`submitted`/`result` are reset and B's choices render (no crash). This locks the render-time reset idiom (FE-07).
4. **`RequireAuth` guard** (`App.jsx`) — renders `Loading…` while `authChecked` is false; redirects to `/login` when `authChecked && !user`; renders children when authed.
5. **Two-strike / reveal gating in `QuestionWrapper`** — first wrong submit shows hint + "Try Again", no `correct_ids` reveal; second wrong shows explanation + "Next Question" and highlights green when `correct_ids` present; exam mode hides hint/explanation but still reveals. (Mock `sessionStore.submitAnswer`.)
6. **`hasSelection` / `initialSelection` per type** — Submit button enable/disable logic; ordering starts fully populated, multi_select starts empty, choice types start null.
7. **Unsupported-type fallback (after FE-04)** — a `drag_drop`/`fill_blank` question renders the skip affordance rather than a dead Submit button.
