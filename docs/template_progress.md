# Template Library Progress

## 1. async-webhook-ledger

Status: golden.

Coverage:
- backend reliability
- idempotency
- queue redelivery
- Postgres ledger state
- LocalStack SQS
- WireMock provider behavior
- Docker-backed expected starter failure in CI

## 2. rag-retrieval-quality-lab

Status: golden-template-candidate.

Coverage:
- AI backend retrieval quality
- tenant isolation
- ACL filtering
- freshness ranking
- grounded citations
- Qdrant vector search
- Postgres metadata and eval results
- MinIO document storage
- fake deterministic embedding API

## 3. gpu-fault-correlation-drain-scheduler

Status: golden-template-candidate.

Coverage:
- ML infrastructure fault correlation
- synthetic GPU metrics
- NCCL log correlation
- InfiniBand counter correlation
- Slurm-aware drain scheduling
- thermal and missing telemetry handling
- idempotent drain decisions
- Docker-backed GPU cluster simulator

Acceptance:
- solution passes public and hidden tests
- unsolved candidate fails public tests for known expected reasons
- Docker-backed public integration expected failure is validated locally and remotely
- rendered candidate main contains no private material
## Machine-Readable Contract Migration

- machine_readable_manifest: present
- root_make_aliases: present
- render_context_support: present
- check_render_contract: present
- scan_safety_uses_manifest: present
- remote_ci_manifest_validation: passed

