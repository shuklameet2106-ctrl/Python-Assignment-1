import sys

MOD = 1000000007

n, m = map(int, sys.stdin.readline().split())

grid = []
for _ in range(n):
    grid.append(sys.stdin.readline().split())

if grid[0][0] == "X" or grid[n - 1][m - 1] == "X":
    print("IMPOSSIBLE")
    raise SystemExit

NEG = None

best_prev = [NEG] * m
ways_prev = [0] * m

for i in range(n):
    best_cur = [NEG] * m
    ways_cur = [0] * m
    row = grid[i]

    for j in range(m):
        if row[j] == "X":
            continue

        value = int(row[j])

        if i == 0 and j == 0:
            best_cur[j] = value
            ways_cur[j] = 1
            continue

        top = best_prev[j]
        left = best_cur[j - 1] if j > 0 else NEG
        diag = best_prev[j - 1] if j > 0 else NEG

        candidates = [c for c in (top, left, diag) if c is not NEG]
        if not candidates:
            continue

        top_best = max(candidates)
        total = 0

        if top is not NEG and top == top_best:
            total += ways_prev[j]
        if left is not NEG and left == top_best:
            total += ways_cur[j - 1]
        if diag is not NEG and diag == top_best:
            total += ways_prev[j - 1]

        best_cur[j] = top_best + value
        ways_cur[j] = total % MOD

    best_prev = best_cur
    ways_prev = ways_cur

if best_prev[m - 1] is NEG:
    print("IMPOSSIBLE")
else:
    print(best_prev[m - 1], ways_prev[m - 1])
