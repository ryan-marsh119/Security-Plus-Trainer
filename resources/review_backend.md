# Backend Code Review — Security+ Trainer (Django + DRF)

**Reviewer:** Senior Backend Engineer (read-only review)
**Date:** 2026-06-04
**Scope:** `backend/**` — `questions`, `progress`, `users`, `securityplus` apps.

## Summary

The backend is small, well-documented, and the core design is sound: answer-key logic is correctly funnelled through `Question.check_answer()` / accessor helpers, the answer key is never serialized to the client, and the server-side two-strike reveal gate (`correct_ids`/`correct_order` only included once `resolved`) is a genuine security control implemented in the right place. The most material problems are operational rather than functional: the answer-submission endpoint has a **count-then-create race with no surrounding transaction**, several views use **bare `.get()` that returns HTTP 500 instead of 404 and leaks no clean error to the client**, there is **zero input validation** on `question_id`/`answer`/filter params, the `ObjectiveProgressView` issues **~2 queries per objective (N+1, ~45 queries/request)**, `UserDomainProgress` is **read but never written** (the `/progress/domains/` endpoint always returns stale zeros), there are **no DB indexes** on the hot foreign-key/date columns the SM-2 scheduler filters on, and there is **no LOGGING configuration**. Test coverage is two happy-path smoke tests plus an empty `users/tests.py`; all negative paths (wrong-answer hint→explanation, SM-2 transitions, user isolation, malformed input) are untested. None of these block the current single-user hobby deploy, but the race, the missing transaction, and the validation gaps are the items to fix before any multi-user or untrusted-client usage.

---

## Findings

### BE-01 — Answer submit: count-then-create race + no transaction
- **Severity:** High
- **File:** `backend/progress/views.py` lines 98–152 (`SessionAnswerView.post`)
- **What's wrong:** `attempt_number` is derived from `SessionAnswer.objects.filter(...).count()` (line 106–109) and then a row is created (line 112). Two concurrent submissions for the same `(session, question)` both read `count()==0`, both compute `attempt_number=1`, and one `create()` fails on the `unique_together(session, question, attempt_number)` constraint with an unhandled `IntegrityError` → HTTP 500. Worse, the `SessionAnswer.create()` and the `UserQuestionProgress.update_sm2()` (line 149–152) are **not** wrapped in a transaction, so a failure between them leaves SM-2 state advanced without a recorded answer (or vice-versa). The `unique_together` is only *partial* protection — it converts the race into a 500 rather than preventing it.
- **Why it matters:** Double-click / retry / two tabs produce 500s and can desync SM-2 vs. answer history. The `update_sm2` write is also not isolated from the answer write.
- **Proposed fix:** Wrap the create + SM-2 update in `with transaction.atomic():`. Compute `attempt_number` defensively and catch `IntegrityError` to re-resolve the attempt count (or use `select_for_update()` on prior attempts within the transaction). Minimal version:
  ```python
  from django.db import transaction, IntegrityError
  ...
  with transaction.atomic():
      prior = SessionAnswer.objects.select_for_update().filter(
          session=session, question=question).count()
      attempt_number = prior + 1
      is_correct = question.check_answer(submitted)
      SessionAnswer.objects.create(...)
      if session.session_type == 'study':
          progress, _ = UserQuestionProgress.objects.get_or_create(...)
          progress.update_sm2(2 if is_correct else 0)
  ```
- **Cross-stack flag:** No.
- **Effort:** S

### BE-02 — Bare `.get()` returns 500 instead of 404 across all session views
- **Severity:** High
- **File:** `backend/progress/views.py` — line 64 (`SessionNextQuestionView`), line 99 + line 104 (`SessionAnswerView`), line 170 (`SessionResultsView`), line 187 (`SessionCompleteView`)
- **What's wrong:** Every session view does `ExamSession.objects.get(pk=pk, user=request.user)` and `SessionAnswerView` additionally does `Question.objects.get(pk=question_id)` (line 104). A non-existent or other-user's session id raises `ExamSession.DoesNotExist` → unhandled → HTTP 500. A bad/absent `question_id` raises `Question.DoesNotExist` (or `ValueError` if `question_id` is non-int) → 500. The user-isolation filter (`user=request.user`) is good — but a foreign session id should be a clean **404**, not a 500.
- **Why it matters:** Wrong HTTP semantics (500 for "not found"), noisy error logs, and the 500 path can expose a stack trace if `DEBUG` is ever true in prod. Also obscures genuine server errors.
- **Proposed fix:** Use `django.shortcuts.get_object_or_404`:
  ```python
  from django.shortcuts import get_object_or_404
  session = get_object_or_404(ExamSession, pk=pk, user=request.user)
  question = get_object_or_404(Question, pk=question_id)
  ```
  Apply to all five `.get()` call sites. (DRF renders `Http404` as a clean 404 JSON body.)
- **Cross-stack flag:** No.
- **Effort:** S

### BE-03 — No input validation on answer-submit payload
- **Severity:** High
- **File:** `backend/progress/views.py` lines 100–110 (`SessionAnswerView`)
- **What's wrong:** `question_id = request.data.get('question_id')` and `submitted = request.data.get('answer', {})` are passed straight into `Question.objects.get()` and `question.check_answer()`. `check_answer()` (`questions/models.py` lines 149–180) explicitly "assumes submitted shape is well-formed (no validation)." A missing `question_id` → `get(pk=None)`; a string `question_id` → `ValueError` → 500; an `answer` that is a list/str instead of a dict → `submitted.get(...)` `AttributeError` → 500. There is also no check that `question_id` belongs to a question the session is actually serving.
- **Why it matters:** Any malformed client request becomes a 500 instead of a 400. Combined with BE-01/BE-02, the endpoint is brittle to anything but the exact happy-path shape.
- **Proposed fix:** Add a DRF serializer to validate the request body before touching the DB:
  ```python
  class AnswerSubmitSerializer(serializers.Serializer):
      question_id = serializers.IntegerField()
      answer = serializers.DictField(required=False, default=dict)
  ```
  In the view: `s = AnswerSubmitSerializer(data=request.data); s.is_valid(raise_exception=True)` (raises a clean 400). `check_answer()` already tolerates missing keys via `.get(..., default)`, so a validated dict is safe to pass through. Optionally validate `question_id` resolves via `get_object_or_404` (BE-02).
- **Cross-stack flag:** Yes — defines the request contract the frontend's answer-submit POST must satisfy: `{question_id: int, answer: <dict per type>}`.
- **Effort:** S

### BE-04 — ObjectiveProgressView N+1 (~2 queries × every objective)
- **Severity:** Medium
- **File:** `backend/progress/views.py` lines 252–270 (`ObjectiveProgressView.get`)
- **What's wrong:** Loops over all objectives (28 in `seed_domains`, scope note says ~22 used) and, per objective, runs **two** `UserQuestionProgress.objects.filter(...).count()` queries (lines 259 and 260). With the `prefetch_related('questions')` (line 254) that's ~1 + N×2 ≈ 45+ queries per request. The prefetch only helps `len(q_ids)`, not the two per-objective count queries.
- **Why it matters:** Dashboard heatmap load scales linearly with objective count and progress-table size; cheap to collapse.
- **Proposed fix:** Replace the loop with two aggregated queries, then assemble in Python. One query for per-objective question totals, one for the user's per-objective seen/correct counts grouped by `question__objective_id`:
  ```python
  from django.db.models import Count, Q
  totals = dict(Objective.objects.annotate(n=Count('questions'))
                .values_list('id', 'n'))
  prog = (UserQuestionProgress.objects.filter(user=user)
          .values('question__objective_id')
          .annotate(
              seen=Count('id'),
              correct=Count('id', filter=Q(card_state__in=['review', 'mastered'])),
          ))
  ```
  Then build `data` by merging `totals` with a `{objective_id: row}` map from `prog`. Drops ~45 queries to 3 (objectives + totals + prog).
- **Cross-stack flag:** No (response shape unchanged).
- **Effort:** M

### BE-05 — UserDomainProgress is read but never written → `/progress/domains/` always returns stale/empty data
- **Severity:** Medium
- **File:** `backend/progress/views.py` lines 223–235 (`DomainProgressView`); `backend/progress/models.py` lines 242–270 (model docstring claims "Updated by the app after each answer")
- **What's wrong:** A repo-wide search shows `UserDomainProgress` is only ever **read** (the view + serializer + admin); no code path ever creates or increments `total_seen`/`total_correct`. The model docstring asserts it is "Updated by the app after each answer to keep dashboard queries fast" — that update was never implemented. The endpoint therefore returns an empty list (no rows are ever created) for every user.
- **Why it matters:** The domain radar/accuracy view is silently broken — it shows nothing or stale zeros, which is misleading. Either wire the denormalized counter or compute live.
- **Proposed fix (pick one):**
  - **Live compute (simplest, recommended for current scale):** drop the denormalized model from the read path and aggregate `SessionAnswer`/`UserQuestionProgress` per domain on demand (reuse the `select_related('question__objective__domain')` pattern from `calculate_score`, `questions/models.py`-style accessors).
  - **Maintain the counter:** in `SessionAnswerView` (inside the BE-01 transaction), `update_or_create` the `(user, domain, is_pbq)` row on first attempt and bump `total_seen` / `total_correct` (first-attempt-correct per the docstring). Heavier; only worth it if the live query becomes slow.
- **Cross-stack flag:** Yes — `/progress/domains/` response is consumed by the frontend domain chart; today it gets `[]`.
- **Effort:** M

### BE-06 — No DB indexes on hot SM-2 / session columns
- **Severity:** Medium
- **File:** `backend/progress/models.py` (model `Meta`s); `backend/progress/migrations/0001_initial.py`
- **What's wrong:** `get_next_question()` (`progress/models.py` lines 106–118) filters `UserQuestionProgress` on `user` + `due_date__lte` + `question__in`, and again on `user` for unseen exclusion; `ProgressOverviewView` filters on `user` + `card_state` + `due_date`; `calculate_score`/`SessionAnswerView` filter `SessionAnswer` on `session` (+`question`). The only indexes that exist are the `unique_together` composites and implicit FK indexes. There is no index on `UserQuestionProgress.due_date` or `card_state`, and the `unique_together(user, question)` index can't serve a `due_date`-ordered range scan well.
- **Why it matters:** As the progress table grows (per user × 392 questions) the SM-2 due-card lookup and dashboard counts do sequential-ish scans. Cheap to fix with composite indexes matching the query shapes.
- **Proposed fix:** Add `Meta.indexes` (a migration the user can generate later):
  ```python
  # UserQuestionProgress.Meta
  indexes = [
      models.Index(fields=['user', 'due_date']),
      models.Index(fields=['user', 'card_state']),
  ]
  # SessionAnswer.Meta
  indexes = [models.Index(fields=['session', 'question'])]
  ```
  (Read-only review — do not run `makemigrations`; flag for the user.)
- **Cross-stack flag:** No.
- **Effort:** S (code) + migration

### BE-07 — SM-2 rating not validated; out-of-range ratings corrupt ease factor / interval
- **Severity:** Medium
- **File:** `backend/progress/models.py` lines 194–239 (`update_sm2`)
- **What's wrong:** `update_sm2(rating)` documents `rating ∈ 0..3` but does no bounds check. The ease formula `ease + 0.1 - (3-rating)*(0.08 + (3-rating)*0.02)` and the `rating < 2` branch silently misbehave for out-of-range input: `rating=4` *raises* nothing but inflates ease; negative ratings inflate interval growth. Today the only caller passes a hard-coded `2` or `0` (`progress/views.py` line 148), so it's latent — but the function is a public model method and the next caller (a PBQ rater, a self-rating UI) can pass anything.
- **Why it matters:** A future caller silently corrupts the spaced-repetition schedule with no error. Also note `interval_days` is a `PositiveIntegerField`; a path that produced a negative interval would raise only on save, not at compute time.
- **Proposed fix:** Clamp/validate at the top of `update_sm2`:
  ```python
  if not 0 <= rating <= 3:
      raise ValueError(f'rating must be 0..3, got {rating}')
  ```
  (or `rating = max(0, min(3, rating))` if silent clamping is preferred). Keep the single source of truth in the model.
- **Cross-stack flag:** No.
- **Effort:** S

### BE-08 — Unvalidated `question_type` / `domain` filter params
- **Severity:** Low
- **File:** `backend/questions/views.py` lines 78–87 (`QuestionListView.get_queryset`)
- **What's wrong:** `question_type` is split on comma and passed to `filter(question_type__in=types)` with no whitelist; an unknown type just yields `[]` (benign). `domain` is passed to `filter(objective__domain_id=domain)` — a non-integer `?domain=abc` raises `ValueError` → 500.
- **Why it matters:** `?domain=abc` is a trivial 500. Minor, but it's an unvalidated query param reaching the ORM.
- **Proposed fix:** Validate via a lightweight serializer or guard: coerce `domain` with `int()` in a `try/except` → 400, and optionally intersect `types` against `dict(Question.QUESTION_TYPES)` keys so the contract is explicit. A DRF `query_params` serializer is the clean option.
- **Cross-stack flag:** Yes (minor) — defines accepted `?question_type=` / `?domain=` values for the PBQ Hub.
- **Effort:** S

### BE-09 — No LOGGING configuration; no audit log on answer submission
- **Severity:** Medium
- **File:** `backend/securityplus/settings.py` (no `LOGGING` block anywhere)
- **What's wrong:** There is no `LOGGING` dict, so the app relies on Django's bare defaults. Under gunicorn on Railway, unhandled 500s (which BE-01/02/03 can produce) and any `logger` calls are effectively invisible/inconsistent. There is also no audit trail beyond the `SessionAnswer` rows themselves.
- **Why it matters:** When a 500 fires in prod there's no structured record to debug from; security-relevant events (login failures, answer submissions) aren't logged.
- **Proposed fix:** Add a `LOGGING` block to settings: console handler, `django` + app loggers at `INFO` (env-overridable level), `WARNING`+ for `django.request` so 500s/4xx are captured. Add a module logger to `SessionAnswerView` and log answer submissions at `INFO` (user id, session id, question id, correct, attempt) and login failures in `LoginView` (`users/views.py` line 62) at `WARNING`. Keep it dependency-free (stdlib `logging.config.dictConfig` via Django's `LOGGING`).
- **Cross-stack flag:** No.
- **Effort:** M

### BE-10 — Dev DB password hard-coded as a source-code fallback
- **Severity:** Low
- **File:** `backend/securityplus/settings.py` line 92 (`'PASSWORD': os.environ.get('DB_PASSWORD', 'secplus_dev_password')`)
- **What's wrong:** A literal default DB password lives in source. In prod `DATABASE_URL` is used (line 81–85), so this only applies to the local/`DB_*` path — but a checked-in credential is poor hygiene and can mask a missing-env-var misconfiguration (the app "works" against a default instead of failing loudly).
- **Why it matters:** Low for a local-only default, but it's a credential in version control and a silent-fallback footgun.
- **Proposed fix:** Leave the local default for dev ergonomics if desired, but at minimum keep it out of the prod path (already true) and document it as dev-only. Better: default to `''` / raise when `DEBUG=False` and no DB config is present so a misconfigured prod fails fast. Same applies to `SECRET_KEY` default on line 10 — fine for dev, but consider asserting a non-default key when `DEBUG=False`.
- **Cross-stack flag:** No.
- **Effort:** S

### BE-11 — `ProgressOverviewView` recomputes `Question.objects.count()` every request
- **Severity:** Nit
- **File:** `backend/progress/views.py` lines 209–213 (`ProgressOverviewView.get`)
- **What's wrong:** `total_questions = Question.objects.count()` runs a `COUNT(*)` on every dashboard load. The question bank is effectively static (392, loaded by `import_questions`), so this is a constant queried live. The three `progress_qs` counts are per-user and legitimate.
- **Why it matters:** Trivial cost, but it's an avoidable `COUNT(*)` on a static table per request. Calling out because the dashboard is the most-hit endpoint.
- **Proposed fix:** Acceptable as-is at this scale; if it ever matters, cache with `cache.get_or_set('total_questions', Question.objects.count, 3600)` (low-effort, stdlib local-mem cache). Not worth a change now.
- **Cross-stack flag:** No.
- **Effort:** S

### BE-12 — SM-2 not run for `pbq` sessions, but `get_next_question` schedules them as if it were
- **Severity:** Low
- **File:** `backend/progress/models.py` lines 101–118 (`get_next_question`); `backend/progress/views.py` lines 147–152 (`SessionAnswerView`)
- **What's wrong:** `get_next_question` routes both `study` and `pbq` through the SM-2 due-date branch (the `if session_type == 'exam'` is the only special case). But `SessionAnswerView` only calls `update_sm2` when `session_type == 'study'` (line 147). So PBQ sessions are *ordered* by SM-2 due dates that PBQ answers never update — PBQ practice will keep surfacing whatever the user's *study* SM-2 state says is due, never advancing from PBQ activity, and the reveal gate also treats PBQ as a two-attempt flow (resolved gate line 138 doesn't list pbq, so PBQ correctly gets the two-strike reveal — that part is fine).
- **Why it matters:** Inconsistent: PBQ reads SM-2 but never writes it. Likely fine for the current usage, but the intent is ambiguous — either PBQ should update SM-2 too, or it should use a non-SM-2 ordering (e.g. random/unseen) like exam.
- **Proposed fix:** Decide the intended PBQ semantics. If PBQ should be SM-2-tracked, add `pbq` to the `update_sm2` condition (line 147). If not, branch PBQ to a simpler unseen/random ordering in `get_next_question`. Document the choice in the model docstring.
- **Cross-stack flag:** No.
- **Effort:** S

### BE-13 — `calculate_score` counts all attempts (incl. 2nd attempts) in totals
- **Severity:** Low
- **File:** `backend/progress/models.py` lines 48–76 (`calculate_score`)
- **What's wrong:** `total` and `by_domain` totals count every `SessionAnswer` row, including a question's 2nd attempt. A user who misses then re-answers a question contributes 2 to `total` and (if the retry is right) 1 to `correct`, so a single question can be both "wrong" and "right" in the denominator. For an `exam` (single attempt) this is correct; for `study`/`pbq` the percentage is diluted by retries.
- **Why it matters:** "Score" semantics differ silently between exam and study. Probably acceptable for study, but the field name `percent` implies a clean accuracy.
- **Proposed fix:** If a per-question score is intended, aggregate distinct `question_id` (e.g. first-attempt or best-attempt per question) before computing `percent`. At minimum document that `calculate_score` counts attempts, not distinct questions. Reuse the existing `select_related('question__objective__domain')` queryset.
- **Cross-stack flag:** Yes (minor) — `/sessions/<id>/results/` shape is consumed by the Results page; semantics, not shape, change.
- **Effort:** S

### BE-14 — Empty `users/tests.py`; no negative-path coverage anywhere
- **Severity:** Medium
- **File:** `backend/users/tests.py` (empty); `backend/questions/tests.py`; `backend/progress/tests.py`
- **What's wrong:** Coverage is one happy-path study flow (`progress/tests.py`), a healthz + anon-gate check (`questions/tests.py`), and an empty `users/tests.py`. None of the two-strike feedback, SM-2 transitions, exam-mode reveal, multi-select/ordering checking, user isolation, or malformed-input behavior is tested. The CI gate (`needs: test`) therefore can't catch regressions in any of those.
- **Why it matters:** The most security/correctness-sensitive logic (the reveal gate, `check_answer` per type, user isolation) has no test guarding it. See "Critical Missing Tests" below.
- **Proposed fix:** Add the test cases enumerated in the Critical Missing Tests section.
- **Cross-stack flag:** No.
- **Effort:** M

### BE-15 — `import_questions` CSV-position→PK mapping has an ambiguity footgun
- **Severity:** Low
- **File:** `backend/questions/management/commands/import_questions.py` lines 114–131
- **What's wrong:** The importer maps each choice to a real PK via `csv_id_to_pk[choice.get('id', i + 1)] = created_choice.pk`, then remaps `correct_ids`/`ordered_ids` with `csv_id_to_pk.get(cid, cid)`. The `.get(cid, cid)` fallback means an answer-key id that doesn't match any choice id is **silently passed through unchanged** as if it were already a PK — exactly the class of bug `repair_answer_keys.py` exists to fix. If a CSV mixes explicit `id` fields on some choices and not others, the `i+1` positional fallback can collide with an explicit `id`. Idempotency is keyed on `(objective, question_text)` (line 99), which is correct, and `--dry-run` is supported (good).
- **Why it matters:** A malformed answer-key id imports silently and only surfaces as a wrong-answer-marked-correct bug later. The existing `repair_answer_keys` command is the safety net, but the importer should fail loudly instead.
- **Proposed fix:** In the remap loop, raise (or warn + skip) when `cid not in csv_id_to_pk` rather than passing it through, so a bad CSV is caught at import. Keep `--dry-run` exercising the same validation path so it actually catches these.
- **Cross-stack flag:** No.
- **Effort:** S

### BE-16 — `SECURE_PROXY_SSL_HEADER` trusted unconditionally
- **Severity:** Low
- **File:** `backend/securityplus/settings.py` line 164
- **What's wrong:** `SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')` is set unconditionally, including in local/dev. On Railway this is correct (the edge proxy sets it and clients can't reach the container directly). But trusting `X-Forwarded-Proto` is only safe behind a proxy that *overwrites* it; if the app were ever exposed without that proxy, a client could spoof `X-Forwarded-Proto: https` and Django would treat plain HTTP as secure.
- **Why it matters:** Low for the current Railway-only topology, but it's an unconditional trust of a client-controllable header.
- **Proposed fix:** Gate it on the Railway environment marker that's already used elsewhere (line 31): set `SECURE_PROXY_SSL_HEADER` only when `os.environ.get('RAILWAY_ENVIRONMENT')` (or behind an explicit `TRUST_PROXY` env flag). Dev doesn't need it.
- **Cross-stack flag:** No.
- **Effort:** S

### BE-17 — `SessionAnswerView` re-imports `Question` inside the method
- **Severity:** Nit
- **File:** `backend/progress/views.py` line 103 (also lines 92, 209, 253 use the same local-import pattern)
- **What's wrong:** `from questions.models import Question` is a function-local import. There's no circular-import need here (`questions` doesn't import `progress`), so it's just per-call overhead and noise. `get_next_question` (`progress/models.py` line 92) does have a plausible circular-import reason at module load; the views do not.
- **Why it matters:** Cosmetic; minor per-request cost and inconsistency.
- **Proposed fix:** Move `from questions.models import Question, Objective` to the top of `progress/views.py`. Leave the model-level local import in `get_next_question` if it's load-order-sensitive.
- **Cross-stack flag:** No.
- **Effort:** S

---

## Cross-Stack Contract (flagged explicitly — keep server-authoritative)

This is the contract the frontend depends on; document it and do **not** weaken the gate.

**Answer-submit request** (`POST /api/v1/sessions/<id>/answers/`):
```
{ "question_id": <int>, "answer": <dict> }
```
`answer` shape per `question_type` (consumed by `Question.check_answer`, `questions/models.py` 168–179):
| question_type | `answer` shape |
|---|---|
| multiple_choice / true_false | `{"selected_id": <int>}` |
| multi_select | `{"selected_ids": [<int>, ...]}` |
| ordering | `{"ordered_ids": [<int>, ...]}` |
| drag_drop | `{"matches": {"<item>": "<zone>", ...}}` |
| fill_blank | `{"answers": ["<str>", ...]}` (compared case/space-insensitive) |
| pbq_simulation | falls through `check_answer` → always `False` (no branch) |

**Answer-submit response** (`SessionAnswerView`, lines 120–144) — **field presence is the gate**:
- Always: `correct` (bool), `attempt_number` (int), `hint` (str|null), `explanation` (str|null).
- `hint` populated **only** on 1st wrong attempt; `explanation` populated **only** when correct or `attempt_number >= 2`.
- `correct_ids` (choice types) / `correct_order` (ordering) included **only when `resolved`** = `is_correct or attempt_number >= 2 or session_type == 'exam'`. Their **absence** is what tells the frontend not to reveal. **This is a server-enforced security gate** preventing a study/PBQ user from reading the answer off the network before their 2nd attempt — it must stay server-side; never move the gating to the client and never include these fields unconditionally.

**Note:** `pbq_simulation` has no branch in `check_answer`, so it always returns `False` (line 180). If PBQ questions are ever scored, this needs a branch; today PBQ practice is effectively un-scorable as "correct."

---

## Proposed Change Plan (ordered)

1. **BE-02 + BE-03 + BE-01 (one pass on `SessionAnswerView`):** add `get_object_or_404`, an `AnswerSubmitSerializer` for input validation, and wrap create + SM-2 in `transaction.atomic()` with `IntegrityError` handling. This is the highest-value, lowest-risk fix and hardens the single most important endpoint. *(S–M)*
2. **BE-07:** add rating bounds check in `update_sm2` (single source of truth). *(S)*
3. **BE-05:** decide and implement domain-progress behavior (recommend live-compute in `DomainProgressView`); the endpoint currently returns `[]`. *(M)*
4. **BE-04:** collapse `ObjectiveProgressView` N+1 to ~3 aggregated queries. *(M)*
5. **BE-09:** add a `LOGGING` block + answer-submit/login-failure audit logging. *(M)*
6. **BE-06:** add `Meta.indexes` for the SM-2/session hot paths (flag the migration for the user to generate). *(S)*
7. **BE-14:** add the negative-path test suite (see below) so the CI gate guards the above. *(M)*
8. **BE-08 / BE-12 / BE-13 / BE-15 / BE-16 / BE-10:** smaller correctness/hardening items as time permits. *(S each)*
9. **BE-11 / BE-17:** nits — fold in opportunistically. *(S)*

> Per CLAUDE.md, none of the above should be committed/migrated without explicit user approval; this review writes only this report.

---

## Critical Missing Tests

Add under the existing `TestCase`s (reuse the `setUpTestData` fixture pattern in `progress/tests.py`):

1. **Two-strike feedback (study):** 1st wrong → `hint` present, `explanation` null, `correct_ids` **absent**; 2nd wrong → `explanation` present, `correct_ids` **present**. Asserts the reveal gate.
2. **Reveal gate not leaked early:** 1st wrong attempt response must NOT contain `correct_ids`/`correct_order` keys at all (use `assertNotIn`).
3. **Exam-mode reveal-always:** exam session, 1st (only) attempt → `correct_ids` present regardless of correctness; confirm no SM-2 row created.
4. **`check_answer` per type:** unit-test `multi_select` (set equality, order-independent), `ordering` (order-sensitive), `fill_blank` (case/space-insensitive), `true_false`, `drag_drop` matches; and `pbq_simulation` returns False.
5. **SM-2 transitions:** `update_sm2(2)` from `repetitions=0→1→2` drives interval 1→6→round(6×EF) and `card_state` new→learning/review→mastered (interval≥21); `update_sm2(0)` resets `repetitions`/`interval`; ease-factor floor 1.3 holds.
6. **SM-2 rating bounds (after BE-07):** `update_sm2(4)` / `update_sm2(-1)` raises `ValueError`.
7. **User isolation:** user B `GET/POST` on user A's session id → 404 (after BE-02), and cannot read/advance it.
8. **Malformed input → 400 (after BE-03):** missing `question_id`, non-int `question_id`, `answer` as a list/string → 400 not 500.
9. **Not-found → 404 (after BE-02):** session id that doesn't exist; `question_id` that doesn't exist.
10. **Race / duplicate attempt:** two submissions producing the same `attempt_number` don't 500 (after BE-01) — at least assert the `IntegrityError` path resolves cleanly.
11. **`/progress/objectives/` correctness (after BE-04):** counts match a hand-built fixture; assert query count with `assertNumQueries` to lock in the N+1 fix.
12. **`/progress/domains/` (after BE-05):** returns real per-domain numbers, not `[]`.
13. **Auth endpoints (`users/tests.py` is empty):** register (happy + duplicate username 400 + short password 400), login bad credentials → 401, `/auth/me/` anon → 403, logout clears session.
14. **Filter validation (after BE-08):** `?domain=abc` → 400; `?question_type=bogus` → empty list, not 500.
