import os
from dotenv import load_dotenv
from openai import OpenAI
import boto3

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ OPENAI_API_KEY not found.")

client = OpenAI(api_key=api_key)

# Optional: Map OS names to SSM Parameter paths for AMI lookup
SSM_AMI_PATHS = {
    "amazon linux 2": "/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2",
    "ubuntu 22.04": "/aws/service/canonical/ubuntu/server/22.04/stable/current/amd64/hvm/ebs-gp2/ami-id",
    "ubuntu 20.04": "/aws/service/canonical/ubuntu/server/20.04/stable/current/amd64/hvm/ebs-gp2/ami-id",
    "windows server 2019": "/aws/service/ami-windows-latest/Windows_Server-2019-English-Full-Base"
}

def get_latest_ami(region, os_type):
    os_key = os_type.strip().lower()
    path = SSM_AMI_PATHS.get(os_key)
    if not path:
        raise ValueError(f"No known AMI path for OS type: {os_type}")

    ssm = boto3.client('ssm', region_name=region)
    response = ssm.get_parameter(Name=path)
    return response['Parameter']['Value']

def map_to_instance(cpu, memory, os_type, region):
    prompt = (
        f"What is the most suitable AWS EC2 instance type for a {os_type} server "
        f"with {cpu} vCPUs and {memory}MB of memory? Respond only with the instance type name."
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    instance_type = response.choices[0].message.content.strip()
    ami = get_latest_ami(region, os_type)

    return instance_type, ami
