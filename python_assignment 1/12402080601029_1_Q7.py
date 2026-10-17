class InvalidFormatError(Exception):
    pass


class UnknownVariableError(Exception):
    pass


class DivisionByZeroError(Exception):
    pass


class UnsupportedOperatorError(Exception):
    pass


variables = {}


def get_value(value):
    try:
        return float(value)
    except ValueError:
        if value not in variables:
            raise UnknownVariableError
        return variables[value]


def calculate(left, operator, right):
    left = get_value(left)
    right = get_value(right)

    if operator == "+":
        return left + right
    if operator == "-":
        return left - right
    if operator == "*":
        return left * right
    if operator == "/":
        if right == 0:
            raise DivisionByZeroError
        return left / right
    if operator == "%":
        if right == 0:
            raise DivisionByZeroError
        return left % right

    raise UnsupportedOperatorError


while True:
    line = input().strip()

    if line.lower() == "quit":
        break

    try:
        if "=" in line:
            parts = line.split("=")

            if len(parts) != 2:
                raise InvalidFormatError

            name = parts[0].strip()
            value = parts[1].strip()

            if not name.isidentifier():
                raise InvalidFormatError

            variables[name] = get_value(value)
            continue

        parts = line.split()

        if len(parts) != 3:
            raise InvalidFormatError

        result = calculate(parts[0], parts[1], parts[2])

        if result.is_integer():
            print(int(result))
        else:
            print(result)

    except InvalidFormatError:
        print("InvalidFormatError")
    except UnknownVariableError:
        print("UnknownVariableError")
    except DivisionByZeroError:
        print("DivisionByZeroError")
    except UnsupportedOperatorError:
        print("UnsupportedOperatorError")
