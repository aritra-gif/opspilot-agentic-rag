# Deployment Troubleshooting Guide

doc_type: guide
last_updated: 2026-05-10

## Incidents immediately after deployment

When an incident starts within 15 minutes of a deployment, first suspect release-related causes.

Common causes:
- Missing environment variables.
- Secret not mounted.
- Database migration mismatch.
- Incompatible service version.
- Bad feature flag rollout.
- Incorrect container image tag.

Recommended investigation order:
1. Identify the exact deployment timestamp.
2. Compare the new version with the last stable version.
3. Check logs from the first failing pod.
4. Check whether config, secrets, or migrations changed.
5. Verify dependencies are healthy.
6. Roll back when customer impact is high and no safe fix is available.

## Strong rollback signal

Rollback should be considered when:
- The incident started right after deployment.
- Error rate is high.
- The previous version was stable.
- The root cause is not confirmed quickly.