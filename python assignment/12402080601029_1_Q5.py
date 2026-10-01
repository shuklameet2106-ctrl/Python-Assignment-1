class BankError(Exception):
    pass


class Account:
    def __init__(self, account_id, balance):
        self.account_id = account_id
        self.balance = balance
        self.history = []

    def deposit(self, amount):
        if amount <= 0:
            raise BankError("Invalid amount")
        self.balance += amount
        self.history.append(("DEPOSIT", amount))

    def withdraw(self, amount):
        if amount <= 0:
            raise BankError("Invalid amount")
        if amount > self.balance:
            raise BankError("Insufficient balance")
        self.balance -= amount
        self.history.append(("WITHDRAW", amount))


class Transaction:
    def __init__(self, kind, data):
        self.kind = kind
        self.data = data


class Bank:
    def __init__(self):
        self.accounts = {}

    def add_account(self, account):
        self.accounts[account.account_id] = account

    def deposit(self, account_id, amount):
        if account_id not in self.accounts:
            raise BankError("Account not found")
        self.accounts[account_id].deposit(amount)

    def withdraw(self, account_id, amount):
        if account_id not in self.accounts:
            raise BankError("Account not found")
        self.accounts[account_id].withdraw(amount)

    def transfer(self, source, target, amount):
        if source not in self.accounts or target not in self.accounts:
            raise BankError("Account not found")

        self.accounts[source].withdraw(amount)
        self.accounts[target].deposit(amount)


n = int(input())
bank = Bank()

for _ in range(n):
    account_id, balance = input().split()
    bank.add_account(Account(account_id, int(balance)))

q = int(input())

batch = []
batch_number = 0
failed_batches = []

for _ in range(q):
    parts = input().split()

    if parts[0] == "BATCH_BEGIN":
        batch_number += 1
        batch = []
        continue

    if parts[0] == "BATCH_END":
        old_balances = {
            account_id: account.balance
            for account_id, account in bank.accounts.items()
        }

        failed = False

        for operation in batch:
            try:
                if operation[0] == "DEPOSIT":
                    bank.deposit(operation[1], int(operation[2]))
                elif operation[0] == "WITHDRAW":
                    bank.withdraw(operation[1], int(operation[2]))
                else:
                    bank.transfer(operation[1], operation[2], int(operation[3]))
            except BankError:
                failed = True
                break

        if failed:
            for account_id, balance in old_balances.items():
                bank.accounts[account_id].balance = balance
            failed_batches.append(batch_number)

        batch = []
        continue

    if batch is not None and batch_number > 0:
        batch.append(parts)
    else:
        try:
            if parts[0] == "DEPOSIT":
                bank.deposit(parts[1], int(parts[2]))
            elif parts[0] == "WITHDRAW":
                bank.withdraw(parts[1], int(parts[2]))
            elif parts[0] == "TRANSFER":
                bank.transfer(parts[1], parts[2], int(parts[3]))
        except BankError:
            pass

for account_id in sorted(bank.accounts):
    print(account_id, bank.accounts[account_id].balance)

for number in failed_batches:
    print("FAILED", number)
