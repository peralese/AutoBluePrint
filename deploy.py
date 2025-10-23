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
S3_BUCKET = os.getenv("S3_BUCKET")
S3_KEY = os.getenv("S3_KEY")
WEB_SERVER = os.getenv("WEB_SERVER", "nginx")
SECURITY_GROUP_ID = os.getenv("SECURITY_GROUP_ID", "")

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

    parameters = []
    if S3_BUCKET and S3_KEY:
        parameters.extend([
            {"ParameterKey": "S3Bucket", "ParameterValue": S3_BUCKET},
            {"ParameterKey": "S3Key", "ParameterValue": S3_KEY},
        ])
    else:
        print("⚠ S3_BUCKET and/or S3_KEY not set. You must provide these parameters manually in the console or set environment variables.")
    if WEB_SERVER:
        parameters.append({"ParameterKey": "WebServer", "ParameterValue": WEB_SERVER})
    if SECURITY_GROUP_ID:
        parameters.append({"ParameterKey": "SecurityGroupId", "ParameterValue": SECURITY_GROUP_ID})

    try:
        cf.create_stack(
            StackName=STACK_NAME,
            TemplateBody=template_body,
            Capabilities=["CAPABILITY_NAMED_IAM"],
            OnFailure="DELETE",
            Parameters=parameters
        )
        print(f"✅ Stack creation initiated. Monitor progress in AWS Console.")
    except cf.exceptions.AlreadyExistsException:
        print(f"⚠️ Stack '{STACK_NAME}' already exists. Updating instead...")
        cf.update_stack(
            StackName=STACK_NAME,
            TemplateBody=template_body,
            Capabilities=["CAPABILITY_NAMED_IAM"],
            Parameters=parameters
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
