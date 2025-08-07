import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def classify_programs(raw_programs):
    # Prioritize non-Microsoft software to improve GPT relevance
    interesting = [p for p in raw_programs if p.get("publisher") and "microsoft" not in p["publisher"].lower()]
    sample = interesting[:50] if len(interesting) >= 50 else raw_programs[:50]

    system_prompt = (
        "You are an AI assistant that classifies software discovered via OSQuery.\n"
        "Remove default system utilities, drivers, or irrelevant software.\n"
        "Return only components that are application runtimes, middleware, databases, or app servers.\n"
        "Tag each remaining entry with one of: 'runtime', 'middleware', 'database', 'app_server'.\n"
        "Respond only with a valid JSON array."
    )

    user_prompt = f"Here is a list of installed programs (JSON):\n\n{json.dumps(sample, indent=2)}"

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )

        response_text = response.choices[0].message.content.strip()
        print("🧠 Raw GPT response:\n", response_text)

        # Extract the first JSON array from the GPT output
        json_match = re.search(r"\[\s*{.*?}\s*\]", response_text, re.DOTALL)
        if json_match:
            json_data = json_match.group(0)
            return json.loads(json_data)
        else:
            print("❌ No JSON array found in GPT response.")
            return []

    except Exception as e:
        print(f"❌ GPT classification failed: {e}")
        return []
