import re
from functools import lru_cache


v = int(input())
variables = {}

for _ in range(v):
    line = input()
    name, expression = line.split("=", 1)
    variables[name.strip()] = expression.strip()

expression = input().strip()
tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*|\d+|[()+\-*]", expression)

if "".join(tokens) != re.sub(r"\s+", "", expression):
    print("INVALID")
    raise SystemExit


class Parser:
    def __init__(self, tokens, stack):
        self.tokens = tokens
        self.pos = 0
        self.stack = stack

    def parse(self):
        value = self.expression()

        if self.pos != len(self.tokens):
            raise ValueError

        return value

    def expression(self):
        value = self.term()

        while self.pos < len(self.tokens) and self.tokens[self.pos] in "+-":
            op = self.tokens[self.pos]
            self.pos += 1
            right = self.term()

            if op == "+":
                value += right
            else:
                value -= right

        return value

    def term(self):
        value = self.factor()

        while self.pos < len(self.tokens) and self.tokens[self.pos] == "*":
            self.pos += 1
            value *= self.factor()

        return value

    def factor(self):
        if self.pos >= len(self.tokens):
            raise ValueError

        token = self.tokens[self.pos]
        self.pos += 1

        if token.isdigit():
            return int(token)

        if token == "(":
            value = self.expression()

            if self.pos >= len(self.tokens) or self.tokens[self.pos] != ")":
                raise ValueError

            self.pos += 1
            return value

        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", token):
            return get_value(token)

        raise ValueError


@lru_cache(None)
def get_value(name):
    if name not in variables:
        raise ValueError

    if name in active:
        raise RuntimeError

    active.add(name)

    text = variables[name]
    parts = re.findall(r"[A-Za-z_][A-Za-z0-9_]*|\d+|[()+\-*]", text)

    if "".join(parts) != re.sub(r"\s+", "", text):
        active.remove(name)
        raise ValueError

    try:
        value = Parser(parts, active).parse()
    except Exception:
        active.discard(name)
        raise

    active.remove(name)
    return value


active = set()

try:
    answer = Parser(tokens, active).parse()
    print(answer)
except RuntimeError:
    print("CYCLE")
except Exception:
    print("INVALID")
