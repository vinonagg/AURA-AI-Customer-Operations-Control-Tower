# Security Notes

This repository is a portfolio/demo application and must not be deployed with real customer data without an enterprise security review.

## Current controls
- Pydantic request validation
- No API key committed to source
- `.env` excluded from Git
- Human approval boundary
- Audit events
- Evidence-constrained prompts
- Deterministic fallback mode

## Required enterprise controls
- OIDC/SSO and RBAC
- Secret manager
- PII detection/redaction
- Encryption and key management
- Centralized audit logging
- Network controls
- Rate limiting
- Dependency/SAST scanning
- Threat modeling and penetration testing
- Data retention/deletion policy
