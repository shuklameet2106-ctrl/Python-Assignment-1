import os
import re
import pickle
import zipfile


mode = input().strip().upper()

if mode == "BUILD":
    folder = input().strip()
    archive = input().strip()

    index = {}
    total_files = 0
    total_lines = 0

    for filename in sorted(os.listdir(folder)):
        path = os.path.join(folder, filename)

        if not os.path.isfile(path) or not filename.lower().endswith(".txt"):
            continue

        total_files += 1

        with open(path, "r", encoding="utf-8", errors="ignore") as file:
            for line_number, line in enumerate(file, 1):
                total_lines += 1
                words = re.findall(r"[A-Za-z0-9_]+", line.lower())

                for word in words:
                    if word not in index:
                        index[word] = []

                    index[word].append((filename, line_number))

    pickle_file = "index.pkl"

    with open(pickle_file, "wb") as file:
        pickle.dump(index, file)

    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for filename in os.listdir(folder):
            path = os.path.join(folder, filename)
            if os.path.isfile(path):
                z.write(path, os.path.join("logs", filename))

        z.write(pickle_file)

    print("FILES", total_files)
    print("LINES", total_lines)
    print("TOKENS", len(index))

elif mode == "SEARCH":
    pickle_file = input().strip()
    q = int(input())

    with open(pickle_file, "rb") as file:
        index = pickle.load(file)

    for _ in range(q):
        word = input().strip().lower()

        if word in index:
            for filename, line in index[word]:
                print(f"{filename}:{line}")
