import os
import json
from datetime import datetime
from cleaner.classify import classify_programs
from generator.cloudformation import generate_cloudformation_template


def main():
    input_path = input("Enter the path to your OSQuery discovery JSON file [default: input/programs.json]: ").strip()
    if not input_path:
        input_path = "input/programs.json"

    if not os.path.isfile(input_path):
        print(f"❌ File not found: {input_path}")
        return

    with open(input_path, "r") as f:
        raw_programs = json.load(f)

    print("🔍 Classifying software components with GPT...")
    classified_components = classify_programs(raw_programs)

    if not classified_components:
        print("⚠️ No middleware or runtimes detected after cleanup.")
        return

    print("📦 Generating CloudFormation template...")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = os.path.join("output", timestamp)
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "autoblueprint_template.yaml")

    with open(output_file, "w") as f:
        f.write(generate_cloudformation_template(classified_components))

    print(f"✅ CloudFormation template saved to: {output_file}")


if __name__ == "__main__":
    main()
