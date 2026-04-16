import flet as ft
from datetime import datetime
import database
import os

# ═══════════════════════════════════════
# THEME COLORS
# ═══════════════════════════════════════
BG      = "#0a0f1e"
BG2     = "#111827"
ACCENT  = "#1d4ed8"
ACCENT2 = "#3b82f6"
SUCCESS = "#22c55e"
DANGER  = "#ef4444"
WARNING = "#f59e0b"
TEXT    = "#f1f5f9"
TEXT2   = "#94a3b8"
CARD    = "#1e293b"

CAT_COLORS = [
    "#3b82f6", "#8b5cf6", "#ec4899",
    "#f59e0b", "#22c55e", "#ef4444",
    "#06b6d4", "#f97316",
]

CAT_ICONS = {
    "food":          "🍔",
    "travel":        "✈️",
    "bills":         "💡",
    "shopping":      "🛍️",
    "health":        "💊",
    "entertainment": "🎬",
    "education":     "📚",
    "other":         "💸",
}


def get_icon(category):
    return CAT_ICONS.get(category.lower(), "💸")


# ═══════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════
def main(page: ft.Page):

    page.title      = "Expense Tracker"
    page.bgcolor    = BG
    page.padding    = 0
    page.theme_mode = ft.ThemeMode.DARK

    database.create_tables()

    # ── State ──
    current_month = {"value": datetime.now().strftime("%Y-%m")}
    current_tab   = {"value": 0}
    delete_target = {"id": None}
    edit_target   = {"data": None}
    search_month  = {"value": None}

    # ═══════════════════════════════════
    # HELPER — CARD CONTAINER
    # ═══════════════════════════════════
    def card(content, padding=16, margin_bottom=12, bgcolor=CARD):
        return ft.Container(
            content=content,
            bgcolor=bgcolor,
            border_radius=16,
            padding=padding,
            margin=ft.margin.only(bottom=margin_bottom),
        )

    # ═══════════════════════════════════
    # SPENDING BREAKDOWN (replaces pie chart)
    # ═══════════════════════════════════
    def build_pie_chart(month):
        data = database.get_category_totals(month)

        if not data:
            return ft.Container(
                content=ft.Text("No data yet!", color=TEXT2, size=14),
                alignment=ft.Alignment(0, 0),        # ✅ Fixed
                height=80,
            )

        total = sum(d[1] for d in data)
        rows  = []

        for i, (cat, amt) in enumerate(data):
            color   = CAT_COLORS[i % len(CAT_COLORS)]
            percent = (amt / total) * 100

            rows.append(
                ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text(
                                    f"{get_icon(cat)} {cat}",
                                    color=TEXT,
                                    size=12,
                                    expand=True,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                    max_lines=1,
                                ),
                                ft.Text(
                                    f"₹{amt:.0f}",
                                    color=TEXT2,
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    f"{percent:.0f}%",
                                    color=color,
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ],
                            spacing=8,
                        ),
                        ft.Stack(
                            controls=[
                                ft.Container(
                                    width=float("inf"),
                                    height=8,
                                    bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                                    border_radius=5,
                                ),
                                ft.Container(
                                    width=percent * 2.5,
                                    height=8,
                                    bgcolor=color,
                                    border_radius=5,
                                ),
                            ],
                            clip_behavior=ft.ClipBehavior.HARD_EDGE,
                        ),
                    ],
                    spacing=6,
                )
            )

        return ft.Column(
            controls=[
                ft.Text(
                    "💰 Spending Breakdown",
                    size=15,
                    weight=ft.FontWeight.BOLD,
                    color=TEXT,
                ),
                ft.Container(height=4),
                *rows,
            ],
            spacing=14,
        )

    # ═══════════════════════════════════
    # EXPENSE CARD
    # ═══════════════════════════════════
    def make_expense_card(e_id, category, amount, date):

        def on_delete(ev):
            delete_target["id"] = e_id
            confirm_dialog.open = True
            page.update()

        def on_edit(ev):
            edit_target["data"] = {
                "id":       e_id,
                "category": category,
                "amount":   str(amount),
                "date":     date,
            }
            open_edit_sheet()

        return ft.Container(
            content=ft.Row(
                controls=[
                    # ── Icon ──
                    ft.Container(
                        content=ft.Text(get_icon(category), size=20),
                        bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
                        border_radius=12,
                        width=42,
                        height=42,
                        alignment=ft.Alignment(0, 0),        # ✅ Fixed
                    ),
                    # ── Details ──
                    ft.Column(
                        controls=[
                            ft.Text(
                                category,
                                size=13,
                                weight=ft.FontWeight.BOLD,
                                color=TEXT,
                                overflow=ft.TextOverflow.ELLIPSIS,
                                max_lines=1,
                            ),
                            ft.Text(
                                date,
                                size=10,
                                color=TEXT2,
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    # ── Amount + Actions ──
                    ft.Column(
                        controls=[
                            ft.Text(
                                f"₹{amount:.0f}",
                                size=13,
                                weight=ft.FontWeight.BOLD,
                                color=DANGER,
                            ),
                            ft.Row(
                                controls=[
                                    ft.IconButton(
                                        icon=ft.Icons.EDIT_OUTLINED,        # ✅ Fixed
                                        icon_color=ACCENT2,
                                        icon_size=16,
                                        on_click=on_edit,
                                        padding=0,
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE,       # ✅ Fixed
                                        icon_color=DANGER,
                                        icon_size=16,
                                        on_click=on_delete,
                                        padding=0,
                                    ),
                                ],
                                spacing=0,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                        spacing=0,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            bgcolor=BG2,
            border_radius=14,
            padding=ft.padding.symmetric(horizontal=12, vertical=10),
            margin=ft.margin.only(bottom=8),
        )

    # ═══════════════════════════════════
    # SALARY DIALOG
    # ═══════════════════════════════════
    salary_input = ft.TextField(
        label="Enter your salary (₹)",
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=12,
        filled=True,
        fill_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
        label_style=ft.TextStyle(color=TEXT2),
        text_style=ft.TextStyle(color=TEXT),
        border_color=ft.Colors.TRANSPARENT,
        focused_border_color=ACCENT2,
    )

    def save_salary(e):
        val = salary_input.value.strip()
        if val:
            database.set_salary(current_month["value"], float(val))
        salary_dialog.open = False
        salary_input.value = ""
        refresh_home()
        page.update()

    def close_salary_dialog():
        salary_dialog.open = False
        page.update()

    salary_dialog = ft.AlertDialog(
        modal=True,
        bgcolor=CARD,
        title=ft.Text("💵 Monthly Salary", color=TEXT, weight=ft.FontWeight.BOLD),
        content=ft.Column(
            controls=[
                ft.Text(
                    "Set your salary for this month to track balance.",
                    color=TEXT2,
                    size=13,
                ),
                salary_input,
            ],
            spacing=12,
            tight=True,
        ),
        actions=[
            ft.TextButton(
                "Skip",
                on_click=lambda e: close_salary_dialog(),
                style=ft.ButtonStyle(color=TEXT2),
            ),
            ft.ElevatedButton(
                "Save",
                on_click=save_salary,
                bgcolor=ACCENT,
                color=TEXT,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(salary_dialog)

    def open_salary_dialog():
        existing = database.get_salary(current_month["value"])
        if existing:
            salary_input.value = str(existing)
        salary_dialog.open = True
        page.update()

    # ═══════════════════════════════════
    # CONFIRM DELETE DIALOG
    # ═══════════════════════════════════
    def on_confirm_delete(e):
        database.delete_expense(delete_target["id"])
        confirm_dialog.open = False
        refresh_home()
        page.update()

    def on_cancel_delete(e):
        confirm_dialog.open = False
        page.update()

    confirm_dialog = ft.AlertDialog(
        modal=True,
        bgcolor=CARD,
        title=ft.Text("Delete Expense?", color=TEXT),
        content=ft.Text("This action cannot be undone.", color=TEXT2),
        actions=[
            ft.TextButton(
                "Cancel",
                on_click=on_cancel_delete,
                style=ft.ButtonStyle(color=TEXT2),
            ),
            ft.TextButton(
                "Delete",
                on_click=on_confirm_delete,
                style=ft.ButtonStyle(color=DANGER),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(confirm_dialog)

    # ═══════════════════════════════════
    # EDIT BOTTOM SHEET
    # ═══════════════════════════════════
    edit_category = ft.TextField(
        label="Category",
        border_radius=12,
        filled=True,
        fill_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
        label_style=ft.TextStyle(color=TEXT2),
        text_style=ft.TextStyle(color=TEXT),
        border_color=ft.Colors.TRANSPARENT,
        focused_border_color=ACCENT2,
    )

    edit_amount = ft.TextField(
        label="Amount (₹)",
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=12,
        filled=True,
        fill_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
        label_style=ft.TextStyle(color=TEXT2),
        text_style=ft.TextStyle(color=TEXT),
        border_color=ft.Colors.TRANSPARENT,
        focused_border_color=ACCENT2,
    )

    edit_date = ft.TextField(
        label="Date (YYYY-MM-DD)",
        border_radius=12,
        filled=True,
        fill_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
        label_style=ft.TextStyle(color=TEXT2),
        text_style=ft.TextStyle(color=TEXT),
        border_color=ft.Colors.TRANSPARENT,
        focused_border_color=ACCENT2,
    )

    def save_edit(e):
        database.edit_expense(
            edit_target["data"]["id"],
            edit_category.value.strip(),
            float(edit_amount.value.strip()),
            edit_date.value.strip(),
        )
        edit_sheet.open = False
        refresh_home()
        page.update()

    edit_sheet = ft.BottomSheet(
        bgcolor=CARD,
        content=ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "✏️ Edit Expense",
                        size=17,
                        weight=ft.FontWeight.BOLD,
                        color=TEXT,
                    ),
                    edit_category,
                    edit_amount,
                    edit_date,
                    ft.ElevatedButton(
                        "Save Changes",
                        on_click=save_edit,
                        bgcolor=ACCENT,
                        color=TEXT,
                        width=float("inf"),
                        height=48,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=12)
                        ),
                    ),
                ],
                spacing=14,
            ),
            padding=24,
        ),
    )

    page.overlay.append(edit_sheet)

    def open_edit_sheet():
        data                = edit_target["data"]
        edit_category.value = data["category"]
        edit_amount.value   = data["amount"]
        edit_date.value     = data["date"]
        edit_sheet.open     = True
        page.update()

    # ═══════════════════════════════════
    # MONTH SUMMARY SHEET
    # ═══════════════════════════════════
    summary_note = ft.TextField(
        label="Write your month summary...",
        multiline=True,
        min_lines=3,
        max_lines=5,
        border_radius=12,
        filled=True,
        fill_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
        label_style=ft.TextStyle(color=TEXT2),
        text_style=ft.TextStyle(color=TEXT),
        border_color=ft.Colors.TRANSPARENT,
        focused_border_color=ACCENT2,
    )

    def save_summary_note(e):
        month       = current_month["value"]
        total_spent = database.get_total(month)
        salary      = database.get_salary(month) or 0
        saved       = salary - total_spent
        database.save_summary(month, summary_note.value, total_spent, saved)
        summary_sheet.open  = False
        page.snack_bar      = ft.SnackBar(
            ft.Text("✅ Summary saved!", color=TEXT),
            bgcolor=SUCCESS,
        )
        page.snack_bar.open = True
        page.update()

    summary_sheet = ft.BottomSheet(
        bgcolor=CARD,
        content=ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "📝 Month End Summary",
                        size=17,
                        weight=ft.FontWeight.BOLD,
                        color=TEXT,
                    ),
                    ft.Text(
                        "Write notes about this month's spending.",
                        color=TEXT2,
                        size=13,
                    ),
                    summary_note,
                    ft.ElevatedButton(
                        "Save Summary",
                        on_click=save_summary_note,
                        bgcolor=ACCENT,
                        color=TEXT,
                        width=float("inf"),
                        height=48,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=12)
                        ),
                    ),
                ],
                spacing=14,
            ),
            padding=24,
        ),
    )

    page.overlay.append(summary_sheet)

    def open_summary_sheet():
        month   = search_month["value"] or current_month["value"]
        summary = database.get_summary(month)
        if summary:
            summary_note.value = summary[2]
        summary_sheet.open = True
        page.update()

    # ═══════════════════════════════════
    # HOME TAB
    # ═══════════════════════════════════
    home_content = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=0,
        expand=True,
    )

    def refresh_home():
        month       = current_month["value"]            # Always current month on home
        expenses    = database.get_month(month)
        total_spent = database.get_total(month)
        salary      = database.get_salary(month)
        remaining   = (salary - total_spent) if salary else None
        summary     = database.get_summary(month)

        # ── Budget Alert ──
        alert = []
        if salary and total_spent >= salary * 0.8:
            pct = (total_spent / salary) * 100
            alert = [
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.WARNING_AMBER, color=WARNING, size=18),  # ✅ Fixed
                            ft.Text(
                                f"⚠️ Used {pct:.0f}% of budget!",
                                color=WARNING,
                                size=12,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        spacing=8,
                    ),
                    bgcolor=ft.Colors.with_opacity(0.15, WARNING),
                    border_radius=12,
                    padding=10,
                    margin=ft.margin.only(bottom=10),
                )
            ]

        # ── Salary Card ──
        salary_card = card(
            ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(
                                f"👋 {datetime.now().strftime('%B %Y')}",
                                size=13,
                                color=TEXT2,
                            ),
                            ft.TextButton(
                                "Set Salary",
                                on_click=lambda e: open_salary_dialog(),
                                style=ft.ButtonStyle(color=ACCENT2),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Divider(color=ft.Colors.WHITE12),
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text("Salary", size=10, color=TEXT2),
                                    ft.Text(
                                        f"₹{salary:.0f}" if salary else "—",
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEXT,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                        max_lines=1,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                expand=True,
                                spacing=2,
                            ),
                            ft.VerticalDivider(color=ft.Colors.WHITE12, width=1),
                            ft.Column(
                                controls=[
                                    ft.Text("Spent", size=10, color=TEXT2),
                                    ft.Text(
                                        f"₹{total_spent:.0f}",
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color=DANGER,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                        max_lines=1,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                expand=True,
                                spacing=2,
                            ),
                            ft.VerticalDivider(color=ft.Colors.WHITE12, width=1),
                            ft.Column(
                                controls=[
                                    ft.Text("Left", size=10, color=TEXT2),
                                    ft.Text(
                                        f"₹{remaining:.0f}" if remaining is not None else "—",
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color=SUCCESS if remaining and remaining > 0 else DANGER,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                        max_lines=1,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                expand=True,
                                spacing=2,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                spacing=10,
            )
        )

        # ── Summary Card ──
        summary_card = []
        if summary:
            summary_card = [
                card(
                    ft.Column(
                        controls=[
                            ft.Text(
                                "📝 Month Summary",
                                size=13,
                                weight=ft.FontWeight.BOLD,
                                color=TEXT,
                            ),
                            ft.Text(summary[2], color=TEXT2, size=12),
                            ft.Row(
                                controls=[
                                    ft.Text(f"Spent: ₹{summary[3]:.0f}", color=DANGER, size=12),
                                    ft.Text(f"Saved: ₹{summary[4]:.0f}", color=SUCCESS, size=12),
                                ],
                                spacing=16,
                            ),
                        ],
                        spacing=8,
                    )
                )
            ]

        # ── Expense List ──
        exp_list = [
            ft.Text(
                "Recent Expenses",
                size=14,
                weight=ft.FontWeight.BOLD,
                color=TEXT,
            )
        ]

        if not expenses:
            exp_list.append(
                ft.Container(
                    content=ft.Text("No expenses yet!", color=TEXT2, size=13),
                    alignment=ft.Alignment(0, 0),        # ✅ Fixed
                    height=60,
                )
            )
        else:
            for e in expenses:
                exp_list.append(make_expense_card(e[0], e[1], e[2], e[3]))

        home_content.controls = (
            alert
            + [salary_card]
            + summary_card
            + [
                ft.Container(
                    content=ft.Column(controls=exp_list, spacing=8),
                    padding=ft.padding.only(bottom=80),
                )
            ]
        )
        page.update()

    # ═══════════════════════════════════
    # ADD TAB
    # ═══════════════════════════════════
    add_category = ft.TextField(
        label="Category",
        hint_text="e.g. Food, Travel",
        border_radius=12,
        filled=True,
        fill_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
        label_style=ft.TextStyle(color=TEXT2),
        text_style=ft.TextStyle(color=TEXT),
        border_color=ft.Colors.TRANSPARENT,
        focused_border_color=ACCENT2,
        expand=True,
    )

    add_amount = ft.TextField(
        label="Amount (₹)",
        hint_text="e.g. 500",
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=12,
        filled=True,
        fill_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
        label_style=ft.TextStyle(color=TEXT2),
        text_style=ft.TextStyle(color=TEXT),
        border_color=ft.Colors.TRANSPARENT,
        focused_border_color=ACCENT2,
        expand=True,
    )

    add_date = ft.TextField(
        label="Date (YYYY-MM-DD)",
        hint_text=datetime.now().strftime("%Y-%m-%d"),
        border_radius=12,
        filled=True,
        fill_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
        label_style=ft.TextStyle(color=TEXT2),
        text_style=ft.TextStyle(color=TEXT),
        border_color=ft.Colors.TRANSPARENT,
        focused_border_color=ACCENT2,
        value=datetime.now().strftime("%Y-%m-%d"),
    )

    selected_cat = {"value": ""}
    cat_chip_row = ft.Row(wrap=True, spacing=8)
    quick_cats   = ["Food", "Travel", "Bills", "Shopping", "Health", "Entertainment", "Education", "Other"]

    def make_chip(label):
        is_sel = selected_cat["value"] == label

        def on_sel(e):
            selected_cat["value"] = label
            add_category.value    = label
            refresh_chips()

        return ft.Container(
            content=ft.Text(
                f"{get_icon(label)} {label}",
                color=TEXT if is_sel else TEXT2,
                size=11,
                weight=ft.FontWeight.BOLD if is_sel else ft.FontWeight.NORMAL,
            ),
            bgcolor=ACCENT if is_sel else ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
            border_radius=20,
            padding=ft.padding.symmetric(horizontal=10, vertical=6),
            on_click=on_sel,
        )

    def refresh_chips():
        cat_chip_row.controls = [make_chip(c) for c in quick_cats]
        page.update()

    refresh_chips()

    def on_add_expense(e):
        cat  = add_category.value.strip()
        amt  = add_amount.value.strip()
        date = add_date.value.strip() or datetime.now().strftime("%Y-%m-%d")

        if not cat or not amt:
            page.snack_bar      = ft.SnackBar(
                ft.Text("Please fill category and amount!", color=TEXT),
                bgcolor=DANGER,
            )
            page.snack_bar.open = True
            page.update()
            return

        try:
            float(amt)
        except ValueError:
            page.snack_bar      = ft.SnackBar(
                ft.Text("Amount must be a number!", color=TEXT),
                bgcolor=DANGER,
            )
            page.snack_bar.open = True
            page.update()
            return

        database.add_expense(cat, float(amt), date)
        add_category.value    = ""
        add_amount.value      = ""
        add_date.value        = datetime.now().strftime("%Y-%m-%d")
        selected_cat["value"] = ""
        refresh_chips()

        page.snack_bar      = ft.SnackBar(
            ft.Text("✅ Expense added!", color=TEXT),
            bgcolor=SUCCESS,
        )
        page.snack_bar.open = True
        refresh_home()
        page.update()

    add_tab_content = ft.Column(
        controls=[
            ft.Container(height=10),
            ft.Text("➕ Add Expense", size=20, weight=ft.FontWeight.BOLD, color=TEXT),
            ft.Text("Fill in the details below", color=TEXT2, size=12),
            ft.Container(height=4),
            add_category,
            add_amount,
            add_date,
            ft.Text("Quick Category", color=TEXT2, size=12),
            cat_chip_row,
            ft.Container(height=4),
            ft.ElevatedButton(
                "ADD EXPENSE",
                on_click=on_add_expense,
                bgcolor=ACCENT,
                color=TEXT,
                width=float("inf"),
                height=50,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=14)),
            ),
        ],
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    # ═══════════════════════════════════
    # ANALYTICS TAB
    # ═══════════════════════════════════
    analytics_content = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=0,
        expand=True,
    )

    search_field = ft.TextField(
        label="Search month (YYYY-MM)",
        hint_text="e.g. 2025-01",
        border_radius=12,
        filled=True,
        fill_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
        label_style=ft.TextStyle(color=TEXT2),
        text_style=ft.TextStyle(color=TEXT),
        border_color=ft.Colors.TRANSPARENT,
        focused_border_color=ACCENT2,
        prefix_icon=ft.Icons.SEARCH,                    # ✅ Fixed
        expand=True,
    )

    def on_search(e):
        val = search_field.value.strip()
        search_month["value"] = val if val else None
        refresh_analytics()

    def refresh_analytics():
        month       = search_month["value"] or current_month["value"]
        total_spent = database.get_total(month)
        salary      = database.get_salary(month)
        remaining   = (salary - total_spent) if salary else None
        months      = database.get_months()

        db_size = os.path.getsize("expenses.db") if os.path.exists("expenses.db") else 0
        db_kb   = db_size / 1024

        month_pills = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(m, color=TEXT if m == month else TEXT2, size=11),
                    bgcolor=ACCENT if m == month else ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
                    border_radius=20,
                    padding=ft.padding.symmetric(horizontal=10, vertical=6),
                    on_click=lambda e, mo=m: select_month(mo),
                )
                for m in months
            ],
            wrap=True,
            spacing=6,
        )

        analytics_content.controls = [
            ft.Container(height=10),
            ft.Text("📊 Analytics", size=20, weight=ft.FontWeight.BOLD, color=TEXT),
            ft.Container(height=4),

            # Search row
            ft.Row(
                controls=[
                    search_field,
                    ft.IconButton(
                        icon=ft.Icons.SEARCH,           # ✅ Fixed
                        icon_color=ACCENT2,
                        on_click=on_search,
                        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                    ),
                ],
                spacing=8,
            ),

            ft.Text("All Months", color=TEXT2, size=12),
            month_pills,
            ft.Divider(color=ft.Colors.WHITE12),

            # Stats card
            card(
                ft.Column(
                    controls=[
                        ft.Text(f"📅 {month}", size=14, weight=ft.FontWeight.BOLD, color=TEXT),
                        ft.Row(
                            controls=[
                                ft.Column(
                                    controls=[
                                        ft.Text("Spent", size=10, color=TEXT2),
                                        ft.Text(
                                            f"₹{total_spent:.0f}",
                                            size=16,
                                            weight=ft.FontWeight.BOLD,
                                            color=DANGER,
                                            overflow=ft.TextOverflow.ELLIPSIS,
                                            max_lines=1,
                                        ),
                                    ],
                                    expand=True,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=2,
                                ),
                                ft.VerticalDivider(color=ft.Colors.WHITE12, width=1),
                                ft.Column(
                                    controls=[
                                        ft.Text("Salary", size=10, color=TEXT2),
                                        ft.Text(
                                            f"₹{salary:.0f}" if salary else "—",
                                            size=16,
                                            weight=ft.FontWeight.BOLD,
                                            color=TEXT,
                                            overflow=ft.TextOverflow.ELLIPSIS,
                                            max_lines=1,
                                        ),
                                    ],
                                    expand=True,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=2,
                                ),
                                ft.VerticalDivider(color=ft.Colors.WHITE12, width=1),
                                ft.Column(
                                    controls=[
                                        ft.Text("Saved", size=10, color=TEXT2),
                                        ft.Text(
                                            f"₹{remaining:.0f}" if remaining is not None else "—",
                                            size=16,
                                            weight=ft.FontWeight.BOLD,
                                            color=SUCCESS if remaining and remaining > 0 else DANGER,
                                            overflow=ft.TextOverflow.ELLIPSIS,
                                            max_lines=1,
                                        ),
                                    ],
                                    expand=True,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=2,
                                ),
                            ],
                        ),
                    ],
                    spacing=10,
                )
            ),

            # Spending breakdown
            card(build_pie_chart(month)),

            # Month summary button
            ft.ElevatedButton(
                "📝 Write Month Summary",
                on_click=lambda e: open_summary_sheet(),
                bgcolor=ft.Colors.with_opacity(0.15, ACCENT),
                color=ACCENT2,
                width=float("inf"),
                height=46,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
            ),

            # Data usage card
            card(
                ft.Column(
                    controls=[
                        ft.Text("🗄️ Data Usage", size=14, weight=ft.FontWeight.BOLD, color=TEXT),
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.STORAGE, color=ACCENT2, size=18),     # ✅ Fixed
                                ft.Text(f"Database size: {db_kb:.2f} KB", color=TEXT2, size=12),
                            ],
                            spacing=8,
                        ),
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.RECEIPT_LONG, color=ACCENT2, size=18), # ✅ Fixed
                                ft.Text(f"Total months tracked: {len(months)}", color=TEXT2, size=12),
                            ],
                            spacing=8,
                        ),
                    ],
                    spacing=10,
                )
            ),

            ft.Container(height=80),
        ]
        page.update()

    def select_month(month):
        search_month["value"] = month
        search_field.value    = month
        refresh_analytics()

    # ═══════════════════════════════════
    # BOTTOM NAVIGATION
    # ═══════════════════════════════════
    tab_body = ft.Container(
        content=home_content,
        expand=True,
        padding=ft.padding.symmetric(horizontal=16),
    )

    def on_nav_change(e):
        idx = e.control.selected_index
        current_tab["value"] = idx

        if idx == 0:
            tab_body.content = home_content
            refresh_home()
        elif idx == 1:
            tab_body.content = ft.Container(
                content=add_tab_content,
                padding=ft.padding.symmetric(horizontal=16),
                expand=True,
            )
            page.update()
        elif idx == 2:
            tab_body.content = ft.Container(
                content=analytics_content,
                padding=ft.padding.symmetric(horizontal=16),
                expand=True,
            )
            refresh_analytics()

        page.update()

    nav_bar = ft.NavigationBar(
        bgcolor=CARD,
        indicator_color=ft.Colors.with_opacity(0.2, ACCENT2),
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.HOME_OUTLINED,            # ✅ Fixed
                selected_icon=ft.Icons.HOME,
                label="Home",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.ADD_CIRCLE_OUTLINE,       # ✅ Fixed
                selected_icon=ft.Icons.ADD_CIRCLE,
                label="Add",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.BAR_CHART_OUTLINED,       # ✅ Fixed
                selected_icon=ft.Icons.BAR_CHART,
                label="Analytics",
            ),
        ],
        on_change=on_nav_change,
        selected_index=0,
    )

    # ═══════════════════════════════════
    # MAIN LAYOUT
    # ═══════════════════════════════════
    page.add(
        ft.Column(
            controls=[
                # App Bar
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(
                                "💙 Expenses",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=TEXT,
                                expand=True,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED,  # ✅ Fixed
                                icon_color=ACCENT2,
                                tooltip="Set Salary",
                                on_click=lambda e: open_salary_dialog(),
                            ),
                        ],
                    ),
                    bgcolor=BG2,
                    padding=ft.padding.only(left=16, right=8, top=40, bottom=12),
                ),

                tab_body,
                nav_bar,
            ],
            expand=True,
            spacing=0,
        )
    )

    # ── Startup ──
    def check_salary():
        if database.get_salary(current_month["value"]) is None:
            salary_dialog.open = True
            page.update()

    refresh_home()
    check_salary()


ft.run(main)                                            # ✅ Flet 0.80+
