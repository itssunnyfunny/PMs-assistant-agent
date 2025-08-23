if __name__ == "__main__":
import argparse
import sys
try:
from agent.planner import (
create_portia_client,
generate_plan_dict,
print_steps,
interactive_edit_loop,
)
except Exception as e:
print("ERROR: failed to import core module. Make sure both files are in the same directory.")
raise


parser = argparse.ArgumentParser(description="Portia project planner CLI (no server).")
parser.add_argument("--idea", type=str, help="Project idea to generate plan for (optional).")
args = parser.parse_args()


try:
portia_client = create_portia_client()
except ImportError as ie:
print(str(ie))
sys.exit(1)


if args.idea:
idea_text = args.idea
else:
try:
idea_text = input("Enter your project idea: ").strip()
except (EOFError, KeyboardInterrupt):
print("\nNo idea provided. Exiting.")
sys.exit(1)
if not idea_text:
print("Empty idea. Exiting.")
sys.exit(1)


print("\nGenerating plan (this calls Portia planner)...\n")
plan_dict = generate_plan_dict(portia_client, idea_text)
print("Plan generated. Plan id:", plan_dict.get("id", "<no-id>"))
print("\nSteps:")
print_steps(plan_dict.get("steps", []))


# Enter interactive editor
interactive_edit_loop(plan_dict, portia_client, idea_text)