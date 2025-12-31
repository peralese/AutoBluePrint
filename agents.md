# AGENTS.md – AutoBlueprint

## Purpose

AutoBlueprint is a proof-of-concept migration automation tool that:

1. Ingests OSQuery discovery data from Linux and Windows hosts
2. Normalizes and classifies meaningful software components using LLMs
3. Extracts host specifications (OS, CPU, RAM, architecture)
4. Generates infrastructure-as-code (CloudFormation first) to re-provision workloads in AWS
5. Preserves explainability, evidence, and human-in-the-loop control

This file defines **canonical intent, data models, and guardrails** for all AI-assisted changes in this repository.

---

## Core Design Principles

- Deterministic outputs over “clever” inference
- Evidence-backed decisions only
- Human approval at execution boundaries
- Cloud re-hosting first (no implicit modernization)
- One workload = one canonical record

---

## Canonical Artifact: `workload.json`

All pipelines MUST converge on a single canonical artifact per workload:

This file is the **system of record** between:
- raw discovery inputs
- AI classification
- infrastructure generation
- validation and reporting

Downstream generators (CloudFormation, Terraform) MUST consume `workload.json`, not raw OSQuery output.

---

## `workload.json` (v0) – Required Sections

### 1. Metadata & Provenance
- schema_version
- workload_id
- generation timestamp
- input file references (OSQuery tables, hashes)
- LLM provider/model + prompt hash (if used)

### 2. Host Specification
- hostname
- OS family / name / version
- CPU (logical cores)
- memory (MB)
- architecture

### 3. Software Components
Each detected component MUST include:
- component_id
- type (runtime, middleware, database, app_server, utility)
- name + version (if known)
- confidence score (0.0–1.0)
- evidence[] (see below)

### 4. Sizing Recommendation
- recommended instance family / size / type
- basis (rules used, host specs)
- confidence

### 5. IaC Intent
- target platform (aws)
- generator (cloudformation)
- migration strategy (rehost)
- allowed resource types
- blocked resource types

### 6. Open Questions (Optional)
- missing data required for safe deployment
- items that require human clarification

---

## Evidence & Confidence Rules (Non-Negotiable)

- No infrastructure MAY be generated from LLM-only inference.
- Every component MUST record its evidence sources.
- Evidence types may include:
  - osquery_record
  - file_presence
  - running_process
  - llm_classification
- Confidence MUST be reduced when:
  - evidence is single-source
  - evidence is inferential
  - version info is missing
- Low-confidence components should be recorded but excluded from IaC generation.

---

## Execution Boundaries

Autonomous actions allowed:
- Parsing discovery data
- Normalizing inventories
- Generating draft IaC
- Generating reports and summaries

Actions requiring explicit human approval:
- CloudFormation deployment
- Network exposure decisions
- Database provisioning
- Production cutovers

---

## Code Structure Expectations

- Mapping logic produces `workload.json` first
- IaC generators consume only `workload.json`
- LLM usage must be isolated, replaceable, and logged
- New generators (Terraform, Bicep) should reuse the same canonical model

---

## Versioning

- `workload.json` schema MUST include `schema_version`
- Breaking changes require version bump
- Older schema versions should remain readable

---

## Agent Instructions

When modifying this repo:
1. Read this file first
2. Preserve existing behavior unless explicitly instructed
3. Favor additive, minimal refactors
4. Do not remove human-in-the-loop controls
5. Explain why any confidence or inference rule is changed


