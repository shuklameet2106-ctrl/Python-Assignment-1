import csv
import sys

import mysql.connector
from mysql.connector import Error

BATCH = 5000


def read_batches(path, converter):
    batch = []
    with open(path, "r", encoding="utf-8", newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            if not row:
                continue
            try:
                record = converter(row)
            except (ValueError, IndexError):
                continue
            batch.append(record)
            if len(batch) >= BATCH:
                yield batch
                batch = []
    if batch:
        yield batch


def student_record(row):
    student_id = int(row[0])
    spi = float(row[2])
    if not 0.0 <= spi <= 10.0:
        raise ValueError
    return (student_id, row[1].strip(), spi)


def registration_record(row):
    return (int(row[0]), row[1].strip())


host, user, password, database = input().split()
student_file = input().strip()
registration_file = input().strip()
course_id = input().strip()
threshold = float(input())

connection = None

try:
    connection = mysql.connector.connect(
        host=host, user=user, password=password, database=database
    )
    cursor = connection.cursor()

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS Student ("
        "student_id INT PRIMARY KEY, "
        "name VARCHAR(100) NOT NULL, "
        "spi DECIMAL(4,2) NOT NULL, "
        "CHECK (spi >= 0 AND spi <= 10))"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS CourseRegistration ("
        "student_id INT NOT NULL, "
        "course_id VARCHAR(20) NOT NULL, "
        "PRIMARY KEY (student_id, course_id), "
        "FOREIGN KEY (student_id) REFERENCES Student(student_id))"
    )

    cursor.execute("SHOW INDEX FROM CourseRegistration WHERE Key_name = 'idx_course'")
    if not cursor.fetchall():
        cursor.execute("CREATE INDEX idx_course ON CourseRegistration (course_id)")

    cursor.execute("SHOW INDEX FROM Student WHERE Key_name = 'idx_spi'")
    if not cursor.fetchall():
        cursor.execute("CREATE INDEX idx_spi ON Student (spi)")

    for batch in read_batches(student_file, student_record):
        cursor.executemany(
            "INSERT IGNORE INTO Student (student_id, name, spi) VALUES (%s, %s, %s)",
            batch,
        )
        connection.commit()

    for batch in read_batches(registration_file, registration_record):
        cursor.executemany(
            "INSERT IGNORE INTO CourseRegistration (student_id, course_id) "
            "VALUES (%s, %s)",
            batch,
        )
        connection.commit()

    cursor.execute(
        "SELECT s.student_id, s.name, s.spi, r.course_id "
        "FROM Student s JOIN CourseRegistration r ON s.student_id = r.student_id "
        "WHERE r.course_id = %s AND s.spi > %s "
        "ORDER BY s.spi DESC, s.student_id ASC",
        (course_id, threshold),
    )

    for student_id, name, spi, course in cursor:
        print(student_id, name, float(spi), course)

except Error as error:
    if connection is not None:
        connection.rollback()
    print("DATABASE ERROR:", error)
    sys.exit(1)
except OSError as error:
    print("FILE ERROR:", error)
    sys.exit(1)
finally:
    if connection is not None and connection.is_connected():
        connection.close()
