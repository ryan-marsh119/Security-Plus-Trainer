# Phase 5 v2 Audit — Domain 4 (Security Operations)

Audited: 27 questions. Pass rate: 27/27 AGREE.

## Summary

| ID | Type | Obj | Verdict | One-line note |
|---|---|---|---|---|
| 336 | multi_select | 4.1 | AGREE | ICS/SCADA, RTOS, cloud are explicit §4.1 hardening targets. |
| 337 | true_false | 4.1 | AGREE | Baseline = establish/deploy/maintain; not one-time. |
| 338 | ordering | 4.1 | AGREE | Baseline → benchmark → reduce surface → defaults → logging → scans. |
| 339 | multi_select | 4.2 | AGREE | Sanitization, destruction, certification all under disposal in §4.2. |
| 340 | true_false | 4.2 | AGREE | NIST SP 800-88r1 §2.5 — Purge allows release outside org. |
| 341 | ordering | 4.2 | AGREE | Acquisition → Assignment → Monitoring → Disposal per §4.2. |
| 342 | multi_select | 4.3 | AGREE | SAST/OSINT/pen testing all listed under identification methods. |
| 343 | true_false | 4.3 | AGREE | CVSS v3.1 Base is intrinsic; Temporal/Environmental adjust for context. |
| 344 | ordering | 4.3 | AGREE | Identify → Analyze → Prioritize → Respond → Validate → Report. |
| 345 | multi_select | 4.4 | AGREE | Log aggregation, alert tuning, archiving are activities; AV/NetFlow/SIEM are tools. |
| 346 | true_false | 4.4 | AGREE | SCAP is a NIST SP 800-126r3 protocol suite, not a product. |
| 347 | ordering | 4.4 | AGREE | Ingest → Normalize → Correlate → Enrich → Score → Notify. |
| 348 | multi_select | 4.5 | AGREE | SPF/DKIM/DMARC are DNS-published per RFCs 7208/6376/7489. |
| 349 | true_false | 4.5 | AGREE | Reputation-based filters block low/no-reputation domains by design. |
| 350 | ordering | 4.5 | AGREE | NIST SP 800-40r4 phased rollout model. |
| 351 | multi_select | 4.6 | AGREE | Know/Have/Are/Somewhere-you-are are the four §4.6 factor categories. |
| 352 | true_false | 4.6 | AGREE | JIT + ephemeral credentials eliminate standing privilege. |
| 353 | ordering | 4.6 | AGREE | Provisioning → AuthN → AuthZ → Attestation → Deprovisioning. |
| 354 | multi_select | 4.7 | AGREE | User provisioning, guard rails, CI/testing all listed in §4.7. |
| 355 | true_false | 4.7 | AGREE | §4.7 "Other considerations" lists SPOF and technical debt explicitly. |
| 356 | ordering | 4.7 | AGREE | Trigger → Enrich → Decide → Act → Verify → Document — canonical SOAR flow. |
| 357 | multi_select | 4.8 | AGREE | Legal hold, chain of custody, e-discovery all listed under §4.8 digital forensics. |
| 358 | true_false | 4.8 | AGREE | NIST SP 800-61r2 — eradication MUST precede recovery. |
| 359 | ordering | 4.8 | AGREE | Identify → Acquire → Preserve → Analyze → Report → Present (SWGDE/ACPO). |
| 360 | multi_select | 4.9 | AGREE | Firewall, endpoint, OS security logs all listed §4.9 sources. |
| 361 | true_false | 4.9 | AGREE | PCAP = payload; NetFlow/IPFIX (RFC 3954/7011) = flow metadata only. |
| 362 | ordering | 4.9 | AGREE | Exact RFC 3227 §2.1 order of volatility. |

## Flagged items

None. All 27 Phase 5 Domain 4 questions verified correct against the SY0-701 Objectives PDF and the cited NIST/RFC authorities. The set demonstrates strong alignment with the objective enumeration (most multi_selects pull directly from the bullet lists), accurate citation discipline in explanations, and correct phase ordering in all six `ordering` items. The RFC 3227 question (Q362) in particular maps 1:1 to the §2.1 sequence — a common item to get wrong, and it is right here.

Notable strengths worth preserving in future batches:
- All multi_select distractors are governance/policy artifacts pulled from other domains (Domain 5), making the contrast clean rather than tricky.
- T/F items consistently cite a specific NIST SP, RFC, or FIRST.org spec rather than hand-waving.
- Ordering items use 5–8 steps each, which keeps the question discriminative without becoming a memorization gauntlet.

No proposals to hand to the question-db-admin agent. This batch is ready to ship.
