# Phase 5 v2 Audit — Domain 2 (Threats, Vulnerabilities, and Mitigations)

Audited: 30 questions (IDs 284-313). Pass rate: 28/30 AGREE, 2 UNSURE.

## Summary

| ID | Type | Obj | Verdict | One-line note |
|---|---|---|---|---|
| 284 | multi_select | 2.1 | AGREE | Hacktivist motivations (philosophical, disruption, revenge) match §2.1. |
| 285 | multi_select | 2.1 | AGREE | APT attributes (custom tooling, long dwell, funding) match §2.1 and MITRE. |
| 286 | multi_select | 2.2 | AGREE | Vishing/pretexting/MFA fatigue all listed as human vectors §2.2. |
| 287 | multi_select | 2.2 | AGREE | Email/SMS/IM are the three message-based vectors in §2.2. |
| 288 | multi_select | 2.3 | AGREE | Buffer overflow, memory injection, race condition all under §2.3 Application. |
| 289 | multi_select | 2.3 | AGREE | VM escape and resource reuse are exactly the §2.3 Virtualization bullets. |
| 290 | multi_select | 2.4 | AGREE | Account lockout, impossible travel, missing logs all listed in §2.4 Indicators. |
| 291 | multi_select | 2.4 | UNSURE | Stem says "password / credential attacks" but Birthday is a cryptographic attack in §2.4, not strictly a password attack. Minor stem-precision issue. |
| 292 | multi_select | 2.5 | AGREE | Segmentation, least privilege, patching all explicitly listed mitigations. |
| 293 | multi_select | 2.5 | AGREE | Mobile, workstations, cloud infrastructure all in §2.5 Hardening targets. |
| 294 | true_false | 2.1 | AGREE | Shadow IT is explicitly a §2.1 threat actor. |
| 295 | true_false | 2.1 | AGREE | Unskilled attacker uses pre-built tooling — canonical. |
| 296 | true_false | 2.2 | AGREE | MFA fatigue is a human vector per §2.2 and MITRE T1621. |
| 297 | true_false | 2.2 | AGREE | Default credentials ARE an attack surface (answer: False). |
| 298 | true_false | 2.3 | AGREE | Zero-day = no vendor patch at exploitation; correct. |
| 299 | true_false | 2.3 | AGREE | TOCTOU is a race condition, not memory injection (CWE-367). |
| 300 | true_false | 2.4 | AGREE | Logic bomb = trigger-conditional payload. |
| 301 | true_false | 2.4 | AGREE | Impossible travel is a listed §2.4 indicator. |
| 302 | true_false | 2.5 | AGREE | Allow-listing is default-deny per NIST SP 800-167. |
| 303 | true_false | 2.5 | AGREE | Decommissioning IS a mitigation in §2.5 (answer: False). |
| 304 | ordering | 2.4 | AGREE | Lockheed Cyber Kill Chain 7-step order is canonical. |
| 305 | ordering | 2.4 | AGREE | Stem hedges with "typical macro-order"; chosen 6 tactics follow ATT&CK matrix left-to-right. |
| 306 | ordering | 2.5 | AGREE | detect → contain → patch → verify → decommission is defensible. |
| 307 | ordering | 2.3 | AGREE | SolarWinds-style supply-chain stages match CISA AA20-352A. |
| 308 | ordering | 2.5 | AGREE | Hardening flow per NIST SP 800-128 and CIS Controls. |
| 309 | ordering | 2.1 | UNSURE | Stages match "pathway to violence" / radicalization frameworks, but attribution to CMU CERT Insider Threat Center is questionable — CERT's published "Critical Pathway to Insider Risk" (Shaw/Stock) uses different stage labels (predispositions → stressors → concerning behaviors → org responses → hostile acts). |
| 310 | ordering | 2.2 | AGREE | Phishing chain maps cleanly onto kill chain and MITRE T1566. |
| 311 | ordering | 2.4 | AGREE | Ransomware stages match MITRE ATT&CK T1486 and CISA #StopRansomware. |
| 312 | ordering | 2.3 | AGREE | Coordinated disclosure order matches ISO/IEC 29147. |
| 313 | ordering | 2.5 | AGREE | Zero-day IR order matches NIST SP 800-61r2 §3.3 containment-before-eradication. |

## Flagged items

### Q291 — Password/credential attacks listed under SY0-701 Objective 2.4

**Stored key:** Spraying, Brute force, Birthday collision against a hash
**Your answer:** All three are listed under §2.4, but Birthday collision is taxonomically a *cryptographic attack* in the SY0-701 objectives, not strictly a *password attack*. The SY0-701 PDF §2.4 splits these into two sub-categories: "Password attacks" (Spraying, Brute force) and "Cryptographic attacks" (Downgrade, Collision, Birthday).
**Issue:** Stem says "password / credential attacks listed under SY0-701 Objective 2.4". Birthday is a cryptographic attack, not a password/credential attack — although it is often *applied* to crack password hashes, the SY0-701 taxonomy keeps them in separate sub-bullets. A purist would mark Birthday wrong here. The distractors (buffer overflow, XSS, jailbreaking) are clearly more wrong, so the question is still unambiguously answerable, but the stem's category label is imprecise.
**Proposed fix:** Reword the stem to "Which of the following are attacks listed under SY0-701 Objective 2.4? (Select THREE.)" — drop the "password / credential" qualifier. Alternatively, swap Birthday for "Password reuse / credential stuffing" or "Rainbow table attack" to keep all three squarely in the password-attack sub-bullet. Either edit keeps the answer key the same in shape and removes the taxonomy friction.
**Source:** CompTIA SY0-701 Exam Objectives PDF §2.4 (Password attacks vs. Cryptographic attacks bullets); NIST SP 800-63B §5.1.1 (password attacks); NIST SP 800-107r1 §4.2 (birthday/collision attacks as cryptographic-hash attacks).

### Q309 — CERT Insider Threat Center stage model

**Stored key:** Grievance → Ideation → Planning → Preparation → Action (attributed to CMU CERT Insider Threat Center)
**Your answer:** The five-stage sequence (grievance → ideation → planning → preparation → action) closely matches the FBI's / behavioral-threat-assessment community's "Pathway to Violence" model (Calhoun & Weston, 2003) and the U.S. Secret Service NTAC research on targeted violence. CMU CERT's most cited insider-threat framework is the "Critical Pathway to Insider Risk" by Shaw, Ruby & Post (later refined with Stock), whose canonical stages are typically labeled: Personal Predispositions → Stressors → Concerning Behaviors → Problematic Organizational Responses → Hostile Act. CERT also publishes a separate "MERIT" (Management and Education of the Risk of Insider Threat) model.
**Issue:** The stage labels and ordering in the question are correct in their own right (the pathway-to-violence framework does flow this way), but attributing them specifically to "the Carnegie Mellon CERT Insider Threat Center model" risks misleading a candidate who looks up CERT's actual published model and finds different stage names. SY0-701 §2.1 does not require knowledge of any specific named insider-threat pathway model, so this is essentially extra-curricular framing.
**Proposed fix:** Either (a) re-attribute the stem to a more neutral framing — e.g., "Place the stages of the behavioral 'pathway to violence' model an insider typically progresses through before committing a malicious act, from earliest to latest." — or (b) keep the CERT attribution but relabel the choices to match CERT's Critical Pathway terminology (Predispositions → Stressors → Concerning Behaviors → Org Response → Hostile Act). Option (a) is the smaller edit and keeps the existing answer key intact.
**Source:** CompTIA SY0-701 Exam Objectives PDF §2.1 (Insider threat — note this depth is beyond the exam); Shaw & Stock, "Behavioral Risk Indicators of Malicious Insider Theft of Intellectual Property" (CMU SEI 2011); Calhoun & Weston, "Contemporary Threat Management" (2003); U.S. Secret Service NTAC Operational Guide (2018).

---

Both flags are *minor precision/attribution issues* and neither inverts the stored answer key. The question bank is solid: 28/30 clean AGREE, 2/30 UNSURE on stem-precision grounds only.

Save this report to `C:\Users\rmars\security_plus_trainer\resources\audit_summary_v2_d2.md` (per task instruction the main thread handles the write).
