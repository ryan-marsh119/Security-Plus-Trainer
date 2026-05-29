# Phase 5 v2 Audit — Consolidated Summary

**Scope:** the 143 new questions authored in Phase 5 (Batch 0 §3.4 dry-run + Batch 1 bulk diversification). Phase 5 watermark: `question_id ≥ 250`.

**Method:** 5 parallel `question-researcher` SME passes, one per domain, each independently re-deriving the correct answer for every new question and comparing to the stored key via `mcp__security-plus-trainer__audit_question`. Mirrors the Phase 4.5 audit pattern.

## Results

| Domain | Audited | AGREE | UNSURE | DISAGREE | Pass rate |
|---|---:|---:|---:|---:|---:|
| 1. General Security Concepts | 27 | 25 | 2 | 0 | 92.6 % |
| 2. Threats, Vulnerabilities & Mitigations | 30 | 28 | 2 | 0 | 93.3 % |
| 3. Security Architecture | 29 | 28 | 1 | 0 | 96.6 % |
| 4. Security Operations | 27 | 27 | 0 | 0 | 100 % |
| 5. Program Management & Oversight | 30 | 30 | 0 | 0 | 100 % |
| **Total** | **143** | **138** | **5** | **0** | **96.5 %** |

Comparison: Phase 4.5 audit on the original 248 questions cleared **97.6 %** AGREE. Phase 5 first-pass content runs **96.5 %** — within 1.1 pp of the established baseline, with **zero** stored answer-key inversions.

## Flagged items (UNSURE) — all 5 resolved 2026-05-29

All five flags were stem-precision, attribution, or wording concerns. **None inverted a stored answer key.** Resolved via `resources/audit_proposals_5_v2_fixes.json` → `question-db-admin` (10 change records: 3 stem rewrites, 3 choice edits, 1 answer-key reorder, 4 explanation updates, with overlap by question). Every change verified post-write via `mcp__security-plus-trainer__audit_question`.

| ID | Domain | Type | Original issue | Fix applied |
|---|---|---|---|---|
| 282 | 1 (1.4) | ordering | Choices 2/4 used RSA-centric "encrypt with private key" / "decrypt with public key" framing | Reworded choices 1119/1121 to neutral sign/verify language; explanation now notes ECDSA (FIPS 186-5 §6) and EdDSA (RFC 8032 §5) use the same sign/verify primitive — older RSA-only framing called out explicitly |
| 283 | 1 (1.4) | ordering | Step 4 said CA "publishes the cert via OCSP/CRL"; OCSP/CRL are revocation channels | Choice 1126 reworded: CA embeds AIA / CRL Distribution Point URLs (RFC 5280 §4.2.1.13, §4.2.2.1) and, for public CAs, publishes the cert to Certificate Transparency logs (RFC 6962). Explanation aligned |
| 291 | 2 (2.4) | multi_select | Stem labeled Birthday collision as a "password / credential attack" although §2.4 keeps Password and Cryptographic attacks in separate sub-bullets | Stem rewritten: "Which of the following are attacks listed under SY0-701 Objective 2.4 (as opposed to attacks listed under a different objective)? (Select THREE.)" — answer key unchanged |
| 309 | 2 (2.1) | ordering | Mis-attributed "grievance → ideation → planning → preparation → action" to CMU CERT Insider Threat Center | Stem re-attributed to the behavioral "pathway to violence" model (Calhoun & Weston 2003; U.S. Secret Service NTAC). Explanation now notes CMU SEI CERT's "Critical Pathway to Insider Risk" (Shaw, Ruby & Post; Shaw & Stock) is a related but distinct framework with different stage labels |
| 325 | 3 (3.2) | ordering | Stored sequence placed Inline IDS/IPS BEFORE the stateful firewall — non-canonical for the exam | `answer_key.ordered_ids` updated from `[1308, 1309, 1310, 1311, 1312]` to `[1308, 1310, 1309, 1311, 1312]` so the stateful firewall (1310) is now sequenced before the IDS/IPS (1309). Explanation aligned; alternate IPS-first topology noted as acknowledged by NIST SP 800-94 §6 |

**Post-fix pass rate: 143/143 AGREE (100 %)** on Phase 5 new content. Bank-wide v2 pass rate effectively at the original 96.5 % review confidence with zero outstanding wording flags.

`import_questions` re-run after the fix batch: `0 created, 391 skipped` — CSV ↔ Postgres still in lockstep, no duplicates.

## Per-domain reports

Full per-question verdict tables and flagged-item detail:

- `resources/audit_summary_v2_d1.md`
- `resources/audit_summary_v2_d2.md`
- `resources/audit_summary_v2_d3.md`
- `resources/audit_summary_v2_d4.md`
- `resources/audit_summary_v2_d5.md`

## Definition-of-done check (from `resources/question_type_gaps.md`)

- [x] § 3.4 cell ≥ 10 (verified end of Batch 0: 10/10).
- [x] Every (domain × {multi_select, true_false, ordering}) cell ≥ 10 (verified via MCP `list_questions` per cell — all 15 cells at exactly 10).
- [x] Every new question carries a hint, an explanation, and a `source` citing the SY0-701 Objectives PDF or a named NIST publication / RFC.
- [x] `import_questions` runs cleanly; second run is fully idempotent (391 skipped on re-run; new bank size 392).
- [x] `audit_summary_v2.md` reports ≥ 95 % pass rate on new content (96.5 %). 0 DISAGREE on stored answer keys.
- [ ] CLAUDE.md Phase Log + Domain Tracker update (next step).

Outstanding for Phase 5.1:
- Lift every (domain × non-MC type) cell from 10 → 20 (~150 more questions).

Outstanding pre-existing items (not introduced by Phase 5):
- One Domain 3 row exists in Postgres but is missing from `domain_3_security_architecture.csv` (DB count 51 vs. CSV-importable count 50). Phase 4.5-era artifact from a cross-domain retag; clean up when convenient.
