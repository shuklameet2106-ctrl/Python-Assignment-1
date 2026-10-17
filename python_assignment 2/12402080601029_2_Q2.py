import re


block_pattern = re.compile(
    r"<(div|li|article|tr)[^>]*class=[\"'][^\"']*product[^\"']*[\"'][^>]*>(.*?)</\1>",
    re.S | re.I,
)
name_pattern = re.compile(
    r"class=[\"'][^\"']*name[^\"']*[\"'][^>]*>(.*?)</", re.S | re.I
)
price_pattern = re.compile(
    r"class=[\"'][^\"']*price[^\"']*[\"'][^>]*>(.*?)</", re.S | re.I
)
rating_pattern = re.compile(
    r"class=[\"'][^\"']*rating[^\"']*[\"'][^>]*>(.*?)</", re.S | re.I
)
tag_pattern = re.compile(r"<[^>]+>")


def clean_text(text):
    return " ".join(tag_pattern.sub(" ", text).split())


def normalize_price(text):
    match = re.search(r"\d[\d,]*(?:\.\d+)?", clean_text(text))
    if not match:
        return None
    value = float(match.group().replace(",", ""))
    if value == int(value):
        return int(value)
    return value


def parse_rating(text):
    match = re.search(r"\d+(?:\.\d+)?", clean_text(text))
    if not match:
        return None
    return float(match.group())


def better(a, b):
    return (-a[1], a[0]) < (-b[1], b[0])


p, k = map(int, input().split())
paths = [input().strip() for _ in range(p)]

products = {}

for path in paths:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as file:
            html = file.read()
    except OSError:
        continue

    for block in block_pattern.finditer(html):
        body = block.group(2)
        name_match = name_pattern.search(body)
        price_match = price_pattern.search(body)
        rating_match = rating_pattern.search(body)

        if not (name_match and price_match and rating_match):
            continue

        name = clean_text(name_match.group(1))
        price = normalize_price(price_match.group(1))
        rating = parse_rating(rating_match.group(1))

        if not name or price is None or rating is None:
            continue

        candidate = (price, rating)

        if name not in products:
            products[name] = candidate
        else:
            old = products[name]
            if (-rating, price) < (-old[1], old[0]):
                products[name] = candidate

ranked = sorted(products.items(), key=lambda x: (-x[1][1], x[1][0], x[0]))

for name, (price, rating) in ranked[:k]:
    print(name, price, rating)
