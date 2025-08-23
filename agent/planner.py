import json
import argparse
import sys
from typing import List, Dict, Any, Optional

# Portia imports
try:
    from portia import Portia, example_tool_registry
    from portia.plan import PlanBuilderV2
except Exception as e:
    print("ERROR: Could not import portia. Install with: pip install portia-sdk-python")
    raise e

def generate_plan_dict(portia_client: Portia, idea: str) -> Dict[str, Any]:
    plan = portia_client.plan(idea)
    # portia Plan -> JSON-serializable dict
    plan_json = json.loads(plan.model_dump_json())
    return plan_json


def print_steps(steps: List[Dict[str, Any]]):
    if not steps:
        print("[no steps]")
        return
    for i, s in enumerate(steps):
        task = s.get("task") or s.get("description") or "<no task text>"
        print(f"{i:02d}. {task}")

def apply_edits_to_steps(original_steps: List[Dict[str, Any]], edits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Supported edits format:
      { "action": "edit",   "index": 1, "task": "new text" }
      { "action": "add",    "index": 2, "task": "inserted step" }  # index optional -> append
      { "action": "remove", "index": 3 }
      { "action": "move",   "index": 2, "to_index": 0 }
    """
    print(f"applying edits to steps: {edits}")
    print(f"original steps: {original_steps}")
    steps = [s.copy() for s in original_steps]
    for e in edits:
        a = e.get("action", "").lower()
        if a == "edit":
            idx = e.get("index")
            if idx is None or idx < 0 or idx >= len(steps):
                print(f"skipping invalid edit index: {idx}")
                continue
            new_task = e.get("task", "").strip()
            if not new_task:
                print("edit missing 'task' text -> skipping")
                continue
            steps[idx]["task"] = new_task
        elif a == "add":
            new_step = {
                "task": e.get("task", "New step"),
                "inputs": [],
                "tool_id": "llm_tool",
                "output": None,
            }
            idx = e.get("index")
            if idx is None or idx < 0 or idx > len(steps):
                steps.append(new_step)
            else:
                steps.insert(idx, new_step)
        elif a == "remove":
            idx = e.get("index")
            if idx is None or idx < 0 or idx >= len(steps):
                print(f"skipping invalid remove index: {idx}")
                continue
            steps.pop(idx)
        elif a == "move":
            idx = e.get("index")
            to_idx = e.get("to_index")
            if idx is None or to_idx is None:
                print("move requires 'index' and 'to_index' -> skipping")
                continue
            if idx < 0 or idx >= len(steps) or to_idx < 0 or to_idx > len(steps):
                print(f"invalid move indices: {idx} -> {to_idx}")
                continue
            step = steps.pop(idx)
            steps.insert(to_idx, step)
        else:
            print(f"unknown action '{a}' -> skipping")
    return steps

    
def rebuild_plan_from_steps(objective: str, project_idea: str, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
    builder = PlanBuilderV2(objective)
    # keep the original idea as an input for traceability
    builder.input(name="project_idea", description="Original project idea", default_value=project_idea)
    for s in steps:
        task_text = s.get("task") or "Perform the described task"
        # For simplicity we add as an LLM step
        builder.llm_step(task=task_text)
    new_plan = builder.build()
    return json.loads(new_plan.model_dump_json())

def interactive_edit_loop(original_plan: Dict[str, Any], portia_client: Portia, idea_text: str):
    steps = original_plan.get("steps", [])
    objective = original_plan.get("plan_context", {}).get("query") or original_plan.get("id") or f"Plan for: {idea_text}"

    print("\n=== Generated plan steps ===")
    print_steps(steps)
    print("\nEnter commands to modify the plan. Type 'help' for commands, 'done' to finish.\n")

    edits: List[Dict[str, Any]] = []

    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nexiting interactive mode.")
            break
        if not raw:
            continue
        parts = raw.split()
        cmd = parts[0].lower()

        if cmd in ("exit", "quit", "done"):
            break
        if cmd == "help":
            print("""Commands:
  show
    - print current steps (after applying queued edits)
  edit <index> <new text>
    - replace step text at index
  add [index] <text>
    - insert new step at index (or append if index omitted)
  remove <index>
    - delete step at index
  move <from_index> <to_index>
    - move step
  queue
    - show queued edits (not applied yet)
  apply
    - apply queued edits immediately and show resulting steps
  rebuild
    - build a new Plan from the current (applied) steps and print JSON
  save <filename.json>
    - save the rebuilt plan JSON to file (runs a rebuild automatically)
  export
    - print rebuilt plan JSON to stdout
  help
    - show this help
  done
    - finish and exit
""")
            continue
