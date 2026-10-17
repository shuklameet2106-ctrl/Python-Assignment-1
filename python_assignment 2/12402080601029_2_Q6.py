import re
import sys
from collections import deque

line_pattern = re.compile(
    r"^\s*(\d{1,2}):(\d{2})\s+(\S+)\s+(\S+)\s+(SUCCESS|FAIL)\s*$", re.I
)

first = sys.stdin.readline().split()
x, t = int(first[0]), int(first[1])
n = int(sys.stdin.readline())

failures = {}
suspicious = {}

for _ in range(n):
    line = sys.stdin.readline()
    match = line_pattern.match(line)
    if not match:
        continue

    hour, minute, user, ip, status = match.groups()
    stamp = f"{int(hour):02d}:{minute}"
    time = int(hour) * 60 + int(minute)

    window = failures.setdefault(user, deque())

    while window and time - window[0][0] > t:
        window.popleft()

    if status.upper() == "FAIL":
        window.append((time, ip))
    else:
        if user not in suspicious and len(window) >= x and window[-1][1] != ip:
            suspicious[user] = stamp
        window.clear()

for user in sorted(suspicious):
    print(user, suspicious[user])
