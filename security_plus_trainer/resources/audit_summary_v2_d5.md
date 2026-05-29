# Phase 5 v2 Audit — Domain 5 (Security Program Management and Oversight)

Audited: 30 questions. Pass rate: 30/30 AGREE.

Scope: every Domain 5 question with `id >= 250` — IDs 363-392, distributed across objectives 5.1 (5), 5.2 (6), 5.3 (5), 5.4 (5), 5.5 (5), 5.6 (4). Types in scope: multi_select (10), true_false (10), ordering (10).

## Summary

| ID  | Type         | Obj | Verdict | One-line note |
|-----|--------------|-----|---------|---------------|
| 363 | multi_select | 5.1 | AGREE   | AUP elements vs. firewall/IDS rules and RTO/RPO — correctly identifies the three policy-content items. |
| 364 | multi_select | 5.1 | AGREE   | Owner/controller/processor/custodian — matches GDPR Art. 4(7) & 4(8). |
| 365 | true_false   | 5.1 | AGREE   | Guidelines are advisory, not mandatory — answer False is correct per SY0-701 §5.1 and NIST SP 800-100. |
| 366 | true_false   | 5.1 | AGREE   | Decentralized governance can run under a central policy — True is correct (ISO 27001 cl. 5.2). |
| 367 | ordering     | 5.1 | AGREE   | Mission -> Policy -> Standard -> Procedure -> Guideline matches the SY0-701 governance pyramid. |
| 368 | multi_select | 5.2 | AGREE   | Risk-register fields (owner, KRI, treatment) per NIST SP 800-39 §2.4. |
| 369 | multi_select | 5.2 | AGREE   | Qualitative vs. quantitative — correctly notes quantitative is not fully objective. |
| 370 | true_false   | 5.2 | AGREE   | Control cost > ALE fails financial cost-benefit — True per NIST SP 800-30r1 §3.4. |
| 371 | true_false   | 5.2 | AGREE   | Risk acceptance is documented, not deletion — False is correct. |
| 372 | ordering     | 5.2 | AGREE   | RMF: Prepare -> Categorize -> Select -> Implement -> Assess -> Authorize -> Monitor (NIST SP 800-37r2 §3). |
| 373 | ordering     | 5.2 | AGREE   | AV -> EF -> SLE -> ARO -> ALE -> compare to control cost. Canonical 800-30r1 quantitative chain. |
| 374 | multi_select | 5.3 | AGREE   | Right-to-audit clause scope; multi-tenant SaaS pentest needs separate ROE. |
| 375 | multi_select | 5.3 | AGREE   | SLA / MSA / NDA definitions correct; MOU and BPA distractors correctly excluded. |
| 376 | true_false   | 5.3 | AGREE   | Audit clause does not authorize pentest without ROE — False is correct (NIST SP 800-115 §3.2). |
| 377 | ordering     | 5.3 | AGREE   | Vendor lifecycle: due diligence -> selection -> contract -> onboard -> monitor -> renew/offboard. |
| 378 | ordering     | 5.3 | AGREE   | Independence ladder: self-assess -> internal -> regulatory -> independent 3rd-party -> pentest. Defensible per AICPA SSAE 18 + NIST SP 800-115. |
| 379 | multi_select | 5.4 | AGREE   | GDPR consequences: 4% / EUR 20M fines per Art. 83(5), reputational and DPA contractual impacts. |
| 380 | multi_select | 5.4 | AGREE   | GDPR data subject / controller / processor roles per Art. 4(1), 4(7), 4(8); data subject is a natural person only. |
| 381 | true_false   | 5.4 | AGREE   | Outsourced card processing still leaves merchant PCI scope — True per PCI DSS v4 §4 + SAQ-A. |
| 382 | true_false   | 5.4 | AGREE   | 72-hour breach window — True, GDPR Art. 33(1) verbatim. |
| 383 | ordering     | 5.4 | AGREE   | Detect -> validate -> classify/legal -> notify SA (Art. 33) -> notify subjects (Art. 34) -> document (Art. 33(5)). |
| 384 | multi_select | 5.5 | AGREE   | Internal vs. external audit roles per IIA IPPF Std 1110 / AICPA SSAE 18. |
| 385 | true_false   | 5.5 | AGREE   | Self-assessment != independent 3rd-party — False is correct (IIA IPPF Std 1100). |
| 386 | true_false   | 5.5 | AGREE   | Recon = passive + active — True per SY0-701 §5.5 explicit sub-bullets + NIST SP 800-115 §5.1. |
| 387 | ordering     | 5.5 | AGREE   | NIST SP 800-115 §5 four phases: Planning -> Discovery -> Attack -> Reporting. |
| 388 | ordering     | 5.5 | AGREE   | Unknown -> partially known -> known (black/gray/white) matches SY0-701 §5.5. |
| 389 | multi_select | 5.6 | AGREE   | Phishing campaign design: baseline, JIT training, report button. Anti-patterns correctly distractor. |
| 390 | true_false   | 5.6 | AGREE   | Anomalous behavior recognition covers Risky + Unexpected + Unintentional — False is correct. |
| 391 | ordering     | 5.6 | AGREE   | Awareness lifecycle: identify needs -> develop -> deliver -> measure -> iterate (NIST SP 800-50r1 §3). |
| 392 | ordering     | 5.6 | AGREE   | Insider-threat workflow: recognize -> report -> triage -> coordinate HR/Legal -> contain -> post-incident review. Matches NIST SP 800-53r5 PM-12 + CISA insider-threat guide. |

## Flagged items

None. All 30 Phase 5 Domain 5 questions verified.

## Audit notes

- **RMF order (Q372)** matches NIST SP 800-37r2 §3 exactly (Prepare -> Categorize -> Select -> Implement -> Assess -> Authorize -> Monitor). The new Prepare step distinguishes r2 from the legacy six-step RMF; the stem correctly cites 800-37r2.
- **Quant risk chain (Q373)** uses the AV -> EF -> SLE -> ARO -> ALE -> compare-to-control sequence; matches SY0-701 §5.2 sub-bullets and 800-30r1 §3.2.
- **Governance pyramid (Q367)** treats Mission as the apex above Policy. This is consistent with SY0-701 §5.1 wording (which lists Mission/charter ahead of Policies, Standards, Procedures, Guidelines) and with NIST SP 800-100 §2.1.
- **GDPR 72-hour clock (Q382, Q383)** correctly uses "without undue delay and, where feasible, not later than 72 hours after becoming aware" — the exact Article 33(1) wording, and correctly distinguishes Art. 33 (supervisory authority) from Art. 34 (data subjects, high-risk only).
- **Right-to-audit vs. pentest ROE (Q374, Q376)** correctly treats them as separate contractual artifacts. The audit clause is examination of records; ROE per NIST SP 800-115 §3.2 is required for any active testing.
- **Independence ladder (Q378)** is a judgment call but defensible: self-assessment is lowest (no third-party), penetration testing is highest (active adversarial validation of deployed controls). Reasonable interpretations could swap regulatory examination and independent 3rd-party assessment depending on scope; the explanation correctly notes regulatory exams are scope-bounded while independent 3rd-party (SOC 2 Type II) is broader, justifying the ordering chosen.
- **Anomalous behavior recognition (Q390)** correctly maps to the SY0-701 §5.6 sub-bullets (Risky, Unexpected, Unintentional). The False answer is unambiguous.

## Next step

Hand off to the main thread to save this report as `C:\Users\rmars\security_plus_trainer\resources\audit_summary_v2_d5.md`. No proposals — nothing flagged for the `question-db-admin` agent.
