# Phase 5 v2 Audit — Domain 1 (General Security Concepts)

Audited: 27 questions (IDs 257–283). Pass rate: 25/27 AGREE, 0 DISAGREE, 2 UNSURE.

## Summary

| ID  | Type         | Obj | Verdict | One-line note |
|-----|--------------|-----|---------|---------------|
| 257 | multi_select | 1.1 | AGREE   | — |
| 258 | multi_select | 1.1 | AGREE   | — |
| 259 | true_false   | 1.1 | AGREE   | — |
| 260 | true_false   | 1.1 | AGREE   | — |
| 261 | ordering     | 1.1 | AGREE   | — |
| 262 | ordering     | 1.1 | AGREE   | — |
| 263 | multi_select | 1.2 | AGREE   | — |
| 264 | multi_select | 1.2 | AGREE   | — |
| 265 | multi_select | 1.2 | AGREE   | — |
| 266 | true_false   | 1.2 | AGREE   | — |
| 267 | true_false   | 1.2 | AGREE   | — |
| 268 | ordering     | 1.2 | AGREE   | — |
| 269 | ordering     | 1.2 | AGREE   | — |
| 270 | multi_select | 1.3 | AGREE   | — |
| 271 | multi_select | 1.3 | AGREE   | — |
| 272 | true_false   | 1.3 | AGREE   | — |
| 273 | true_false   | 1.3 | AGREE   | — |
| 274 | ordering     | 1.3 | AGREE   | — |
| 275 | ordering     | 1.3 | AGREE   | — |
| 276 | ordering     | 1.3 | AGREE   | — |
| 277 | multi_select | 1.4 | AGREE   | — |
| 278 | multi_select | 1.4 | AGREE   | — |
| 279 | true_false   | 1.4 | AGREE   | — |
| 280 | true_false   | 1.4 | AGREE   | — |
| 281 | ordering     | 1.4 | AGREE   | — |
| 282 | ordering     | 1.4 | UNSURE  | "Encrypts the hash with private key" is RSA-centric; not strictly true for ECDSA/EdDSA |
| 283 | ordering     | 1.4 | UNSURE  | Step 4 says CA publishes the cert "via OCSP/CRL" — OCSP/CRL are revocation channels, not cert publication |

## Flagged items

### Q282 — Digital signature steps
**Stored key (order):** hash message → encrypt hash with private key → transmit → recipient decrypts with public key → recipient hashes & compares.
**Your answer:** The ORDER is correct. The concern is purely with the verbal model in steps 2 and 4 ("encrypts the hash with their private key", "decrypts the signature with the sender's public key").
**Issue:** This RSA-centric "sign = encrypt with private key" framing is technically accurate only for RSA-PKCS#1 v1.5 / RSA-PSS. For ECDSA (FIPS 186-5 §6) and EdDSA (RFC 8032), the signing operation is mathematically a sign primitive, not an encryption — there is no "decrypt with public key" step. FIPS 186-5 §3 actually uses the neutral verbs "sign" and "verify," not "encrypt"/"decrypt."
**Proposed fix:** Optional softening of the choice text and explanation to use "transforms the hash with the private key to produce the signature" and "uses the sender's public key to verify the signature against a freshly computed hash." This matches what CompTIA's own SY0-701 reference materials and FIPS 186-5 say. However: CompTIA training materials (Messer, Sybex SY0-701, Pearson) commonly use the "encrypt with private key" simplification, and the exam itself sometimes echoes it. Net: defensible as written; recommend wording refinement but not a hard correction.
**Source:** FIPS 186-5 §3; RFC 8032 §5 (EdDSA); SY0-701 Exam Objectives PDF §1.4.

### Q283 — TLS certificate enrollment ordering
**Stored key (order):** generate key pair → create CSR → submit to CA → CA signs & issues "optionally publishing it via OCSP/CRL infrastructure" → install on server.
**Your answer:** The ORDER is correct. The issue is the wording of step 4.
**Issue:** OCSP (RFC 6960) and CRLs (RFC 5280 §5) are *revocation status* mechanisms, not certificate *publication* mechanisms. Issued certificates are delivered to the requester and may be published to Certificate Transparency logs (RFC 6962). The CA does embed the AIA / CRL Distribution Point URLs into the issued cert at signing time, but it doesn't "publish the cert via OCSP/CRL." A learner reading this step could pick up the wrong mental model.
**Proposed fix:** Reword choice 4 to: "CA signs and issues the X.509 certificate, embedding OCSP responder and CRL distribution point URLs and (for public CAs) submitting to Certificate Transparency logs." Update the explanation accordingly. The ordering of the question itself is unchanged.
**Source:** RFC 5280 §4.2.1.13 (CRL Distribution Points), §4.2.2.1 (Authority Information Access / OCSP); RFC 6962 §3 (CT logs); SY0-701 Exam Objectives PDF §1.4 ("Certificate signing request (CSR) generation").

## Notes

- All 27 questions correctly map to their stated SY0-701 objective_code (verified against the SY0-701 Exam Objectives PDF §1.1–§1.4).
- All sources cited in explanations (NIST SP 800-207, RFC 5280, RFC 6960, RFC 8446, FIPS 186-5, FIPS 180-4, NIST SP 800-128, RFC 9106, NIST SP 800-167) are real and the section references are accurate.
- The two UNSURE flags are wording-quality concerns, not answer-correctness concerns. The stored keys are defensible as-is and align with mainstream Security+ pedagogy. If the goal is "technically precise on the merits," apply the fixes; if the goal is "matches what the exam itself says," leave them.
- No DISAGREE rows. No objective_code retags needed. No answer-key changes proposed.

Next step: the main thread should save this report to `C:\Users\rmars\security_plus_trainer\resources\audit_summary_v2_d1.md` and decide whether to forward Q282/Q283 wording refinements to the `question-db-admin` agent.
