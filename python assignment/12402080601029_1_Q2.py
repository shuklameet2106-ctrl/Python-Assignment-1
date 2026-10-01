from collections import deque
import re


class Node:
    def __init__(self):
        self.next = {}
        self.fail = 0
        self.output = False


def build_automaton(words):
    nodes = [Node()]

    for word in words:
        current = 0
        for ch in word.lower():
            if ch not in nodes[current].next:
                nodes[current].next[ch] = len(nodes)
                nodes.append(Node())
            current = nodes[current].next[ch]
        nodes[current].output = True

    queue = deque()

    for child in nodes[0].next.values():
        queue.append(child)

    while queue:
        current = queue.popleft()

        for ch, child in nodes[current].next.items():
            queue.append(child)

            fail = nodes[current].fail

            while fail and ch not in nodes[fail].next:
                fail = nodes[fail].fail

            if ch in nodes[fail].next:
                nodes[child].fail = nodes[fail].next[ch]

            if nodes[nodes[child].fail].output:
                nodes[child].output = True

    return nodes


def compromised(password, nodes):
    current = 0

    for ch in password.lower():
        while current and ch not in nodes[current].next:
            current = nodes[current].fail

        if ch in nodes[current].next:
            current = nodes[current].next[ch]
        else:
            current = 0

        if nodes[current].output:
            return True

    return False


b = int(input())
banned = []

for _ in range(b):
    banned.append(input().strip())

nodes = build_automaton(banned)

n = int(input())

for i in range(1, n + 1):
    password = input().rstrip("\n")

    if len(password) < 6 or len(password) > 12:
        result = "WEAK_LENGTH"
    elif compromised(password, nodes):
        result = "COMPROMISED"
    elif re.search(r"(.)\1\1\1", password):
        result = "WEAK_PATTERN"
    elif not re.search(r"[a-z]", password):
        result = "WEAK_PATTERN"
    elif not re.search(r"[A-Z]", password):
        result = "WEAK_PATTERN"
    elif not re.search(r"\d", password):
        result = "WEAK_PATTERN"
    elif not re.search(r"[$#@]", password):
        result = "WEAK_PATTERN"
    else:
        result = "STRONG"

    print(f"{i}: {result}")
