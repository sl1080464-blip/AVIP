# Face Detection and Face Identification

## Separation of concerns

Face detection and face identification must remain strictly separate. A face crop discovered in a frame should not automatically imply a known identity.

## Governance requirements

- explicit consent or lawful basis before any identification workflow is enabled
- access control and least-privilege authorization
- encryption of stored biometric data and metadata
- retention limits and deletion workflows
- audit logging for all identification actions
- human review before making material security decisions

## Architecture note

The platform should define two independent service boundaries:

- `Face Detection`: find and classify visible faces
- `Face Identification`: match a detected face against a restricted, consented identity dataset

The second capability should not be introduced as a default path in this initial phase.
