from django.core.management.base import BaseCommand
from questions.models import Domain, Objective

DOMAINS = [
    {
        'number': 1,
        'name': 'General Security Concepts',
        'weight_pct': '12.00',
        'objectives': [
            ('1.1', 'Compare and contrast various types of security controls'),
            ('1.2', 'Summarize fundamental security concepts'),
            ('1.3', 'Explain the importance of change management processes and the impact to security'),
            ('1.4', 'Explain the importance of using appropriate cryptographic solutions'),
        ],
    },
    {
        'number': 2,
        'name': 'Threats, Vulnerabilities, and Mitigations',
        'weight_pct': '22.00',
        'objectives': [
            ('2.1', 'Compare and contrast common threat actors and motivations'),
            ('2.2', 'Explain common threat vectors and attack surfaces'),
            ('2.3', 'Explain various types of vulnerabilities'),
            ('2.4', 'Given a scenario, analyze indicators of malicious activity'),
            ('2.5', 'Explain the purpose of mitigation techniques used to secure the enterprise'),
        ],
    },
    {
        'number': 3,
        'name': 'Security Architecture',
        'weight_pct': '18.00',
        'objectives': [
            ('3.1', 'Compare and contrast security implications of different architecture models'),
            ('3.2', 'Given a scenario, apply security principles to secure enterprise infrastructure'),
            ('3.3', 'Compare and contrast concepts and strategies to protect data'),
            ('3.4', 'Explain the importance of resilience and recovery in security architecture'),
        ],
    },
    {
        'number': 4,
        'name': 'Security Operations',
        'weight_pct': '28.00',
        'objectives': [
            ('4.1', 'Given a scenario, apply common security techniques to computing resources'),
            ('4.2', 'Explain the security implications of proper hardware, software, and data asset management'),
            ('4.3', 'Explain various activities associated with vulnerability management'),
            ('4.4', 'Explain security alerting and monitoring concepts and tools'),
            ('4.5', 'Given a scenario, modify enterprise capabilities to enhance security'),
            ('4.6', 'Given a scenario, implement and maintain identity and access management'),
            ('4.7', 'Explain the importance of automation and orchestration related to secure operations'),
            ('4.8', 'Explain appropriate incident response activities'),
            ('4.9', 'Given a scenario, use data sources to support an investigation'),
        ],
    },
    {
        'number': 5,
        'name': 'Security Program Management and Oversight',
        'weight_pct': '20.00',
        'objectives': [
            ('5.1', 'Summarize elements of effective security governance'),
            ('5.2', 'Explain elements of the risk management process'),
            ('5.3', 'Explain the processes associated with third-party risk assessment and management'),
            ('5.4', 'Summarize elements of effective security compliance'),
            ('5.5', 'Explain types and purposes of audits and assessments'),
            ('5.6', 'Given a scenario, implement security awareness practices'),
        ],
    },
]


class Command(BaseCommand):
    help = 'Seed SY0-701 domains and objectives (idempotent — safe to re-run)'

    def handle(self, *args, **options):
        domains_created = objectives_created = 0

        for d in DOMAINS:
            domain, created = Domain.objects.get_or_create(
                number=d['number'],
                defaults={'name': d['name'], 'weight_pct': d['weight_pct']},
            )
            if created:
                domains_created += 1
            else:
                # Update name/weight in case they changed
                Domain.objects.filter(pk=domain.pk).update(name=d['name'], weight_pct=d['weight_pct'])

            for code, title in d['objectives']:
                _, created = Objective.objects.get_or_create(
                    code=code,
                    defaults={'domain': domain, 'title': title},
                )
                if created:
                    objectives_created += 1

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {domains_created} new domains, {objectives_created} new objectives '
            f'({Domain.objects.count()} domains, {Objective.objects.count()} objectives total)'
        ))
