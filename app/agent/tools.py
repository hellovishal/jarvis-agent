
AVAILABLE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "sum_numbers",
            "description": (
                "Calculate the sum of a list of numbers. "
                "Use this when the user asks to add numbers."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "numbers": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Numbers to add",
                    }
                },
                "required": ["numbers"],
                "additionalProperties": False,
            },
        },
    }
]
