# Pharma compliance design (architecture support — not certification)

- RBAC/ABAC least privilege, MFA + SSO (production IdP)
- Append-only hash-chained audit trail (`core/audit.py`); ship to immutable store
- E-signatures for approvals/releases (`esign()`); versioned specs/formulations
- SoD: requester ≠ approver; approval matrices by amount/type (`core/workflow.py`)
- Encryption in transit/at rest (TLS, RDS/S3 KMS), secrets manager, tenant isolation
- Backup/DR/retention per deployment; validation-ready SDLC (reqs → risk → tests → release)
- Design with 21 CFR Part 11 / GxP electronic-record controls in mind; qualify per geography/use.
