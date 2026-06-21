# Review Reconciliation & Execution Plan — Security+ Trainer

**Supervisor:** Staff Engineer (reconciliation of two independent reviews)
**Date:** 2026-06-04
**Inputs:** `resources/review_frontend.md` (FE-01..FE-15), `resources/review_backend.md` (BE-01..BE-17)
**Status:** PLAN ONLY — no source/config changed, no mutating commands run. Awaiting owner approval.

All cross-stack contract claims in both reviews were independently spot-checked against source:
`backend/questions/models.py` (`check_answer`), `backend/progress/views.py` (`SessionAnswerView`),
`backend/questions/views.py` (`QuestionListView`), `frontend/src/components/questions/QuestionWrapper.jsx`
(`buildAnswer`, reveal consumption), and `frontend/src/store/sessionStore.js` (`submitAnswer`).
**The contracts match exactly today** — verification notes are inline below.

---

## Summary

### Counts by severity (32 findings total)

| Severity | Backend | Frontend | Total |
|----------|---------|----------|-------|
| High     | BE-01, BE-02, BE-03 (3) | FE-01, FE-02, FE-04, FE-11 (4) | 7 |
| Medium   | BE-04, BE-05, BE-06, BE-07, BE-09, BE-14 (6) | FE-03, FE-05, FE-06, FE-07, FE-10 (5) | 11 |
| Low      | BE-08, BE-10, BE-12, BE-13, BE-15, BE-16 (6) | FE-08, FE-09, FE-13, FE-14 (4) | 10 |
| Nit      | BE-11, BE-17 (2) | FE-12, FE-15 (2) | 4 |

### Headline risks
1. **Answer-submit endpoint is brittle to anything but the happy path** (BE-01 race/no-transaction, BE-02 500-not-404, BE-03 no input validation). This is the single most important endpoint and three High findings converge on it — fix as one pass.
2. **Frontend has zero error handling** (FE-02): any 500/network drop → infinite spinner or white screen. The backend hardening above directly reduces how often the FE hits this, but the FE still needs guards.
3. **Three declared question types render nothing** (FE-04): `drag_drop`/`fill_blank` are *scored by the backend already* but the FE dead-ends the session (permanently-disabled Submit, no skip). `pbq_simulation` is unscorable on both sides.
4. **No test infrastructure on either side** (FE-11, BE-14) guarding delicate, security-sensitive logic (the reveal gate, two-strike gating, per-type payloads, SM-2). The CI `needs: test` gate exists but guards almost nothing.
5. **`/progress/domains/` silently returns `[]`** (BE-05) — denormalized counter is never written; the domain chart shows nothing, masked by a FE `.catch(() => ({data: []}))`.

### Severity adjustments (supervisor)
- **FE-11 (no tests): High → keep High, but treat as P4 prerequisite, not a standalone fix.** It is the enabling infra for locking every correctness fix; rated correctly.
- **BE-14 (no negative-path tests): Medium → effectively High in combination.** Individually Medium, but it is the *only* thing that will keep the BE-01/02/03 fixes from regressing. Sequenced as a hard dependency on those fixes (P4).
- **FE-04 fallback (the "Skip" panel): the *fallback* sub-item is High-value/S-effort and belongs in P1; the *full implementations* of drag_drop/fill_blank are L-effort and deferred (see Deferred).** The review bundles them; I split them.
- **BE-03 vs FE buildAnswer: confirmed NON-conflicting** (see Contract Decisions) — the proposed `AnswerSubmitSerializer` accepts exactly what `buildAnswer` emits. No severity change; flagged so the FE side isn't broken by the BE change.
- **FE-05 (timer stale closure / double-completion): Medium is correct**, but note the double-`POST /complete/` is partially masked because `completeSession` already early-returns on null session (verified `sessionStore.js:88`). The unhandled-throw path the review describes is the timer calling a stale `handleComplete` inside a state setter — real, keep Medium.
- Everything else: severities are consistent and accepted as rated.

---

## Cross-Stack Contract Decisions (LOCKED)

These are the authoritative contracts. Any work item touching submit/reveal must preserve them verbatim. Owner: **both** sides; the **backend is the source of truth**.

### Contract A — Answer-submit REQUEST
`POST /api/v1/sessions/<id>/answers/`
```json
{ "question_id": <int>, "answer": <dict> }
```
The FE store wraps the `buildAnswer()` output under `answer` and adds `question_id` (verified `sessionStore.js:70-73`). The `answer` dict shape per `question_type` (verified `models.py:168-179` ↔ `QuestionWrapper.jsx:487-498`):

| question_type | `answer` shape | FE emits | BE reads | status |
|---|---|---|---|---|
| multiple_choice / true_false | `{"selected_id": <int>}` | ✓ `buildAnswer` L489 | ✓ `submitted.get('selected_id')` L169 | **MATCH** |
| multi_select | `{"selected_ids": [<int>...]}` | ✓ L492 | ✓ L171 | **MATCH** |
| ordering | `{"ordered_ids": [<int>...]}` | ✓ L495 | ✓ L173 | **MATCH** |
| drag_drop | `{"matches": {"<item>":"<zone>"}}` | ✗ FE renders nothing | ✓ L175 | **BE-only (FE-04)** |
| fill_blank | `{"answers": ["<str>"...]}` (case/space-insensitive) | ✗ FE renders nothing | ✓ L177-178 | **BE-only (FE-04)** |
| pbq_simulation | — falls through → always `False` | ✗ | ✗ no branch L180 | **UNSCORABLE (deferred)** |

**Decision A1:** `AnswerSubmitSerializer` (BE-03) MUST be `{question_id: IntegerField(), answer: DictField(required=False, default=dict)}`. A `DictField` accepts every shape `buildAnswer` currently emits. **It must NOT add per-type field validation** that could reject a valid payload — `check_answer` already tolerates missing keys via `.get(default)`. This serializer is request-shape validation only.

**Decision A2:** The FE `buildAnswer` fallback `return { answer: selected }` (L497) for unmapped types is a latent silent-fail (it produces `{answer:{answer:...}}` server-side → scored wrong invisibly). Replace with a thrown error in dev / the FE-04 skip panel in the UI. Do **not** "fix" it by inventing a new server key.

### Contract B — Answer-submit RESPONSE (the reveal gate — SERVER-AUTHORITATIVE)
`SessionAnswerView` response (verified `views.py:120-144`):
- **Always present:** `correct` (bool), `attempt_number` (int), `hint` (str|null), `explanation` (str|null).
- `hint` populated **only** on 1st wrong attempt.
- `explanation` populated **only** when `correct` or `attempt_number >= 2`.
- `correct_ids` (choice types) / `correct_order` (ordering) included **ONLY when** `resolved = is_correct or attempt_number >= 2 or session_type == 'exam'`. **Field ABSENCE is the gate.** The FE reveals based purely on field presence (verified `QuestionWrapper.jsx:138,148,158` consume `result?.correct_ids`/`result?.correct_order`).

**Decision B1:** This gate is a server-enforced security control (prevents reading the answer off the wire before attempt 2 in study/PBQ). It MUST stay server-side. No FE work item (error handling, FE-04 wiring, FE-01 extraction) may move gating to the client, include these fields unconditionally, or change the `resolved` formula. Any test for the reveal must assert **`assertNotIn('correct_ids', response)` on the 1st wrong attempt** (BE-14 test #2), not just a falsy value.

**Decision B2:** When FE-04 wires `drag_drop`/`fill_blank`, the reveal for those types is currently **undefined** on the server (no `correct_*` branch for them in `views.py:141-144`). Either keep them unrevealed (acceptable) or add explicit branches — but if added, they MUST sit inside the same `if resolved:` block. Flag for the owner.

---

## Ordered Execution Plan

Phases are dependency-ordered. Within a phase, items can proceed in parallel unless noted. **Per CLAUDE.md: no commits/migrations without explicit owner approval; pause after each phase for review. Backend changes need an image rebuild to take effect (`docker compose up -d --build web`).**

### P1 — Correctness & dead-end elimination (highest user impact)

| ID | Covers | Owner | Sev | Eff | Change | Verify |
|----|--------|-------|-----|-----|--------|--------|
| **W1** | BE-02, BE-03, BE-01 | BE | High | M | Single pass on `SessionAnswerView.post`: (1) `get_object_or_404` for session + question (BE-02); (2) `AnswerSubmitSerializer` per Decision A1, `is_valid(raise_exception=True)` → 400 (BE-03); (3) wrap `SessionAnswer.create()` + `update_sm2` in `transaction.atomic()`, recompute `attempt_number` via `select_for_update()` and catch `IntegrityError` to re-resolve (BE-01). | `curl` missing/non-int `question_id` → 400; foreign session id → 404; valid submit still returns two-strike hint. Locked by P4 tests W12 #8/#9/#10. **Must not change Contract A/B.** |
| **W2** | FE-04 (fallback only), FE-07 (defensive `answer_choices ?? []`) | FE | High | S | Add explicit `else` branch in the type switch rendering an "Unsupported question type — Skip" panel whose button calls `fetchNextQuestion()`; replace `buildAnswer` silent fallback per Decision A2; default `const choices = question.answer_choices ?? []` in `computeDisplayChoices`. Session can never dead-end. | UI: force a `drag_drop` question → Skip button advances; a question with null `answer_choices` doesn't white-screen. Locked by FE test W11 #7. |
| **W3** | FE-02 | FE | High | M | (1) `<ErrorBoundary>` around `<Routes>` in `App.jsx`; (2) Axios **response** interceptor in `client.js` normalizing errors + optional 401→`/login` redirect; (3) `error` field on `sessionStore`, wrap each action body in try/catch, session pages render retry instead of infinite spinner; (4) `try/catch` on `QuestionWrapper.handleSubmit` await. | UI: kill backend mid-session → retry affordance, not infinite "Loading question…"; force a render throw → boundary fallback, not white screen. |

**Sequencing note:** W1 (BE) lands **before or with** W3 (FE error handling) so the FE is hardened against the *correct* error responses (400/404) rather than 500s. W1 also must precede P4 BE tests that assert 400/404.

### P2 — Robustness & data-correctness

| ID | Covers | Owner | Sev | Eff | Change | Verify |
|----|--------|-------|-----|-----|--------|--------|
| **W4** | BE-07 | BE | Med | S | Bounds-check `rating` at top of `update_sm2` → `raise ValueError` if not `0..3`. Single source of truth in the model. | Unit test W12 #6: `update_sm2(4)`/`(-1)` raises. |
| **W5** | BE-05 | BE | Med | M | Implement `/progress/domains/` via **live compute** (recommended) in `DomainProgressView` — aggregate per-domain seen/correct on demand; stop relying on the never-written `UserDomainProgress` counter. Response shape unchanged. | W12 #12: endpoint returns real per-domain numbers, not `[]`. UI: Domains page chart populates (currently masked by FE `.catch(()=>({data:[]}))`). **Owner decision: live-compute vs. maintain counter (see Open Questions).** |
| **W6** | BE-04 | BE | Med | M | Collapse `ObjectiveProgressView` N+1 (~45 queries) to ~3 aggregated queries (totals + per-objective seen/correct), assemble in Python. Response shape unchanged. | W12 #11: counts match fixture; `assertNumQueries` locks the fix. |
| **W7** | BE-08 | BE | Low | S | Guard `domain` query param with `try/except int()` → 400; optionally intersect `question_type` against `QUESTION_TYPES` keys. | W12 #14: `?domain=abc` → 400; `?question_type=bogus` → `[]`, not 500. |
| **W8** | FE-05, FE-06, FE-15 (counter) | FE | Med | M | (1) Move exam completion out of the `setSecondsLeft` setter into a dedicated effect when it hits 0; add a `completing` ref so timer+manual can't both fire (FE-05); fix stale `handleComplete` via `getState()`/`useCallback`. (2) `Results` fetches `/sessions/:id/results/` on mount when `location.state.results` absent; pass `sessionId` in nav state; wire study/PBQ to show results (FE-06). (3) Exam question counter (FE-15). | UI: let timer expire AND click Submit Exam → single completion, no double POST/throw; refresh `/results` → results still shown; exam shows "Q n of N". |

### P3 — Observability, hygiene, structure

| ID | Covers | Owner | Sev | Eff | Change | Verify |
|----|--------|-------|-----|-----|--------|--------|
| **W9** | BE-09 | BE | Med | M | Add stdlib `LOGGING` dict to settings (console handler, env-overridable level, `django.request` at WARNING+); module logger in `SessionAnswerView` logging submissions at INFO and login failures at WARNING in `LoginView`. Dependency-free. | Hit a 4xx/5xx → structured log line; submit an answer → INFO audit line. |
| **W10** | FE-01 (+ folds FE-07 `resetForQuestion`, FE-15 `replaceAll`), FE-13, FE-14, FE-08, FE-09, FE-12 | FE | High/Low/Nit | M | (1) **FE-01 extraction** of `QuestionWrapper` into `inputs/{MultipleChoice,MultiSelect,Ordering}.jsx`, `answerLogic.js` (pure helpers — makes them unit-testable), `QuestionFeedback.jsx`; container keeps state+dispatch only. Mechanical, no behavior change. Fold in `resetForQuestion` helper (FE-07) and `replaceAll`/`/_/g` (FE-15). (2) `userStore.logout` clears `user` in `finally` + matching catch in `Dashboard.handleLogout` (FE-14). (3) `cancelled` guard + `.catch` error state on `Domains`/`Dashboard`/`PBQHub` fetches (FE-08). (4) Robust CSRF cookie parse / native Axios `xsrfCookieName`/`xsrfHeaderName` (FE-09 — header name must stay `X-CSRFToken`). (5) Delete `App.css`, empty dirs, unused starter assets; fix `exhaustive-deps` lint (FE-12, FE-13). | `npm run build` clean; `npm run lint` clean; all session types render identically (no behavior change). **FE-01 must land before P4 FE tests** so helpers are importable. **Must not weaken Contract B (reveal-by-presence).** |

**Sequencing note:** W10's FE-01 extraction is a **hard prerequisite** for the P4 FE tests (they import the extracted `answerLogic.js`). Do the extraction first within W10.

### P4 — Tests (locks every fix above; CI `needs: test` then guards them)

| ID | Covers | Owner | Sev | Eff | Change | Verify |
|----|--------|-------|-----|-----|--------|--------|
| **W11** | FE-11 + critical FE tests | FE | High | M | Scaffold `vitest` + `@testing-library/react` + `jest-dom` + `jsdom`; `test` script; `vitest.config.js` (`environment:'jsdom'`). Then tests (see Testing Plan): buildAnswer per type (Contract A guard), shuffle, render-time reset, RequireAuth guard, two-strike/reveal gating (Contract B guard), hasSelection/initialSelection, FE-04 fallback. | `npm test` green; CI runs it. |
| **W12** | BE-14 + critical BE tests | BE | Med→High | M | Add negative-path/SM-2/isolation/malformed tests under existing `TestCase`s + fill empty `users/tests.py` (see Testing Plan). Several assert the P1/P2 fixes (W1,W4,W5,W6,W7). | `manage.py test` green; CI `needs: test` gate now meaningful. |

**Sequencing note:** W11 depends on W10 (FE-01 extraction). W12 depends on W1/W4/W5/W6/W7 (tests assert their behavior). Test infra (scaffold) lands before the tests that use it — within W11/W12 do scaffold first.

### P5 — Polish / nits (opportunistic, lowest priority)

| ID | Covers | Owner | Sev | Eff | Change | Verify |
|----|--------|-------|-----|-----|--------|--------|
| **W13** | FE-10 | FE | Med | M | Accessibility pass: `role="status" aria-live="polite"` on feedback panel; `aria-pressed` on choice buttons + non-color correct marker in `MultipleChoice`; `aria-label`/`aria-roledescription="sortable"` + visible DnD hint + @dnd-kit announcements; focus management after submit/retry. | Keyboard-only walkthrough; SR announces result. |
| **W14** | BE-06 | BE | Med | S+mig | Add `Meta.indexes` (`user,due_date`; `user,card_state`; `session,question`). **Flag migration for owner to generate** (don't auto-`makemigrations` per review). | Owner generates migration; `migrate`; `EXPLAIN` on due-card query. |
| **W15** | BE-12, BE-13, BE-15, BE-16, BE-10 | BE | Low | S each | PBQ SM-2 semantics decision (BE-12); document/`calculate_score` distinct-question note (BE-13); `import_questions` raise on unmapped answer-key id (BE-15); gate `SECURE_PROXY_SSL_HEADER` on Railway env (BE-16); DB-password/SECRET_KEY fail-fast when `DEBUG=False` (BE-10). | Per-item targeted check; BE-12/BE-13 need owner intent (Open Questions). |
| **W16** | BE-11, BE-17 | BE | Nit | S | Optional `cache.get_or_set` for `Question.objects.count()` (BE-11 — acceptable as-is); hoist function-local `Question`/`Objective` imports to module top in `progress/views.py` (BE-17). | `manage.py check`; smoke. |

---

## Testing Plan

### Setup (do first, before the tests that use it)
- **FE:** add `vitest`, `@testing-library/react`, `@testing-library/jest-dom`, `jsdom` to devDeps; `"test": "vitest"` script; `vitest.config.js` with `environment: 'jsdom'` + jest-dom setup. Requires W10's FE-01 extraction so pure helpers (`answerLogic.js`) are importable.
- **BE:** reuse the `setUpTestData` fixture pattern already in `progress/tests.py`. No new infra needed (Django test runner + Postgres service already in CI).

### First FE tests (W11) — highest value first
1. **`buildAnswer` per type** — exact shapes `{selected_id}`/`{selected_ids}`/`{ordered_ids}`. **Contract A guard.**
2. **`shuffle`** — new array, no mutation, set-equality, same length; ordering "reshuffle once if it reproduces served order" (mock `Math.random`).
3. **Render-time reset** — render question A, select, rerender question B (new id): `selected`/`submitted`/`result` reset, B renders, no crash.
4. **`RequireAuth` guard** — Loading while `!authChecked`; redirect `/login` when checked & no user; children when authed.
5. **Two-strike / reveal gating** — 1st wrong: hint + Try Again, **no `correct_ids`**; 2nd wrong: explanation + Next + green reveal when `correct_ids` present; exam: hides hint/explanation but reveals. **Contract B guard.**
6. **`hasSelection`/`initialSelection` per type** — ordering starts populated, multi_select empty, choice types null; Submit enable/disable.
7. **FE-04 fallback** — `drag_drop`/`fill_blank` renders the Skip affordance, not a dead Submit.

### First BE tests (W12) — highest value first
1. **Two-strike feedback (study):** 1st wrong → `hint` present, `explanation` null, **`correct_ids` absent (`assertNotIn`)**; 2nd wrong → `explanation` + `correct_ids` present. **Contract B guard.**
2. **Reveal not leaked early:** 1st wrong response has no `correct_ids`/`correct_order` keys at all.
3. **Exam reveal-always:** exam 1st attempt → `correct_ids` present regardless of correctness; no SM-2 row created.
4. **`check_answer` per type:** multi_select (order-independent set), ordering (order-sensitive), fill_blank (case/space-insensitive), true_false, drag_drop matches; pbq_simulation → False.
5. **SM-2 transitions:** `update_sm2(2)` 0→1→2 drives interval 1→6→round(6×EF), card_state new→learning/review→mastered (≥21); `update_sm2(0)` resets; ease floor 1.3.
6. **SM-2 bounds (after W4):** `update_sm2(4)`/`(-1)` raises `ValueError`.
7. **User isolation (after W1):** user B on user A's session → 404.
8. **Malformed input → 400 (after W1):** missing/non-int `question_id`, `answer` as list/string → 400 not 500.
9. **Not-found → 404 (after W1):** nonexistent session id / question id.
10. **Race / duplicate attempt (after W1):** same `attempt_number` doesn't 500; IntegrityError path resolves cleanly.
11. **`/progress/objectives/` (after W6):** counts match fixture; `assertNumQueries` locks N+1 fix.
12. **`/progress/domains/` (after W5):** real per-domain numbers, not `[]`.
13. **Auth (`users/tests.py`):** register happy + duplicate username 400 + short password 400; login bad creds → 401; `/auth/me/` anon → 403; logout clears session.
14. **Filter validation (after W7):** `?domain=abc` → 400; `?question_type=bogus` → `[]` not 500.

---

## Deferred / Won't-Do (with rationale)

| Item | Findings | Rationale |
|------|----------|-----------|
| **Full `drag_drop` + `fill_blank` FE input implementations** | FE-04 (full), Contract A | L-effort each; the **Skip fallback (W2)** removes the dead-end risk at S-effort. Backend already scores them, but there are currently **no such questions served** (per CLAUDE.md the bank is MC/multi_select/true_false/ordering). Build the inputs when content actually needs them. |
| **`pbq_simulation` scoring** | FE-04 note, BE Contract note | No `check_answer` branch exists; needs a backend scoring design first, then FE input. Out of scope for a fix pass — it's a feature. |
| **Shared payload-shape schema module** (codegen / single source across stacks) | FE-03 (longer-term) | The **unit tests (W11 #1 + W12 #4)** are the cheap, sufficient drift guard now. A shared schema is a larger architecture change; revisit only if drift actually occurs. |
| **`SECURE_PROXY_SSL_HEADER` / SECRET_KEY / DB-password hardening if it changes prod behavior** | BE-16, BE-10 | Low severity, Railway-only topology is safe today. **Do pre-deploy-test carefully** — gating the proxy header wrong could break TLS detection. Keep in W15 but verify against a live Railway hit before relying on it. |
| **`UserDomainProgress` denormalized-counter maintenance** | BE-05 (alt) | Rejected in favor of live-compute (W5). The denormalized path adds write-coupling inside the BE-01 transaction for no benefit at current scale. Don't build it. |
| **`calculate_score` distinct-question rewrite** | BE-13 | Behavior change with UX implications (study % would shift). Default to **document-only** unless the owner wants the semantics changed (Open Question). |
| **Regenerating `backend/requirements.txt`** | — | Explicitly forbidden by CLAUDE.md (reintroduces pywin32/gunicorn/whitenoise defects). Any new BE dep (none required by this plan) must be hand-added. |
| **Switching whitenoise to ManifestStaticFilesStorage** | — | Forbidden by CLAUDE.md (Vite already content-hashes). Not touched. |

---

## Open Questions for the Owner

1. **BE-05 domain progress:** confirm **live-compute** in `DomainProgressView` (recommended, no write-coupling) vs. maintaining the `UserDomainProgress` counter inside the answer transaction. (Plan assumes live-compute.)
2. **BE-12 PBQ SM-2 semantics:** PBQ sessions currently *read* SM-2 due-dates but never *write* them. Should PBQ (a) update SM-2 like study, or (b) use unseen/random ordering like exam? Needed to finalize W15.
3. **BE-13 score semantics:** should study/PBQ `percent` count distinct questions (first/best attempt) instead of all attempts, or just document the current attempt-counting behavior? (Plan defaults to document-only.)
4. **Contract B2 — reveal for `drag_drop`/`fill_blank`:** if/when wired, leave them unrevealed, or add `correct_*` branches inside the `if resolved:` gate? (Only relevant once those types are served.)
5. **Migrations (W14):** confirm you'll run `makemigrations`/`migrate` yourself for the BE-06 indexes (per CLAUDE.md the review must not auto-generate them). Note this requires an image rebuild for the combined deploy.
6. **Scope/stop-point:** is the intended scope P1–P4 (correctness + robustness + tests) with P5 polish deferred, or all five phases? This determines the milestone pause points.

---

## Execution Record (2026-06-04)

All five phases executed and verified. **Not committed** (awaiting approval per CLAUDE.md).

**Owner decisions applied:** W5 → persisted `UserDomainProgress` counter (not live-compute); BE-13 → `calculate_score` rewritten to first-attempt distinct-question accuracy; BE-12 (PBQ SM-2) → dropped (PBQ being deprecated, trademark concerns); drag_drop/fill_blank reveal → deferred; W14 migration generated + applied by Claude.

**Verification:** backend `manage.py test` → 37 passed; frontend `npm test` → 25 passed; `npm run build` clean; `npm run lint` clean; `manage.py check` clean; index migration `0002` applied.

**Deferred (unchanged from plan):** full drag_drop/fill_blank inputs; pbq_simulation scoring; shared-schema codegen; BE-11 `Question.count()` cache (acceptable as-is).
