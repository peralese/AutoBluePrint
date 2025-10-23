# 🤖 AutoBlueprint: Agentic AI-Powered CloudFormation Generator (Middleware Mode)

**AutoBlueprint** is a proof-of-concept tool that analyzes OSQuery discovery data, uses GPT to classify useful software components (runtimes, middleware, databases), and generates a ready-to-deploy **CloudFormation template** to re-provision the workload in AWS.

---

## ✅ Features

- 🧠 **AI-Powered Middleware Detection**
- 🧹 **Noise Reduction**
- 🏗️ **CloudFormation Template Generator**
- ⚙️ **GitLab Runner Integration for CI/CD Deployment**
- 📄 **Input Flexibility**

---

## 📦 Folder Structure

```
autoblueprint/
├── main.py
├── mapper.py
├── cleaner/
│   └── classify.py
├── generator/
│   └── cloudformation.py
├── templates/
│   └── cloudformation_template.j2
├── input/
│   ├── programs.json
│   └── os_version.json  # Optional
├── output/
│   └── <timestamp>/
│       └── autoblueprint_template.yaml
├── deploy.py
├── .env
├── .gitignore
├── .gitlab-ci.yml
└── README.md
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables in `.env`
```env
OPENAI_API_KEY=sk-xxxxxxxx
GPT_MODEL=gpt-3.5-turbo

# Deployment options
AWS_REGION=us-east-1
STACK_NAME=autoblueprint-stack
```

### 3. Run AutoBlueprint Manually
```bash
python main.py
python deploy.py  # Optional: deploy the latest template to AWS
```

---

## ⚙️ GitLab CI/CD Integration

### `.gitlab-ci.yml`

```yaml
stages:
  - classify
  - deploy

before_script:
  - pip install -r requirements.txt

classify:
  stage: classify
  script:
    - python main.py

deploy:
  stage: deploy
  script:
    - python deploy.py
  only:
    - main
```

### GitLab CI/CD Variables Required

| Variable                | Description                 |
|-------------------------|-----------------------------|
| `OPENAI_API_KEY`        | OpenAI key for GPT access   |
| `AWS_ACCESS_KEY_ID`     | IAM access key              |
| `AWS_SECRET_ACCESS_KEY` | IAM secret key              |
| `AWS_REGION`            | AWS region (e.g., us-east-1)|
| `STACK_NAME`            | CloudFormation stack name   |

---

## 🧠 Prompt Used for Classification

> “You are an AI assistant that classifies software discovered via OSQuery. Remove system drivers, utilities, and irrelevant components. Return only runtimes, middleware, databases, or app servers. Tag each entry with one of: 'runtime', 'middleware', 'database', 'app_server'. Return a valid JSON array.”

---

## 🛣️ Roadmap

### Phase 1 – MVP Middleware Mode ✅
- Discovery via OSQuery JSON
- GPT-based middleware tagging
- Generate CloudFormation template

### Phase 2 – Deployment Integration ✅
- Add deploy.py with boto3 CloudFormation support
- GitLab CI automation via `.gitlab-ci.yml`

### Phase 3 – Next
- Use os_version.json to auto-select AMIs
- Merge with server-mode logic (mapper.py)
- Generate `user_data` install scripts for middleware
- Full boto3-based EC2 provisioning
- Optional: Flask UI

---

## 👨‍💻 Author

Erick Perales  
Cloud Migration Architect, AI Automation Advocate
<https://github.com/peralese>
---

## MVP Usage

### Package and Upload Data to S3
- Create a manifest based on data_manifest.json.example (Linux example includes /var/www/html).
`ash
cp data_manifest.json.example data_manifest.json
# Edit include/exclude paths as needed
python packager.py --manifest data_manifest.json --bucket <your-bucket> --key demo/site.zip
``r

### Generate Template
`ash
python main.py
``r

### Deploy
Set env vars for the deploy helper or pass parameters in the console:
`ash
set S3_BUCKET=<your-bucket>
set S3_KEY=demo/site.zip
set WEB_SERVER=nginx  # or httpd
python deploy.py
``r
Notes:
- Template uses Amazon Linux 2 via SSM AMI parameter and installs 
ginx or httpd.
- Without SECURITY_GROUP_ID, default SG applies (may not allow inbound 80). Set SECURITY_GROUP_ID to attach a SG that allows HTTP.

