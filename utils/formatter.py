import json

def pretty_print_plan(plan_json: str):
    try:
        parsed = json.loads(plan_json)
        print("\n📌 Project Plan:\n")
        for idx, task in enumerate(parsed.get("tasks", []), 1):
            print(f"{idx}. {task['title']} ({task['suggested_role']})")
            print(f"   {task['description']}\n")
    except Exception:
        print("⚠️ Could not parse JSON, raw output:\n", plan_json)
