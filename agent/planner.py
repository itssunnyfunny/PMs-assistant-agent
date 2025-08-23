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

        if cmd == "show":
            # preview: show steps after applying queued edits
            preview = apply_edits_to_steps(steps, edits)
            print_steps(preview)
            continue

        if cmd == "queue":
            print("Queued edits:")
            if not edits:
                print("  [none]")
            else:
                for i, e in enumerate(edits):
                    print(f"  {i}: {e}")
            continue

        if cmd == "apply":
            steps = apply_edits_to_steps(steps, edits)
            edits = []
            print("Applied queued edits. Current steps:")
            print_steps(steps)
            continue

        if cmd == "edit":
            if len(parts) < 3:
                print("usage: edit <index> <new text>")
                continue
            try:
                idx = int(parts[1])
            except ValueError:
                print("index must be an integer")
                continue
            new_text = " ".join(parts[2:])
            edits.append({"action": "edit", "index": idx, "task": new_text})
            print(f"queued edit @ {idx}")
            continue

        if cmd == "add":
            # add [index] <text>
            if len(parts) < 2:
                print("usage: add [index] <text>")
                continue
            # detect if second token is an integer index
            try:
                maybe_idx = int(parts[1])
                text = " ".join(parts[2:]) if len(parts) >= 3 else "New step"
                edits.append({"action": "add", "index": maybe_idx, "task": text})
            except ValueError:
                text = " ".join(parts[1:])
                edits.append({"action": "add", "task": text})
            print("queued add")
            continue

        if cmd == "remove":
            if len(parts) != 2:
                print("usage: remove <index>")
                continue
            try:
                idx = int(parts[1])
            except ValueError:
                print("index must be an integer")
                continue
            edits.append({"action": "remove", "index": idx})
            print(f"queued remove @ {idx}")
            continue

        if cmd == "move":
            if len(parts) != 3:
                print("usage: move <from_index> <to_index>")
                continue
            try:
                a = int(parts[1]); b = int(parts[2])
            except ValueError:
                print("indices must be integers")
                continue
            edits.append({"action": "move", "index": a, "to_index": b})
            print(f"queued move {a} -> {b}")
            continue

        if cmd == "rebuild" or cmd == "export":
            # apply queued edits then rebuild
            applied_steps = apply_edits_to_steps(steps, edits)
            new_plan = rebuild_plan_from_steps(objective, idea_text, applied_steps)
            pretty = json.dumps(new_plan, indent=2)
            print("\n=== Rebuilt Plan JSON ===\n")
            print(pretty)
            print("\n=== End plan ===\n")
            continue

        if cmd == "save":
            if len(parts) != 2:
                print("usage: save <filename.json>")
                continue
            fname = parts[1]
            applied_steps = apply_edits_to_steps(steps, edits)
            new_plan = rebuild_plan_from_steps(objective, idea_text, applied_steps)
            with open(fname, "w", encoding="utf-8") as f:
                json.dump(new_plan, f, indent=2)
            print(f"saved rebuilt plan to {fname}")
            continue

        print("unknown command; type 'help' for available commands.")

    # final: if user left queued edits, apply them and show plan summary
    if edits:
        print("Applying queued edits before exit...")
        steps = apply_edits_to_steps(steps, edits)
        edits = []

    rebuilt = rebuild_plan_from_steps(objective, idea_text, steps)
    print("\nFinal rebuilt plan summary (first lines):")
    print(json.dumps({
        "id": rebuilt.get("id"),
        "objective": objective,
        "num_steps": len(rebuilt.get("steps", []))
    }, indent=2))
    # offer to save automatically
    try:
        want = input("\nSave rebuilt plan to file? (y/N) ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        want = "n"
    if want == "y":
        fname = input("filename (e.g. plan.json): ").strip() or "plan.json"
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(rebuilt, f, indent=2)
        print(f"Saved to {fname}.")
    print("Done.")
