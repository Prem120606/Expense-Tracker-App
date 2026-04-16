import sqlite3
from datetime import datetime

import os

DB = os.path.join(os.getcwd(), "expenses.db")


def connect():
    return sqlite3.connect(DB)


def create_tables():
    conn = connect()
    c = conn.cursor()

    # Expenses table
    c.execute("""
        CREATE TABLE IF NOT EXISTS expenses(
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            amount   REAL,
            date     TEXT
        )
    """)

    # Salary table — one entry per month
    c.execute("""
        CREATE TABLE IF NOT EXISTS salary(
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            month  TEXT UNIQUE,
            amount REAL
        )
    """)

    # Monthly summary/note table
    c.execute("""
        CREATE TABLE IF NOT EXISTS monthly_summary(
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            month       TEXT UNIQUE,
            note        TEXT,
            total_spent REAL,
            saved       REAL
        )
    """)

    conn.commit()
    conn.close()


# ── Expense Functions ──

def add_expense(category, amount, date):
    conn = connect()
    c = conn.cursor()
    c.execute(
        "INSERT INTO expenses(category, amount, date) VALUES(?,?,?)",
        (category, amount, date)
    )
    conn.commit()
    conn.close()


def get_month(month):
    conn = connect()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM expenses WHERE date LIKE ? ORDER BY id DESC",
        (month + "%",)
    )
    data = c.fetchall()
    conn.close()
    return data


def get_months():
    conn = connect()
    c = conn.cursor()
    c.execute(
        "SELECT DISTINCT substr(date,1,7) FROM expenses ORDER BY date DESC"
    )
    data = [m[0] for m in c.fetchall()]
    conn.close()
    return data


def delete_expense(expense_id):
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    conn.commit()
    conn.close()


def edit_expense(expense_id, category, amount, date):
    conn = connect()
    c = conn.cursor()
    c.execute(
        "UPDATE expenses SET category=?, amount=?, date=? WHERE id=?",
        (category, amount, date, expense_id)
    )
    conn.commit()
    conn.close()


def get_total(month):
    conn = connect()
    c = conn.cursor()
    c.execute(
        "SELECT SUM(amount) FROM expenses WHERE date LIKE ?",
        (month + "%",)
    )
    total = c.fetchone()[0]
    conn.close()
    return total if total else 0


def get_category_totals(month):
    conn = connect()
    c = conn.cursor()
    c.execute(
        "SELECT category, SUM(amount) FROM expenses WHERE date LIKE ? GROUP BY category",
        (month + "%",)
    )
    data = c.fetchall()
    conn.close()
    return data


# ── Salary Functions ──

def set_salary(month, amount):
    conn = connect()
    c = conn.cursor()
    c.execute(
        "INSERT INTO salary(month, amount) VALUES(?,?) ON CONFLICT(month) DO UPDATE SET amount=?",
        (month, amount, amount)
    )
    conn.commit()
    conn.close()


def get_salary(month):
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT amount FROM salary WHERE month=?", (month,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


# ── Monthly Summary Functions ──

def save_summary(month, note, total_spent, saved):
    conn = connect()
    c = conn.cursor()
    c.execute("""
        INSERT INTO monthly_summary(month, note, total_spent, saved)
        VALUES(?,?,?,?)
        ON CONFLICT(month) DO UPDATE SET note=?, total_spent=?, saved=?
    """, (month, note, total_spent, saved, note, total_spent, saved))
    conn.commit()
    conn.close()


def get_summary(month):
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT * FROM monthly_summary WHERE month=?", (month,))
    row = c.fetchone()
    conn.close()
    return row


def get_all_summaries():
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT * FROM monthly_summary ORDER BY month DESC")
    data = c.fetchall()
    conn.close()
    return data