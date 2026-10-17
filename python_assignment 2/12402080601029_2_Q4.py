import json
import sys

import mysql.connector
from mysql.connector import Error

COLUMNS = {
    "student.id": "Student.student_id",
    "student.name": "Student.name",
    "student.spi": "Student.spi",
    "course.id": "Course.course_id",
    "course.name": "Course.name",
    "registration.student_id": "CourseRegistration.student_id",
    "registration.course_id": "CourseRegistration.course_id",
}

OPERATORS = {"=", "!=", "<", "<=", ">", ">=", "LIKE", "BETWEEN"}
DIRECTIONS = {"ASC", "DESC"}


def get_column(name):
    key = str(name).strip().lower()
    if key not in COLUMNS:
        raise ValueError("Invalid column: " + str(name))
    return COLUMNS[key]


def build_query(spec):
    columns = spec.get("columns")
    if not isinstance(columns, list) or not columns:
        raise ValueError("columns must be a non-empty list")

    select_part = ", ".join(get_column(c) for c in columns)

    where_parts = []
    params = []

    for condition in spec.get("where", []):
        column = get_column(condition.get("column"))
        operator = str(condition.get("op", "=")).upper()
        value = condition.get("value")

        if operator not in OPERATORS:
            raise ValueError("Invalid operator: " + operator)

        if operator == "BETWEEN":
            if not isinstance(value, list) or len(value) != 2:
                raise ValueError("BETWEEN needs two values")
            where_parts.append(column + " BETWEEN %s AND %s")
            params.extend(value)
        else:
            if isinstance(value, (list, dict)) or value is None:
                raise ValueError("Invalid value for " + operator)
            where_parts.append(column + " " + operator + " %s")
            params.append(value)

    sql = (
        "SELECT " + select_part + " FROM Student "
        "JOIN CourseRegistration ON Student.student_id = CourseRegistration.student_id "
        "JOIN Course ON Course.course_id = CourseRegistration.course_id"
    )

    if where_parts:
        sql += " WHERE " + " AND ".join(where_parts)

    order = spec.get("order")
    if order:
        order_column = get_column(order.get("column"))
        direction = str(order.get("direction", "ASC")).upper()
        if direction not in DIRECTIONS:
            raise ValueError("Invalid sort direction")
        sql += " ORDER BY " + order_column + " " + direction

    limit = spec.get("limit", 100)
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 1000:
        raise ValueError("LIMIT must be an integer between 1 and 1000")

    sql += " LIMIT %s"
    params.append(limit)

    return sql, params


host, user, password, database = input().split()
raw = sys.stdin.read()

try:
    spec = json.loads(raw)
    sql, params = build_query(spec)
except (ValueError, AttributeError, TypeError) as error:
    print("SQL_REJECTED:", error)
    sys.exit(1)

print("SQL_OK")
print(sql)
print(params)

connection = None

try:
    connection = mysql.connector.connect(
        host=host, user=user, password=password, database=database
    )
    cursor = connection.cursor()
    cursor.execute(sql, params)
    for row in cursor.fetchall():
        print(*row)
except Error as error:
    print("DATABASE ERROR:", error)
    sys.exit(1)
finally:
    if connection is not None and connection.is_connected():
        connection.close()
