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

