def average(marks):
    return sum(marks) / len(marks)


n, k, m = map(int, input().split())

students = []

for _ in range(n):
    data = input().split()
    enrollment = data[0]
    name = data[1]
    semester = int(data[2])
    cpi = float(data[3])
    marks = tuple(map(int, data[4:]))
    students.append((enrollment, name, semester, cpi, marks))

semesters = {}

for student in students:
    semester = student[2]
    if semester not in semesters:
        semesters[semester] = []
    semesters[semester].append(student)

for semester in sorted(semesters):
    group = semesters[semester]
    group.sort(key=lambda x: (-x[3], -average(x[4]), x[0]))
    print(f"Semester {semester}:", *[x[0] for x in group[:k]])

for i in range(m):
    highest = -1
    toppers = []

    for student in students:
        mark = student[4][i]

        if mark > highest:
            highest = mark
            toppers = [student[0]]
        elif mark == highest:
            toppers.append(student[0])

    toppers.sort()
    print(f"S{i + 1}:", *toppers)
