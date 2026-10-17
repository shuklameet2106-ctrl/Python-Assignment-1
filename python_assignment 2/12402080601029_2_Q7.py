import json
import math


def read_lines(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            line = line.strip()
            if line:
                yield line


def parse_records(lines):
    for line in lines:
        try:
            record = json.loads(line)
        except ValueError:
            yield None, None
            continue

        if not isinstance(record, dict):
            yield None, None
            continue

        device = record.get("device_id")
        if not isinstance(device, str) or not device:
            yield None, None
            continue

        yield device, record


def clean_records(records):
    for device, record in records:
        if device is None:
            yield "UNKNOWN", None
            continue

        temperature = record.get("temperature_c")
        if isinstance(temperature, bool) or not isinstance(temperature, (int, float)):
            yield device, None
            continue
        if not math.isfinite(temperature):
            yield device, None
            continue

        humidity = record.get("humidity")
        if humidity is not None:
            if isinstance(humidity, bool) or not isinstance(humidity, (int, float)):
                yield device, None
                continue

        yield device, float(temperature)


def aggregate(cleaned):
    stats = {}
    for device, temperature in cleaned:
        if device not in stats:
            stats[device] = [0, None, None, 0.0, 0]
        entry = stats[device]
        if temperature is None:
            entry[4] += 1
            continue
        entry[0] += 1
        entry[3] += temperature
        if entry[1] is None or temperature < entry[1]:
            entry[1] = temperature
        if entry[2] is None or temperature > entry[2]:
            entry[2] = temperature
    return stats


def show(value):
    if value == int(value):
        return str(int(value))
    return str(round(value, 2))


path = input().strip()

try:
    stats = aggregate(clean_records(parse_records(read_lines(path))))
except OSError as error:
    print("FILE ERROR:", error)
    raise SystemExit(1)

for device in sorted(stats):
    count, low, high, total, bad = stats[device]
    if count:
        print(
            f"{device} count={count} min={show(low)} max={show(high)} "
            f"avg={total / count:.2f} corrupted={bad}"
        )
    else:
        print(f"{device} count=0 min=NA max=NA avg=NA corrupted={bad}")
