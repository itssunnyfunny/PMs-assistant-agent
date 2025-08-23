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
