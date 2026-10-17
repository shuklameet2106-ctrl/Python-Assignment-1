import re
import tkinter as tk
from tkinter import ttk, messagebox

import mysql.connector
from mysql.connector import Error

EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
PHONE_PATTERN = re.compile(r"^\+?[0-9]{7,15}$")
CATEGORIES = ["Family", "Friend", "Faculty", "Work", "Other"]


def connect():
    return mysql.connector.connect(
        host="localhost", user="root", password="", database="contacts_db"
    )


def setup_database():
    root_connection = mysql.connector.connect(host="localhost", user="root", password="")
    cursor = root_connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS contacts_db")
    root_connection.close()

    connection = connect()
    cursor = connection.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS Contact ("
        "id INT AUTO_INCREMENT PRIMARY KEY, "
        "name VARCHAR(100) NOT NULL, "
        "email VARCHAR(150) NOT NULL UNIQUE, "
        "phone VARCHAR(20), "
        "category VARCHAR(30), "
        "notes TEXT)"
    )
    cursor.execute("SHOW INDEX FROM Contact WHERE Key_name = 'idx_name'")
    if not cursor.fetchall():
        cursor.execute("CREATE INDEX idx_name ON Contact (name)")
    connection.commit()
    connection.close()


def run_query(sql, params=(), fetch=False):
    connection = connect()
    try:
        cursor = connection.cursor()
        cursor.execute(sql, params)
        if fetch:
            return cursor.fetchall()
        connection.commit()
        return cursor.rowcount
    finally:
        connection.close()


class ContactManager:
    def __init__(self, window):
        self.window = window
        window.title("Contact Manager")
        self.selected_id = None

        self.name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.category_var = tk.StringVar(value=CATEGORIES[0])
        self.search_var = tk.StringVar()
        self.search_by = tk.StringVar(value="name")
        self.sort_var = tk.StringVar(value="name")
        self.favourite_var = tk.BooleanVar()

        form = tk.Frame(window, padx=10, pady=10)
        form.grid(row=0, column=0, sticky="n")

        tk.Label(form, text="Name").grid(row=0, column=0, sticky="w")
        tk.Entry(form, textvariable=self.name_var, width=30).grid(row=0, column=1)
        tk.Label(form, text="Email").grid(row=1, column=0, sticky="w")
        tk.Entry(form, textvariable=self.email_var, width=30).grid(row=1, column=1)
        tk.Label(form, text="Phone").grid(row=2, column=0, sticky="w")
        tk.Entry(form, textvariable=self.phone_var, width=30).grid(row=2, column=1)
        tk.Label(form, text="Category").grid(row=3, column=0, sticky="w")
        ttk.Combobox(
            form, textvariable=self.category_var, values=CATEGORIES, state="readonly", width=27
        ).grid(row=3, column=1)
        tk.Label(form, text="Notes").grid(row=4, column=0, sticky="nw")
        self.notes_text = tk.Text(form, width=23, height=5)
        self.notes_text.grid(row=4, column=1)
        tk.Checkbutton(form, text="Mark as favourite", variable=self.favourite_var).grid(
            row=5, column=1, sticky="w"
        )

        buttons = tk.Frame(form, pady=8)
        buttons.grid(row=6, column=0, columnspan=2)
        tk.Button(buttons, text="Add", command=self.add_contact).pack(side="left", padx=3)
        tk.Button(buttons, text="Update", command=self.update_contact).pack(side="left", padx=3)
        tk.Button(buttons, text="Delete", command=self.delete_contact).pack(side="left", padx=3)
        tk.Button(buttons, text="Clear", command=self.clear_form).pack(side="left", padx=3)

        right = tk.Frame(window, padx=10, pady=10)
        right.grid(row=0, column=1, sticky="n")

        search_frame = tk.Frame(right)
        search_frame.pack(fill="x")
        tk.Entry(search_frame, textvariable=self.search_var, width=22).pack(side="left")
        for label in ("name", "email", "phone"):
            tk.Radiobutton(
                search_frame, text=label, variable=self.search_by, value=label
            ).pack(side="left")
        tk.Button(search_frame, text="Search", command=self.refresh).pack(side="left", padx=3)

        sort_frame = tk.Frame(right)
        sort_frame.pack(fill="x", pady=4)
        tk.Label(sort_frame, text="Sort by").pack(side="left")
        ttk.Combobox(
            sort_frame,
            textvariable=self.sort_var,
            values=["name", "email", "phone", "category"],
            state="readonly",
            width=12,
        ).pack(side="left", padx=4)
        self.sort_var.trace_add("write", lambda *args: self.refresh())

        list_frame = tk.Frame(right)
        list_frame.pack()
        self.listbox = tk.Listbox(list_frame, width=70, height=18)
        scroll = tk.Scrollbar(list_frame, command=self.listbox.yview)
        self.listbox.config(yscrollcommand=scroll.set)
        self.listbox.pack(side="left")
        scroll.pack(side="left", fill="y")
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        self.rows = []
        self.refresh()

    def read_form(self):
        name = self.name_var.get().strip()
        email = self.email_var.get().strip().lower()
        phone = self.phone_var.get().strip()
        category = self.category_var.get()
        notes = self.notes_text.get("1.0", "end").strip()
        if self.favourite_var.get():
            notes = "[Favourite] " + notes

        if not name:
            messagebox.showerror("Error", "Name is required")
            return None
        if not EMAIL_PATTERN.match(email):
            messagebox.showerror("Error", "Invalid email")
            return None
        if phone and not PHONE_PATTERN.match(phone):
            messagebox.showerror("Error", "Invalid phone number")
            return None
        return name, email, phone, category, notes

    def add_contact(self):
        data = self.read_form()
        if data is None:
            return
        try:
            run_query(
                "INSERT INTO Contact (name, email, phone, category, notes) "
                "VALUES (%s, %s, %s, %s, %s)",
                data,
            )
        except mysql.connector.IntegrityError:
            messagebox.showerror("Error", "Duplicate email")
            return
        except Error as error:
            messagebox.showerror("Database error", str(error))
            return
        self.clear_form()
        self.refresh()

    def update_contact(self):
        if self.selected_id is None:
            messagebox.showwarning("Select", "Select a contact first")
            return
        data = self.read_form()
        if data is None:
            return
        try:
            run_query(
                "UPDATE Contact SET name=%s, email=%s, phone=%s, category=%s, notes=%s "
                "WHERE id=%s",
                data + (self.selected_id,),
            )
        except mysql.connector.IntegrityError:
            messagebox.showerror("Error", "Duplicate email")
            return
        except Error as error:
            messagebox.showerror("Database error", str(error))
            return
        self.clear_form()
        self.refresh()

    def delete_contact(self):
        if self.selected_id is None:
            messagebox.showwarning("Select", "Select a contact first")
            return
        if not messagebox.askyesno("Confirm", "Delete this contact?"):
            return
        try:
            run_query("DELETE FROM Contact WHERE id=%s", (self.selected_id,))
        except Error as error:
            messagebox.showerror("Database error", str(error))
            return
        self.clear_form()
        self.refresh()

    def clear_form(self):
        self.selected_id = None
        self.name_var.set("")
        self.email_var.set("")
        self.phone_var.set("")
        self.category_var.set(CATEGORIES[0])
        self.favourite_var.set(False)
        self.notes_text.delete("1.0", "end")

    def refresh(self):
        column = self.search_by.get()
        sort_column = self.sort_var.get()
        if column not in ("name", "email", "phone") or sort_column not in (
            "name", "email", "phone", "category"
        ):
            return
        term = self.search_var.get().strip()
        try:
            self.rows = run_query(
                "SELECT id, name, email, phone, category, notes FROM Contact "
                "WHERE " + column + " LIKE %s ORDER BY " + sort_column + " LIMIT 1000",
                (term + "%",),
                fetch=True,
            )
        except Error as error:
            messagebox.showerror("Database error", str(error))
            return
        self.listbox.delete(0, "end")
        for row in self.rows:
            self.listbox.insert("end", f"{row[1]} | {row[2]} | {row[3]} | {row[4]}")

    def on_select(self, event):
        selection = self.listbox.curselection()
        if not selection:
            return
        row = self.rows[selection[0]]
        self.selected_id = row[0]
        self.name_var.set(row[1])
        self.email_var.set(row[2])
        self.phone_var.set(row[3] or "")
        self.category_var.set(row[4] or CATEGORIES[0])
        notes = row[5] or ""
        self.favourite_var.set(notes.startswith("[Favourite] "))
        if notes.startswith("[Favourite] "):
            notes = notes[len("[Favourite] "):]
        self.notes_text.delete("1.0", "end")
        self.notes_text.insert("1.0", notes)


try:
    setup_database()
except Error as error:
    print("DATABASE ERROR:", error)
    raise SystemExit(1)

window = tk.Tk()
ContactManager(window)
window.mainloop()
