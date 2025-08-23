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
