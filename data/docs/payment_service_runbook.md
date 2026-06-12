# Payment Service Runbook

service: payment-service
owner: payments-platform-team
last_updated: 2026-04-18
doc_type: runbook

## Common incident: downstream payment failures

Symptoms:
- Checkout API reports payment authorization failures.
- payment-service health endpoint may still return healthy.
- Logs may show provider timeout, invalid merchant key, or gateway rejected errors.

Most likely causes:
1. Payment gateway timeout.
2. Invalid or expired merchant credentials.
3. Rate limit from payment provider.
4. Network path issue between checkout-api and payment-service.

Recommended triage steps:
1. Check payment-service latency and error rate.
2. Search payment-service logs for gateway_timeout, invalid_merchant_key, and provider_rate_limit.
3. Confirm gateway credentials were not rotated recently.
4. If only checkout-api is failing but payment-service is healthy, check checkout-api configuration first.