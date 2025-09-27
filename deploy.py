import os
import boto3
from datetime import datetime
from pathlib import Path

# Load env variables
from dotenv import load_dotenv
load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
STACK_NAME = os.getenv("STACK_NAME", "autoblueprint-stack")
OUTPUT_DIR = Path("output")

# Find the latest output folder
def get_latest_template_path():
    output_folders = sorted(OUTPUT_DIR.glob("*/"), reverse=True)
    for folder in output_folders:
        candidate = folder / "autoblueprint_template.yaml"
        if candidate.exists():
            return candidate
    return None

def deploy_cloudformation(template_path):
    with open(template_path, "r") as f:
        template_body = f.read()

    cf = boto3.client("cloudformation", region_name=AWS_REGION)

    print(f"\U0001F4E6 Deploying stack '{STACK_NAME}' using {template_path} ...")

    try:
        cf.create_stack(
            StackName=STACK_NAME,
            TemplateBody=template_body,
            Capabilities=["CAPABILITY_NAMED_IAM"],
            OnFailure="DELETE"
        )
        print(f"✅ Stack creation initiated. Monitor progress in AWS Console.")
    except cf.exceptions.AlreadyExistsException:
        print(f"⚠️ Stack '{STACK_NAME}' already exists. Updating instead...")
        cf.update_stack(
            StackName=STACK_NAME,
            TemplateBody=template_body,
            Capabilities=["CAPABILITY_NAMED_IAM"]
        )
        print("🔄 Stack update initiated.")
    except Exception as e:
        print(f"❌ Deployment failed: {e}")

if __name__ == "__main__":
    path = get_latest_template_path()
    if path:
        deploy_cloudformation(path)
    else:
        print("❌ No CloudFormation template found in 'output/' folder.")
