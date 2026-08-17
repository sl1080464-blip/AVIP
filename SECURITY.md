# Security Policy

## Reporting vulnerabilities

Please report security concerns privately through the repository maintainers or the designated security contact. Do not disclose details in public issues until a fix is available.

## Secret handling

- never commit API keys, tokens, raw credentials, or `.env` files
- use environment variables and CI secret stores
- rotate any exposed credentials immediately

## Authentication and authorization

AVIP will separate authentication from video analytics logic. Access control must be enforced before any camera or alert action is exposed through the API.

## Audit and privacy

- log administrative actions
- restrict access to sensitive stream metadata
- keep retention policies explicit and minimal
- separate face detection from face identification workflows
- use encryption for sensitive stored data and in transit where applicable

## Data protection

Video streams and derived event metadata can be sensitive. Minimal retention, access review, and strong policy separation are required before any production deployment.
