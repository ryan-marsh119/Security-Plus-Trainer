# SY0-701 Question Coverage Map
Generated: 2026-05-18 | Phase 2 output

## Summary

| Domain | Name | Questions | Objectives | Avg/Obj |
|--------|------|-----------|-----------|---------|
| 1 | General Security Concepts | 24 | 4 (1.1–1.4) | 6.0 |
| 2 | Threats, Vulnerabilities, Mitigations | 23 | 5 (2.1–2.5) | 4.6 |
| 3 | Security Architecture | 14 | 3 (3.1–3.3) | 4.7 |
| 4 | Security Operations | 24 | 9 (4.1–4.9) | 2.7 |
| 5 | Program Management & Oversight | 15 | 6 (5.1–5.6) | 2.5 |
| **Total** | | **100** | **27** | **3.7** |

**Target:** ≥ 5 questions per objective (≥ 135 questions total)

---

## Domain 1 — General Security Concepts (24 q)

| Objective | Topic | Count | Status |
|-----------|-------|-------|--------|
| 1.1 | Security controls: categories & types | 5 | ✓ Good |
| 1.2 | Threat actors, motivations, attributes | 5 | ✓ Good |
| 1.3 | Cryptography basics (symmetric, asymmetric, hashing) | 5 | ✓ Good |
| 1.4 | Authentication, authorization, AAA | 9 | ✓ Strong |

---

## Domain 2 — Threats, Vulnerabilities, Mitigations (23 q)

| Objective | Topic | Count | Status |
|-----------|-------|-------|--------|
| 2.1 | Threat intelligence & indicators of compromise | 5 | ✓ Good |
| 2.2 | Common vulnerability types (CVSS, zero-day, etc.) | 5 | ✓ Good |
| 2.3 | Malware types and attack techniques | 5 | ✓ Good |
| 2.4 | Social engineering (phishing, pretexting, vishing) | 4 | ~ Adequate |
| 2.5 | Application attacks (SQL injection, XSS, etc.) | 4 | ~ Adequate |

---

## Domain 3 — Security Architecture (14 q)

| Objective | Topic | Count | Status |
|-----------|-------|-------|--------|
| 3.1 | Architecture concepts (zero trust, defense-in-depth) | 5 | ✓ Good |
| 3.2 | Cloud and infrastructure security | 5 | ✓ Good |
| 3.3 | Resilience, HA, and recovery | 4 | ~ Adequate |

---

## Domain 4 — Security Operations (24 q)

| Objective | Topic | Count | Status |
|-----------|-------|-------|--------|
| 4.1 | Identity and access management (IAM, PAM, RBAC) | 4 | ~ Adequate |
| 4.2 | Alerting, monitoring, SIEM, SOAR | 3 | ⚠ Low |
| 4.3 | Incident response lifecycle | 3 | ⚠ Low |
| 4.4 | Digital forensics (chain of custody, data collection) | 3 | ⚠ Low |
| 4.5 | Vulnerability management (scanning, patching) | 3 | ⚠ Low |
| 4.6 | Security awareness and training | 3 | ⚠ Low |
| 4.7 | Application security (SAST, DAST, WAF) | 2 | ⚠ Low |
| 4.8 | Network security (segmentation, IDS/IPS, firewall) | 2 | ⚠ Low |
| 4.9 | Endpoint security (EDR, DLP, hardening) | 1 | ❌ Needs expansion |

---

## Domain 5 — Program Management & Oversight (15 q)

| Objective | Topic | Count | Status |
|-----------|-------|-------|--------|
| 5.1 | Security governance (policies, frameworks, roles) | 3 | ⚠ Low |
| 5.2 | Risk management (likelihood, impact, treatment) | 3 | ⚠ Low |
| 5.3 | Third-party risk (vendors, SLAs, supply chain) | 2 | ⚠ Low |
| 5.4 | Compliance (GDPR, HIPAA, PCI-DSS, SOX) | 2 | ⚠ Low |
| 5.5 | Audits and assessments (pen testing, vulnerability) | 3 | ⚠ Low |
| 5.6 | Security awareness and training programs | 2 | ⚠ Low |

---

## Question Type Distribution

| Type | Count | % |
|------|-------|---|
| multiple_choice | 72 | 72% |
| multi_select | 16 | 16% |
| true_false | 8 | 8% |
| ordering | 4 | 4% |

**Target for production:** Add PBQ (performance-based) questions in Phase 5.

---

## Expansion Priorities for Phase 5

1. **Domain 4, objectives 4.7–4.9** — lowest coverage, high exam weight
2. **Domain 5, all objectives** — averaging only 2.5 q/obj
3. **Ordering questions** — expand to crypto, vulnerability lifecycle, incident response
4. **PBQ questions** — at least 5 per domain before go-live
5. **Multi-select** — increase to ~20% of total pool (currently on target)

---

## Exam Domain Weight Reference (SY0-701)

| Domain | Exam Weight |
|--------|-------------|
| 1 — General Security Concepts | 12% |
| 2 — Threats, Vulnerabilities, Mitigations | 22% |
| 3 — Security Architecture | 18% |
| 4 — Security Operations | 28% |
| 5 — Program Management & Oversight | 20% |

Domain 4 (28% of exam) has the lowest questions-per-objective ratio — highest expansion priority.
