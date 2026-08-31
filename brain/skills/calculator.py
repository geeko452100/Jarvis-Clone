"""Skill: calculator — evaluates a basic math expression.

Uses simpleeval (pip install simpleeval) instead of Python's raw eval()
or a hand-rolled parser. simpleeval is a small, well-established library
built specifically for this: safely evaluating a math expression string
without the ability to run arbitrary Python code the way eval() can.
"""

from simpleeval import simple_eval

NAME = "calculator"
DESCRIPTION = "Evaluate a basic math expression, e.g. '12 * (4 + 3)'."
PARAMETERS = {
    "type": "object",
    "properties": {
        "expression": {
            "type": "string",
            "description": "The math expression to evaluate.",
        }
    },
    "required": ["expression"],
}


def run(expression):
    try:
        return simple_eval(expression)
    except Exception:
        return f"Error: couldn't evaluate '{expression}' as a math expression."