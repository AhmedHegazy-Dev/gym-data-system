import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Optional

from services.gym import Gym
from models.member import Member
from models.trainer import Trainer
from models.enums import MembershipType, PaymentMethod
from models.exception import GymException, ValidationError, BusinessRuleError


class GymApp(tk.Tk):

    def __init__(self, gym: Optional[Gym] = None):
        super().__init__()
        self.gym: Gym = gym if gym is not None else Gym()

        self.title("Gym Management System — Instant Fitness")
        self.geometry("1150x700")
        self.minsize(950, 600)
        self.configure(bg="#0f172a")

        self.current_view: Optional[tk.Frame] = None
        self.nav_buttons = {}

        self._setup_styles()
        self._build_layout()
        self.show_view("dashboard")

    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("Treeview",
                        background="#ffffff",
                        foreground="#1e293b",
                        rowheight=28,
                        fieldbackground="#ffffff",
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading",
                        background="#e2e8f0",
                        foreground="#0f172a",
                        font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", "#3b82f6")], foreground=[("selected", "#ffffff")])

        style.configure("TCombobox", padding=4)
        style.configure("TEntry", padding=4)

    def _build_layout(self):
        self.sidebar = tk.Frame(self, bg="#1e293b", width=220)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        logo_frame = tk.Frame(self.sidebar, bg="#1e293b", pady=20)
        logo_frame.pack(fill=tk.X)

        tk.Label(logo_frame, text="⚡ GYM SYSTEM", font=("Segoe UI", 14, "bold"), fg="#38bdf8", bg="#1e293b").pack()
        tk.Label(logo_frame, text="Instant Management", font=("Segoe UI", 8), fg="#94a3b8", bg="#1e293b").pack()

        nav_items = [
            ("dashboard", "📊 Dashboard"),
            ("members", "👥 Members"),
            ("trainers", "🏋️ Trainers"),
            ("memberships", "💳 Memberships & Pay"),
            ("attendance", "⏱️ Attendance"),
        ]

        for key, text in nav_items:
            btn = tk.Button(
                self.sidebar,
                text=f"  {text}",
                font=("Segoe UI", 10),
                fg="#cbd5e1",
                bg="#1e293b",
                activebackground="#334155",
                activeforeground="#ffffff",
                bd=0,
                anchor="w",
                padx=15,
                pady=10,
                cursor="hand2",
                command=lambda k=key: self.show_view(k)
            )
            btn.pack(fill=tk.X, pady=2)
            self.nav_buttons[key] = btn

        bottom_frame = tk.Frame(self.sidebar, bg="#1e293b", pady=15)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        tk.Button(
            bottom_frame,
            text="💾 Save All Data",
            font=("Segoe UI", 9, "bold"),
            bg="#2563eb",
            fg="#ffffff",
            activebackground="#1d4ed8",
            bd=0,
            pady=6,
            cursor="hand2",
            command=self._save_all_data
        ).pack(fill=tk.X, padx=15)

        self.main_container = tk.Frame(self, bg="#f8fafc")
        self.main_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def _save_all_data(self):
        try:
            self.gym.save_data()
            messagebox.showinfo("Success", "All application data saved to disk successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {e}")

    def show_view(self, view_name: str):
        for k, btn in self.nav_buttons.items():
            if k == view_name:
                btn.configure(bg="#334155", fg="#38bdf8", font=("Segoe UI", 10, "bold"))
            else:
                btn.configure(bg="#1e293b", fg="#cbd5e1", font=("Segoe UI", 10))

        if self.current_view:
            self.current_view.destroy()

        if view_name == "dashboard":
            self.current_view = self._create_dashboard_view()
        elif view_name == "members":
            self.current_view = self._create_members_view()
        elif view_name == "trainers":
            self.current_view = self._create_trainers_view()
        elif view_name == "memberships":
            self.current_view = self._create_memberships_view()
        elif view_name == "attendance":
            self.current_view = self._create_attendance_view()

        self.current_view.pack(fill=tk.BOTH, expand=True)

    # ==========================================================
    # 1. DASHBOARD VIEW
    # ==========================================================
    def _create_dashboard_view(self) -> tk.Frame:
        view = tk.Frame(self.main_container, bg="#f8fafc", padx=25, pady=20)

        header = tk.Frame(view, bg="#f8fafc")
        header.pack(fill=tk.X, pady=(0, 20))
        tk.Label(header, text="Dashboard Overview", font=("Segoe UI", 18, "bold"), fg="#0f172a", bg="#f8fafc").pack(anchor="w")
        tk.Label(header, text="Live real-time statistics from gym records", font=("Segoe UI", 9), fg="#64748b", bg="#f8fafc").pack(anchor="w")

        stats = self.gym.get_dashboard_stats()

        cards_frame = tk.Frame(view, bg="#f8fafc")
        cards_frame.pack(fill=tk.X, pady=(0, 25))

        card_data = [
            ("Total Members", stats["total_members"], "#2563eb", "👥"),
            ("Active Plans", stats["active_memberships"], "#16a34a", "✅"),
            ("Expired Plans", stats["expired_memberships"], "#dc2626", "⚠️"),
            ("Trainers", stats["total_trainers"], "#0891b2", "🏋️"),
            ("Today Check-ins", stats["today_attendances"], "#7c3aed", "⏱️"),
            ("Total Revenue", f"${stats['total_revenue']:.2f}", "#d97706", "💵"),
        ]

        for i, (title, val, color, icon) in enumerate(card_data):
            card = tk.Frame(cards_frame, bg="#ffffff", bd=1, relief=tk.SOLID, padx=15, pady=12)
            card.grid(row=i // 3, column=i % 3, padx=8, pady=8, sticky="nsew")
            cards_frame.grid_columnconfigure(i % 3, weight=1)

            top = tk.Frame(card, bg="#ffffff")
            top.pack(fill=tk.X)
            tk.Label(top, text=icon, font=("Segoe UI", 14), bg="#ffffff").pack(side=tk.LEFT)
            tk.Label(top, text=title, font=("Segoe UI", 9, "bold"), fg="#64748b", bg="#ffffff").pack(side=tk.LEFT, padx=6)

            tk.Label(card, text=str(val), font=("Segoe UI", 18, "bold"), fg=color, bg="#ffffff").pack(anchor="w", pady=(6, 0))

        summary_frame = tk.Frame(view, bg="#ffffff", bd=1, relief=tk.SOLID, padx=15, pady=15)
        summary_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(summary_frame, text="Quick Overview & System Health", font=("Segoe UI", 12, "bold"), fg="#0f172a", bg="#ffffff").pack(anchor="w", pady=(0, 10))

        info_text = (
            f"• Gym Name: {self.gym.name}\n"
            f"• Total Attendance Records: {len(self.gym.attendances)}\n"
            f"• Total Transactions Logged: {len(self.gym.payments)}\n"
            f"• Storage Type: JSON File Persistence (FileManager)\n"
            f"• Business Rules Active: Strict Expiration Check, Single Active Plan, Validated Payments\n"
        )
        tk.Label(summary_frame, text=info_text, font=("Segoe UI", 10), justify=tk.LEFT, fg="#334155", bg="#ffffff").pack(anchor="w")

        return view

    # ==========================================================
    # 2. MEMBERS VIEW
    # ==========================================================
    def _create_members_view(self) -> tk.Frame:
        view = tk.Frame(self.main_container, bg="#f8fafc", padx=25, pady=20)

        header = tk.Frame(view, bg="#f8fafc")
        header.pack(fill=tk.X, pady=(0, 15))
        tk.Label(header, text="Members Management", font=("Segoe UI", 18, "bold"), fg="#0f172a", bg="#f8fafc").pack(side=tk.LEFT)

        action_frame = tk.Frame(header, bg="#f8fafc")
        action_frame.pack(side=tk.RIGHT)

        tk.Button(action_frame, text="+ Add Member", bg="#16a34a", fg="#ffffff", font=("Segoe UI", 9, "bold"), bd=0, padx=12, pady=6, cursor="hand2", command=self._modal_add_member).pack(side=tk.LEFT, padx=4)
        tk.Button(action_frame, text="Delete Member", bg="#dc2626", fg="#ffffff", font=("Segoe UI", 9, "bold"), bd=0, padx=12, pady=6, cursor="hand2", command=self._delete_selected_member).pack(side=tk.LEFT, padx=4)

        toolbar = tk.Frame(view, bg="#ffffff", bd=1, relief=tk.SOLID, padx=12, pady=8)
        toolbar.pack(fill=tk.X, pady=(0, 12))

        tk.Label(toolbar, text="Search:", font=("Segoe UI", 9, "bold"), bg="#ffffff").pack(side=tk.LEFT, padx=(0, 5))
        self.member_search_var = tk.StringVar()
        search_entry = ttk.Entry(toolbar, textvariable=self.member_search_var, width=25)
        search_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(toolbar, text="Search", bg="#3b82f6", fg="#ffffff", bd=0, padx=8, pady=3, cursor="hand2", command=self._refresh_members_table).pack(side=tk.LEFT, padx=4)
        tk.Button(toolbar, text="Reset", bg="#64748b", fg="#ffffff", bd=0, padx=8, pady=3, cursor="hand2", command=self._reset_member_filters).pack(side=tk.LEFT, padx=4)

        tk.Label(toolbar, text="Filter Status:", font=("Segoe UI", 9, "bold"), bg="#ffffff").pack(side=tk.LEFT, padx=(20, 5))
        self.member_filter_var = tk.StringVar(value="All")
        filter_combo = ttk.Combobox(toolbar, textvariable=self.member_filter_var, values=["All", "Active", "Expired"], state="readonly", width=12)
        filter_combo.pack(side=tk.LEFT, padx=5)
        filter_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_members_table())

        table_frame = tk.Frame(view, bg="#ffffff", bd=1, relief=tk.SOLID)
        table_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("id", "name", "phone", "email", "joined", "status", "plan")
        self.members_tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")

        self.members_tree.heading("id", text="ID")
        self.members_tree.heading("name", text="Name")
        self.members_tree.heading("phone", text="Phone")
        self.members_tree.heading("email", text="Email")
        self.members_tree.heading("joined", text="Join Date")
        self.members_tree.heading("status", text="Membership Status")
        self.members_tree.heading("plan", text="Current Plan")

        self.members_tree.column("id", width=80, anchor="center")
        self.members_tree.column("name", width=160)
        self.members_tree.column("phone", width=110, anchor="center")
        self.members_tree.column("email", width=160)
        self.members_tree.column("joined", width=90, anchor="center")
        self.members_tree.column("status", width=130, anchor="center")
        self.members_tree.column("plan", width=110, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.members_tree.yview)
        self.members_tree.configure(yscrollcommand=scrollbar.set)

        self.members_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._refresh_members_table()
        return view

    def _reset_member_filters(self):
        self.member_search_var.set("")
        self.member_filter_var.set("All")
        self._refresh_members_table()

    def _refresh_members_table(self):
        for item in self.members_tree.get_children():
            self.members_tree.delete(item)

        query = self.member_search_var.get().strip()
        status_filter = self.member_filter_var.get()

        if query:
            members = self.gym.search_members(query)
        else:
            members = self.gym.filter_members(status_filter)

        for m in members:
            active_ms = m.active_membership
            status_text = "Active" if active_ms else "Expired / None"
            plan_text = active_ms.type.value if active_ms else "—"

            self.members_tree.insert(
                "",
                tk.END,
                values=(m.id, m.name, m.phone, m.email, m.join_date.isoformat(), status_text, plan_text)
            )

    def _modal_add_member(self):
        modal = tk.Toplevel(self)
        modal.title("Add New Member")
        modal.geometry("380x320")
        modal.configure(bg="#f8fafc")
        modal.transient(self)
        modal.grab_set()

        tk.Label(modal, text="New Member Registration", font=("Segoe UI", 12, "bold"), bg="#f8fafc").pack(pady=10)

        form = tk.Frame(modal, bg="#f8fafc", padx=20)
        form.pack(fill=tk.BOTH, expand=True)

        fields = [("ID:", "id"), ("Name:", "name"), ("Phone:", "phone"), ("Email:", "email")]
        entries = {}

        for i, (label_text, key) in enumerate(fields):
            tk.Label(form, text=label_text, font=("Segoe UI", 9, "bold"), bg="#f8fafc").grid(row=i, column=0, sticky="w", pady=4)
            ent = ttk.Entry(form, width=25)
            ent.grid(row=i, column=1, sticky="e", pady=4)
            entries[key] = ent

        entries["id"].insert(0, f"M{len(self.gym.members) + 101}")

        def submit():
            try:
                m_id = entries["id"].get().strip()
                name = entries["name"].get().strip()
                phone = entries["phone"].get().strip()
                email = entries["email"].get().strip()

                new_m = Member(id=m_id, name=name, phone=phone, email=email)
                self.gym.add_member(new_m)
                messagebox.showinfo("Success", f"Member '{name}' registered successfully!", parent=modal)
                modal.destroy()
                self._refresh_members_table()
            except GymException as ge:
                messagebox.showerror("Validation Error", ge.message, parent=modal)
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=modal)

        tk.Button(modal, text="Save Member", bg="#16a34a", fg="#ffffff", font=("Segoe UI", 10, "bold"), bd=0, pady=6, cursor="hand2", command=submit).pack(fill=tk.X, padx=25, pady=15)

    def _delete_selected_member(self):
        selected = self.members_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a member to delete.")
            return

        item = self.members_tree.item(selected[0])
        m_id = item["values"][0]
        m_name = item["values"][1]

        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete member [{m_id}] {m_name}?"):
            try:
                self.gym.delete_member(str(m_id))
                messagebox.showinfo("Deleted", f"Member {m_name} was deleted successfully.")
                self._refresh_members_table()
            except GymException as ge:
                messagebox.showerror("Error", ge.message)

    # ==========================================================
    # 3. TRAINERS VIEW
    # ==========================================================
    def _create_trainers_view(self) -> tk.Frame:
        view = tk.Frame(self.main_container, bg="#f8fafc", padx=25, pady=20)

        header = tk.Frame(view, bg="#f8fafc")
        header.pack(fill=tk.X, pady=(0, 15))
        tk.Label(header, text="Trainers Management", font=("Segoe UI", 18, "bold"), fg="#0f172a", bg="#f8fafc").pack(side=tk.LEFT)

        tk.Button(header, text="+ Add Trainer", bg="#16a34a", fg="#ffffff", font=("Segoe UI", 9, "bold"), bd=0, padx=12, pady=6, cursor="hand2", command=self._modal_add_trainer).pack(side=tk.RIGHT)

        table_frame = tk.Frame(view, bg="#ffffff", bd=1, relief=tk.SOLID)
        table_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("id", "name", "phone", "email", "specialty", "salary", "available", "assigned_count")
        self.trainers_tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")

        self.trainers_tree.heading("id", text="ID")
        self.trainers_tree.heading("name", text="Name")
        self.trainers_tree.heading("phone", text="Phone")
        self.trainers_tree.heading("email", text="Email")
        self.trainers_tree.heading("specialty", text="Specialty")
        self.trainers_tree.heading("salary", text="Salary")
        self.trainers_tree.heading("available", text="Available")
        self.trainers_tree.heading("assigned_count", text="Assigned Members")

        for col in cols:
            self.trainers_tree.column(col, anchor="center")
        self.trainers_tree.column("name", anchor="w", width=140)

        self.trainers_tree.pack(fill=tk.BOTH, expand=True)
        self._refresh_trainers_table()
        return view

    def _refresh_trainers_table(self):
        for item in self.trainers_tree.get_children():
            self.trainers_tree.delete(item)

        for t in self.gym.trainers:
            avail_text = "Yes" if t.is_available else "No"
            self.trainers_tree.insert(
                "",
                tk.END,
                values=(t.id, t.name, t.phone, t.email, t.specialty, f"${t.salary:.2f}", avail_text, len(t.assigned_members))
            )

    def _modal_add_trainer(self):
        modal = tk.Toplevel(self)
        modal.title("Add New Trainer")
        modal.geometry("380x360")
        modal.configure(bg="#f8fafc")
        modal.transient(self)
        modal.grab_set()

        tk.Label(modal, text="New Trainer Registration", font=("Segoe UI", 12, "bold"), bg="#f8fafc").pack(pady=10)
        form = tk.Frame(modal, bg="#f8fafc", padx=20)
        form.pack(fill=tk.BOTH, expand=True)

        fields = [("ID:", "id"), ("Name:", "name"), ("Phone:", "phone"), ("Email:", "email"), ("Specialty:", "specialty"), ("Salary ($):", "salary")]
        entries = {}

        for i, (label_text, key) in enumerate(fields):
            tk.Label(form, text=label_text, font=("Segoe UI", 9, "bold"), bg="#f8fafc").grid(row=i, column=0, sticky="w", pady=3)
            ent = ttk.Entry(form, width=23)
            ent.grid(row=i, column=1, sticky="e", pady=3)
            entries[key] = ent

        entries["id"].insert(0, f"T{len(self.gym.trainers) + 101}")
        entries["specialty"].insert(0, "Fitness & Strength")
        entries["salary"].insert(0, "1500.00")

        def submit():
            try:
                t_id = entries["id"].get().strip()
                name = entries["name"].get().strip()
                phone = entries["phone"].get().strip()
                email = entries["email"].get().strip()
                specialty = entries["specialty"].get().strip()
                salary = float(entries["salary"].get().strip())

                new_t = Trainer(id=t_id, name=name, phone=phone, email=email, specialty=specialty, salary=salary)
                self.gym.add_trainer(new_t)
                messagebox.showinfo("Success", f"Trainer '{name}' registered successfully!", parent=modal)
                modal.destroy()
                self._refresh_trainers_table()
            except GymException as ge:
                messagebox.showerror("Error", ge.message, parent=modal)
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=modal)

        tk.Button(modal, text="Save Trainer", bg="#16a34a", fg="#ffffff", font=("Segoe UI", 10, "bold"), bd=0, pady=6, cursor="hand2", command=submit).pack(fill=tk.X, padx=25, pady=12)

    # ==========================================================
    # 4. MEMBERSHIPS & PAYMENTS VIEW
    # ==========================================================
    def _create_memberships_view(self) -> tk.Frame:
        view = tk.Frame(self.main_container, bg="#f8fafc", padx=25, pady=20)

        header = tk.Frame(view, bg="#f8fafc")
        header.pack(fill=tk.X, pady=(0, 15))
        tk.Label(header, text="Memberships & Payments", font=("Segoe UI", 18, "bold"), fg="#0f172a", bg="#f8fafc").pack(side=tk.LEFT)

        action_frame = tk.Frame(header, bg="#f8fafc")
        action_frame.pack(side=tk.RIGHT)

        tk.Button(action_frame, text="+ Issue Membership", bg="#2563eb", fg="#ffffff", font=("Segoe UI", 9, "bold"), bd=0, padx=12, pady=6, cursor="hand2", command=self._modal_create_membership).pack(side=tk.LEFT, padx=4)
        tk.Button(action_frame, text="💵 Record Payment", bg="#16a34a", fg="#ffffff", font=("Segoe UI", 9, "bold"), bd=0, padx=12, pady=6, cursor="hand2", command=self._modal_record_payment).pack(side=tk.LEFT, padx=4)

        table_frame = tk.Frame(view, bg="#ffffff", bd=1, relief=tk.SOLID)
        table_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("id", "member_id", "member_name", "type", "dates", "price", "paid", "balance", "status")
        self.memberships_tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")

        self.memberships_tree.heading("id", text="Plan ID")
        self.memberships_tree.heading("member_id", text="Member ID")
        self.memberships_tree.heading("member_name", text="Member Name")
        self.memberships_tree.heading("type", text="Plan Type")
        self.memberships_tree.heading("dates", text="Validity Range")
        self.memberships_tree.heading("price", text="Total Price")
        self.memberships_tree.heading("paid", text="Total Paid")
        self.memberships_tree.heading("balance", text="Remaining")
        self.memberships_tree.heading("status", text="Status")

        for col in cols:
            self.memberships_tree.column(col, anchor="center")
        self.memberships_tree.column("member_name", anchor="w", width=130)
        self.memberships_tree.column("dates", width=160)

        self.memberships_tree.pack(fill=tk.BOTH, expand=True)
        self._refresh_memberships_table()
        return view

    def _refresh_memberships_table(self):
        for item in self.memberships_tree.get_children():
            self.memberships_tree.delete(item)

        for ms in self.gym.memberships:
            member = self.gym.find_member(ms.member_id)
            name = member.name if member else "Unknown"
            dates = f"{ms.start_date} → {ms.end_date}"

            self.memberships_tree.insert(
                "",
                tk.END,
                values=(
                    ms.id,
                    ms.member_id,
                    name,
                    ms.type.value,
                    dates,
                    f"${ms.price:.2f}",
                    f"${ms.get_total_paid():.2f}",
                    f"${ms.get_remaining_balance():.2f}",
                    ms.status.value
                )
            )

    def _modal_create_membership(self):
        modal = tk.Toplevel(self)
        modal.title("Issue Membership Plan")
        modal.geometry("380x300")
        modal.configure(bg="#f8fafc")
        modal.transient(self)
        modal.grab_set()

        tk.Label(modal, text="Assign Membership Plan", font=("Segoe UI", 12, "bold"), bg="#f8fafc").pack(pady=10)
        form = tk.Frame(modal, bg="#f8fafc", padx=20)
        form.pack(fill=tk.BOTH, expand=True)

        member_choices = [f"{m.id} - {m.name}" for m in self.gym.members]

        tk.Label(form, text="Select Member:", font=("Segoe UI", 9, "bold"), bg="#f8fafc").grid(row=0, column=0, sticky="w", pady=6)
        member_combo = ttk.Combobox(form, values=member_choices, state="readonly", width=22)
        member_combo.grid(row=0, column=1, sticky="e", pady=6)
        if member_choices:
            member_combo.current(0)

        tk.Label(form, text="Plan Type:", font=("Segoe UI", 9, "bold"), bg="#f8fafc").grid(row=1, column=0, sticky="w", pady=6)
        type_combo = ttk.Combobox(form, values=[t.value for t in MembershipType], state="readonly", width=22)
        type_combo.grid(row=1, column=1, sticky="e", pady=6)
        type_combo.current(0)

        tk.Label(form, text="Price ($):", font=("Segoe UI", 9, "bold"), bg="#f8fafc").grid(row=2, column=0, sticky="w", pady=6)
        price_entry = ttk.Entry(form, width=24)
        price_entry.grid(row=2, column=1, sticky="e", pady=6)
        price_entry.insert(0, "50.00")

        def submit():
            try:
                selected_m_str = member_combo.get()
                if not selected_m_str:
                    raise ValidationError("Please choose a member.", 400)
                m_id = selected_m_str.split(" - ")[0]

                selected_type = MembershipType(type_combo.get())
                price = float(price_entry.get().strip())

                # Calls Gym.create_membership -> Enforces Business Rule 2
                self.gym.create_membership(member_id=m_id, membership_type=selected_type, price=price)
                messagebox.showinfo("Success", "Membership assigned successfully!", parent=modal)
                modal.destroy()
                self._refresh_memberships_table()
            except GymException as ge:
                messagebox.showerror("Business Rule / Validation Error", ge.message, parent=modal)
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=modal)

        tk.Button(modal, text="Create Plan", bg="#2563eb", fg="#ffffff", font=("Segoe UI", 10, "bold"), bd=0, pady=6, cursor="hand2", command=submit).pack(fill=tk.X, padx=25, pady=15)

    def _modal_record_payment(self):
        modal = tk.Toplevel(self)
        modal.title("Record Payment")
        modal.geometry("380x280")
        modal.configure(bg="#f8fafc")
        modal.transient(self)
        modal.grab_set()

        tk.Label(modal, text="Record Subscription Payment", font=("Segoe UI", 12, "bold"), bg="#f8fafc").pack(pady=10)
        form = tk.Frame(modal, bg="#f8fafc", padx=20)
        form.pack(fill=tk.BOTH, expand=True)

        ms_choices = [f"{ms.id} ({ms.member_id})" for ms in self.gym.memberships]

        tk.Label(form, text="Membership ID:", font=("Segoe UI", 9, "bold"), bg="#f8fafc").grid(row=0, column=0, sticky="w", pady=6)
        ms_combo = ttk.Combobox(form, values=ms_choices, state="readonly", width=22)
        ms_combo.grid(row=0, column=1, sticky="e", pady=6)
        if ms_choices:
            ms_combo.current(0)

        tk.Label(form, text="Amount ($):", font=("Segoe UI", 9, "bold"), bg="#f8fafc").grid(row=1, column=0, sticky="w", pady=6)
        amount_entry = ttk.Entry(form, width=24)
        amount_entry.grid(row=1, column=1, sticky="e", pady=6)
        amount_entry.insert(0, "50.00")

        tk.Label(form, text="Method:", font=("Segoe UI", 9, "bold"), bg="#f8fafc").grid(row=2, column=0, sticky="w", pady=6)
        method_combo = ttk.Combobox(form, values=[m.value for m in PaymentMethod], state="readonly", width=22)
        method_combo.grid(row=2, column=1, sticky="e", pady=6)
        method_combo.current(0)

        def submit():
            try:
                selected_ms = ms_combo.get()
                if not selected_ms:
                    raise ValidationError("Please select a membership.", 400)
                ms_id = selected_ms.split(" ")[0]
                amount = float(amount_entry.get().strip())
                method = PaymentMethod(method_combo.get())

                # Calls Gym.record_payment -> Enforces Business Rule 3 (amount > 0)
                self.gym.record_payment(membership_id=ms_id, amount=amount, method=method)
                messagebox.showinfo("Success", f"Payment of ${amount:.2f} recorded!", parent=modal)
                modal.destroy()
                self._refresh_memberships_table()
            except GymException as ge:
                messagebox.showerror("Error", ge.message, parent=modal)
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=modal)

        tk.Button(modal, text="Submit Payment", bg="#16a34a", fg="#ffffff", font=("Segoe UI", 10, "bold"), bd=0, pady=6, cursor="hand2", command=submit).pack(fill=tk.X, padx=25, pady=15)

    # ==========================================================
    # 5. ATTENDANCE VIEW
    # ==========================================================
    def _create_attendance_view(self) -> tk.Frame:
        view = tk.Frame(self.main_container, bg="#f8fafc", padx=25, pady=20)

        header = tk.Frame(view, bg="#f8fafc")
        header.pack(fill=tk.X, pady=(0, 15))
        tk.Label(header, text="Attendance & Check-Ins", font=("Segoe UI", 18, "bold"), fg="#0f172a", bg="#f8fafc").pack(side=tk.LEFT)

        checkin_bar = tk.Frame(view, bg="#ffffff", bd=1, relief=tk.SOLID, padx=15, pady=10)
        checkin_bar.pack(fill=tk.X, pady=(0, 15))

        member_choices = [f"{m.id} - {m.name}" for m in self.gym.members]
        trainer_choices = ["None"] + [f"{t.id} - {t.name}" for t in self.gym.trainers]

        tk.Label(checkin_bar, text="Member:", font=("Segoe UI", 9, "bold"), bg="#ffffff").pack(side=tk.LEFT, padx=(0, 4))
        self.att_member_combo = ttk.Combobox(checkin_bar, values=member_choices, state="readonly", width=22)
        self.att_member_combo.pack(side=tk.LEFT, padx=(0, 10))
        if member_choices:
            self.att_member_combo.current(0)

        tk.Label(checkin_bar, text="Trainer:", font=("Segoe UI", 9, "bold"), bg="#ffffff").pack(side=tk.LEFT, padx=(0, 4))
        self.att_trainer_combo = ttk.Combobox(checkin_bar, values=trainer_choices, state="readonly", width=18)
        self.att_trainer_combo.pack(side=tk.LEFT, padx=(0, 15))
        self.att_trainer_combo.current(0)

        tk.Button(
            checkin_bar,
            text="⚡ Check-In Member",
            bg="#7c3aed",
            fg="#ffffff",
            font=("Segoe UI", 9, "bold"),
            bd=0,
            padx=12,
            pady=4,
            cursor="hand2",
            command=self._handle_record_attendance
        ).pack(side=tk.LEFT)

        table_frame = tk.Frame(view, bg="#ffffff", bd=1, relief=tk.SOLID)
        table_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("id", "member_id", "member_name", "trainer", "check_in", "check_out", "duration")
        self.attendance_tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")

        self.attendance_tree.heading("id", text="Record ID")
        self.attendance_tree.heading("member_id", text="Member ID")
        self.attendance_tree.heading("member_name", text="Member Name")
        self.attendance_tree.heading("trainer", text="Supervising Trainer")
        self.attendance_tree.heading("check_in", text="Check-In Time")
        self.attendance_tree.heading("check_out", text="Check-Out Time")
        self.attendance_tree.heading("duration", text="Duration")

        for col in cols:
            self.attendance_tree.column(col, anchor="center")
        self.attendance_tree.column("member_name", anchor="w", width=130)

        self.attendance_tree.pack(fill=tk.BOTH, expand=True)
        self._refresh_attendance_table()
        return view

    def _refresh_attendance_table(self):
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)

        for a in reversed(self.gym.attendances):
            member = self.gym.find_member(a.member_id)
            name = member.name if member else "Unknown"
            trainer_text = a.trainer_id if a.trainer_id else "None"
            check_in_str = a.check_in.strftime("%Y-%m-%d %H:%M:%S")
            check_out_str = a.check_out.strftime("%Y-%m-%d %H:%M:%S") if a.check_out else "Active Session"
            dur_text = f"{a.duration_minutes()} mins" if a.check_out else "In Progress"

            self.attendance_tree.insert(
                "",
                tk.END,
                values=(a.id, a.member_id, name, trainer_text, check_in_str, check_out_str, dur_text)
            )

    def _handle_record_attendance(self):
        selected_m = self.att_member_combo.get()
        if not selected_m:
            messagebox.showwarning("Warning", "Please select a member to check in.")
            return

        m_id = selected_m.split(" - ")[0]
        t_val = self.att_trainer_combo.get()
        t_id = None if t_val == "None" else t_val.split(" - ")[0]

        try:
            # Calls Gym.record_attendance -> Enforces Business Rule 1 (not expired) and Rule 4 (member exists)
            att = self.gym.record_attendance(member_id=m_id, trainer_id=t_id)
            messagebox.showinfo("Access Granted", f"Attendance logged for Member [{m_id}]!\nTime: {att.check_in.strftime('%H:%M:%S')}")
            self._refresh_attendance_table()
        except BusinessRuleError as bre:
            messagebox.showerror("Access Denied (Business Rule)", f"❌ {bre.message}\n\nPlease renew membership first.")
        except ValidationError as ve:
            messagebox.showerror("Validation Error", ve.message)
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    app = GymApp()
    app.mainloop()
