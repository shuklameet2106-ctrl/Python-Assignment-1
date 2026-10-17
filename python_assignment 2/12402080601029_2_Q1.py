import re

pattern = re.compile(
    r"(?<![A-Za-z0-9+._@-])"
    r"([A-Za-z0-9+._-]+)@"
    r"((?:[A-Za-z0-9-]+\.)+(?:com|edu|org))"
    r"(?![A-Za-z0-9@_-])(?!\.[A-Za-z0-9])"
)

path = input().strip()

users = {}
smallest = {}

with open(path, "r", encoding="utf-8", errors="ignore") as file:
    for line in file:
        for match in pattern.finditer(line):
            user = match.group(1)
            domain = match.group(2).lower()
            email = user + "@" + domain

            if domain not in users:
                users[domain] = set()
                smallest[domain] = email

            users[domain].add(user)

            if email < smallest[domain]:
                smallest[domain] = email

for domain in sorted(users):
    print(domain, len(users[domain]), smallest[domain])
