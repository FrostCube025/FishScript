import random
from dataclasses import dataclass
from typing import Any, Callable

from .errors import FishScriptError


class ReturnBubble(Exception):
    def __init__(self, value: Any):
        self.value = value


@dataclass
class Line:
    number: int
    text: str


class FishScript:
    def __init__(self, output: Callable[[str], None] | None = None, ask: Callable[[str], str] | None = None):
        self.fish: dict[str, Any] = {}
        self.functions: dict[str, tuple[list[str], list[Line]]] = {}
        self.output = output or print
        self.ask = ask or input

    def _error(self, message: str, line: Line | None = None):
        if line:
            raise FishScriptError(message, line.number, line.text)
        raise FishScriptError(message)

    def _split_args(self, text: str) -> list[str]:
        args = []
        current = []
        depth = 0
        in_string = False
        quote_char = ""

        for char in text:
            if char in ["'", '"']:
                if not in_string:
                    in_string = True
                    quote_char = char
                elif quote_char == char:
                    in_string = False

            if not in_string:
                if char == "[":
                    depth += 1
                elif char == "]":
                    depth -= 1
                elif char == "," and depth == 0:
                    args.append("".join(current).strip())
                    current = []
                    continue

            current.append(char)

        if current:
            args.append("".join(current).strip())

        return args

    def value(self, text: str, line: Line | None = None) -> Any:
        text = text.strip()

        if text == "":
            self._error("Empty value", line)

        if text.startswith('"') and text.endswith('"'):
            return text[1:-1]

        if text.startswith("'") and text.endswith("'"):
            return text[1:-1]

        if text.lower() == "true":
            return True

        if text.lower() == "false":
            return False

        if text.lower() == "nothing":
            return None

        if text.lstrip("-").isdigit():
            return int(text)

        if text.startswith("[") and text.endswith("]"):
            inside = text[1:-1].strip()
            if not inside:
                return []
            return [self.value(part, line) for part in self._split_args(inside)]

        if text.startswith("DICEFISH "):
            parts = text.split()
            if len(parts) != 3:
                self._error("DICEFISH expects two values, example: DICEFISH 1 10", line)
            return random.randint(int(self.value(parts[1], line)), int(self.value(parts[2], line)))

        if text.startswith("LENGTH OF "):
            return len(self.value(text[10:].strip(), line))

        if text.startswith("CHOOSE FROM "):
            collection = self.value(text[12:].strip(), line)
            if not collection:
                self._error("Cannot CHOOSE FROM an empty list", line)
            return random.choice(collection)

        if text.startswith("INDEX ") and " FROM " in text:
            index_text, list_name = text[6:].split(" FROM ", 1)
            collection = self.value(list_name.strip(), line)
            index = int(self.value(index_text.strip(), line))
            return collection[index]

        math_ops = {
            "SUM OF ": lambda a, b: a + b,
            "DIFFERENCE OF ": lambda a, b: a - b,
            "PRODUCT OF ": lambda a, b: a * b,
            "QUOTIENT OF ": lambda a, b: a / b,
            "REMAINDER OF ": lambda a, b: a % b,
        }

        for prefix, func in math_ops.items():
            if text.startswith(prefix) and " AND " in text:
                a, b = text[len(prefix):].split(" AND ", 1)
                return func(self.value(a.strip(), line), self.value(b.strip(), line))

        if "(" in text and text.endswith(")"):
            name = text[:text.index("(")].strip()
            args_text = text[text.index("(") + 1:-1].strip()
            args = [] if not args_text else [self.value(a, line) for a in self._split_args(args_text)]
            return self.call_function(name, args, line)

        if text in self.fish:
            return self.fish[text]

        self._error(f"Unknown fish/value: {text}", line)

    def condition(self, text: str, line: Line | None = None) -> bool:
        checks = [
            (" SMELLS NOT LIKE ", lambda a, b: a != b),
            (" SMELLS LIKE ", lambda a, b: a == b),
            (" SMELLS LESS THAN ", lambda a, b: a < b),
            (" SMELLS MORE THAN ", lambda a, b: a > b),
            (" EXISTS IN ", lambda a, b: a in b),
        ]

        for phrase, func in checks:
            if phrase in text:
                left, right = text.split(phrase, 1)
                return func(self.value(left.strip(), line), self.value(right.strip(), line))

        self._error(f"Bad fish condition: {text}", line)

    def collect_block(self, lines: list[Line], start: int) -> tuple[list[Line], int]:
        block = []
        depth = 0
        i = start

        while i < len(lines):
            current = lines[i]
            text = current.text.strip()

            if text == "REEF":
                depth += 1
            elif text == "SURFACE":
                if depth == 0:
                    return block, i
                depth -= 1

            block.append(current)
            i += 1

        self._error("Missing SURFACE")

    def call_function(self, name: str, args: list[Any], line: Line | None = None) -> Any:
        if name not in self.functions:
            self._error(f"Unknown ritual: {name}", line)

        params, body = self.functions[name]

        if len(params) != len(args):
            self._error(f"{name} expected {len(params)} argument(s), got {len(args)}", line)

        old_fish = self.fish.copy()

        for param, arg in zip(params, args):
            self.fish[param] = arg

        try:
            self.run_lines(body)
            result = None
        except ReturnBubble as bubble:
            result = bubble.value
        finally:
            self.fish = old_fish

        return result

    def run(self, code: str):
        lines = [Line(i + 1, text) for i, text in enumerate(code.splitlines())]
        self.run_lines(lines)

    def run_lines(self, lines: list[Line]):
        i = 0

        while i < len(lines):
            line = lines[i]
            text = line.text.strip()

            if not text or text.startswith("BUBBLE"):
                i += 1
                continue

            if text == "AQUARIUM OPENS":
                i += 1
                continue

            if text == "AQUARIUM CLOSES":
                break

            try:
                if text.startswith("HATCH ") and " AS " in text:
                    name, val = text[6:].split(" AS ", 1)
                    self.fish[name.strip()] = self.value(val, line)

                elif " MUTATES INTO " in text:
                    name, val = text.split(" MUTATES INTO ", 1)
                    self.fish[name.strip()] = self.value(val, line)

                elif " SWALLOWS " in text:
                    name, val = text.split(" SWALLOWS ", 1)
                    self.fish[name.strip()] += self.value(val, line)

                elif " NIBBLES " in text:
                    name, val = text.split(" NIBBLES ", 1)
                    self.fish[name.strip()] -= self.value(val, line)

                elif text.startswith("SING "):
                    self.output(str(self.value(text[5:], line)))

                elif text.startswith("FISH ") and text.endswith(" FROM VOID"):
                    name = text[5:-10].strip()
                    answer = self.ask(f"The void gives {name}: ")
                    self.fish[name] = int(answer) if answer.lstrip("-").isdigit() else answer

                elif text.startswith("DROP ") and " INTO " in text:
                    val, list_name = text[5:].split(" INTO ", 1)
                    target = list_name.strip()
                    if target not in self.fish or not isinstance(self.fish[target], list):
                        self._error(f"{target} is not a list", line)
                    self.fish[target].append(self.value(val, line))

                elif text.startswith("EAT INDEX ") and " FROM " in text:
                    index, list_name = text[10:].split(" FROM ", 1)
                    target = list_name.strip()
                    self.fish[target].pop(int(self.value(index, line)))

                elif text.startswith("IF "):
                    cond = text[3:].strip()

                    if i + 1 >= len(lines) or lines[i + 1].text.strip() != "REEF":
                        self._error("Expected REEF after IF", line)

                    if_block, end = self.collect_block(lines, i + 2)
                    else_block = []

                    if end + 1 < len(lines) and lines[end + 1].text.strip() == "OTHERWATER":
                        if end + 2 >= len(lines) or lines[end + 2].text.strip() != "REEF":
                            self._error("Expected REEF after OTHERWATER", lines[end + 1])
                        else_block, end = self.collect_block(lines, end + 3)

                    if self.condition(cond, line):
                        self.run_lines(if_block)
                    else:
                        self.run_lines(else_block)

                    i = end

                elif text.startswith("WHILE ") and text.endswith(" STILL SWIMMING"):
                    name = text[6:-15].strip()

                    if i + 1 >= len(lines) or lines[i + 1].text.strip() != "REEF":
                        self._error("Expected REEF after WHILE", line)

                    block, end = self.collect_block(lines, i + 2)

                    safety = 0
                    while self.value(name, line) > 0:
                        self.run_lines(block)
                        safety += 1
                        if safety > 100000:
                            self._error("Loop stopped after 100000 swims. Possible infinite fish.", line)

                    i = end

                elif text.startswith("RITUAL "):
                    header = text[7:].strip()
                    if " WITH " not in header:
                        self._error("RITUAL syntax: RITUAL NAME WITH arg1, arg2", line)

                    name, params_text = header.split(" WITH ", 1)
                    params = [p.strip() for p in params_text.split(",")] if params_text.strip() else []

                    if i + 1 >= len(lines) or lines[i + 1].text.strip() != "REEF":
                        self._error("Expected REEF after RITUAL", line)

                    body, end = self.collect_block(lines, i + 2)
                    self.functions[name.strip()] = (params, body)
                    i = end

                elif text.startswith("RELEASE "):
                    raise ReturnBubble(self.value(text[8:], line))

                elif text == "PANICFISH":
                    self.output(random.choice([
                        "🐟 the aquarium has chosen violence",
                        "🐠 glub glub undefined behavior",
                        "🐡 fish.exe forgot how to swim",
                        "🦈 a shark reviewed your code and left",
                        "🫧 bubble stack overflow",
                    ]))

                else:
                    self._error(f"FishScript does not understand: {text}", line)

            except ReturnBubble:
                raise
            except FishScriptError:
                raise
            except Exception as exc:
                self._error(str(exc), line)

            i += 1