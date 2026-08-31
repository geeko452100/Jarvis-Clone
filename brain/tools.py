"""Skill loader.

Scans the skills/ folder for .py files, imports each one, and pulls out
the NAME / DESCRIPTION / PARAMETERS / run() convention every skill file
is expected to follow. Builds the two things brain.py needs:
AVAILABLE_TOOLS (name -> function to call) and TOOL_SCHEMAS (what gets
sent to the API so the model knows the tools exist).
"""

import os
import importlib.util

SKILLS_DIR = "skills"

# Both start empty and get filled in by load_skills(). Kept as
# module-level containers (not returned values) so that other files
# importing them see updates after a reload, without needing to
# re-import.
AVAILABLE_TOOLS = {}
TOOL_SCHEMAS = []


def load_skills():
    """Import every .py file in skills/ and register it as a tool."""
    for filename in os.listdir(SKILLS_DIR):
        if not filename.endswith(".py"):
            continue

        module_name = filename[:-3]  # strip the ".py"
        filepath = os.path.join(SKILLS_DIR, filename)

        # Dynamically import the file as a module — same end result as a
        # normal "import skillname" line, but the filename is decided at
        # runtime instead of being hardcoded, which is what lets new
        # skill files get picked up without editing this loader.
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Confirm the file actually follows the skill convention before
        # trusting it. Skip (and report) anything incomplete rather than
        # crashing the whole assistant over one bad file.
        required = ["NAME", "DESCRIPTION", "PARAMETERS", "run"]
        if not all(hasattr(module, attr) for attr in required):
            print(f"Skipping {filename}: missing one of {required}")
            continue

        AVAILABLE_TOOLS[module.NAME] = module.run
        TOOL_SCHEMAS.append(
            {
                "type": "function",
                "function": {
                    "name": module.NAME,
                    "description": module.DESCRIPTION,
                    "parameters": module.PARAMETERS,
                },
            }
        )


# Run once immediately on import, so a normal startup already has every
# skill in skills/ loaded before the chat loop begins.
load_skills()