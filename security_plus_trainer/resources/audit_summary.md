# Question Bank Audit — All Domains

**Date:** 2026-05-27
**Method:** 5 parallel subagents (one per domain), each using the `security-plus-trainer` MCP server (`list_domains`, `list_questions`, `audit_question`). Each agent decided the correct answer in isolation before comparing to the stored key.
**Database modifications:** none. MCP is read-only.

## Headline numbers

| Domain | Audited | AGREE | UNSURE | DISAGREE |
|--------|--------:|------:|-------:|---------:|
| 1 — General Security Concepts | 41 | 39 | 2 | 0 |
| 2 — Threats, Vulnerabilities, Mitigations | 29 | 27 | 2 | 0 |
| 3 — Security Architecture | 21 | 20 | 1 | 0 |
| 4 — Security Operations | 118 | 118 | 0 | 0 |
| 5 — Security Program Management | 39 | 38 | 0 | 1 |
| **Total** | **248** | **242** | **5** | **1** |

**242 / 248 (97.6%) stored answer keys verified correct on the merits.**

## DISAGREE — 1 row, needs a content fix

### Q212 (Obj 5.1) — Governance structure question
- **Stem:** "Which governance structure type makes security decisions through **consensus among a group of stakeholders** rather than through a single authority?"
- **Stored answer:** Decentralized governance
- **Should be:** Committee-based governance
- **Why:** SY0-701 5.1 separates two dimensions: centralized/decentralized describes *where authority sits* (one office vs. distributed across business units — each unit still typically has a single local authority, not consensus); committee/board describes *how* a body reaches decisions (consensus, voting, deliberation). The stem's "consensus among a group of stakeholders" is the textbook definition of committee-based. The stored explanation even contradicts the stem (talks about distribution across BUs, not consensus).
- **Action:** Update `correct_ids` to the committee-based choice and revise the explanation.

## UNSURE — 5 rows, mostly tagging or wording issues

| ID | Obj (current) | Obj (suggested) | Issue |
|----|---------------|-----------------|-------|
| 26 | 1.1 | 1.2 | Non-repudiation belongs under "fundamental security concepts", not "control types". |
| 41 | 1.3 | 1.4 | SSL deprecation due to POODLE/DROWN/BEAST is a cryptography topic, not change management. |
| 65 | 2.3 | 2.4 | Stem says "files missing" — that's wiper behavior, not ransomware (ransomware encrypts in place). Also "lock symbol on login screen" is ambiguous vs. HTTPS padlock. Re-tag as 2.4 (indicators of malicious activity). |
| 70 | 2.3 | 2.4 | "Until the server crashes" overstates a SYN flood — it exhausts the SYN backlog, doesn't panic the host. Re-tag as 2.4. |
| 80 | 3.3 | (rewrite) | Stem mixes "national security" (gov classification: Confidential/Secret/Top Secret) with "organizational competitiveness" (commercial: Public/Private/Confidential/Restricted). Choices are commercial-only — keyed answer is still best fit, but the stem is muddled. |

## Cross-cutting observation — Domain 4 objective_code tagging

Answer keys in Domain 4 are 100% correct, but the `objective_code` field is mis-mapped on a large fraction of questions (does not affect scoring; only affects how questions are grouped in the Objectives view):

- **Q117** tagged 4.3, content is 4.8 (IR final step).
- **Q138-143, 145-148, 152-153, 155-183, 195, 198-199, 201-207** tagged 4.8, content is 4.5 (enterprise capabilities — secure protocols, firewalls, wireless, VPN, AAA, proxies).
- **Q184-191, 200** tagged 4.2, content is 4.5 (IDS/IPS).
- **Q192-194** (honeypots/honeynets/honeyfiles) tagged 4.1 — better fit under mitigation techniques.
- **Q208-209** tagged 4.9 (data sources), content is 4.1 (system hardening).

## Other notes

- **Q232 (NIST CSF five functions)** — correct for CSF 1.1 / current SY0-701. Will need updating if exam objectives shift to CSF 2.0 (six functions; adds "Govern").
- **Q241 and Q247** — near-duplicates (both ask about the RMF Monitor step with essentially the same phrasing).
- **Domain 3 objective 3.4** only has 3 questions (IDs 82, 83, 84). If 3.4 carries meaningful exam weight, consider authoring items for HA/clustering, geographic dispersion, replication modes, backup types, power resilience, and the full exercise spectrum (walkthrough → simulation → parallel → full failover).

## Suggested fix order

1. **Q212** — only true content error. Update DB + CSV.
2. **Q65, Q70** — rewrite stems for accuracy; re-tag to 2.4.
3. **Q80** — disambiguate stem (drop "national security" or add gov-tier choices).
4. **Q26, Q41** — pure objective re-tag, low risk.
5. **Domain 4 objective_code cleanup** — bulk metadata pass.
