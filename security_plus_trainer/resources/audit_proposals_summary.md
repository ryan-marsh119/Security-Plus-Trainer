All 4.8-tagged questions in the 138-183 range are confirmed to be enterprise capabilities content (firewall/IDS/IPS/secure protocols/wireless/VPN/AAA/proxies) — all correctly remapped to 4.5. Q184-191 and Q200 (IDS/IPS) also correctly remap to 4.5 (IDS/IPS is explicitly listed under 4.5).

I have everything I need now. Let me compose the proposals.

---

## Summary

- **Q26** [objective_retag] — 1.1 → 1.2: Non-repudiation is listed under fundamental security concepts (1.2), not control types (1.1).
- **Q41** [objective_retag] — 1.3 → 1.4: SSL deprecation / POODLE / DROWN / BEAST is cryptography (1.4), not change management (1.3).
- **Q65** [stem_rewrite + objective_retag] — 2.3 → 2.4: Drop wiper-implying "files missing" wording; restate as encryption + ransom note; re-tag to indicators of malicious activity (2.4 lists "Ransomware" under malware attacks).
- **Q70** [stem_rewrite + choice_edit + objective_retag] — 2.3 → 2.4: Replace "until the server crashes" with accurate RFC 4987 SYN-backlog exhaustion language; choice 3 also needs the same wording fix; re-tag to 2.4 (DDoS / network attacks).
- **Q80** [stem_rewrite] — Drop "national security" since the choices are commercial-scheme only; clean stem stays in 3.3.
- **Q117** [objective_retag] — 4.3 → 4.8: IR final step (Lessons Learned) is under 4.8 (Process: Preparation → ... → Lessons learned). Already matches stored explanation citing NIST SP 800-61.
- **Q138–143, 145–148, 152–153, 155–183, 195, 198–199, 201–207** [objective_retag] — 4.8 → 4.5: All verified as enterprise-capabilities content (firewall rules / secure protocols / IDS-IPS / wireless / VPN / AAA / proxies / NAC), which is exactly the 4.5 bullet list.
- **Q184–191, 200** [objective_retag] — 4.2 → 4.5: IDS/IPS is explicitly listed under 4.5 (4.2 is asset management).
- **Q192–194** [objective_retag] — 4.1 → 1.2: Honeypot, honeynet, honeyfile are explicitly listed under 1.2 "Deception and disruption technology" in the PDF. This is a cross-domain re-tag (D4 → D1) — flagging that the question would also move domains. The audit's "mitigation techniques" guess (2.5) was wrong; 1.2 is the canonical home in SY0-701.
- **Q208–209** [objective_retag] — 4.9 → 4.1: Hardening / default credentials / secure baselines is exactly 4.1 (Secure baselines, Hardening targets); 4.9 is investigation data sources.
- **Q212** [answer_key_change + explanation_update + hint_update] — Committee-based governance, not Decentralized. 5.1 explicitly lists "Boards" and "Committees" alongside "Centralized/decentralized" as distinct governance-structure types. The stem's "consensus among a group of stakeholders" is the textbook description of a committee.

Single line per question:

- Q26 [objective_retag] — 1.1 → 1.2 (Non-repudiation is fundamental security concept, not control type)
- Q41 [objective_retag] — 1.3 → 1.4 (SSL deprecation is cryptography, not change management)
- Q65 [stem_rewrite + objective_retag] — 2.3 → 2.4; replace "files missing/lock symbol" with accurate ransomware indicators
- Q70 [stem_rewrite + choice_edit + objective_retag] — 2.3 → 2.4; fix SYN-flood mechanics per RFC 4987 (backlog exhaustion, not crash)
- Q80 [stem_rewrite] — Remove "national security" muddling; align with commercial classification choices
- Q117 [objective_retag] — 4.3 → 4.8 (IR final step belongs under IR process)
- Q138–143, 145–148, 152–153, 155–183, 195, 198–199, 201–207 [objective_retag] — 4.8 → 4.5 (enterprise capabilities)
- Q184–191, 200 [objective_retag] — 4.2 → 4.5 (IDS/IPS explicitly under 4.5)
- Q192–194 [objective_retag] — 4.1 → 1.2 (CROSS-DOMAIN: honeypots/honeynets/honeyfiles are under 1.2 Deception & disruption tech)
- Q208–209 [objective_retag] — 4.9 → 4.1 (system hardening is 4.1 secure baselines/hardening targets)
- Q212 [answer_key_change + explanation_update + hint_update] — Decentralized → Committee-based governance