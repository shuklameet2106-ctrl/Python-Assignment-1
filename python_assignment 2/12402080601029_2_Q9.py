from functools import total_ordering


def number(text):
    try:
        return int(text)
    except ValueError:
        return float(text)


class Product:
    def __init__(self, product_id, name, stock, purchase, selling):
        self.product_id = product_id
        self.name = name
        self.stock = stock
        self.purchase = purchase
        self.selling = selling

    def value(self):
        return self.stock * self.purchase

    def __add__(self, other):
        return Product(
            self.product_id,
            self.name,
            self.stock + other.stock,
            min(self.purchase, other.purchase),
            max(self.selling, other.selling),
        )

    def __str__(self):
        return (
            f"{self.product_id} {self.name} stock={self.stock} "
            f"purchase={self.purchase} selling={self.selling}"
        )


@total_ordering
class Inventory:
    def __init__(self):
        self.products = {}

    def add_product(self, product):
        if product.product_id in self.products:
            self.products[product.product_id] = self.products[product.product_id] + product
        else:
            self.products[product.product_id] = product

    def delete_product(self, product_id):
        if product_id not in self.products:
            return False
        del self.products[product_id]
        return True

    def update_stock(self, product_id, stock):
        if product_id not in self.products:
            return False
        self.products[product_id].stock = stock
        return True

    def total_value(self):
        return sum(p.value() for p in self.products.values())

    def __add__(self, other):
        merged = Inventory()
        for product in self.products.values():
            merged.products[product.product_id] = Product(
                product.product_id, product.name, product.stock,
                product.purchase, product.selling,
            )
        for product in other.products.values():
            if product.product_id in merged.products:
                merged.products[product.product_id] = (
                    merged.products[product.product_id] + product
                )
            else:
                merged.products[product.product_id] = Product(
                    product.product_id, product.name, product.stock,
                    product.purchase, product.selling,
                )
        return merged

    def __eq__(self, other):
        return self.total_value() == other.total_value()

    def __lt__(self, other):
        return self.total_value() < other.total_value()

    def __len__(self):
        return len(self.products)


def load_inventory(path):
    inventory = Inventory()
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            parts = line.split()
            if len(parts) != 5:
                continue
            try:
                product = Product(
                    parts[0], parts[1], number(parts[2]), number(parts[3]), number(parts[4])
                )
            except ValueError:
                continue
            inventory.add_product(product)
    return inventory


def print_summary(inventory):
    for product_id in sorted(inventory.products):
        print(inventory.products[product_id])
    print("TOTAL", inventory.total_value())


path_a = input().strip()
path_b = input().strip()
q = int(input())

try:
    inventory_a = load_inventory(path_a)
    inventory_b = load_inventory(path_b)
except OSError as error:
    print("FILE ERROR:", error)
    raise SystemExit(1)

for _ in range(q):
    parts = input().split()
    if not parts:
        continue

    command = parts[0].upper()

    try:
        if command == "ADD":
            inventory_a.add_product(
                Product(parts[1], parts[2], number(parts[3]), number(parts[4]), number(parts[5]))
            )
            print("ADDED", parts[1])
        elif command == "DELETE":
            print("DELETED" if inventory_a.delete_product(parts[1]) else "NOT_FOUND", parts[1])
        elif command == "UPDATE":
            print(
                "UPDATED" if inventory_a.update_stock(parts[1], number(parts[2])) else "NOT_FOUND",
                parts[1],
            )
        elif command == "MERGE":
            inventory_a = inventory_a + inventory_b
            print("MERGED")
            print_summary(inventory_a)
        elif command == "COMPARE":
            if inventory_a > inventory_b:
                print("A_GREATER")
            elif inventory_a < inventory_b:
                print("B_GREATER")
            else:
                print("EQUAL")
        else:
            print("INVALID_OPERATION")
    except (IndexError, ValueError):
        print("INVALID_OPERATION")
