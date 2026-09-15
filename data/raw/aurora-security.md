# Aurora Cloud Platform - Security and Compliance

## Encryption

All data is encrypted at rest with AES-256 and in transit with TLS 1.3.
Encryption keys are managed by Aurora by default. Customers on the Business and
Enterprise plans can bring their own keys (BYOK) using a customer-managed KMS key.

## Access control

Single sign-on (SSO) via SAML 2.0 and OpenID Connect is available on the Team plan and
above. Multi-factor authentication (MFA) is mandatory for all administrator accounts
on every plan.

## Compliance

- SOC 2 Type II certified since 2022.
- ISO/IEC 27001 certified since 2021.
- GDPR compliant, with a Data Processing Agreement available on request.

## Audit logging

Every API call is recorded in an immutable audit log. Audit logs are retained for 365
days on the Business plan and 730 days on the Enterprise plan.
