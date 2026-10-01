import tkinter as tk
from tkinter import ttk, messagebox
import json
import csv
import os


FILE_NAME = "assignments.json"


def load_data():
    if not os.path.exists(FILE_NAME):
        return []

    try:
        with open(FILE_NAME, "r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return []


data = load_data()


def save_data():
    with open(FILE_NAME, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def add_record():
    enrollment = enrollment_entry.get().strip()
    name = name_entry.get().strip()
    assignment = assignment_entry.get().strip()
    status = status_box.get()
    marks = marks_entry.get().strip()
    remarks = remarks_entry.get().strip()

    if not enrollment or not name or not assignment:
        messagebox.showerror("Error", "Please fill all required fields")
        return

    try:
        marks_value = float(marks) if marks else 0
    except ValueError:
        messagebox.showerror("Error", "Marks must be a number")
        return

    record = {
        "enrollment": enrollment,
        "name": name,
        "assignment": assignment,
        "status": status,
        "marks": marks_value,
        "remarks": remarks
    }

    data.append(record)
    save_data()
    show_data()
    clear_fields()


def clear_fields():
    enrollment_entry.delete(0, tk.END)
    name_entry.delete(0, tk.END)
    assignment_entry.delete(0, tk.END)
    marks_entry.delete(0, tk.END)
    remarks_entry.delete(0, tk.END)


def show_data():
    for item in table.get_children():
        table.delete(item)

    selected = filter_box.get()

    for record in data:
        if selected != "All" and record["status"] != selected:
            continue

        table.insert(
            "",
            tk.END,
            values=(
                record["enrollment"],
                record["name"],
                record["assignment"],
                record["status"],
                record["marks"],
                record["remarks"]
            )
        )


def export_csv():
    with open("assignment_report.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "enrollment",
            "name",
            "assignment",
            "status",
            "marks",
            "remarks"
        ])

        for record in data:
            writer.writerow([
                record["enrollment"],
                record["name"],
                record["assignment"],
                record["status"],
                record["marks"],
                record["remarks"]
            ])

    messagebox.showinfo("Done", "CSV report exported")


root = tk.Tk()
root.title("Assignment Tracker")
root.geometry("900x600")

tk.Label(root, text="Enrollment").grid(row=0, column=0, padx=5, pady=5)
enrollment_entry = tk.Entry(root)
enrollment_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="Name").grid(row=0, column=2, padx=5, pady=5)
name_entry = tk.Entry(root)
name_entry.grid(row=0, column=3, padx=5, pady=5)

tk.Label(root, text="Assignment").grid(row=1, column=0, padx=5, pady=5)
assignment_entry = tk.Entry(root)
assignment_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(root, text="Status").grid(row=1, column=2, padx=5, pady=5)
status_box = ttk.Combobox(root, values=["Pending", "Completed"], state="readonly")
status_box.set("Pending")
status_box.grid(row=1, column=3, padx=5, pady=5)

tk.Label(root, text="Marks").grid(row=2, column=0, padx=5, pady=5)
marks_entry = tk.Entry(root)
marks_entry.grid(row=2, column=1, padx=5, pady=5)

tk.Label(root, text="Remarks").grid(row=2, column=2, padx=5, pady=5)
remarks_entry = tk.Entry(root)
remarks_entry.grid(row=2, column=3, padx=5, pady=5)

tk.Button(root, text="Add Submission", command=add_record).grid(
    row=3, column=0, columnspan=2, pady=10
)

tk.Button(root, text="Export CSV", command=export_csv).grid(
    row=3, column=2, columnspan=2, pady=10
)

tk.Label(root, text="Filter").grid(row=4, column=0, padx=5, pady=5)

filter_box = ttk.Combobox(
    root,
    values=["All", "Pending", "Completed"],
    state="readonly"
)
filter_box.set("All")
filter_box.grid(row=4, column=1, padx=5, pady=5)
filter_box.bind("<<ComboboxSelected>>", lambda event: show_data())

columns = (
    "Enrollment",
    "Name",
    "Assignment",
    "Status",
    "Marks",
    "Remarks"
)

table = ttk.Treeview(root, columns=columns, show="headings")

for column in columns:
    table.heading(column, text=column)
    table.column(column, width=120)

table.grid(row=5, column=0, columnspan=4, padx=10, pady=10)

show_data()

root.mainloop()
