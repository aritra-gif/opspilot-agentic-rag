# Checkout API Runbook

service: checkout-api
owner: payments-platform-team
last_updated: 2026-05-01
doc_type: runbook

## Common incident: 500 errors after deployment

Symptoms:
- POST /checkout/complete returns HTTP 500.
- Error rate increases immediately after a new deployment.
- Customers report failed checkout attempts.
- Logs may show missing environment variables or failed calls to payment-service.

Most likely causes:
1. PAYMENT_SERVICE_URL is missing or incorrectly configured.
2. Database migration was not applied before the application release.
3. Checkout API is calling an incompatible payment-service version.
4. Feature flag CHECKOUT_V2_ENABLED was enabled without required config.

Recommended triage steps:
1. Check recent deployment version for checkout-api.
2. Search logs for PAYMENT_SERVICE_URL, connection refused, timeout, and migration errors.
3. Verify payment-service health.
4. Compare current environment variables with the last stable release.
5. If customer impact is high and root cause is unclear, rollback checkout-api to the last stable version.

Rollback guidance:
- Rollback is recommended when error rate remains above 5% for more than 10 minutes.
- Use the last known stable artifact.
- After rollback, verify checkout success rate and payment authorization logs.