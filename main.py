import os
import json
from datetime import datetime
from cleaner.classify import classify_programs
from generator.cloudformation import generate_cloudformation_template
from osquery_parser import extract_specs, parse_osquery_dump


def main():
    input_path = input("Enter the path to your OSQuery discovery JSON file [default: input/programs.json]: ").strip()
    if not input_path:
        input_path = "input/programs.json"

    if not os.path.isfile(input_path):
        print(f"❌ File not found: {input_path}")
        return

    # Try to parse OSQuery multi-block exports; fall back to a simple JSON list
    raw_programs = []
    specs = {}
    try:
        parsed = parse_osquery_dump(input_path)
        specs = extract_specs(parsed)
        raw_programs = parsed.get("programs") or []
        print(f"📥 Parsed OSQuery dump with {len(raw_programs)} programs discovered.")
    except Exception as e:
        print(f"ℹ️ Could not parse as OSQuery dump ({e}); falling back to plain JSON list.")
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                raw_programs = data
                print(f"📥 Loaded {len(raw_programs)} programs from simple JSON list.")
            else:
                print("❌ Input JSON is not a list of programs.")
                return

    print("🔍 Classifying software components with GPT...")
    classified_components = classify_programs(raw_programs)

    if not classified_components:
        print("⚠️ No middleware or runtimes detected after cleanup.")
        return

    if specs:
        print(
            "🖥️  Detected specs:",
            f"OS={specs.get('os_name')} {specs.get('os_version')} ({specs.get('platform')}) | "
            f"CPU={specs.get('cpu_model')} "
            f"cores={specs.get('cpu_physical_cores')}p/{specs.get('cpu_logical_cores')}l | "
            f"RAM={specs.get('memory_bytes')} bytes",
        )

    print("📦 Generating CloudFormation template...")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = os.path.join("output", timestamp)
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "autoblueprint_template.yaml")

    with open(output_file, "w") as f:
        f.write(generate_cloudformation_template(classified_components, specs=specs))

    print(f"✅ CloudFormation template saved to: {output_file}")


if __name__ == "__main__":
    main()
