# 🤖 AutoBlueprint: Agentic AI-Powered CloudFormation Generator (Middleware Mode)

**AutoBlueprint** is a proof-of-concept tool that analyzes OSQuery discovery data, uses GPT to classify useful software components (runtimes, middleware, databases), and generates a ready-to-deploy **CloudFormation template** to re-provision the workload in AWS.

---

## ✅ Features

- 🧠 **AI-Powered Middleware Detection**  
  Uses GPT to scan noisy OSQuery discovery output and identify meaningful components such as Tomcat, .NET, Java, SQL Server, Plex, etc.

- 🧹 **Noise Reduction**  
  Automatically filters out Windows system components, default tools, and drivers — keeping only deployable building blocks.

- 🏗️ **CloudFormation Template Generator**  
  Renders an EC2 instance for each identified component, tagged with its type (`runtime`, `middleware`, `app_server`, `database`) for traceability.

- 📄 **Input Flexibility**  
  Takes standard OSQuery JSON outputs (`programs.json`, `os_version.json`, etc.)

- 💡 **Middleware Mode MVP**  
  Focuses on software component reconstruction — not full server rehosting.

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
│   └── 2025-08-06_14-00-00/
│       └── autoblueprint_template.yaml
├── .env
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start

1. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Set Your OpenAI API Key**

   Create a `.env` file in the root:
   ```
   OPENAI_API_KEY=sk-xxxxxx...
   GPT_MODEL=gpt-3.5-turbo   # Optional: default is gpt-4 if not set
   ```

3. **Prepare Your OSQuery Input**

   Copy your OSQuery `programs.json` file to `input/`.

   _(Optional)_ If targeting EC2 deployment, add a fake `os_version.json` like:
   ```json
   [
     {
       "name": "Windows Server 2019",
       "version": "10.0.17763",
       "platform": "windows",
       "arch": "x86_64"
     }
   ]
   ```

4. **Run AutoBlueprint**

   ```bash
   python main.py
   ```

5. **Deploy via CloudFormation**

   - Go to the AWS Console → CloudFormation → Create Stack
   - Upload the generated YAML file in the `output/` folder

---

## 🧠 GPT Prompt Used

> “You are an AI assistant that classifies software discovered via OSQuery. Remove system drivers, utilities, and irrelevant components. Return only runtimes, middleware, databases, or app servers. Tag each entry with one of: 'runtime', 'middleware', 'database', 'app_server'. Return a valid JSON array.”

---

## ⚠️ Limitations

- No automatic EC2 deployment — template must be uploaded manually.
- No user data, security group, or IAM role generation yet.
- GPT output formatting may vary; classification is best-effort.
- AMI resolution requires a known OS or fallback logic (manual `os_version.json` used in MVP).

---

## 🛣️ Roadmap

### 🔧 Phase 1: MVP (✅ Complete)
- Parse `programs.json` discovery data
- Clean and classify with GPT
- Generate CFN template for EC2 deployment

### 🧩 Phase 2: Near-Term
- Auto-resolve AMI from `os_version.json`
- Add security groups, key pairs, and optional EBS size tuning
- Post-deploy script generation (e.g., install Tomcat, .NET)

### 🌐 Phase 3: Long-Term
- Merge with `server mode` (CPU/RAM-based sizing)
- Enable actual `boto3`-based CFN deployment
- Support VPC/network mapping
- Web UI (Flask or Streamlit)

---

## ❓ License

This tool is for internal testing and demonstration purposes only.

---

## 👨‍💻 Author

Erick Perales  
Cloud Migration IT Architect, Cloud Migration Specialist
[https://github.com/peralese](https://github.com/peralese)