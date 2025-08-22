import argparse
import dotenv
import os

from agent.planner import generate_project_plan
from utils.formatter import pretty_print_plan

# Load env vars
dotenv.load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Project Manager AI Agent")
    parser.add_argument("--idea", type=str, required=True, help="Project idea description")
    args = parser.parse_args()

    project_idea = args.idea
    print("🤖 Generating project plan for:", project_idea)

    plan_json = generate_project_plan(project_idea)
    pretty_print_plan(plan_json)

if __name__ == "__main__":
    main()
