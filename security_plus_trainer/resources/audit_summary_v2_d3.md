# Phase 5 v2 Audit — Domain 3 (Security Architecture)

Audited: 29 questions (Batch 0 §3.4 IDs 250-256 + Batch 1 IDs 314-335). Pass rate: 28/29 AGREE, 1 UNSURE, 0 DISAGREE.

## Summary

| ID | Type | Obj | Verdict | One-line note |
|---|---|---|---|---|
| 250 | multi_select | 3.4 | AGREE | LB vs clustering distinctions correct per SY0-701 §3.4. |
| 251 | multi_select | 3.4 | AGREE | Cold/warm/geographic-dispersion definitions correct per NIST SP 800-34r1 §3.4.1. |
| 252 | multi_select | 3.4 | AGREE | Platform diversity / multi-cloud trade-offs correct; replication-replaces-backups properly excluded. |
| 253 | true_false | 3.4 | AGREE | Capacity = People + Technology + Infrastructure matches SY0-701 §3.4 explicit sub-bullets. |
| 254 | true_false | 3.4 | AGREE | Async replication is NOT a backup substitute — propagates corruption/ransomware. |
| 255 | true_false | 3.4 | AGREE | UPS and generator are complementary, not interchangeable. |
| 256 | ordering | 3.4 | AGREE | Tabletop → walkthrough → simulation → parallel → full failover matches NIST SP 800-84 §3.4. |
| 314 | multi_select | 3.1 | AGREE | SaaS always-customer: IAM, data, tenant config — per CSA / NIST SP 800-144. |
| 315 | multi_select | 3.1 | AGREE | Container vs VM isolation per NIST SP 800-190 §2.3 and SP 800-125. |
| 316 | true_false | 3.1 | AGREE | IaC pre-deploy review = shift-left, matches watch-item. |
| 317 | true_false | 3.1 | AGREE | Air gap not immune to USB — Stuxnet precedent. |
| 318 | ordering | 3.1 | AGREE | SaaS → PaaS → IaaS → On-prem responsibility progression correct. |
| 319 | ordering | 3.1 | AGREE | Plan-Assess-Migrate-Optimize-Govern matches AWS/Microsoft CAF. |
| 320 | ordering | 3.1 | AGREE | Flat → VLAN → subnet → micro-seg → Zero Trust progression correct per NIST SP 800-207. |
| 321 | multi_select | 3.2 | AGREE | Fail-closed for confidentiality, fail-open for availability and life safety (NFPA 101). |
| 322 | multi_select | 3.2 | AGREE | NGFW / UTM / WAF differentiation correct per NIST SP 800-41r1 §2.4. |
| 323 | true_false | 3.2 | AGREE | IDS is passive (span/tap), IPS is inline — statement correctly reversed. |
| 324 | true_false | 3.2 | AGREE | SASE = SD-WAN + SWG/CASB/ZTNA/FWaaS matches Gartner. |
| 325 | ordering | 3.2 | UNSURE | Edge ACL → IDS/IPS → firewall → WAF → server is defensible but non-canonical; firewall-before-IPS is the more common textbook depiction. |
| 326 | ordering | 3.2 | AGREE | 802.1X EAP-TLS flow matches IEEE 802.1X-2020 and RFC 5216. |
| 327 | ordering | 3.2 | AGREE | TLS 1.3 1-RTT handshake correct per RFC 8446 §2 (key derivation framed as logical step). |
| 328 | multi_select | 3.3 | AGREE | Tokenization vs masking vs encryption correct per PCI SSC Tokenization Guidelines §2.1. |
| 329 | multi_select | 3.3 | AGREE | At rest (FDE) / in transit (TLS 1.3) / in use (TEE) per NIST SP 800-111, SP 800-52r2, IR 8320. |
| 330 | true_false | 3.3 | AGREE | Hashing provides integrity not confidentiality — matches watch-item. |
| 331 | true_false | 3.3 | AGREE | Data sovereignty (legal) vs geolocation (physical) properly distinguished. |
| 332 | ordering | 3.3 | AGREE | Create → Store → Use → Share → Archive → Destroy matches CSA Data Security Lifecycle. |
| 333 | ordering | 3.3 | AGREE | Pre-activation → Activation → Operational → Deactivation → Compromise/Archive → Destruction matches NIST SP 800-57 Part 1 Rev. 5 §7.2. |
| 334 | multi_select | 3.4 | AGREE | Capacity planning = People + Technology + Infrastructure per SY0-701 §3.4. |
| 335 | ordering | 3.4 | AGREE | RPO/RTO → systems → strategy → implement → test → maintain matches NIST SP 800-34r1 §3.4. |

## Flagged items

### Q325 — Perimeter defense-in-depth ordering

**Stored key:** Edge router ACL → Inline IDS/IPS → Stateful perimeter firewall → WAF → Internal web server.

**Your answer:** The placement of the IDS/IPS BEFORE the stateful perimeter firewall is defensible but is not the most common textbook ordering for SY0-701. The more typical depiction is: edge router → stateful firewall → IDS/IPS → WAF → server. Rationale: the stateful firewall is the primary policy boundary and consumes/drops most unwanted traffic cheaply; the IDS/IPS then performs deeper signature/behavior inspection on already-permitted traffic. Sybex SY0-701 OCG, CompTIA OCG, and the Cisco SAFE reference architecture all generally place the IPS behind the firewall in canonical "defense in depth" depictions. NIST SP 800-41r1 §3.2 and SP 800-94 §6 acknowledge BOTH placements exist in practice, but the firewall-before-IPS layout is the dominant exam pattern.

**Issue:** The stored ordering is one of two industry-valid topologies, but for a study question the "canonical" Security+ answer is firewall-before-IPS. Students who learned the more common ordering will get marked wrong on a question where their answer matches the prevailing textbook.

**Proposed fix:** Two options — (a) reorder the choices to edge router ACL → stateful firewall → IDS/IPS → WAF → server and update the explanation to match the firewall-first convention; (b) rewrite the stem to anchor the ordering by an unambiguous criterion such as "from STATELESS to STATEFUL inspection depth" (which would justify ACL → IDS/IPS → firewall → WAF as ordered by inspection sophistication, not packet path). Option (a) is the lower-risk change because it conforms to the dominant Security+ study material.

**Source:** NIST SP 800-41r1 §3.2 (Firewall Topology Architecture); NIST SP 800-94 §6 (Deployment); Cisco SAFE Reference Guide (typical perimeter topology); Sybex CompTIA Security+ SY0-701 Official Study Guide (Chapter on Network Security Devices).

---

Next step: hand this report to the user for review. No DISAGREE items; one UNSURE item (Q325) needs a stem/ordering reconsideration before being released to learners.
