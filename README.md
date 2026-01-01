# 🤖 AutoBlueprint: Agentic AI-Powered CloudFormation Generator  
**(Middleware Mode → Canonical Workload Model)**

**AutoBlueprint** is a proof-of-concept migration automation tool that ingests **OSQuery discovery data**, uses **LLM-assisted classification** to identify meaningful software components (runtimes, middleware, databases), and produces a **canonical `workload.json` artifact** that represents *everything known about a workload at a specific point in time*.  

That canonical model is then used to generate a **ready-to-deploy AWS CloudFormation template** to re-provision the workload in the cloud.

AutoBlueprint is intentionally designed to be **auditable, explainable, and human-in-the-loop**, serving as the foundation for a broader agentic migration workflow.

---

## 🎯 Project Goals

- Treat migration as a **pipeline**, not a one-off script
- Normalize noisy discovery data into a **single source of truth**
- Preserve **evidence, confidence, and provenance** for every decision
- Enable **repeatable, deterministic infrastructure generation**
- Lay groundwork for future:
  - Terraform support
  - Validation agents
  - Multi-source enrichment (CMDB, interviews, ServiceNow)

---

## ✅ Current Capabilities

- 🧠 **AI-Assisted Software Classification**
- 🧹 **Discovery Noise Reduction**
- 🧾 **Canonical `workload.json` Generation**
- 🏗️ **CloudFormation Template Generation**
- ⚙️ **Instance Sizing Heuristics**
- 🚀 **Optional Deployment Helper**
- 🔁 **CI/CD Friendly**

---

## 🧠 Canonical Artifact: `workload.json`

`workload.json` is the **system of record** for AutoBlueprint.

It captures:
- All known facts at generation time
- Inferred vs confirmed data
- Evidence and confidence per field
- The exact input used for infrastructure generation

---

## 📦 Repository Structure

```
autoblueprint/
├── main.py
├── mapper.py
├── workload.py
├── cleaner/
│   └── classify.py
├── generator/
│   └── cloudformation.py
├── templates/
│   └── cloudformation_template.j2
├── input/
│   └── discovery.json
├── output/
│   └── <timestamp>/
│       ├── workload.json
│       └── autoblueprint_template.yaml
├── deploy.py
├── AGENTS.md
├── .env
├── .gitignore
├── .gitlab-ci.yml
└── README.md
```

---

## 🚀 Quick Start

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Configure Environment Variables
```env
OPENAI_API_KEY=sk-xxxxxxxx
GPT_MODEL=gpt-3.5-turbo
AWS_REGION=us-east-1
STACK_NAME=autoblueprint-stack
```

### Run
```bash
python main.py
```

### Optional Deploy
```bash
python deploy.py
```

---

## 🛣️ Roadmap

### Initial MVP (Completed)
- OSQuery discovery ingestion
- GPT-based middleware classification
- CloudFormation generation
- Deployment helper + CI

### Agentic Roadmap (Current Direction)

**Phase A – Canonical Model**
- workload.json as system of record
- Evidence & confidence tracking

**Phase B – Enrichment**
- CMDB, interviews, ServiceNow

**Phase C – Generators**
- Terraform, validation, analysis

**Phase D – Orchestration**
- State tracking, approval gates

**Phase E – Extensibility**
- Plugin architecture, optional UI

---

## 👨‍💻 Author

Erick Perales  
Cloud Migration Architect · AI Automation Advocate  
https://github.com/peralese
