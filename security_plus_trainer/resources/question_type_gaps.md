# Phase 5 — Question Type Gaps & Sourcing Plan

> **Status:** Baseline survey for Phase 5 first pass. Generated 2026-05-28 against the live Postgres bank via `mcp__security-plus-trainer__list_questions`. Pre-existing question IDs span 1–249; Phase 5 content will begin at ID ≥ 250.

---

## 1. Current distribution (per domain × per type)

| Domain | multiple_choice | multi_select | true_false | ordering | Domain total |
|---|---:|---:|---:|---:|---:|
| 1. General Security Concepts (12 %) | 41 | 1 | 2 | 0 | 44 |
| 2. Threats, Vulnerabilities & Mitigations (22 %) | 29 | 0 | 0 | 0 | 29 |
| 3. Security Architecture (18 %) | 21 | 0 | 1 | 0 | 22 |
| 4. Security Operations (28 %) | 112 | 1 | 1 | 1 | 115 |
| 5. Program Management & Oversight (20 %) | 39 | 0 | 0 | 0 | 39 |
| **Bank totals** | **242** | **2** | **4** | **1** | **249** |

Out-of-scope types confirmed at 0 across the bank: `drag_drop`, `fill_blank`, `pbq_simulation` (PBQ work on hold per plan.md).

### Domain 3 § 3.4 callout — Resilience & Recovery

| Objective | Question count |
|---|---:|
| 3.1 Network architecture | 8 |
| 3.2 Network access controls | 6 |
| 3.3 Data protection / DLP | 5 |
| **3.4 Resilience & recovery** | **3** |

Existing § 3.4 questions: IDs 82 (hot site), 83 (RPO/backup frequency), 84 (tabletop exercise). All `multiple_choice`. Sub-bullets in the SY0-701 v7.0 Objectives PDF for § 3.4 (HA, site types, platform diversity, multi-cloud, COOP, capacity planning, testing spectrum, backups, power) are largely unrepresented — this objective is the single thinnest cell on the SY0-701 weight-adjusted exam blueprint.

---

## 2. Target distribution

### Phase 5 first pass — `≥ 10` per (domain × type) for the four in-scope types

| Domain | multiple_choice | multi_select | true_false | ordering |
|---|---:|---:|---:|---:|
| 1 | 10 (✓) | 10 | 10 | 10 |
| 2 | 10 (✓) | 10 | 10 | 10 |
| 3 | 10 (✓) | 10 | 10 | 10 |
| 4 | 10 (✓) | 10 | 10 | 10 |
| 5 | 10 (✓) | 10 | 10 | 10 |

Plus § 3.4 specifically: **≥ 10** (lift from 3).

### Phase 5.1 stretch (deferred) — `≥ 20` per cell

Matches the original plan.md target of 4 × 5 × 20 = 400 minimum bank. Not part of this execution; revisit after the first pass audits clean.

---

## 3. Gap per cell (first pass)

| Domain | multi_select Δ | true_false Δ | ordering Δ | Domain total |
|---|---:|---:|---:|---:|
| 1 | +9 | +8 | +10 | **+27** |
| 2 | +10 | +10 | +10 | **+30** |
| 3 | +10 | +9 | +10 | **+29** |
| 4 | +9 | +9 | +9 | **+27** |
| 5 | +10 | +10 | +10 | **+30** |
| **Totals** | **+48** | **+46** | **+49** | **≈ +143** |

Domain 3's 29 new questions split roughly 7 in the § 3.4 dry-run batch (Batch 0) and ~22 in the bulk batch (Batch 1).

`multiple_choice` is already ≥ 20 in every domain; no new MC authoring planned. Re-balancing MC down is also out of scope — the existing MC pool is well-audited (Phase 4.5, 97.6 % pass rate) and stays.

---

## 4. Local source candidates

Mined from `resources/CompTIA Security+ SY0-701 Exam Objectives (7.0).pdf` (24 pages, full text in `_extracted_objectives_v7.txt`). Every objective lists explicit sub-bullets that map cleanly onto non-MC formats — local mining can cover the bulk of the gap with researcher-agent generation needed mostly for hint/explanation prose and source citation polish.

### Ordering candidates (sequenced processes)

| Domain | Objective | Sequence | Source |
|---|---|---|---|
| 1 | 1.3 | Change management workflow: approval → impact analysis → test results → backout plan → maintenance window → documentation | Objectives § 1.3 |
| 2 | 2.5 | Vulnerability mitigation lifecycle: segmentation → access control → patching → encryption → monitoring → decommissioning | Objectives § 2.5 |
| 3 | 3.4 | DR testing spectrum (least → most disruptive): tabletop → walkthrough → simulation → parallel → full failover | Objectives § 3.4 + NIST SP 800-84 |
| 3 | 3.4 | Recovery sequence: detect outage → invoke DR → fail over to site → verify → fail back | NIST SP 800-34 Rev. 1 |
| 4 | 4.8 | NIST IR lifecycle: Preparation → Detection → Analysis → Containment → Eradication → Recovery → Lessons Learned | NIST SP 800-61 Rev. 2; existing Q at ID 112 |
| 4 | 4.3 | Vulnerability management: identify (scan) → confirm (false-positive check) → prioritize (CVSS) → remediate (patch) → validate (rescan) | Objectives § 4.3 |
| 4 | 4.6 | Identity lifecycle: provision → assign permissions → assign roles → attest → deprovision | Objectives § 4.6 |
| 5 | 5.2 | NIST RMF: Categorize → Select → Implement → Assess → Authorize → Monitor | NIST SP 800-37 Rev. 2 |
| 5 | 5.2 | Risk handling: identify → assess (qualitative/quantitative) → treat (transfer/accept/avoid/mitigate) → report | Objectives § 5.2 |
| 5 | 5.3 | Vendor lifecycle: due diligence → contract (SLA/MSA/SOW) → onboarding → monitoring (right-to-audit) → offboarding | Objectives § 5.3 |
| 5 | 5.5 | Audit progression: attestation → internal audit → external audit → penetration test | Objectives § 5.5 |

Estimated yield: ~11 ordering questions from explicitly sequenced material; each domain needs ~10, so additional ordering questions for Domain 1/2/3 will draw from secondary sequences (cryptographic key lifecycle, kill chain, OWASP testing methodology, etc.).

### True/false candidates (declarative facts)

The objectives PDF supplies many unambiguous declaratives in every domain. Representative examples by domain:

- **Domain 1:** "Compensating controls mitigate risk after a primary control fails" (§ 1.1). "Hashing is a one-way function and is not reversible" (§ 1.4). "Symmetric encryption uses the same key to encrypt and decrypt" (§ 1.4).
- **Domain 2:** "A zero-day vulnerability has no patch available at the time of discovery" (§ 2.3). "Allow lists are stricter than block lists" (§ 2.5). "Race conditions are timing-based software vulnerabilities" (§ 2.3).
- **Domain 3:** "Fail-closed firewalls block traffic when they lose power" (§ 3.2). "Tokenization replaces sensitive data with a non-sensitive equivalent that has no exploitable meaning" (§ 3.3). "Hot sites have near-zero RTO and current data replication" (§ 3.4). "RPO and RTO can be different for the same system" (§ 3.4).
- **Domain 4:** "SIEM tools aggregate logs from multiple sources" (§ 4.4). "SPF, DKIM, and DMARC are email authentication mechanisms" (§ 4.5). "FIM detects unauthorized changes to critical files by comparing hashes" (§ 4.5; existing Q 105).
- **Domain 5:** "ALE = SLE × ARO" (§ 5.2). "A right-to-audit clause permits the customer to audit the vendor's controls" (§ 5.3). "Penetration testing scope can be known, partially known, or unknown environment" (§ 5.5).

Estimated yield: easily ≥ 10 per domain from objectives PDF alone. No external sourcing needed.

### Multi-select candidates (bullet groups)

Every objective in the v7.0 PDF lists multi-item bullets. High-yield groups:

- **§ 1.1** — Categories: Technical / Managerial / Operational / Physical. Control types: Preventive / Deterrent / Detective / Corrective / Compensating / Directive.
- **§ 1.2** — Zero Trust control plane: Adaptive identity / Threat scope reduction / Policy-driven access / PEP / PA / PE.
- **§ 1.4** — Cryptographic tools: TPM / HSM / KMS / Secure enclave.
- **§ 2.1** — Threat actors: Nation-state / Unskilled / Hacktivist / Insider / Organized crime / Shadow IT.
- **§ 2.4** — Indicators: Account lockout / Concurrent session usage / Blocked content / Impossible travel / Resource consumption / Resource inaccessibility / Out-of-cycle logging / Missing logs / Published or documented.
- **§ 2.5** — Hardening techniques: Encryption / Endpoint protection / Host-based firewall / HIPS / Disabling ports / Default password change / Removal of unnecessary software.
- **§ 3.2** — Network appliances: Jump server / Proxy / IPS/IDS / Load balancer / Sensors / WAF / NGFW.
- **§ 3.3** — Data security methods: Geographic restrictions / Encryption / Hashing / Masking / Tokenization / Obfuscation / Segmentation / Permission restrictions.
- **§ 3.4** — HA techniques: Load balancing / Clustering / Replication / Multi-cloud / Platform diversity / Geographic dispersion / Journaling.
- **§ 4.5** — Enterprise security capabilities: Firewall / IDS-IPS / Web filter / OS security / DNS filtering / Email security (SPF/DKIM/DMARC) / FIM / DLP / NAC / EDR-XDR / UBA.
- **§ 4.6** — MFA factors: something you know / have / are / somewhere you are; implementations: Biometrics / Hard token / Soft token / Security key.
- **§ 4.9** — Investigation log sources: Firewall / Application / Endpoint / OS security / IPS/IDS / Network / Vulnerability scans / Automated reports / Dashboards / Packet captures.
- **§ 5.2** — Risk strategies: Transfer / Accept / Avoid / Mitigate. Risk assessment types: ad hoc / recurring / one-time / continuous.
- **§ 5.3** — Agreement types: SLA / MSA / MOA / MOU / SOW / NDA / BPA.
- **§ 5.4** — Privacy roles: Controller / Processor / Owner / Custodian / Steward.

Estimated yield: ≥ 15 per domain. No external sourcing needed.

---

## 5. Sourcing plan

**Primary source for all new questions: `resources/CompTIA Security+ SY0-701 Exam Objectives (7.0).pdf`.** Every new question's `source` column will cite this PDF (specific § section) or a NIST publication / RFC where the canonical sequence or definition originates (NIST SP 800-37, 800-61, 800-84, etc.).

| Domain | Batch | Sub-source mix |
|---|---|---|
| 3 § 3.4 (Batch 0 dry run, ~7 Q) | researcher | Objectives § 3.4 sub-bullets + NIST SP 800-34 / 800-84 for testing sequence |
| 1 (Batch 1, +27 Q) | researcher | Objectives § 1.1–1.4 + NIST SP 800-53 control families for multi-select; change-management ISO/IEC for ordering |
| 2 (Batch 1, +30 Q) | researcher | Objectives § 2.1–2.5 + MITRE ATT&CK reference for threat-actor multi-select |
| 3 (Batch 1, +22 Q, excludes § 3.4) | researcher | Objectives § 3.1–3.3 + NIST SP 800-145 for cloud-model multi-select |
| 4 (Batch 1, +27 Q) | researcher | Objectives § 4.1–4.9 + NIST SP 800-61 Rev. 2 (IR), 800-115 (vuln mgmt) for ordering |
| 5 (Batch 1, +30 Q) | researcher | Objectives § 5.1–5.6 + NIST SP 800-37 Rev. 2 (RMF) for ordering |

External free-site mining (`lognpacific.com`, `examcompass.com`, `comptia.org` practice tests) — **not required** at first-pass volume. Reserved as a fallback for Phase 5.1 if local material proves thin for the 10 → 20 lift.

---

## 6. Definition of done (first pass)

- [ ] § 3.4 cell ≥ 10 (currently 3).
- [ ] Every (domain × {multi_select, true_false, ordering}) cell ≥ 10.
- [ ] Every new question carries a hint, an explanation, and a `source` citing the SY0-701 Objectives PDF or a named NIST publication / RFC.
- [ ] `import_questions` runs cleanly; second run is fully idempotent (all skipped).
- [ ] `resources/audit_summary_v2.md` reports ≥ 95 % pass rate on new content; any flagged items fixed via `question-db-admin`.
- [ ] CLAUDE.md Phase Log + Domain Tracker updated.

Outstanding for Phase 5.1: lift every (domain × non-MC type) cell from 10 → 20 (~150 additional questions).
