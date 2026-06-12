# Incident Response Policy

doc_type: policy
last_updated: 2026-03-30

## Severity rules

SEV1:
- Major customer-facing outage.
- Revenue-impacting checkout or payment failure.
- Error rate above 10% for critical APIs.

SEV2:
- Partial degradation.
- Error rate between 3% and 10% for critical APIs.
- Workaround exists.

SEV3:
- Minor issue.
- Internal-only impact.
- No immediate customer impact.

## Communication rules

For SEV1:
- Create incident channel.
- Assign incident commander.
- Post update every 15 minutes.
- Prioritize mitigation over perfect root cause analysis.

For SEV2:
- Assign owner.
- Post update every 30 minutes.
- Continue investigation and mitigation in parallel.