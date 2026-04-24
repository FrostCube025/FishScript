class FishScriptError(Exception):
    """FishScript error with optional line number."""

    def __init__(self, message, line_number=None, line_text=None):
        self.message = message
        self.line_number = line_number
        self.line_text = line_text

        if line_number is not None:
            full = f"Line {line_number}: {message}"
            if line_text:
                full += f"\n    {line_text}"
        else:
            full = message

        super().__init__(full)
