"""Skill: get_time — returns the current local time.

Every skill file follows the same convention: NAME, DESCRIPTION,
PARAMETERS, and a run() function. The loader in tools.py looks for
exactly these four things, so any file that has them can be dropped
into this folder and picked up automatically.
"""

import datetime

NAME = "get_time"
DESCRIPTION = "Get the current local time."

# No inputs needed for this one, so properties/required are both empty.
PARAMETERS = {
    "type": "object",
    "properties": {},
    "required": [],
}


def run():
    return datetime.datetime.now().strftime("%I:%M %p")