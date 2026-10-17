import csv
from datetime import datetime
from collections import defaultdict


filename = input().strip()

balances = defaultdict(float)

try:
    with open(filename, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        with open("credit.csv", "w", newline="", encoding="utf-8") as credit_file, \
             open("debit.csv", "w", newline="", encoding="utf-8") as debit_file, \
             open("error.csv", "w", newline="", encoding="utf-8") as error_file:

            fieldnames = reader.fieldnames
            credit_writer = csv.DictWriter(credit_file, fieldnames=fieldnames)
            debit_writer = csv.DictWriter(debit_file, fieldnames=fieldnames)
            error_writer = csv.writer(error_file)

            credit_writer.writeheader()
            debit_writer.writeheader()
            error_writer.writerow(fieldnames + ["reason"])

            for row in reader:
                try:
                    if not row.get("tid") or not row.get("acc"):
                        raise ValueError("missing transaction or account id")

                    if row.get("type") not in ("CREDIT", "DEBIT"):
                        raise ValueError("invalid transaction type")

                    amount = float(row["amount"])

                    if amount <= 0:
                        raise ValueError("amount must be greater than zero")

                    datetime.strptime(row["time"], "%Y-%m-%dT%H:%M:%S")

                    if row["type"] == "CREDIT":
                        credit_writer.writerow(row)
                        balances[row["acc"]] += amount
                    else:
                        debit_writer.writerow(row)
                        balances[row["acc"]] -= amount

                except Exception as error:
                    error_writer.writerow(list(row.values()) + [str(error)])

except FileNotFoundError:
    print("File not found")
    raise SystemExit

for account, balance in sorted(balances.items(), key=lambda x: (-abs(x[1]), x[0])):
    if balance.is_integer():
        balance = int(balance)
    print(account, balance)

print("Files created: credit.csv, debit.csv, error.csv")
