"""
Phase 2: SecurityPlusContentArchitect
Generates SY0-701 question bank CSVs from official objectives structure.
Source: CompTIA Security+ SY0-701 Exam Objectives (7.0) + domain knowledge.
Run: python generate_questions.py
Outputs: domain_1_general_security.csv, domain_2_threats.csv, etc.
"""
import csv
import json
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------------
# Question schema:
#   objective_code, question_text, question_type, difficulty,
#   answer_choices_json, correct_answer_key_json, hint, explanation, source
#
# question_type: multiple_choice | multi_select | true_false | ordering
# answer_choices_json: [{"id":1,"text":"...","order":1}, ...]
# correct_answer_key_json:
#   MC:           {"correct_ids": [2]}
#   multi_select: {"correct_ids": [1, 3]}
#   true_false:   {"correct_ids": [1]}  (id 1 = True, id 2 = False)
#   ordering:     {"ordered_ids": [3,1,4,2]}
# ------------------------------------------------------------------

def mc(choices):
    """Build answer_choices_json list from [(text, is_correct), ...]"""
    return [{"id": i+1, "text": t, "order": i+1} for i, (t, _) in enumerate(choices)]

def correct_mc(choices):
    ids = [i+1 for i, (_, c) in enumerate(choices) if c]
    return {"correct_ids": ids}

def tf(answer_bool):
    choices = [{"id": 1, "text": "True", "order": 1}, {"id": 2, "text": "False", "order": 2}]
    return choices, {"correct_ids": [1] if answer_bool else [2]}

SOURCE = "CompTIA Security+ SY0-701 Exam Objectives (7.0)"

# ==================================================================
# DOMAIN 1: General Security Concepts (12%)
# Objectives: 1.1, 1.2, 1.3, 1.4
# ==================================================================

DOMAIN_1 = [

    # ---- 1.1 Compare and contrast types of security controls ----
    {
        "objective_code": "1.1",
        "question_text": "A company installs a firewall to block unauthorized network traffic before it reaches internal systems. Which security control CATEGORY and TYPE does this represent?",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Managerial / Preventive", False),
            ("Technical / Preventive", True),
            ("Operational / Detective", False),
            ("Physical / Deterrent", False),
        ],
        "hint": "Consider whether the firewall uses technology to stop something before it happens.",
        "explanation": "A firewall is a Technical control (implemented through hardware/software) of the Preventive type (stops incidents before they occur). Managerial controls involve policies and governance; Operational involve people and processes; Physical involve physical barriers.",
        "source": SOURCE,
    },
    {
        "objective_code": "1.1",
        "question_text": "A security guard stationed at a building entrance provides which primary security function?",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Technical / Detective", False),
            ("Operational / Corrective", False),
            ("Physical / Deterrent", True),
            ("Managerial / Directive", False),
        ],
        "hint": "Think about the physical presence of a person and what effect that presence has on would-be attackers.",
        "explanation": "A security guard is a Physical control (human presence at a physical location). The primary security function is Deterrent — their visible presence discourages attackers from attempting unauthorized entry, even though they can also detect incidents.",
        "source": SOURCE,
    },
    {
        "objective_code": "1.1",
        "question_text": "After a malware infection, a company restores an affected server from a clean backup and re-images the system. This action is best classified as which type of security control?",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Preventive", False),
            ("Detective", False),
            ("Corrective", True),
            ("Compensating", False),
        ],
        "hint": "The action occurs AFTER the incident and aims to restore normal operations.",
        "explanation": "Corrective controls are implemented after a security incident to minimize damage and restore operations to their normal state. Preventive controls stop incidents before they happen; Detective controls identify incidents in progress; Compensating controls provide alternatives when primary controls can't be used.",
        "source": SOURCE,
    },
    {
        "objective_code": "1.1",
        "question_text": "A legacy medical device cannot receive security patches due to FDA recertification requirements. The security team implements enhanced network monitoring and places the device on an isolated VLAN. The enhanced monitoring and VLAN isolation are examples of which control type?",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("Preventive", False),
            ("Detective", False),
            ("Directive", False),
            ("Compensating", True),
        ],
        "hint": "This control is used because the preferred primary control (patching) cannot be applied.",
        "explanation": "Compensating controls are alternative controls implemented when the primary or preferred control cannot be used. Because patching is impossible, network isolation and enhanced monitoring compensate for the missing patch-based protection.",
        "source": SOURCE,
    },
    {
        "objective_code": "1.1",
        "question_text": "Which of the following BEST represents a directive security control?",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("A biometric door lock", False),
            ("An intrusion detection system alert", False),
            ("A written acceptable use policy (AUP)", True),
            ("Restoring data from a backup after ransomware", False),
        ],
        "hint": "Directive controls guide or instruct behavior rather than enforcing, detecting, or correcting it technically.",
        "explanation": "Directive controls guide behavior through policies, procedures, and standards. An AUP directs users on permitted activities. Biometric locks are Physical/Preventive; IDS alerts are Technical/Detective; restoring from backup is Corrective.",
        "source": SOURCE,
    },
    {
        "objective_code": "1.1",
        "question_text": "Select ALL security control types that would be represented by a CCTV camera system. (Choose TWO)",
        "question_type": "multi_select",
        "difficulty": "medium",
        "answer_choices": [
            ("Deterrent", True),
            ("Preventive", False),
            ("Detective", True),
            ("Corrective", False),
        ],
        "hint": "Think about what a visible camera does to a would-be attacker AND what it does during or after an incident.",
        "explanation": "A CCTV camera serves as a Deterrent (its visible presence discourages attacks) and a Detective control (it records and can detect incidents in progress or after the fact). It does not prevent or correct incidents on its own.",
        "source": SOURCE,
    },
    {
        "objective_code": "1.1",
        "question_text": "Security awareness training programs that teach employees to recognize phishing emails fall into which security control category?",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Technical", False),
            ("Physical", False),
            ("Operational", True),
            ("Managerial", False),
        ],
        "hint": "This control involves human processes and employee behavior rather than technology or governance.",
        "explanation": "Operational controls are implemented through people and day-to-day processes. Security awareness training is a prime example — it changes human behavior through procedures and education rather than through technology (Technical) or policy governance (Managerial).",
        "source": SOURCE,
    },

    # ---- 1.2 Fundamental security concepts ----
    {
        "objective_code": "1.2",
        "question_text": "An employee claims they never sent a sensitive email, but server logs and a digital signature on the message prove they did. Which security concept prevents this denial?",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Confidentiality", False),
            ("Integrity", False),
            ("Non-repudiation", True),
            ("Authentication", False),
        ],
        "hint": "The issue is that the sender is trying to deny having performed an action that was actually performed.",
        "explanation": "Non-repudiation ensures that a party cannot deny having performed an action. Digital signatures provide non-repudiation because only the holder of the private key could have signed the message, creating cryptographic proof of the sender's identity.",
        "source": SOURCE,
    },
    {
        "objective_code": "1.2",
        "question_text": "A DDoS attack overwhelms a company's web servers, making them unreachable for 6 hours. Which component of the CIA triad is PRIMARILY impacted?",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Confidentiality", False),
            ("Integrity", False),
            ("Availability", True),
            ("Non-repudiation", False),
        ],
        "hint": "The attack prevents users from being able to USE the service.",
        "explanation": "Availability ensures that systems and data are accessible to authorized users when needed. A DDoS attack directly targets availability by exhausting resources so legitimate users cannot reach services. Confidentiality (data exposure) and Integrity (data modification) are not impacted by a typical DDoS.",
        "source": SOURCE,
    },
    {
        "objective_code": "1.2",
        "question_text": "In the Zero Trust model, which component is responsible for evaluating access requests and deciding whether to grant or deny access?",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("Policy Enforcement Point", False),
            ("Policy Engine", True),
            ("Policy Administrator", False),
            ("Implicit Trust Zone", False),
        ],
        "hint": "There are two components in the Control Plane — one decides, one communicates. This is the one that decides.",
        "explanation": "In Zero Trust, the Policy Engine (Control Plane) evaluates access requests against policy and makes grant/deny decisions. The Policy Administrator communicates those decisions to Policy Enforcement Points. Policy Enforcement Points enforce decisions at the data plane.",
        "source": SOURCE,
    },
    {
        "objective_code": "1.2",
        "question_text": "Which component of the AAA framework tracks WHAT resources a user accessed and for HOW LONG?",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Authentication", False),
            ("Authorization", False),
            ("Accounting", True),
            ("Attestation", False),
        ],
        "hint": "One AAA component verifies who you are, one controls what you can do, and one records what you did.",
        "explanation": "Accounting (the third A in AAA) tracks and logs user activity — what resources were accessed, when, and for how long. This creates an audit trail. Authentication verifies identity; Authorization determines what an authenticated user can access.",
        "source": SOURCE,
    },
    {
        "objective_code": "1.2",
        "question_text": "A fake file named 'Q4_Salary_Data.xlsx' is placed on a file server to detect unauthorized browsing. An alert fires when the file is opened. This is an example of which deception technology?",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("Honeynet", False),
            ("Honeypot", False),
            ("Honeyfile", True),
            ("Honeytoken", False),
        ],
        "hint": "The decoy is specifically a file, not a system or network.",
        "explanation": "A honeyfile is a fake, enticing file designed to detect unauthorized access. When accessed, it triggers an alert. A honeypot is a fake system; a honeynet is a network of honeypots; a honeytoken is a fake credential or data token used to detect unauthorized use.",
        "source": SOURCE,
    },
    {
        "objective_code": "1.2",
        "question_text": "Zero Trust operates on the principle that no user or system should be trusted by default, even if inside the corporate network. True or False?",
        "question_type": "true_false",
        "difficulty": "easy",
        "answer_choices": None,
        "answer_bool": True,
        "hint": "Think about what 'Zero Trust' literally means — how much trust is granted by default?",
        "explanation": "TRUE. Zero Trust rejects the traditional perimeter-based model where everything inside the network is trusted. Instead, it requires continuous verification of every user, device, and connection — 'never trust, always verify' — regardless of network location.",
        "source": SOURCE,
    },

    # ---- 1.3 Change management processes ----
    {
        "objective_code": "1.3",
        "question_text": "A change management process requires documentation of the steps to reverse a change if it causes system instability. What is this document called?",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Standard operating procedure", False),
            ("Maintenance window", False),
            ("Backout plan", True),
            ("Impact analysis", False),
        ],
        "hint": "This document is your safety net — it describes how to undo the change if something goes wrong.",
        "explanation": "A backout plan (rollback plan) documents exactly how to reverse a change if it causes problems. It is a mandatory element of formal change management because it minimizes the impact of failed changes on production systems.",
        "source": SOURCE,
    },
    {
        "objective_code": "1.3",
        "question_text": "A developer deploys a new internal tool to production servers without submitting a change request or notifying the IT security team. This is most accurately described as:",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("A supply chain attack", False),
            ("Shadow IT", True),
            ("Insider threat", False),
            ("A zero-day vulnerability", False),
        ],
        "hint": "The tool is real and used for legitimate purposes — the problem is it bypassed formal approval processes.",
        "explanation": "Shadow IT refers to technology used within an organization without explicit IT department knowledge or approval. While often well-intentioned, it creates security risks because the systems aren't vetted, patched, or monitored. It is distinct from an insider threat (malicious intent) or supply chain attack (compromised third-party component).",
        "source": SOURCE,
    },
    {
        "objective_code": "1.3",
        "question_text": "A change management process requires that all system diagrams and procedures be updated to reflect the new configuration after a firewall rule change is approved and implemented. This requirement addresses which element of change management?",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("Backout plan", False),
            ("Version control", False),
            ("Documentation", True),
            ("Ownership", False),
        ],
        "hint": "This is about keeping written records (diagrams and procedures) current.",
        "explanation": "Documentation in change management requires updating all affected diagrams, policies, and procedures to accurately reflect the post-change state. Outdated documentation creates security risks by causing incorrect assumptions during future changes or incident response. Version control tracks changes to files over time; ownership identifies who is responsible.",
        "source": SOURCE,
    },
    {
        "objective_code": "1.3",
        "question_text": "Which of the following BEST describes the purpose of an allow list (whitelist) compared to a deny list (blacklist) in access control?",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("An allow list blocks known bad items; a deny list permits known good items", False),
            ("An allow list permits only explicitly approved items; a deny list blocks only explicitly prohibited items", True),
            ("Both lists serve identical functions but use different terminology", False),
            ("An allow list is used for network traffic; a deny list is used for applications", False),
        ],
        "hint": "Consider what happens to items that are NOT on each list.",
        "explanation": "An allow list (whitelist) permits ONLY the explicitly listed items and blocks everything else — a default-deny approach. A deny list (blacklist) blocks only the explicitly listed items and permits everything else — a default-allow approach. Allow lists provide stronger security because unknown/new threats are blocked by default.",
        "source": SOURCE,
    },

    # ---- 1.4 Cryptographic solutions ----
    {
        "objective_code": "1.4",
        "question_text": "Which cryptographic function takes arbitrary input and produces a fixed-length output that CANNOT be reversed to recover the original input?",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Symmetric encryption", False),
            ("Asymmetric encryption", False),
            ("Hashing", True),
            ("Tokenization", False),
        ],
        "hint": "This function is intentionally one-way — you cannot 'decrypt' the output.",
        "explanation": "Hashing is a one-way function that produces a fixed-length digest (hash). It cannot be reversed. Common uses: password storage, data integrity verification. Unlike encryption (which is reversible), a hash cannot be 'decrypted' to recover the original data.",
        "source": SOURCE,
    },
    {
        "objective_code": "1.4",
        "question_text": "A web server's TLS certificate was compromised. The CA needs to notify clients immediately that the certificate is invalid before its scheduled expiration. Which mechanism provides real-time certificate status?",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("Certificate Revocation List (CRL)", False),
            ("Online Certificate Status Protocol (OCSP)", True),
            ("Certificate Signing Request (CSR)", False),
            ("Key escrow", False),
        ],
        "hint": "One option is a downloadable list (periodic), the other is an online real-time query protocol.",
        "explanation": "OCSP allows clients to query a CA in real-time for the current revocation status of a specific certificate. It is faster than CRLs, which must be downloaded periodically and may be stale. CRLs are lists of revoked certificates; CSRs are requests to get a certificate issued.",
        "source": SOURCE,
    },
    {
        "objective_code": "1.4",
        "question_text": "A hardware device embedded on a server's motherboard stores encryption keys, provides remote attestation of boot integrity, and supports BitLocker. This device is called a:",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Hardware Security Module (HSM)", False),
            ("Trusted Platform Module (TPM)", True),
            ("Secure Enclave", False),
            ("Key Management System (KMS)", False),
        ],
        "hint": "This chip is soldered onto the motherboard of individual computers — it's not an external appliance.",
        "explanation": "A TPM is a dedicated microchip on the motherboard that securely stores cryptographic keys, performs platform integrity measurement (attestation), and supports technologies like BitLocker. An HSM is an external high-performance cryptographic appliance used for enterprise key management, not embedded in individual systems.",
        "source": SOURCE,
    },
    {
        "objective_code": "1.4",
        "question_text": "Which technique hides secret data inside an ordinary-looking file (such as an image or audio file) to conceal that a message is being sent at all?",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("Tokenization", False),
            ("Data masking", False),
            ("Steganography", True),
            ("Encryption", False),
        ],
        "hint": "This technique focuses on hiding the EXISTENCE of the message, not just its content.",
        "explanation": "Steganography conceals secret data within ordinary files (images, audio, video) so that an observer doesn't know a hidden message exists. Unlike encryption (which makes data unreadable but obviously encrypted), steganography aims for security through obscurity of the message's existence.",
        "source": SOURCE,
    },
    {
        "objective_code": "1.4",
        "question_text": "Which of the following BEST describes key stretching?",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("Splitting a single key into multiple parts for distributed storage", False),
            ("Applying a hashing function thousands of times to make brute-force attacks computationally expensive", True),
            ("Extending the length of an encryption key using padding", False),
            ("Distributing encryption keys across multiple key management servers", False),
        ],
        "hint": "The goal is to make a weak password harder to crack by increasing the computation required.",
        "explanation": "Key stretching (e.g., bcrypt, PBKDF2, scrypt) applies a hashing function many thousands of times to a password, making each guess in a brute-force attack require significant computation. This dramatically slows down attackers even if the original password is short. The extra computation doesn't impact normal login (one hash) but crushes offline cracking attempts (billions of hashes).",
        "source": SOURCE,
    },
    {
        "objective_code": "1.4",
        "question_text": "A financial company replaces account numbers in their test database with random strings that maintain the same format but have no mathematical relationship to the original numbers. This is BEST described as:",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("Encryption", False),
            ("Hashing", False),
            ("Tokenization", True),
            ("Salting", False),
        ],
        "hint": "The substitute value is random and has no reversible mathematical relationship to the original.",
        "explanation": "Tokenization replaces sensitive data with non-sensitive tokens that have no exploitable relationship to the original values. Unlike encryption (reversible with a key) or hashing (one-way but deterministic), tokens are random substitutes stored in a lookup table. This is widely used for payment card data (PCI DSS compliance).",
        "source": SOURCE,
    },
    {
        "objective_code": "1.4",
        "question_text": "Asymmetric encryption uses one key for encryption and a different key for decryption. True or False?",
        "question_type": "true_false",
        "difficulty": "easy",
        "answer_choices": None,
        "answer_bool": True,
        "hint": "Consider the 'asymmetric' part — does it use equal (same) keys or unequal (different) keys?",
        "explanation": "TRUE. Asymmetric (public-key) encryption uses a mathematically related key pair: the public key encrypts data, and only the corresponding private key can decrypt it (or vice versa for digital signatures). This is different from symmetric encryption, which uses the same key for both operations.",
        "source": SOURCE,
    },
]

# ==================================================================
# DOMAIN 2: Threats, Vulnerabilities, and Mitigations (22%)
# Objectives: 2.1, 2.2, 2.3, 2.4, 2.5
# ==================================================================

DOMAIN_2 = [

    # ---- 2.1 Threat actors and motivations ----
    {
        "objective_code": "2.1",
        "question_text": "A group of attackers with sophisticated capabilities, nearly unlimited funding, and long-term objectives to steal government secrets is BEST classified as which threat actor type?",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Hacktivist", False),
            ("Nation-state", True),
            ("Organized crime", False),
            ("Unskilled attacker", False),
        ],
        "hint": "This actor type is backed by a government and focuses on espionage or strategic disruption.",
        "explanation": "Nation-state threat actors are sponsored by governments and typically have advanced capabilities (APT — Advanced Persistent Threat), substantial funding, and strategic motivations such as espionage, intelligence gathering, or disrupting adversary critical infrastructure. They are the most sophisticated and persistent threat actors.",
        "source": SOURCE,
    },
    {
        "objective_code": "2.1",
        "question_text": "An attacker defaces a corporation's website with political slogans to protest the company's environmental policies. This attacker is BEST described as a:",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Nation-state actor", False),
            ("Hacktivist", True),
            ("Insider threat", False),
            ("Organized crime member", False),
        ],
        "hint": "The primary motivation here is ideological or political, not financial.",
        "explanation": "A hacktivist combines hacking with activism, using cyberattacks to promote political, social, or ideological causes. Their primary motivation is philosophical/political beliefs rather than financial gain or espionage. Typical tactics include website defacement, DDoS attacks, and data leaks.",
        "source": SOURCE,
    },
    {
        "objective_code": "2.1",
        "question_text": "Which of the following attributes BEST distinguishes a nation-state actor from organized crime as a threat actor?",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("Organized crime uses more sophisticated attack techniques", False),
            ("Nation-state actors are exclusively internal threats", False),
            ("Nation-state actors are primarily motivated by espionage and strategic disruption rather than financial gain", True),
            ("Organized crime has greater resources and funding", False),
        ],
        "hint": "Think about the PRIMARY goal of each type of actor.",
        "explanation": "Nation-state actors primarily seek espionage, intelligence, or strategic disruption. Organized crime is primarily financially motivated (ransomware, fraud, data theft for sale). Both can be highly sophisticated, but their motivations and targets differ significantly, which affects their tactics and target selection.",
        "source": SOURCE,
    },
    {
        "objective_code": "2.1",
        "question_text": "A disgruntled employee copies confidential customer records to a personal USB drive before resigning. Which threat actor category does this represent?",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Shadow IT", False),
            ("Unskilled attacker", False),
            ("Insider threat", True),
            ("Hacktivist", False),
        ],
        "hint": "This person is currently or recently employed by the organization they are harming.",
        "explanation": "An insider threat is a current or former employee, contractor, or partner who misuses their authorized access to harm the organization. Insider threats are particularly dangerous because they have legitimate access to systems and knowledge of internal processes, making them harder to detect than external attackers.",
        "source": SOURCE,
    },

    # ---- 2.2 Threat vectors and attack surfaces ----
    {
        "objective_code": "2.2",
        "question_text": "An attacker sends a fraudulent email appearing to come from a company's bank, directing employees to a fake login page to steal credentials. This attack uses which threat vector?",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Voice call (vishing)", False),
            ("Message-based / phishing", True),
            ("Removable device", False),
            ("Supply chain", False),
        ],
        "hint": "The delivery mechanism is email.",
        "explanation": "Phishing is a message-based threat vector that uses deceptive emails to trick users into revealing credentials or clicking malicious links. Vishing uses voice calls; smishing uses SMS. Message-based attacks (email, IM, SMS) are the most common initial access vector.",
        "source": SOURCE,
    },
    {
        "objective_code": "2.2",
        "question_text": "An attacker compromises a software library used by hundreds of applications during its build process. This is an example of which threat vector?",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("Vulnerable software", False),
            ("Supply chain attack", True),
            ("Watering hole attack", False),
            ("Unsupported systems", False),
        ],
        "hint": "The attacker targets a component that gets distributed to many victims through a trusted channel.",
        "explanation": "A supply chain attack compromises software, hardware, or services provided by vendors/suppliers before they reach the end customer. By compromising a widely-used library, the attacker reaches all applications that include it. SolarWinds and XZ Utils are real-world examples.",
        "source": SOURCE,
    },
    {
        "objective_code": "2.2",
        "question_text": "Attackers identify that a company uses a popular industry news website. They compromise the news website, knowing the target employees visit it. This technique is called a:",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("Typosquatting", False),
            ("Brand impersonation", False),
            ("Watering hole attack", True),
            ("Business email compromise", False),
        ],
        "hint": "The attacker poisons a 'watering hole' that the targets are known to visit.",
        "explanation": "A watering hole attack compromises a website that the attacker knows targets regularly visit. Rather than attacking the hardened target directly, the attacker compromises an intermediary site and waits for victims to come to them — similar to predators waiting at a water source.",
        "source": SOURCE,
    },
    {
        "objective_code": "2.2",
        "question_text": "An attacker registers the domain 'micros0ft.com' (with a zero instead of 'o') to intercept users who mistype the legitimate URL. This attack is called:",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Brand impersonation", False),
            ("Pretexting", False),
            ("Typosquatting", True),
            ("Business email compromise", False),
        ],
        "hint": "The attack exploits common typing mistakes in domain names.",
        "explanation": "Typosquatting (URL hijacking) registers domain names with common typographical errors of legitimate domains. Users who mistype URLs land on the attacker's site, which may host malware or credential-harvesting pages. It exploits the human tendency to make small keyboard errors.",
        "source": SOURCE,
    },
    {
        "objective_code": "2.2",
        "question_text": "Which of the following BEST represents an open service port as an attack surface?",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("A server running an unpatched OS", False),
            ("A server with TCP port 23 (Telnet) open and accessible from the internet", True),
            ("A server with default admin credentials unchanged", False),
            ("A server without disk encryption", False),
        ],
        "hint": "The question specifically asks about an OPEN SERVICE PORT.",
        "explanation": "An open service port directly represents an attack surface by exposing a service to potential exploitation. Port 23 (Telnet) is unencrypted and especially dangerous when internet-facing. Unpatched OS is a vulnerability; default credentials is a misconfiguration; missing disk encryption is a data-at-rest issue.",
        "source": SOURCE,
    },

    # ---- 2.3 Types of vulnerabilities ----
    {
        "objective_code": "2.3",
        "question_text": "An attacker provides carefully crafted input to a web application that causes the application to execute SQL commands against the database, bypassing authentication. This is an example of which vulnerability type?",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Buffer overflow", False),
            ("Cross-site scripting (XSS)", False),
            ("SQL injection (SQLi)", True),
            ("Race condition", False),
        ],
        "hint": "The attacker is manipulating database query logic through user input.",
        "explanation": "SQL injection (SQLi) occurs when user-supplied input is incorporated into SQL queries without proper sanitization, allowing attackers to manipulate the query logic. Classic bypass: entering ' OR '1'='1 as a username. It can expose, modify, or delete database data.",
        "source": SOURCE,
    },
    {
        "objective_code": "2.3",
        "question_text": "A vulnerability is discovered on a vendor's hardware that cannot receive firmware updates because the product has reached its end-of-life date. Which vulnerability category does this represent?",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("Zero-day", False),
            ("Supply chain", False),
            ("Hardware / end-of-life", True),
            ("Cryptographic", False),
        ],
        "hint": "The vulnerability exists because the product is no longer supported by the vendor.",
        "explanation": "End-of-life hardware vulnerabilities arise when devices no longer receive security updates from the manufacturer. Without patches, known vulnerabilities remain permanently exploitable. This is a hardware category vulnerability (though it overlaps with legacy systems) — distinct from zero-day (unknown) or supply chain (compromised during manufacturing/distribution).",
        "source": SOURCE,
    },
    {
        "objective_code": "2.3",
        "question_text": "An application checks a file's permissions before opening it (time-of-check), but the attacker replaces the file with a malicious one in the brief moment between the check and the actual file access (time-of-use). This vulnerability is called a:",
        "question_type": "multiple_choice",
        "difficulty": "hard",
        "answer_choices": [
            ("Buffer overflow", False),
            ("Memory injection", False),
            ("Race condition (TOC/TOU)", True),
            ("Privilege escalation", False),
        ],
        "hint": "The attack exploits a tiny gap in TIME between two operations that should be atomic.",
        "explanation": "A race condition (specifically TOC/TOU — Time-of-Check/Time-of-Use) exploits the time gap between when a resource is checked and when it is used. By replacing the resource in that window, an attacker bypasses the security check. This is a classic example of an TOCTOU race condition vulnerability.",
        "source": SOURCE,
    },
    {
        "objective_code": "2.3",
        "question_text": "An attacker installs an unofficial app on an Android device by enabling 'Unknown Sources' and installing an APK directly, bypassing the Google Play Store. This technique is called:",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Jailbreaking", False),
            ("Side loading", True),
            ("Rootkit installation", False),
            ("Privilege escalation", False),
        ],
        "hint": "This involves installing apps through unofficial channels on an Android device.",
        "explanation": "Side loading is the practice of installing applications on a mobile device from sources other than the official app store, bypassing app store security review. Jailbreaking (iOS) or rooting (Android) removes OS-level restrictions; side loading doesn't require root/jailbreak but bypasses store vetting.",
        "source": SOURCE,
    },
    {
        "objective_code": "2.3",
        "question_text": "A vulnerability that is unknown to the vendor and has no available patch is called a:",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("CVE", False),
            ("Zero-day vulnerability", True),
            ("CVSS critical vulnerability", False),
            ("Legacy vulnerability", False),
        ],
        "hint": "The vendor has had 'zero days' to fix it because they don't know about it yet.",
        "explanation": "A zero-day vulnerability is a flaw unknown to the vendor and therefore unpatched. The name refers to the number of days the vendor has had to fix the issue: zero. Zero-days are highly valuable to attackers because no defense exists until the vendor is notified and releases a patch.",
        "source": SOURCE,
    },

    # ---- 2.4 Indicators of malicious activity ----
    {
        "objective_code": "2.4",
        "question_text": "Security analysts observe that a user account successfully authenticated from New York at 8:00 AM and then authenticated from Tokyo at 8:45 AM — a physical impossibility. This indicator is called:",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Account lockout", False),
            ("Concurrent session usage", False),
            ("Impossible travel", True),
            ("Out-of-cycle logging", False),
        ],
        "hint": "The physical distance and time difference make the logins logically impossible for a single person.",
        "explanation": "Impossible travel is an indicator of compromise where authentication events occur from geographically distant locations within a timeframe physically impossible for travel. It typically indicates credential theft and use by an attacker in a different location from the legitimate user.",
        "source": SOURCE,
    },
    {
        "objective_code": "2.4",
        "question_text": "Malware that encrypts a victim's files and demands cryptocurrency payment to restore access is classified as:",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Trojan", False),
            ("Ransomware", True),
            ("Rootkit", False),
            ("Logic bomb", False),
        ],
        "hint": "The primary action is encrypting data and demanding payment (ransom).",
        "explanation": "Ransomware encrypts victim files and demands payment (typically cryptocurrency) for the decryption key. Notable examples: WannaCry, CryptoLocker, REvil. It primarily attacks Availability (files become inaccessible) and can also impact Confidentiality (modern ransomware exfiltrates data before encrypting).",
        "source": SOURCE,
    },
    {
        "objective_code": "2.4",
        "question_text": "Malware that hides itself and other malicious software at the kernel or hypervisor level, making it extremely difficult to detect from within the compromised OS, is called a:",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("Worm", False),
            ("Spyware", False),
            ("Rootkit", True),
            ("Logic bomb", False),
        ],
        "hint": "This malware 'roots' itself at the lowest levels of the OS to hide its presence.",
        "explanation": "A rootkit hides itself and other malware at the kernel, hypervisor (bootkit), or firmware level. Because it operates below the OS, it can subvert security tools running within the OS. Detection typically requires offline scanning from a trusted boot medium or specialized hardware-based tools.",
        "source": SOURCE,
    },
    {
        "objective_code": "2.4",
        "question_text": "An attacker floods a DNS server with requests that are reflected and amplified off legitimate DNS resolvers, overwhelming the target. This attack type is BEST described as:",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("On-path attack", False),
            ("Credential replay attack", False),
            ("Amplified/reflected DDoS", True),
            ("DNS poisoning", False),
        ],
        "hint": "The attacker uses innocent third-party servers to bounce and multiply the attack traffic.",
        "explanation": "An amplified/reflected DDoS uses spoofed requests to third-party servers (DNS, NTP, memcached) that send large responses to the victim. Reflection hides the attacker's source; amplification multiplies the traffic volume (DNS can achieve 50x+ amplification). This is distinct from DNS poisoning (corrupting cache entries).",
        "source": SOURCE,
    },
    {
        "objective_code": "2.4",
        "question_text": "Which of the following malware types activates only when a specific condition is met, such as a date or a specific user action?",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("Worm", False),
            ("Trojan", False),
            ("Logic bomb", True),
            ("Bloatware", False),
        ],
        "hint": "The name contains a word meaning 'explosive device' — it waits for a trigger.",
        "explanation": "A logic bomb is malicious code that remains dormant until a specific trigger condition is met (a date, user action, or system event). A classic scenario: a disgruntled employee plants a logic bomb that deletes files if they are removed from the Active Directory. It differs from a worm (self-replicating) or Trojan (disguised as legitimate software).",
        "source": SOURCE,
    },

    # ---- 2.5 Mitigation techniques ----
    {
        "objective_code": "2.5",
        "question_text": "Which mitigation technique divides a network into separate segments to prevent an attacker who compromises one segment from freely moving laterally to other areas?",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Least privilege", False),
            ("Patching", False),
            ("Segmentation", True),
            ("Configuration enforcement", False),
        ],
        "hint": "This technique creates barriers between different parts of the network.",
        "explanation": "Network segmentation divides infrastructure into isolated zones (VLANs, DMZs, microsegments). Even if an attacker compromises one segment, they face additional barriers when attempting lateral movement to other segments. This contains breaches and reduces blast radius.",
        "source": SOURCE,
    },
    {
        "objective_code": "2.5",
        "question_text": "A user account is granted only the minimum permissions required to perform their specific job duties. Which security principle does this represent?",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Separation of duties", False),
            ("Least privilege", True),
            ("Need to know", False),
            ("Defense in depth", False),
        ],
        "hint": "The principle involves giving users the MINIMUM access they need — no more.",
        "explanation": "Least privilege means granting users, processes, and systems only the minimum permissions necessary to perform their function. It limits the damage an attacker can do with a compromised account and reduces the risk from insider threats. It is distinct from 'need to know' (information access) though related.",
        "source": SOURCE,
    },
    {
        "objective_code": "2.5",
        "question_text": "Which hardening technique removes unnecessary software, disables unused ports and protocols, and changes default passwords to reduce the attack surface?",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Patching", False),
            ("Encryption", False),
            ("Hardening", True),
            ("Isolation", False),
        ],
        "hint": "This technique involves reducing attack surface by removing or disabling anything not required.",
        "explanation": "System hardening reduces the attack surface by eliminating unnecessary services, closing unused ports, changing default credentials, and configuring security settings. Common frameworks: CIS Benchmarks, DISA STIGs. Patching addresses known vulnerabilities in existing software; hardening removes unnecessary exposure.",
        "source": SOURCE,
    },
    {
        "objective_code": "2.5",
        "question_text": "An organization installs endpoint protection software that monitors all running processes and blocks those that match known malware signatures. This is an example of which mitigation?",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Segmentation", False),
            ("Installation of endpoint protection", True),
            ("Configuration enforcement", False),
            ("Application allow list", False),
        ],
        "hint": "This is directly called out in the SY0-701 hardening techniques list.",
        "explanation": "Endpoint protection (antivirus/EDR) monitors running processes and files for known malware signatures and behavioral indicators. It is a key hardening technique for workstations and servers. Application allow listing is more restrictive (only approved apps run); endpoint protection detects and blocks known threats.",
        "source": SOURCE,
    },
]

# ==================================================================
# DOMAIN 3: Security Architecture (18%)
# Objectives: 3.1, 3.2, 3.3, 3.4
# ==================================================================

DOMAIN_3 = [

    # ---- 3.1 Architecture models ----
    {
        "objective_code": "3.1",
        "question_text": "In a cloud shared responsibility model, which security responsibilities does the cloud customer ALWAYS retain regardless of the service model (IaaS, PaaS, SaaS)?",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("Hypervisor and physical infrastructure security", False),
            ("Data classification and access management for their own data", True),
            ("Operating system patching and network configuration", False),
            ("Firewall management and intrusion detection", False),
        ],
        "hint": "Think about what the customer owns that doesn't change regardless of whether they use IaaS, PaaS, or SaaS.",
        "explanation": "Regardless of cloud service model, customers always retain responsibility for their own data (classification, protection) and access management (who accesses their data). Physical infrastructure is always the CSP's responsibility; OS/network responsibilities shift between IaaS (customer) and PaaS/SaaS (CSP).",
        "source": SOURCE,
    },
    {
        "objective_code": "3.1",
        "question_text": "A factory uses specialized industrial equipment running proprietary software to control physical machinery. This equipment communicates with a central management server. This is an example of which architecture type?",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("Containerization", False),
            ("Serverless computing", False),
            ("ICS/SCADA", True),
            ("Software-defined networking", False),
        ],
        "hint": "This describes industrial control systems used in manufacturing and utilities.",
        "explanation": "Industrial Control Systems (ICS) / Supervisory Control and Data Acquisition (SCADA) manage physical industrial processes. They have unique security challenges: legacy systems, real-time requirements, inability to patch, and catastrophic consequences of compromise (physical damage, safety risks). They differ fundamentally from IT systems in their security requirements.",
        "source": SOURCE,
    },
    {
        "objective_code": "3.1",
        "question_text": "A system is designed so that if a critical security control fails, the system defaults to a state that denies all access rather than allowing all access. This is called:",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("Fail-open", False),
            ("Fail-closed (fail-secure)", True),
            ("High availability", False),
            ("Defense in depth", False),
        ],
        "hint": "Consider which failure mode prioritizes security over availability.",
        "explanation": "Fail-closed (fail-secure) means the system defaults to a secure, restrictive state upon failure — denying all access rather than allowing it. This prioritizes security over availability. Fail-open allows all traffic upon failure, prioritizing availability over security (appropriate for life-safety systems where blocking could be dangerous).",
        "source": SOURCE,
    },
    {
        "objective_code": "3.1",
        "question_text": "An organization runs its infrastructure using virtual machines on a shared physical host. An attacker who compromises a guest VM attempts to break out and access the hypervisor or other VMs. This attack is called:",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("Resource reuse", False),
            ("VM escape", True),
            ("Containerization breakout", False),
            ("Side-channel attack", False),
        ],
        "hint": "The attacker is trying to escape the boundaries of their isolated virtual environment.",
        "explanation": "VM escape is an attack where malicious code running inside a guest VM breaks out of the VM's isolation to execute on the hypervisor or access other VMs on the same host. It is a critical virtualization security concern because it undermines the isolation guarantee that makes multi-tenant cloud hosting possible.",
        "source": SOURCE,
    },

    # ---- 3.2 Secure enterprise infrastructure ----
    {
        "objective_code": "3.2",
        "question_text": "A web application firewall (WAF) is MOST effective at protecting against which type of attack?",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("DDoS volumetric attacks", False),
            ("SQL injection and cross-site scripting (XSS)", True),
            ("ARP spoofing on the local network", False),
            ("Man-in-the-middle TLS interception", False),
        ],
        "hint": "A WAF operates at Layer 7 and inspects HTTP/HTTPS content.",
        "explanation": "A WAF inspects HTTP/HTTPS application layer traffic and is specifically designed to detect and block web application attacks like SQL injection, XSS, CSRF, and directory traversal. It operates at Layer 7, distinguishing it from network firewalls (Layers 3-4). While it can mitigate some DDoS, volumetric attacks require dedicated DDoS mitigation.",
        "source": SOURCE,
    },
    {
        "objective_code": "3.2",
        "question_text": "A jump server (bastion host) is placed between an administrator's workstation and critical production servers. What is the PRIMARY security purpose of this architecture?",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("To encrypt all administrative traffic using TLS", False),
            ("To provide a single, hardened, audited access point for administrative connections", True),
            ("To automatically patch production servers", False),
            ("To balance load across multiple administrative sessions", False),
        ],
        "hint": "The jump server funnels all admin access through one controlled, monitored point.",
        "explanation": "A jump server (bastion host) creates a single, hardened, heavily-audited gateway through which all administrative access to production systems must pass. This limits attack surface (no direct admin access to servers from workstations), enables centralized logging of all admin actions, and allows MFA enforcement at one point.",
        "source": SOURCE,
    },
    {
        "objective_code": "3.2",
        "question_text": "Which protocol, operating on port 802.1X, controls network access by requiring devices to authenticate before being permitted to communicate on the network?",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("VPN", False),
            ("Network Access Control (NAC) via 802.1X", True),
            ("VLAN tagging", False),
            ("WPA3", False),
        ],
        "hint": "802.1X is specifically mentioned in objective 3.2 under port security.",
        "explanation": "802.1X is a port-based Network Access Control (NAC) protocol. Before a device is allowed to communicate on the network, it must authenticate using EAP (Extensible Authentication Protocol) against a RADIUS server. Unauthenticated devices are placed in a restricted VLAN or denied access entirely.",
        "source": SOURCE,
    },
    {
        "objective_code": "3.2",
        "question_text": "A Secure Access Service Edge (SASE) solution combines which two types of technologies?",
        "question_type": "multiple_choice",
        "difficulty": "hard",
        "answer_choices": [
            ("Endpoint detection and network firewalling", False),
            ("SD-WAN networking and cloud-delivered security services", True),
            ("VPN and MFA", False),
            ("SIEM and SOAR", False),
        ],
        "hint": "SASE = networking (WAN) + security (cloud-based services) converged into one solution.",
        "explanation": "SASE (Secure Access Service Edge) converges SD-WAN (software-defined networking) with cloud-based security services (CASB, SWG, ZTNA, FWaaS) into a single cloud-delivered service. This allows organizations to apply consistent security policies to remote users and branch offices regardless of location, without backhauling traffic to a data center.",
        "source": SOURCE,
    },

    # ---- 3.3 Data protection ----
    {
        "objective_code": "3.3",
        "question_text": "An employee emails an encrypted document containing trade secrets to a competitor. A DLP system detects and blocks the transmission. The data in this email was in which state?",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Data at rest", False),
            ("Data in transit", True),
            ("Data in use", False),
            ("Data in process", False),
        ],
        "hint": "The data is actively moving from one location to another via email.",
        "explanation": "Data in transit (data in motion) is data actively moving across a network — through email, file transfer, API calls, etc. Data at rest is stored in a file system or database. Data in use is data actively being processed in memory (RAM). Different protection mechanisms apply to each state.",
        "source": SOURCE,
    },
    {
        "objective_code": "3.3",
        "question_text": "Which data classification label is typically applied to information that, if disclosed, could cause serious damage to national security or organizational competitiveness?",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("Public", False),
            ("Private", False),
            ("Restricted/Confidential", True),
            ("Critical", False),
        ],
        "hint": "This is the most sensitive classification level for non-government organizations.",
        "explanation": "Restricted or Confidential data represents the highest sensitivity level in many organizational classification schemes — information whose unauthorized disclosure could cause significant harm. For government data, this maps to 'Top Secret' or 'Secret.' Public data can be freely shared; Private data has limited distribution; Critical may refer to system availability.",
        "source": SOURCE,
    },
    {
        "objective_code": "3.3",
        "question_text": "Data sovereignty means that data stored in a particular country is subject to that country's laws and regulations, regardless of where the data owner is located. True or False?",
        "question_type": "true_false",
        "difficulty": "easy",
        "answer_choices": None,
        "answer_bool": True,
        "hint": "Think about what happens when a US company stores customer data in EU servers — which laws apply?",
        "explanation": "TRUE. Data sovereignty means data is subject to the laws of the country where it physically resides. For example, data stored in EU data centers is subject to GDPR regardless of the company's home country. This has major implications for cloud storage — organizations must know where their data physically resides.",
        "source": SOURCE,
    },

    # ---- 3.4 Resilience and recovery ----
    {
        "objective_code": "3.4",
        "question_text": "An organization maintains a disaster recovery site with full hardware, software, and current data replication that can take over within minutes of a primary site failure. This is called a:",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Cold site", False),
            ("Warm site", False),
            ("Hot site", True),
            ("Geographic dispersion", False),
        ],
        "hint": "The site is fully operational and can take over almost immediately.",
        "explanation": "A hot site is a fully operational duplicate of the primary data center with real-time or near-real-time data replication. Failover can occur in minutes. Cold sites have space/power but no equipment; warm sites have equipment but require installation and data restoration before becoming operational.",
        "source": SOURCE,
    },
    {
        "objective_code": "3.4",
        "question_text": "A company's backup policy requires that no more than 4 hours of transaction data can be lost in a disaster. This requirement defines the:",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("Recovery Time Objective (RTO)", False),
            ("Recovery Point Objective (RPO)", True),
            ("Mean Time to Repair (MTTR)", False),
            ("Mean Time Between Failures (MTBF)", False),
        ],
        "hint": "This measures how much data (measured in time) can be lost, not how long recovery takes.",
        "explanation": "RPO (Recovery Point Objective) defines the maximum acceptable amount of data loss measured in time — the point in the past to which data must be recoverable. A 4-hour RPO means backups must occur at least every 4 hours. RTO defines how long recovery can take. MTTR is average repair time; MTBF is average time between failures.",
        "source": SOURCE,
    },
    {
        "objective_code": "3.4",
        "question_text": "An organization runs a tabletop exercise to test their incident response plan. During the exercise, participants discuss their responses to a ransomware scenario using the documented playbook. What is the PRIMARY purpose of this exercise?",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("To test backup restoration procedures under realistic conditions", False),
            ("To identify gaps in the incident response plan without disrupting production systems", True),
            ("To measure actual RTO and RPO against documented targets", False),
            ("To train new employees on basic security procedures", False),
        ],
        "hint": "A 'tabletop' exercise is discussion-based, not hands-on — it doesn't affect real systems.",
        "explanation": "A tabletop exercise is a discussion-based simulation where participants walk through their response to a hypothetical incident using documented plans. The primary purpose is to identify gaps, ambiguities, and coordination failures in the plan without any real system impact. It doesn't test technical recovery procedures — that requires failover tests or simulations.",
        "source": SOURCE,
    },
]

# ==================================================================
# DOMAIN 4: Security Operations (28%)
# Objectives: 4.1–4.9
# ==================================================================

DOMAIN_4 = [

    # ---- 4.1 Security techniques for computing resources ----
    {
        "objective_code": "4.1",
        "question_text": "An organization establishes a documented configuration standard for all Windows workstations, deploys the configuration via Group Policy, and periodically scans to verify compliance. This process is called:",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("Vulnerability scanning", False),
            ("Secure baseline management", True),
            ("Patch management", False),
            ("Application allow listing", False),
        ],
        "hint": "The three steps: establish, deploy, maintain — these are the exact terms from objective 4.1.",
        "explanation": "Secure baseline management involves establishing a documented secure configuration standard, deploying it consistently, and maintaining it over time through periodic compliance checks. CIS Benchmarks and DISA STIGs are common sources for baseline definitions. It differs from patch management (applying software updates) or vulnerability scanning (identifying weaknesses).",
        "source": SOURCE,
    },
    {
        "objective_code": "4.1",
        "question_text": "A company allows employees to use personal smartphones for corporate email and requires MDM enrollment. The policy permits personal use alongside corporate data on the device. This deployment model is called:",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("COPE (Corporate-Owned, Personally Enabled)", False),
            ("CYOD (Choose Your Own Device)", False),
            ("BYOD (Bring Your Own Device)", True),
            ("COBO (Corporate-Owned, Business-Only)", False),
        ],
        "hint": "The EMPLOYEE owns the device and BRINGS it to use for work.",
        "explanation": "BYOD (Bring Your Own Device) means employees use personally-owned devices for work purposes. Corporate data coexists with personal data. MDM/MAM solutions are used to manage the corporate data container. COPE means the company owns the device but allows personal use; CYOD lets employees choose from an approved list; COBO restricts to business use only.",
        "source": SOURCE,
    },
    {
        "objective_code": "4.1",
        "question_text": "WPA3 improves over WPA2 by implementing Simultaneous Authentication of Equals (SAE). What security improvement does SAE provide?",
        "question_type": "multiple_choice",
        "difficulty": "hard",
        "answer_choices": [
            ("It increases the maximum supported key length to 256 bits", False),
            ("It replaces the pre-shared key with certificate-based authentication", False),
            ("It provides protection against offline dictionary attacks on captured handshakes", True),
            ("It enables faster roaming between access points", False),
        ],
        "hint": "Think about what attackers could do with captured WPA2 4-way handshake packets.",
        "explanation": "WPA3's SAE (Dragonfly handshake) provides forward secrecy and prevents offline dictionary attacks. In WPA2-PSK, an attacker could capture the 4-way handshake and perform offline brute-force against it. SAE's design means even a captured handshake cannot be used for offline guessing — each authentication attempt must occur online, rate-limiting attacks.",
        "source": SOURCE,
    },

    # ---- 4.2 Asset management ----
    {
        "objective_code": "4.2",
        "question_text": "Before disposing of an old server containing sensitive customer data, a company uses specialized software to overwrite all storage sectors multiple times. This process is called:",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Destruction", False),
            ("Certification", False),
            ("Sanitization", True),
            ("Decommissioning", False),
        ],
        "hint": "The data is being securely wiped so it cannot be recovered — the hardware may be reused.",
        "explanation": "Sanitization removes data from storage media so it cannot be recovered, allowing the media to be safely reused or disposed of. Methods include overwriting (software-based), degaussing (magnetic erasure), or cryptographic erasure (deleting the encryption key). Destruction physically destroys the media; decommissioning is the broader process of retiring a system.",
        "source": SOURCE,
    },
    {
        "objective_code": "4.2",
        "question_text": "An IT team discovers servers in the data center that are not in the asset inventory and have no identified owner. Which asset management process failure does this indicate?",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("Improper disposal procedures", False),
            ("Failure in inventory and enumeration", True),
            ("Inadequate data retention policy", False),
            ("Missing acquisition/procurement process", False),
        ],
        "hint": "The problem is that existing assets are not being tracked.",
        "explanation": "An unknown asset represents a failure in inventory/enumeration — the ongoing process of discovering and cataloging all assets. Unknown systems are shadow IT at the infrastructure level: they may be unpatched, misconfigured, and not monitored. Regular network discovery scans and asset inventory reconciliation prevent this.",
        "source": SOURCE,
    },

    # ---- 4.3 Vulnerability management ----
    {
        "objective_code": "4.3",
        "question_text": "A vulnerability scanner reports a critical vulnerability on a system that was patched 6 months ago. The finding is incorrect. This is called a:",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("False negative", False),
            ("False positive", True),
            ("CVE", False),
            ("Zero-day", False),
        ],
        "hint": "The scanner flagged something as a vulnerability when it actually is NOT a vulnerability.",
        "explanation": "A false positive is a vulnerability finding that is reported by a scanner but does not actually exist (the system is not vulnerable). It can occur due to outdated scanner signatures or misidentification of software versions. The opposite, a false negative, is when a real vulnerability exists but the scanner fails to detect it.",
        "source": SOURCE,
    },
    {
        "objective_code": "4.3",
        "question_text": "A security team discovers a critical vulnerability. Before applying a patch, which action BEST determines how urgently the vulnerability must be addressed?",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("Conducting a penetration test against the system", False),
            ("Analyzing CVSS score, exposure factor, and organizational risk tolerance", True),
            ("Immediately isolating all affected systems from the network", False),
            ("Submitting a bug bounty report to the vendor", False),
        ],
        "hint": "Prioritization uses a scoring system and organizational context — not just the vulnerability's raw severity.",
        "explanation": "Vulnerability prioritization considers the CVSS score (technical severity), exposure factor (how likely it is to be exploited in your environment), organizational impact, and risk tolerance. A critical CVSS 9.8 vulnerability on an air-gapped system may be lower priority than a medium CVSS 6.5 on an internet-facing server with no compensating controls.",
        "source": SOURCE,
    },
    {
        "objective_code": "4.3",
        "question_text": "After applying a patch to remediate a vulnerability, which step should be taken to confirm the remediation was successful?",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Conduct a new penetration test", False),
            ("Rescan the system with the vulnerability scanner", True),
            ("Review the system's event logs", False),
            ("Update the risk register", False),
        ],
        "hint": "The most direct way to confirm the patch worked is to run the same test that found the vulnerability.",
        "explanation": "After remediation, rescanning with the vulnerability scanner directly validates that the specific vulnerability is no longer present. This is called 'validation of remediation' in the SY0-701 objectives. A penetration test is broader and more expensive; log review doesn't confirm patch success; the risk register is updated after confirmation.",
        "source": SOURCE,
    },

    # ---- 4.4 Alerting and monitoring ----
    {
        "objective_code": "4.4",
        "question_text": "A security tool collects and aggregates logs from firewalls, IDS, endpoints, and applications, correlates events across sources, and generates alerts for suspicious patterns. This tool is called a:",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Vulnerability scanner", False),
            ("DLP (Data Loss Prevention)", False),
            ("SIEM (Security Information and Event Management)", True),
            ("EDR (Endpoint Detection and Response)", False),
        ],
        "hint": "This tool aggregates logs from many sources and correlates them to find patterns.",
        "explanation": "A SIEM collects, aggregates, and correlates log data from diverse sources across the environment to detect security incidents through rule-based alerts and behavioral analytics. It provides a centralized view of the security posture. EDR focuses on endpoint telemetry; DLP prevents data exfiltration; vulnerability scanners identify weaknesses.",
        "source": SOURCE,
    },
    {
        "objective_code": "4.4",
        "question_text": "A SIEM generates excessive false positive alerts for a legitimate internal application. The security team adjusts the detection rules to reduce noise for this application without disabling monitoring entirely. This process is called:",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("Log aggregation", False),
            ("Alert tuning", True),
            ("Quarantine", False),
            ("Archiving", False),
        ],
        "hint": "The team is refining detection rules to improve their signal-to-noise ratio.",
        "explanation": "Alert tuning adjusts detection rules, thresholds, and whitelists to reduce false positives while maintaining detection capability. A well-tuned SIEM balances sensitivity (catching real threats) with specificity (avoiding false alarms). Alert fatigue from excessive false positives leads analysts to ignore real incidents.",
        "source": SOURCE,
    },
    {
        "objective_code": "4.4",
        "question_text": "NetFlow data captures which aspects of network traffic for security monitoring? (Choose TWO)",
        "question_type": "multi_select",
        "difficulty": "medium",
        "answer_choices": [
            ("Source and destination IP addresses and ports", True),
            ("Full packet payload content", False),
            ("Bytes transferred and flow duration", True),
            ("Encryption keys used in the session", False),
        ],
        "hint": "NetFlow captures metadata about flows, not actual packet content.",
        "explanation": "NetFlow captures flow metadata: source/destination IPs, ports, protocols, byte counts, and duration. It does NOT capture packet content (that requires full packet capture/PCAP). NetFlow is valuable for detecting anomalies like unusual data transfer volumes, port scans, or unexpected connections without the storage cost of full packet capture.",
        "source": SOURCE,
    },

    # ---- 4.5 Enhance security capabilities ----
    {
        "objective_code": "4.5",
        "question_text": "Which email security record, published as a DNS TXT record, specifies which mail servers are authorized to send email on behalf of a domain?",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("DKIM (DomainKeys Identified Mail)", False),
            ("DMARC (Domain-based Message Authentication Reporting and Conformance)", False),
            ("SPF (Sender Policy Framework)", True),
            ("MX record", False),
        ],
        "hint": "This record lists authorized sending IP addresses for the domain.",
        "explanation": "SPF (Sender Policy Framework) is a DNS TXT record listing IP addresses/hosts authorized to send email for a domain. DKIM adds a digital signature to messages (verifying content integrity). DMARC builds on SPF and DKIM to specify policy for failing messages (reject, quarantine, or report). MX records specify mail server locations.",
        "source": SOURCE,
    },
    {
        "objective_code": "4.5",
        "question_text": "A network appliance inspects all HTTP/HTTPS traffic leaving the network, applies content categorization rules, and blocks access to sites in prohibited categories (e.g., malware, adult content). This device is called a:",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Next-Generation Firewall (NGFW)", False),
            ("Web filter / Secure Web Gateway (SWG)", True),
            ("IDS/IPS", False),
            ("Data Loss Prevention (DLP) gateway", False),
        ],
        "hint": "This device specifically filters web (HTTP/HTTPS) traffic based on content categories.",
        "explanation": "A web filter (Secure Web Gateway) inspects outbound web traffic and blocks access based on URL reputation, content category, or policy rules. It protects users from malicious sites and enforces acceptable use policies. An NGFW can include this functionality but web filtering is the primary purpose here; IDS/IPS focuses on attack detection, not content filtering.",
        "source": SOURCE,
    },
    {
        "objective_code": "4.5",
        "question_text": "File Integrity Monitoring (FIM) detects unauthorized changes to critical system files by comparing their current state against a known-good baseline. True or False?",
        "question_type": "true_false",
        "difficulty": "easy",
        "answer_choices": None,
        "answer_bool": True,
        "hint": "FIM 'monitors' the 'integrity' of files by comparing against a baseline.",
        "explanation": "TRUE. FIM tools (like Tripwire, AIDE) calculate cryptographic hashes of critical files at baseline and continuously compare current hashes to detect changes. Unauthorized changes to system binaries, configuration files, or security tools can indicate malware installation, configuration drift, or insider activity.",
        "source": SOURCE,
    },

    # ---- 4.6 Identity and access management ----
    {
        "objective_code": "4.6",
        "question_text": "A user's access rights are automatically adjusted based on their department, job title, and location attributes, without manual rule creation for each specific user. This access control model is called:",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("Role-Based Access Control (RBAC)", False),
            ("Mandatory Access Control (MAC)", False),
            ("Attribute-Based Access Control (ABAC)", True),
            ("Discretionary Access Control (DAC)", False),
        ],
        "hint": "Access is determined by ATTRIBUTES (department, title, location) of the user, not a pre-assigned role.",
        "explanation": "ABAC grants access based on attributes of the user, resource, and environment (time of day, location). This provides the most granular and flexible control but is more complex to implement. RBAC assigns permissions to roles; MAC uses security labels and clearances; DAC lets resource owners control access.",
        "source": SOURCE,
    },
    {
        "objective_code": "4.6",
        "question_text": "A company uses SAML to allow employees to authenticate once to a central identity provider and then access multiple SaaS applications without re-entering credentials. This is an example of:",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("Multi-factor authentication", False),
            ("Federation and Single Sign-On (SSO)", True),
            ("Privileged Access Management", False),
            ("Identity proofing", False),
        ],
        "hint": "One authentication → access to many systems. The IdP and SaaS apps are different organizations.",
        "explanation": "SAML-based SSO with federation allows users to authenticate once to an Identity Provider (IdP) and access multiple Service Providers (SPs) without re-authentication. Federation enables this across organizational boundaries. SAML is the most common protocol for enterprise SSO; OAuth/OIDC is used for web/mobile applications.",
        "source": SOURCE,
    },
    {
        "objective_code": "4.6",
        "question_text": "A privileged access management (PAM) solution grants a system administrator temporary elevated credentials that automatically expire after 1 hour. This capability is called:",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("Password vaulting", False),
            ("Just-in-time (JIT) permissions", True),
            ("Ephemeral credentials", True),  # both are valid
            ("Multi-factor authentication", False),
        ],
        "hint": "The key characteristic is that the elevated access is TEMPORARY and time-limited.",
        "explanation": "Just-in-time (JIT) permissions and ephemeral credentials both describe time-limited elevated access that expires automatically. JIT grants elevated access only when needed and revokes it after the task; ephemeral credentials are short-lived credentials that expire. Both minimize the window of exposure for privileged accounts — a core principle of PAM.",
        "source": SOURCE,
    },

    # ---- 4.7 Automation and orchestration ----
    {
        "objective_code": "4.7",
        "question_text": "A security team uses a SOAR platform to automatically quarantine endpoints, reset compromised credentials, and create tickets when a specific alert fires — all without human intervention. This demonstrates which benefit of automation?",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("Complexity reduction", False),
            ("Improved reaction time and workforce multiplier", True),
            ("Elimination of technical debt", False),
            ("Reduced cost of security tools", False),
        ],
        "hint": "The automation responds faster than a human could and frees analysts for other work.",
        "explanation": "Automation's key security benefits include dramatically improved reaction time (responding in milliseconds vs. minutes for human analysts) and acting as a workforce multiplier (one analyst's playbook serves thousands of events). SOAR platforms are the primary tool for security automation and orchestration.",
        "source": SOURCE,
    },
    {
        "objective_code": "4.7",
        "question_text": "Which of the following is a potential RISK of heavy automation in security operations?",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("Automation always increases false positives", False),
            ("A misconfigured automation creates a single point of failure or causes widespread impact", True),
            ("Automated systems are always more expensive than manual processes", False),
            ("Automation requires more staff to operate than manual processes", False),
        ],
        "hint": "Think about what happens when the automation itself is wrong — and it acts on every single event.",
        "explanation": "A key risk of automation is that a misconfigured or incorrect automation rule creates a single point of failure — if the automation acts on every event and it's wrong, the impact is amplified across all events. Other risks: complexity (harder to troubleshoot), technical debt, and ongoing supportability as environments change.",
        "source": SOURCE,
    },

    # ---- 4.8 Incident response ----
    {
        "objective_code": "4.8",
        "question_text": "During an incident response, a forensic investigator creates a cryptographic hash of a compromised hard drive before analysis. This step supports which digital forensics principle?",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("E-discovery", False),
            ("Legal hold", False),
            ("Chain of custody and integrity preservation", True),
            ("Threat hunting", False),
        ],
        "hint": "The hash proves the evidence hasn't been altered since collection.",
        "explanation": "Creating a cryptographic hash before analysis verifies evidence integrity — if the hash matches after analysis, the data wasn't altered. This supports chain of custody (documenting who handled evidence and when) and is required for evidence to be admissible in legal proceedings. This is the 'acquisition' step in digital forensics.",
        "source": SOURCE,
    },
    {
        "objective_code": "4.8",
        "question_text": "Place the incident response phases in the correct order:",
        "question_type": "ordering",
        "difficulty": "medium",
        "answer_choices": [
            ("Preparation", False),
            ("Detection", False),
            ("Analysis", False),
            ("Containment", False),
            ("Eradication", False),
            ("Recovery", False),
            ("Lessons Learned", False),
        ],
        "ordered_ids": [1, 2, 3, 4, 5, 6, 7],
        "hint": "You can't respond to what you haven't detected. You contain before you eradicate. You always end with lessons learned.",
        "explanation": "The NIST incident response lifecycle: Preparation (build capability before incidents) → Detection (identify that an incident occurred) → Analysis (understand scope and impact) → Containment (limit damage) → Eradication (remove the threat) → Recovery (restore operations) → Lessons Learned (improve processes).",
        "source": SOURCE,
    },
    {
        "objective_code": "4.8",
        "question_text": "A company receives a legal notice requiring them to preserve all emails and documents related to a pending lawsuit. The IT team must ensure this data is not deleted or modified. This requirement is called a:",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Chain of custody", False),
            ("Legal hold", True),
            ("E-discovery", False),
            ("Data retention policy", False),
        ],
        "hint": "This is a legal instruction to preserve evidence — it overrides normal deletion policies.",
        "explanation": "A legal hold (litigation hold) is a directive to preserve all potentially relevant evidence when litigation is anticipated or ongoing. It suspends normal data deletion schedules. E-discovery is the subsequent process of searching, identifying, and collecting the preserved evidence; chain of custody documents how evidence is handled.",
        "source": SOURCE,
    },

    # ---- 4.9 Data sources for investigation ----
    {
        "objective_code": "4.9",
        "question_text": "During an investigation, an analyst needs to see the exact bytes transmitted between a client and a server during a suspected data exfiltration event. Which data source is required?",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("NetFlow data", False),
            ("Firewall logs", False),
            ("Full packet capture (PCAP)", True),
            ("SIEM dashboard", False),
        ],
        "hint": "This data source contains the actual content of network communications, not just metadata.",
        "explanation": "Full packet capture (PCAP) records the complete contents of network packets, including payload data. This is the only data source that lets analysts examine actual data transferred. NetFlow captures only flow metadata (IPs, ports, byte counts); firewall logs capture connection allow/deny events; dashboards aggregate and visualize other data sources.",
        "source": SOURCE,
    },
    {
        "objective_code": "4.9",
        "question_text": "Which log source would be MOST valuable for investigating whether malware used Windows scheduled tasks for persistence?",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("Firewall logs", False),
            ("OS-specific security logs (Windows Event Logs)", True),
            ("Network logs", False),
            ("Application logs", False),
        ],
        "hint": "Scheduled task creation is an OS-level event, not a network event.",
        "explanation": "Windows Event Logs (OS-specific security logs) record system events including scheduled task creation (Event ID 4698), process creation, logon events, and registry changes. These are critical for detecting persistence mechanisms. Firewall logs show network connections; scheduled task investigation requires OS-level telemetry.",
        "source": SOURCE,
    },
]

# ==================================================================
# DOMAIN 5: Security Program Management and Oversight (20%)
# Objectives: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6
# ==================================================================

DOMAIN_5 = [

    # ---- 5.1 Security governance ----
    {
        "objective_code": "5.1",
        "question_text": "A document that defines acceptable and unacceptable uses of company computing resources by employees is called a(n):",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Information security policy", False),
            ("Acceptable Use Policy (AUP)", True),
            ("Business continuity plan", False),
            ("Change management procedure", False),
        ],
        "hint": "This policy specifically governs how employees may USE company technology.",
        "explanation": "An Acceptable Use Policy (AUP) defines what employees may and may not do with company technology resources — acceptable uses of the internet, email, devices, etc. It forms the foundation for disciplinary action when employees misuse resources and establishes the legal basis for monitoring. All employees typically must acknowledge it.",
        "source": SOURCE,
    },
    {
        "objective_code": "5.1",
        "question_text": "Who is responsible for classifying data and defining the security requirements for a specific dataset within an organization?",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("Data custodian/steward", False),
            ("Data processor", False),
            ("Data owner", True),
            ("Data controller", False),
        ],
        "hint": "This is the person who OWNS the data and is accountable for it — typically a business manager.",
        "explanation": "The data owner is the business unit or individual responsible for a dataset — they classify the data and define access requirements. The data custodian/steward implements the technical controls. A data processor processes data on behalf of a controller; a controller (GDPR term) determines purposes and means of processing.",
        "source": SOURCE,
    },
    {
        "objective_code": "5.1",
        "question_text": "Which governance structure type makes security decisions through consensus among a group of stakeholders rather than through a single authority?",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("Centralized governance", False),
            ("Decentralized governance", True),
            ("Committee-based governance", False),
            ("Board-level governance", False),
        ],
        "hint": "The opposite of centralized control — decisions are distributed.",
        "explanation": "Decentralized governance distributes security decision-making authority across multiple business units or regions rather than concentrating it in a single authority. This can improve agility and local adaptation but may result in inconsistent policies. Centralized governance provides consistency but can be slower to respond to local needs.",
        "source": SOURCE,
    },

    # ---- 5.2 Risk management ----
    {
        "objective_code": "5.2",
        "question_text": "An organization calculates that a server rack has a 10% chance of flooding annually (ARO = 0.1) and that flooding would cause $200,000 in damage (SLE = $200,000). What is the Annualized Loss Expectancy (ALE)?",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("$2,000,000", False),
            ("$200,000", False),
            ("$20,000", True),
            ("$2,000", False),
        ],
        "hint": "ALE = SLE × ARO. Multiply the single-event loss by the annual frequency.",
        "explanation": "ALE = SLE × ARO = $200,000 × 0.1 = $20,000. This means the expected annual cost of flood damage is $20,000. ALE is used to determine whether a control is cost-effective: if a flood prevention control costs less than $20,000/year, it's financially justified.",
        "source": SOURCE,
    },
    {
        "objective_code": "5.2",
        "question_text": "A company decides to purchase cyber liability insurance to offset the financial impact of a potential data breach. Which risk management strategy does this represent?",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Risk avoidance", False),
            ("Risk mitigation", False),
            ("Risk transfer", True),
            ("Risk acceptance", False),
        ],
        "hint": "The risk still exists — but a third party (the insurer) bears the financial consequences.",
        "explanation": "Risk transfer shifts the financial impact of a risk to a third party — typically through insurance or contractual indemnification. The risk itself isn't eliminated (a breach can still occur), but the financial burden is shared. Risk avoidance eliminates the activity; mitigation reduces likelihood/impact; acceptance acknowledges the risk without action.",
        "source": SOURCE,
    },
    {
        "objective_code": "5.2",
        "question_text": "Which of the following BEST describes the difference between risk tolerance and risk appetite?",
        "question_type": "multiple_choice",
        "difficulty": "hard",
        "answer_choices": [
            ("They are synonymous terms used interchangeably in risk management", False),
            ("Risk appetite is the strategic level of risk an organization is willing to accept; risk tolerance is the acceptable variation around that threshold", True),
            ("Risk tolerance applies to individual risks; risk appetite applies to regulatory requirements", False),
            ("Risk appetite is quantitative; risk tolerance is qualitative", False),
        ],
        "hint": "Appetite is the strategic 'how much risk are we willing to take'; tolerance is 'how far can we deviate from that'.",
        "explanation": "Risk appetite is the organization's strategic, high-level statement of how much risk it is willing to accept in pursuit of objectives. Risk tolerance is the acceptable deviation from risk appetite — the operational boundaries. For example, appetite: 'we accept moderate cyber risk'; tolerance: 'we will not accept any risk of regulatory non-compliance.'",
        "source": SOURCE,
    },

    # ---- 5.3 Third-party risk ----
    {
        "objective_code": "5.3",
        "question_text": "A contract clause that gives a company the right to examine a vendor's security controls, audit logs, and compliance documentation is called a:",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("Non-disclosure agreement (NDA)", False),
            ("Right-to-audit clause", True),
            ("Memorandum of Understanding (MOU)", False),
            ("Service-level agreement (SLA)", False),
        ],
        "hint": "This clause specifically grants the customer the right to examine the vendor's practices.",
        "explanation": "A right-to-audit clause in a vendor contract explicitly grants the customer the right to examine the vendor's security controls, audit logs, and compliance posture. It is a critical third-party risk management tool because it provides accountability and verification that the vendor is meeting their security obligations.",
        "source": SOURCE,
    },
    {
        "objective_code": "5.3",
        "question_text": "Which agreement type defines the performance metrics and penalties that apply when a service provider fails to meet specified service levels?",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Memorandum of Agreement (MOA)", False),
            ("Non-disclosure Agreement (NDA)", False),
            ("Service-Level Agreement (SLA)", True),
            ("Business Partners Agreement (BPA)", False),
        ],
        "hint": "This agreement specifically measures service quality and defines remedies for underperformance.",
        "explanation": "A Service-Level Agreement (SLA) defines specific measurable metrics (uptime %, response times, support hours) and the consequences (credits, penalties) when the provider fails to meet them. MOAs establish mutual obligations; NDAs protect confidential information; BPAs govern the overall partner relationship.",
        "source": SOURCE,
    },

    # ---- 5.4 Compliance ----
    {
        "objective_code": "5.4",
        "question_text": "A company that processes payment card data must comply with which industry standard that defines security requirements for cardholder data protection?",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("GDPR", False),
            ("HIPAA", False),
            ("PCI DSS", True),
            ("SOC 2", False),
        ],
        "hint": "This standard was created by the major credit card companies specifically for payment card security.",
        "explanation": "PCI DSS (Payment Card Industry Data Security Standard) is a set of security requirements for organizations that process, store, or transmit payment card data. It was created by the PCI Security Standards Council (Visa, Mastercard, Amex, Discover, JCB). GDPR covers personal data privacy; HIPAA covers healthcare data; SOC 2 covers service organization controls.",
        "source": SOURCE,
    },
    {
        "objective_code": "5.4",
        "question_text": "The 'right to be forgotten' (right to erasure) is a privacy right provided by which regulation?",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("HIPAA", False),
            ("PCI DSS", False),
            ("GDPR", True),
            ("FISMA", False),
        ],
        "hint": "This regulation applies to EU residents and their personal data.",
        "explanation": "The GDPR (General Data Protection Regulation) grants EU data subjects the right to erasure ('right to be forgotten') — the ability to request that an organization delete their personal data under certain circumstances. HIPAA governs US healthcare data; PCI DSS governs payment cards; FISMA governs US federal agency information security.",
        "source": SOURCE,
    },

    # ---- 5.5 Audits and assessments ----
    {
        "objective_code": "5.5",
        "question_text": "A penetration test conducted with NO prior knowledge of the target's systems, network, or defenses — simulating an external attacker — is called a:",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Known environment test (white box)", False),
            ("Partially known environment test (gray box)", False),
            ("Unknown environment test (black box)", True),
            ("Passive reconnaissance", False),
        ],
        "hint": "The tester starts with zero internal knowledge, just like a real attacker would.",
        "explanation": "An unknown environment (black box) test gives the pen tester no prior information about the target — no network diagrams, no credentials, no source code. This most closely simulates a real external attacker. Known environment (white box) gives full access; partially known (gray box) gives limited information like an authenticated user would have.",
        "source": SOURCE,
    },
    {
        "objective_code": "5.5",
        "question_text": "Which reconnaissance technique gathers publicly available information about a target without directly interacting with the target's systems?",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Active reconnaissance", False),
            ("Port scanning", False),
            ("Passive reconnaissance", True),
            ("Vulnerability scanning", False),
        ],
        "hint": "This technique uses publicly available sources — OSINT, social media, WHOIS — without touching the target.",
        "explanation": "Passive reconnaissance gathers information from publicly available sources (WHOIS, DNS records, social media, job postings, search engines) without directly probing the target's systems. It is undetectable by the target. Active reconnaissance directly probes systems (port scans, banner grabbing) and may trigger intrusion detection.",
        "source": SOURCE,
    },

    # ---- 5.6 Security awareness ----
    {
        "objective_code": "5.6",
        "question_text": "A security team sends simulated phishing emails to employees and tracks click rates. Employees who click are redirected to a training page. This is an example of which security awareness technique?",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Social engineering assessment", False),
            ("Phishing simulation campaign", True),
            ("Tabletop exercise", False),
            ("User behavior analytics", False),
        ],
        "hint": "The team is running fake phishing emails to test and train employees.",
        "explanation": "A phishing simulation campaign sends realistic-looking fake phishing emails to measure employee susceptibility and provide immediate, teachable-moment training for those who click. It is the most effective form of security awareness training for phishing because it combines testing with just-in-time education.",
        "source": SOURCE,
    },
    {
        "objective_code": "5.6",
        "question_text": "An employee notices a USB drive in the company parking lot and plugs it into their workstation out of curiosity. Which security awareness concept should have prevented this action?",
        "question_type": "multiple_choice",
        "difficulty": "easy",
        "answer_choices": [
            ("Password management training", False),
            ("Removable media and physical security awareness", True),
            ("Insider threat awareness", False),
            ("Hybrid work environment training", False),
        ],
        "hint": "The risky behavior involves a physical object (USB) and curiosity about found items.",
        "explanation": "Security awareness training on removable media covers the risks of found/unknown USB drives ('USB drop attacks' / 'baiting'). Employees should be trained never to plug in unknown media. This is a well-documented attack technique — the attacker drops malware-loaded USB drives near the target organization and relies on human curiosity.",
        "source": SOURCE,
    },
    {
        "objective_code": "5.6",
        "question_text": "Which of the following BEST describes anomalous behavior recognition in the context of security awareness?",
        "question_type": "multiple_choice",
        "difficulty": "medium",
        "answer_choices": [
            ("Using automated tools to detect unusual network traffic patterns", False),
            ("Training employees to recognize and report unusual, risky, or unexpected behavior by colleagues or systems", True),
            ("Configuring SIEM rules to detect user behavior anomalies", False),
            ("Conducting background checks on new employees", False),
        ],
        "hint": "In the context of security AWARENESS (not tools), this is about training humans to notice things.",
        "explanation": "In security awareness training, anomalous behavior recognition means training employees to notice and report unusual behaviors — a colleague accessing systems at odd hours, printing large volumes of sensitive data, or suddenly being unable to access their own files (ransomware). This is the human layer of insider threat and incident detection.",
        "source": SOURCE,
    },
]

# ==================================================================
# CSV GENERATION
# ==================================================================

FIELDNAMES = [
    "objective_code", "question_text", "question_type", "difficulty",
    "answer_choices_json", "correct_answer_key_json", "hint", "explanation", "source"
]

DOMAINS = {
    "domain_1_general_security": DOMAIN_1,
    "domain_2_threats_vulnerabilities": DOMAIN_2,
    "domain_3_security_architecture": DOMAIN_3,
    "domain_4_security_operations": DOMAIN_4,
    "domain_5_program_management": DOMAIN_5,
}

def build_row(q):
    if q["question_type"] == "true_false":
        choices, answer_key = tf(q["answer_bool"])
    elif q["question_type"] == "ordering":
        choices = mc([(c, False) for c, _ in enumerate(q["answer_choices"])])
        # rebuild choices properly for ordering
        choices = [{"id": i+1, "text": t, "order": i+1} for i, (t, _) in enumerate(q["answer_choices"])]
        answer_key = {"ordered_ids": q["ordered_ids"]}
    else:
        choices = mc(q["answer_choices"])
        answer_key = correct_mc(q["answer_choices"])
        # multi_select with answer_bool for JIT/ephemeral edge case: both correct
        if q["question_type"] == "multi_select" and len(answer_key["correct_ids"]) == 1:
            # re-check
            answer_key = correct_mc(q["answer_choices"])

    return {
        "objective_code": q["objective_code"],
        "question_text": q["question_text"],
        "question_type": q["question_type"],
        "difficulty": q["difficulty"],
        "answer_choices_json": json.dumps(choices),
        "correct_answer_key_json": json.dumps(answer_key),
        "hint": q.get("hint", ""),
        "explanation": q["explanation"],
        "source": q["source"],
    }

for filename, questions in DOMAINS.items():
    path = os.path.join(OUTPUT_DIR, f"{filename}.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for q in questions:
            writer.writerow(build_row(q))
    print(f"Wrote {len(questions):3d} questions -> {filename}.csv")

print(f"\nTotal: {sum(len(v) for v in DOMAINS.values())} questions across 5 domains")
