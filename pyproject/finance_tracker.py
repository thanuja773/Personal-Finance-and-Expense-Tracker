
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
import sqlite3
import os
from datetime import datetime
import calendar
import numpy as np
from pathlib import Path
from PIL import Image, ImageTk
import webbrowser

class FinanceTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Finance Tracker")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        self.root.configure(bg="#f4f6f8")
        
        # Modern color scheme
        self.colors = {
            "primary": "#0f4c81",
            "secondary": "#ffb400",
            "accent": "#6c63ff",
            "success": "#28a745",
            "danger": "#dc3545",
            "light": "#f8f9fa",
            "dark": "#343a40",
            "text": "#1f1f1f",
            "background": "#f4f6f8",
            "card": "#ffffff",
            "chart1": "#4e79a7",
            "chart2": "#f28e2b",
            "chart3": "#e15759",
            "chart4": "#76b7b2"
        }
        
        # Set theme and style
        self.style = ttk.Style()
        self.style.theme_use("clam")
        # Prettify notebook tabs
        self.style.configure("TNotebook", 
            background="#e9ecef", 
            borderwidth=0
        )

        self.style.configure("TNotebook.Tab", 
            background="#f8f9fa",
            foreground="#333",
            padding=(10, 5),
            font=('Segoe UI', 10, 'bold'),
            borderwidth=0
        )

        self.style.map("TNotebook.Tab",
            background=[("selected", "#0f4c81"), ("active", "#dbeafe")],
            foreground=[("selected", "white"), ("active", "#0f4c81")]
        )


        
        # Configure styles
        self.style.configure(".", background=self.colors["background"])
        self.style.configure("TFrame", background=self.colors["background"])
        self.style.configure("TLabel", background=self.colors["background"], foreground=self.colors["text"], font=("Segoe UI", 10))
        self.style.configure("TButton", 
                            background=self.colors["primary"], 
                            foreground="white", 
                            font=("Segoe UI", 10, "bold"),
                            borderwidth=1,
                            relief="flat")
        self.style.map("TButton",
                      background=[("active", self.colors["accent"]), ("pressed", self.colors["accent"])])
        self.style.configure("Heading.TLabel", 
                            font=("Segoe UI", 16, "bold"), 
                            background=self.colors["background"],
                            foreground=self.colors["primary"])
        self.style.configure("Card.TFrame", background=self.colors["card"], relief="solid", borderwidth=1)
        self.style.configure("CardHeader.TLabel", 
                            font=("Segoe UI", 12, "bold"), 
                            background=self.colors["primary"],
                            foreground="white")
        self.style.configure("Secondary.TButton", 
                            background=self.colors["secondary"],
                            foreground="white")
        self.style.configure("Success.TButton", 
                            background=self.colors["success"],
                            foreground="white")
        self.style.configure("Danger.TButton", 
                            background=self.colors["danger"],
                            foreground="white")
        
        # Initialize database
        self.init_database()
        
        # Create header
        self.create_header()
        
        # Create the main notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Create tabs
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.add_expense_tab = ttk.Frame(self.notebook)
        self.add_income_tab = ttk.Frame(self.notebook)
        self.reports_tab = ttk.Frame(self.notebook)
        self.settings_tab = ttk.Frame(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.dashboard_tab, text="📊 Dashboard")
        self.notebook.add(self.add_expense_tab, text="📑 Expenses")
        self.notebook.add(self.add_income_tab, text="💰 Income")
        self.notebook.add(self.reports_tab, text="📁 Reports")
        self.notebook.add(self.settings_tab, text="⚙️ Settings")
        
        # Set up tabs
        self.setup_dashboard()
        self.setup_add_expense()
        self.setup_add_income()
        self.setup_reports()
        self.setup_settings()
        
        # Initialize budget
        self.budget = self.get_budget()
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief="sunken", anchor="w")
        self.status_bar.pack(side="bottom", fill="x")
        self.update_status("Ready")        
        # Load data for dashboard
        self.refresh_dashboard()
        

    
    def create_header(self):
        """Create a modern header with app title and quick actions"""
        header_frame = ttk.Frame(self.root, style="Card.TFrame")
        header_frame.pack(fill="x", padx=20, pady=(20, 0))
        # 🔥 Logo on the left
        logo_img = Image.open("assets/logo.png").resize((40, 40))
        self.logo_photo = ImageTk.PhotoImage(logo_img)
        logo_label = ttk.Label(header_frame, image=self.logo_photo)
        logo_label.pack(side="left", padx=(10, 0), pady=10)
        
        # App title and subtitle
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side="left", padx=20, pady=10)
        
        ttk.Label(title_frame, 
                 text="Personal Finance Tracker", 
                 font=("Segoe UI", 18, "bold"),
                 foreground=self.colors["primary"]).pack(anchor="w")
        ttk.Label(title_frame, 
                 text="Track smarter. Save faster.", 
                 font=("Segoe UI", 10, "italic"),
                 foreground=self.colors["dark"]).pack(anchor="w")
        
        # Quick action buttons
        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side="right", padx=20, pady=10)
        

    
    def update_status(self, message):
        """Update the status bar message"""
        self.status_var.set(f"Status: {message}")
        self.root.update_idletasks()
    
    def init_database(self):
        # Create SQLite database
        self.conn = sqlite3.connect('finance_tracker.db')
        self.cursor = self.conn.cursor()
        
        # Create expenses table if not exists
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                amount REAL,
                category TEXT,
                description TEXT
            )
        ''')
        
        # Create income table if not exists
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS income (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                amount REAL,
                source TEXT,
                description TEXT
            )
        ''')
        
        # Create settings table if not exists
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        self.conn.commit()
    
    def setup_dashboard(self):
        # Main container frame
        container = ttk.Frame(self.dashboard_tab)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create a canvas and scrollbar for responsive layout
        self.dashboard_canvas = tk.Canvas(container, bg=self.colors["background"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.dashboard_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.dashboard_canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.dashboard_canvas.configure(
                scrollregion=self.dashboard_canvas.bbox("all")
            )
        )
        
        self.dashboard_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.dashboard_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.dashboard_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel for scrolling
        self.dashboard_canvas.bind_all("<MouseWheel>", lambda e: self.dashboard_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        # Summary cards frame
        summary_frame = ttk.Frame(self.scrollable_frame)
        summary_frame.pack(fill="x", pady=(0, 20), padx=10)

    
        
        # Create summary cards
        self.total_income_card = self.create_summary_card(summary_frame, "Total Income", "$0.00", self.colors["chart1"])
        self.total_expenses_card = self.create_summary_card(summary_frame, "Total Expenses", "$0.00", self.colors["chart3"])
        self.savings_card = self.create_summary_card(summary_frame, "Savings", "$0.00", self.colors["chart4"])
        self.budget_card = self.create_summary_card(summary_frame, "Budget Status", "No budget set", self.colors["chart2"])

        
        # Charts section
        charts_frame = ttk.Frame(self.scrollable_frame)
        charts_frame.pack(fill="both", expand=True)
        
        # Top charts row
        top_charts_frame = ttk.Frame(charts_frame)
        top_charts_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Bottom charts row
        bottom_charts_frame = ttk.Frame(charts_frame)
        bottom_charts_frame.pack(fill="both", expand=True)
        
        # Store chart frames for updates
        self.chart_frames = {
            "expense_pie": ttk.Frame(top_charts_frame, style="Card.TFrame"),
            "monthly_trend": ttk.Frame(top_charts_frame, style="Card.TFrame"),
            "income_vs_expense": ttk.Frame(bottom_charts_frame, style="Card.TFrame"),
            "savings_trend": ttk.Frame(bottom_charts_frame, style="Card.TFrame")
        }
        
        # Position all charts
        # Top charts
        self.chart_frames["expense_pie"].pack(in_=top_charts_frame, side="left", fill="both", expand=True, padx=10)
        self.chart_frames["monthly_trend"].pack(in_=top_charts_frame, side="left", fill="both", expand=True, padx=10)

        # Bottom charts
        self.chart_frames["income_vs_expense"].pack(in_=bottom_charts_frame, side="left", fill="both", expand=True, padx=10)
        self.chart_frames["savings_trend"].pack(in_=bottom_charts_frame, side="left", fill="both", expand=True, padx=10)

        
        # Button to refresh dashboard
        refresh_btn = ttk.Button(self.scrollable_frame, 
                               text="🔄 Refresh Dashboard", 
                               style="TButton",
                               command=self.refresh_dashboard)
        refresh_btn.pack(pady=20)
        
        # Add some padding at the bottom
        ttk.Frame(self.scrollable_frame, height=20).pack()
    
    def create_summary_card(self, parent, title, value, color):
        """Create a modern summary card with icon and value"""
        card = ttk.Frame(parent, style="Card.TFrame", padding=10)
        card.pack(side="left", fill="both", expand=True, padx=10)
        
        # Card header
        header = ttk.Frame(card)
        header.pack(fill="x", pady=(0, 10))
        
        # Color indicator
        color_indicator = tk.Frame(header, width=5, bg=color)
        color_indicator.pack(side="left", fill="y", padx=(0, 10))
        
        # Title
        ttk.Label(header, 
                 text=title, 
                 font=("Segoe UI", 10, "bold"),
                 foreground=self.colors["text"]).pack(side="left", fill="x", expand=True)
        
        # Value
        value_label = ttk.Label(card, 
                              text=value, 
                              font=("Segoe UI", 16, "bold"),
                              foreground=color)
        value_label.pack(fill="x", pady=(0, 5))
        
        # Store reference to value label for updates
        if title == "Total Income":
            self.total_income_label = value_label
        elif title == "Total Expenses":
            self.total_expenses_label = value_label
        elif title == "Savings":
            self.savings_label = value_label
        elif title == "Budget Status":
            self.budget_label = value_label
        
        return card
    
    def setup_add_expense(self):
        # Main container with padding
        container = ttk.Frame(self.add_expense_tab)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create a two-column layout
        left_frame = ttk.Frame(container)
        left_frame.pack(side="left", fill="both", expand=True, padx=10)
        
        right_frame = ttk.Frame(container)
        right_frame.pack(side="right", fill="both", expand=True, padx=10)
        
        # Add Expense Form (Left)
        form_card = ttk.Frame(left_frame, style="Card.TFrame", padding=15)
        form_card.pack(fill="both", expand=True)
        
        # Card header
        ttk.Label(form_card, 
                 text="📑 Add New Expense", 
                 style="CardHeader.TLabel").pack(fill="x", pady=(0, 15))
        
        # Form fields
        fields_frame = ttk.Frame(form_card)
        fields_frame.pack(fill="x")
        
        # Date
        ttk.Label(fields_frame, text="Date:").grid(row=0, column=0, pady=5, sticky="w")
        self.expense_date = DateEntry(fields_frame,
            width=27,
            background="#274c77",
            foreground="white",
            borderwidth=2,
            headersbackground="#274c77",
            headersforeground="white",
            selectbackground="#6096ba",
            selectforeground="white",
            disabledbackground="#d3d3d3",
            font=("Segoe UI", 10),
            date_pattern="yyyy-mm-dd"
        )
        self.expense_date.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        self.expense_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Amount
        ttk.Label(fields_frame, text="Amount ($):").grid(row=1, column=0, pady=5, sticky="w")
        self.expense_amount = ttk.Entry(fields_frame, width=30)
        self.expense_amount.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        
        # Category
        ttk.Label(fields_frame, text="Category:").grid(row=2, column=0, pady=5, sticky="w")
        self.expense_categories = ["Food", "Housing", "Transportation", "Entertainment", 
                                 "Utilities", "Shopping", "Health", "Education", "Personal", "Other"]
        self.expense_category = ttk.Combobox(fields_frame, values=self.expense_categories, width=27)
        self.expense_category.grid(row=2, column=1, pady=5, padx=5, sticky="w")
        self.expense_category.current(0)
        
        # Description
        ttk.Label(fields_frame, text="Description:").grid(row=3, column=0, pady=5, sticky="w")
        self.expense_description = ttk.Entry(fields_frame, width=30)
        self.expense_description.grid(row=3, column=1, pady=5, padx=5, sticky="w")
        
        # Buttons
        button_frame = ttk.Frame(fields_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, 
                  text="➕ Add Expense", 
                  style="TButton",
                  command=self.add_expense).pack(side="left", padx=5)
        
        ttk.Button(button_frame, 
                  text="📤 Export to Excel", 
                  style="Secondary.TButton",
                  command=lambda: self.export_to_excel("expenses")).pack(side="left", padx=5)
        
        # Recent Expenses (Right)
        recent_card = ttk.Frame(right_frame, style="Card.TFrame", padding=15)
        recent_card.pack(fill="both", expand=True)
        
        # Card header
        ttk.Label(recent_card, 
                 text="🧾 Recent Expenses", 
                 style="CardHeader.TLabel").pack(fill="x", pady=(0, 15))
        
        # Treeview with scrollbar
        tree_frame = ttk.Frame(recent_card)
        tree_frame.pack(fill="both", expand=True)
        
        # Vertical scrollbar
        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side="right", fill="y")
        
        # Horizontal scrollbar
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")
        tree_scroll_x.pack(side="bottom", fill="x")
        
        # Treeview
        self.expenses_tree = ttk.Treeview(
            tree_frame,
            columns=("Date", "Amount", "Category", "Description"),
            show="headings",
            height=15,
            yscrollcommand=tree_scroll.set,
            xscrollcommand=tree_scroll_x.set
        )
        
        # Configure scrollbars
        tree_scroll.config(command=self.expenses_tree.yview)
        tree_scroll_x.config(command=self.expenses_tree.xview)
        
        # Style the treeview
        self.style.configure("Treeview", 
                           background=self.colors["card"],
                           foreground=self.colors["text"],
                           rowheight=25,
                           fieldbackground=self.colors["card"])
        
        self.style.map("Treeview", background=[("selected", self.colors["primary"])])
        
        # Set column headings
        self.expenses_tree.heading("Date", text="Date")
        self.expenses_tree.heading("Amount", text="Amount")
        self.expenses_tree.heading("Category", text="Category")
        self.expenses_tree.heading("Description", text="Description")
        
        # Set column widths
        self.expenses_tree.column("Date", width=100, anchor="center")
        self.expenses_tree.column("Amount", width=100, anchor="center")
        self.expenses_tree.column("Category", width=120, anchor="center")
        self.expenses_tree.column("Description", width=200, anchor="w")
        
        self.expenses_tree.pack(fill="both", expand=True)
        
        # Delete button
        ttk.Button(recent_card, 
                  text="🗑 Delete Selected", 
                  style="Danger.TButton",
                  command=self.delete_selected_expense).pack(pady=(10, 0))
        
        # Populate recent expenses
        self.load_recent_expenses()
    
    def setup_add_income(self):
        # Main container with padding
        container = ttk.Frame(self.add_income_tab)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create a two-column layout
        left_frame = ttk.Frame(container)
        left_frame.pack(side="left", fill="both", expand=True, padx=10)
        
        right_frame = ttk.Frame(container)
        right_frame.pack(side="right", fill="both", expand=True, padx=10)
        
        # Add Income Form (Left)
        form_card = ttk.Frame(left_frame, style="Card.TFrame", padding=15)
        form_card.pack(fill="both", expand=True)
        
        # Card header
        ttk.Label(form_card, 
                 text="💰 Add New Income", 
                 style="CardHeader.TLabel").pack(fill="x", pady=(0, 15))
        
        # Form fields
        fields_frame = ttk.Frame(form_card)
        fields_frame.pack(fill="x")
        
        # Date
        ttk.Label(fields_frame, text="Date:").grid(row=0, column=0, pady=5, sticky="w")
        self.income_date = DateEntry(fields_frame,
            width=27,
            background="#274c77",
            foreground="white",
            borderwidth=2,
            headersbackground="#274c77",
            headersforeground="white",
            selectbackground="#6096ba",
            selectforeground="white",
            disabledbackground="#d3d3d3",
            font=("Segoe UI", 10),
            date_pattern="yyyy-mm-dd"
        )
        self.income_date.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        self.income_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Amount
        ttk.Label(fields_frame, text="Amount ($):").grid(row=1, column=0, pady=5, sticky="w")
        self.income_amount = ttk.Entry(fields_frame, width=30)
        self.income_amount.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        
        # Source
        ttk.Label(fields_frame, text="Source:").grid(row=2, column=0, pady=5, sticky="w")
        self.income_sources = ["Salary", "Freelance", "Investments", "Gift", "Refund", "Other"]
        self.income_source = ttk.Combobox(fields_frame, values=self.income_sources, width=27)
        self.income_source.grid(row=2, column=1, pady=5, padx=5, sticky="w")
        self.income_source.current(0)
        
        # Description
        ttk.Label(fields_frame, text="Description:").grid(row=3, column=0, pady=5, sticky="w")
        self.income_description = ttk.Entry(fields_frame, width=30)
        self.income_description.grid(row=3, column=1, pady=5, padx=5, sticky="w")
        
        # Buttons
        button_frame = ttk.Frame(fields_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, 
                  text="➕ Add Income", 
                  style="Success.TButton",
                  command=self.add_income).pack(side="left", padx=5)
        
        ttk.Button(button_frame, 
                  text="📤 Export to Excel", 
                  style="Secondary.TButton",
                  command=lambda: self.export_to_excel("income")).pack(side="left", padx=5)
        
        # Recent Income (Right)
        recent_card = ttk.Frame(right_frame, style="Card.TFrame", padding=15)
        recent_card.pack(fill="both", expand=True)
        
        # Card header
        ttk.Label(recent_card, 
                 text="🧾 Recent Income", 
                 style="CardHeader.TLabel").pack(fill="x", pady=(0, 15))
        
        # Treeview with scrollbar
        tree_frame = ttk.Frame(recent_card)
        tree_frame.pack(fill="both", expand=True)
        
        # Vertical scrollbar
        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side="right", fill="y")
        
        # Horizontal scrollbar
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")
        tree_scroll_x.pack(side="bottom", fill="x")
        
        # Treeview
        self.income_tree = ttk.Treeview(
            tree_frame,
            columns=("Date", "Amount", "Source", "Description"),
            show="headings",
            height=15,
            yscrollcommand=tree_scroll.set,
            xscrollcommand=tree_scroll_x.set
        )
        
        # Configure scrollbars
        tree_scroll.config(command=self.income_tree.yview)
        tree_scroll_x.config(command=self.income_tree.xview)
        
        # Set column headings
        self.income_tree.heading("Date", text="Date")
        self.income_tree.heading("Amount", text="Amount")
        self.income_tree.heading("Source", text="Source")
        self.income_tree.heading("Description", text="Description")
        
        # Set column widths
        self.income_tree.column("Date", width=100, anchor="center")
        self.income_tree.column("Amount", width=100, anchor="center")
        self.income_tree.column("Source", width=120, anchor="center")
        self.income_tree.column("Description", width=200, anchor="w")
        
        self.income_tree.pack(fill="both", expand=True)
        
        # Delete button
        ttk.Button(recent_card, 
                  text="🗑 Delete Selected", 
                  style="Danger.TButton",
                  command=self.delete_selected_income).pack(pady=(10, 0))
        
        # Populate recent income
        self.load_recent_income()
    
    def setup_reports(self):
        # Main container with padding
        container = ttk.Frame(self.reports_tab)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create a two-column layout
        left_frame = ttk.Frame(container)
        left_frame.pack(side="left", fill="y", padx=10)
        
        right_frame = ttk.Frame(container)
        right_frame.pack(side="right", fill="both", expand=True, padx=10)
        
        # Report Controls (Left)
        controls_card = ttk.Frame(left_frame, style="Card.TFrame", padding=15)
        controls_card.pack(fill="y")
        
        # Card header
        ttk.Label(controls_card, 
                 text="📁 Report Options", 
                 style="CardHeader.TLabel").pack(fill="x", pady=(0, 15))
        
        # Report type
        ttk.Label(controls_card, text="Report Type:").pack(anchor="w", pady=(5, 0))
        self.report_types = ["Monthly", "Annual"]
        self.report_type = ttk.Combobox(controls_card, values=self.report_types, width=20)
        self.report_type.pack(fill="x", pady=5)
        self.report_type.current(0)
        
        # Month selection for monthly report
        self.month_frame = ttk.Frame(controls_card)
        self.month_frame.pack(fill="x", pady=5)
        
        ttk.Label(self.month_frame, text="Month:").pack(side="left", padx=(0, 5))
        self.months = list(calendar.month_name)[1:]
        self.selected_month = ttk.Combobox(self.month_frame, values=self.months, width=12)
        self.selected_month.pack(side="left", fill="x", expand=True)
        self.selected_month.current(datetime.now().month - 1)
        
        # Year selection
        self.year_frame = ttk.Frame(controls_card)
        self.year_frame.pack(fill="x", pady=5)
        
        ttk.Label(self.year_frame, text="Year:").pack(side="left", padx=(0, 5))
        current_year = datetime.now().year
        self.years = [str(year) for year in range(current_year - 5, current_year + 1)]
        self.selected_year = ttk.Combobox(self.year_frame, values=self.years, width=12)
        self.selected_year.pack(side="left", fill="x", expand=True)
        self.selected_year.current(len(self.years) - 1)  # Set to current year
        
        # Generate report button
        ttk.Button(controls_card, 
                  text="🔄 Generate Report", 
                  style="TButton",
                  command=self.generate_report).pack(fill="x", pady=10)
        
        # Export report button
        ttk.Button(controls_card, 
                  text="📥 Export to Excel", 
                  style="Secondary.TButton",
                  command=self.export_report).pack(fill="x", pady=5)
        
        # Report Display (Right)
        self.report_display_card = ttk.Frame(right_frame, style="Card.TFrame", padding=15)
        self.report_display_card.pack(fill="both", expand=True)
        
        # Card header
        self.report_title_label = ttk.Label(self.report_display_card, 
                                          style="CardHeader.TLabel")
        self.report_title_label.pack(fill="x", pady=(0, 15))
        
        # Create a canvas and scrollbar for the report content
        self.report_canvas = tk.Canvas(self.report_display_card, bg=self.colors["card"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.report_display_card, orient="vertical", command=self.report_canvas.yview)
        self.report_content_frame = ttk.Frame(self.report_canvas)
        
        self.report_content_frame.bind(
            "<Configure>",
            lambda e: self.report_canvas.configure(
                scrollregion=self.report_canvas.bbox("all")
            )
        )
        
        self.report_canvas.create_window((0, 0), window=self.report_content_frame, anchor="nw")
        self.report_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.report_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel for scrolling
        self.report_canvas.bind_all("<MouseWheel>", lambda e: self.report_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
    
    def setup_settings(self):
        # Main container with padding
        container = ttk.Frame(self.settings_tab)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create a two-column layout
        left_frame = ttk.Frame(container)
        left_frame.pack(side="left", fill="both", expand=True, padx=10)
        
        right_frame = ttk.Frame(container)
        right_frame.pack(side="right", fill="both", expand=True, padx=10)
        
        # Budget Settings (Left)
        budget_card = ttk.Frame(left_frame, style="Card.TFrame", padding=15)
        budget_card.pack(fill="both", expand=True)
        
        # Card header
        ttk.Label(budget_card, 
                 text="💵 Budget Settings", 
                 style="CardHeader.TLabel").pack(fill="x", pady=(0, 15))
        
        # Budget input
        ttk.Label(budget_card, text="Monthly Budget ($):").pack(anchor="w", pady=(5, 0))
        self.budget_entry = ttk.Entry(budget_card, width=30)
        self.budget_entry.pack(fill="x", pady=5)
        
        # Load current budget
        current_budget = self.get_budget()
        if current_budget:
            self.budget_entry.insert(0, str(current_budget))
        
        # Save button
        ttk.Button(budget_card, 
                  text="💾 Save Budget ", 
                  style="TButton",
                  command=self.save_settings).pack(fill="x", pady=10)
        
        # Category Management (Right)
        category_card = ttk.Frame(right_frame, style="Card.TFrame", padding=15)
        category_card.pack(fill="both", expand=True)
        
        # Card header
        ttk.Label(category_card, 
                 text="📚 Manage Categories", 
                 style="CardHeader.TLabel").pack(fill="x", pady=(0, 15))
        
        # Add new category
        ttk.Label(category_card, text="Add New Category:").pack(anchor="w", pady=(5, 0))
        
        add_frame = ttk.Frame(category_card)
        add_frame.pack(fill="x", pady=5)
        
        self.new_category_entry = ttk.Entry(add_frame)
        self.new_category_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ttk.Button(add_frame, 
                  text="Add ➕", 
                  style="Secondary.TButton",
                  command=self.add_category).pack(side="right")
        
        # Existing categories
        ttk.Label(category_card, text="Existing Categories:").pack(anchor="w", pady=(10, 0))
        
        # Listbox for categories
        self.category_listbox = tk.Listbox(
            category_card,
            height=8,
            selectmode=tk.SINGLE,
            bg=self.colors["card"],
            fg=self.colors["text"],
            highlightthickness=0,
            relief="flat"
        )
        
        # Add existing categories
        for category in self.expense_categories:
            self.category_listbox.insert(tk.END, category)
        
        self.category_listbox.pack(fill="both", expand=True, pady=5)
        
        # Delete button
        ttk.Button(category_card, 
                  text="🗑 Delete Selected", 
                  style="Danger.TButton",
                  command=self.delete_category).pack(fill="x", pady=(5, 0))
        
        # Data Management (Bottom)
        data_card = ttk.Frame(left_frame, style="Card.TFrame", padding=15)
        data_card.pack(fill="x", pady=(10, 0))
        
        # Card header
        ttk.Label(data_card, 
                 text="📈 Data Management", 
                 style="CardHeader.TLabel").pack(fill="x", pady=(0, 15))
        
        # Import/Export buttons
        ttk.Button(data_card, 
                  text="📂 Import from Excel", 
                  style="Secondary.TButton",
                  command=self.import_from_excel).pack(fill="x", pady=5)
        
        ttk.Button(data_card, 
                  text="📤 Export All Data", 
                  style="Secondary.TButton",
                  command=self.export_all_data).pack(fill="x", pady=5)
    
    def add_expense(self):
        try:
            # Get values from form
            date = self.expense_date.get()
            amount = float(self.expense_amount.get())
            category = self.expense_category.get()
            description = self.expense_description.get()
            
            # Validate date format
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Invalid Date", "Please enter date in YYYY-MM-DD format")
                return
            
            # Insert into database
            self.cursor.execute(
                "INSERT INTO expenses (date, amount, category, description) VALUES (?, ?, ?, ?)",
                (date, amount, category, description)
            )
            self.conn.commit()
            
            # Clear form
            self.expense_amount.delete(0, "end")
            self.expense_description.delete(0, "end")
            
            # Refresh expense list and dashboard
            self.load_recent_expenses()
            self.refresh_dashboard()
            
            # Check budget
            self.check_budget()
            
            self.update_status("Expense added successfully")
            messagebox.showinfo("Success", "Expense added successfully!")
        except ValueError:
            messagebox.showerror("Invalid Amount", "Please enter a valid amount")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def add_income(self):
        try:
            # Get values from form
            date = self.income_date.get()
            amount = float(self.income_amount.get())
            source = self.income_source.get()
            description = self.income_description.get()
            
            # Validate date format
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Invalid Date", "Please enter date in YYYY-MM-DD format")
                return
            
            # Insert into database
            self.cursor.execute(
                "INSERT INTO income (date, amount, source, description) VALUES (?, ?, ?, ?)",
                (date, amount, source, description)
            )
            self.conn.commit()
            
            # Clear form
            self.income_amount.delete(0, "end")
            self.income_description.delete(0, "end")
            
            # Refresh income list and dashboard
            self.load_recent_income()
            self.refresh_dashboard()
            
            self.update_status("Income added successfully")
            messagebox.showinfo("Success", "Income added successfully!")
        except ValueError:
            messagebox.showerror("Invalid Amount", "Please enter a valid amount")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def delete_selected_expense(self):
        selected = self.expenses_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an expense to delete")
            return
            confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete the selected expense?")
            if not confirm:
                return
            
            # Get the ID of the selected expense
            item = self.expenses_tree.item(selected[0])
            date = item['values'][0]
            amount = item['values'][1]
            category = item['values'][2]
            description = item['values'][3]
            
            # Delete from database
            self.cursor.execute(
                "DELETE FROM expenses WHERE date=? AND amount=? AND category=? AND description=?",
                (date, float(amount[1:]), category, description)
            )
            self.conn.commit()
            
            # Refresh the treeview
            self.load_recent_expenses()
            self.refresh_dashboard()
            
            self.update_status("Expense deleted successfully")
            messagebox.showinfo("Success", "Expense deleted successfully!")
    
    def delete_selected_income(self):
        selected = self.income_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an income to delete")
            return
        
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete the selected income?")
        if not confirm:
            return
        
        # Get the ID of the selected income
        item = self.income_tree.item(selected[0])
        date = item['values'][0]
        amount = item['values'][1]
        source = item['values'][2]
        description = item['values'][3]
        
        # Delete from database
        self.cursor.execute(
            "DELETE FROM income WHERE date=? AND amount=? AND source=? AND description=?",
            (date, float(amount[1:]), source, description)
        )
        self.conn.commit()
        
        # Refresh the treeview
        self.load_recent_income()
        self.refresh_dashboard()
        
        self.update_status("Income deleted successfully")
        messagebox.showinfo("Success", "Income deleted successfully!")
    
    def add_category(self):
        new_category = self.new_category_entry.get().strip()
        if not new_category:
            messagebox.showwarning("Warning", "Please enter a category name")
            return
        
        if new_category in self.expense_categories:
            messagebox.showwarning("Warning", "This category already exists")
            return
        
        # Add to the list and update the combobox
        self.expense_categories.append(new_category)
        self.expense_category['values'] = self.expense_categories
        self.category_listbox.insert(tk.END, new_category)
        
        # Clear the entry
        self.new_category_entry.delete(0, "end")
        
        self.update_status(f"Category '{new_category}' added")
    
    def delete_category(self):
        selected = self.category_listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a category to delete")
            return
        
        category = self.category_listbox.get(selected[0])
        
        # Check if category is in use
        self.cursor.execute("SELECT COUNT(*) FROM expenses WHERE category=?", (category,))
        count = self.cursor.fetchone()[0]
        
        if count > 0:
            messagebox.showwarning("Warning", f"Cannot delete '{category}' as it has {count} associated expenses")
            return
        
        # Remove from the list and update the combobox
        self.expense_categories.remove(category)
        self.expense_category['values'] = self.expense_categories
        self.category_listbox.delete(selected[0])
        
        self.update_status(f"Category '{category}' deleted")
    
    def load_recent_expenses(self):
        # Clear current items
        for item in self.expenses_tree.get_children():
            self.expenses_tree.delete(item)
        
        # Fetch recent expenses
        self.cursor.execute("SELECT date, amount, category, description FROM expenses ORDER BY date DESC LIMIT 100")
        expenses = self.cursor.fetchall()
        
        # Insert into treeview
        for expense in expenses:
            self.expenses_tree.insert("", "end", values=(expense[0], f"${expense[1]:.2f}", expense[2], expense[3]))
    
    def load_recent_income(self):
        # Clear current items
        for item in self.income_tree.get_children():
            self.income_tree.delete(item)
        
        # Fetch recent income
        self.cursor.execute("SELECT date, amount, source, description FROM income ORDER BY date DESC LIMIT 100")
        incomes = self.cursor.fetchall()
        
        # Insert into treeview
        for income in incomes:
            self.income_tree.insert("", "end", values=(income[0], f"${income[1]:.2f}", income[2], income[3]))
    
    def refresh_dashboard(self):
        self.update_status("Refreshing dashboard...")
        
        # Get current month and year
        current_date = datetime.now()
        current_month = current_date.month
        current_year = current_date.year
        
        # Calculate start and end date for current month
        start_date = f"{current_year}-{current_month:02d}-01"
        
        # Get number of days in current month
        last_day = calendar.monthrange(current_year, current_month)[1]
        end_date = f"{current_year}-{current_month:02d}-{last_day}"
        
        # Get monthly expenses
        self.cursor.execute(
            "SELECT SUM(amount) FROM expenses WHERE date BETWEEN ? AND ?",
            (start_date, end_date)
        )
        monthly_expenses = self.cursor.fetchone()[0] or 0
        
        # Get monthly income
        self.cursor.execute(
            "SELECT SUM(amount) FROM income WHERE date BETWEEN ? AND ?",
            (start_date, end_date)
        )
        monthly_income = self.cursor.fetchone()[0] or 0
        
        # Calculate savings
        savings = monthly_income - monthly_expenses
        
        # Update dashboard summary
        self.total_income_label.config(text=f"${monthly_income:,.2f}")
        self.total_expenses_label.config(text=f"${monthly_expenses:,.2f}")
        self.savings_label.config(text=f"${savings:,.2f}")
        
        # Check budget status
        budget = self.get_budget()
        if budget:
            budget_percentage = (monthly_expenses / budget) * 100
            if budget_percentage >= 100:
                status = f"Exceeded: {budget_percentage:.1f}%"
                self.budget_label.config(text=status, foreground=self.colors["danger"])
            elif budget_percentage >= 80:
                status = f"Warning: {budget_percentage:.1f}%"
                self.budget_label.config(text=status, foreground=self.colors["secondary"])
            else:
                status = f"On Track: {budget_percentage:.1f}%"
                self.budget_label.config(text=status, foreground=self.colors["success"])
        else:
            self.budget_label.config(text="No budget set", foreground=self.colors["text"])
        
        # Clear previous charts
        for widget in self.chart_frames["expense_pie"].winfo_children():
            widget.destroy()
        for widget in self.chart_frames["monthly_trend"].winfo_children():
            widget.destroy()
        for widget in self.chart_frames["income_vs_expense"].winfo_children():
            widget.destroy()
        for widget in self.chart_frames["savings_trend"].winfo_children():
            widget.destroy()
        
        # Create expense by category chart (pie chart)
        self.create_expense_category_chart()
        
        # Create monthly trend chart (bar chart)
        self.create_monthly_trend_chart()
        
        # Create income vs expense chart
        self.create_income_vs_expense_chart()
        
        # Create savings trend chart
        self.create_savings_trend_chart()
        
        self.update_status("Dashboard refreshed")
    
    def create_expense_category_chart(self):
        # Get current month and year
        current_date = datetime.now()
        current_month = current_date.month
        current_year = current_date.year
        
        # Calculate start and end date for current month
        start_date = f"{current_year}-{current_month:02d}-01"
        
        # Get number of days in current month
        last_day = calendar.monthrange(current_year, current_month)[1]
        end_date = f"{current_year}-{current_month:02d}-{last_day}"
        
        # Get expense data by category
        self.cursor.execute(
            "SELECT category, SUM(amount) FROM expenses WHERE date BETWEEN ? AND ? GROUP BY category",
            (start_date, end_date)
        )
        category_data = self.cursor.fetchall()
        
        if not category_data:
            # If no data, show message
            ttk.Label(self.chart_frames["expense_pie"], 
                     text="No expense data for current month",
                     style="TLabel").pack(pady=20)
            return
        
        # Create pie chart
        fig, ax = plt.subplots(figsize=(5, 4))
        categories = [item[0] for item in category_data]
        amounts = [item[1] for item in category_data]
        
        # Create beautiful colors
        colors = plt.cm.Pastel1(np.linspace(0, 1, len(categories)))
        
        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            amounts, 
            labels=categories, 
            autopct='%1.1f%%', 
            startangle=90, 
            colors=colors,
            wedgeprops=dict(width=0.4, edgecolor='w'),
            pctdistance=0.85
        )
        
        # Make labels smaller
        plt.setp(texts, size=8)
        plt.setp(autotexts, size=8, weight="bold")
        
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        plt.title('Expenses by Category', pad=20)
        
        # Add to frame
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frames["expense_pie"])
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Add toolbar
        toolbar = NavigationToolbar2Tk(canvas, self.chart_frames["expense_pie"])
        toolbar.update()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def create_monthly_trend_chart(self):
        # Get the last 6 months of data
        current_date = datetime.now()
        
        # Store month names and expense data
        months = []
        expenses = []
        
        # Get data for each of the last 6 months
        for i in range(5, -1, -1):
            # Calculate month and year
            month = current_date.month - i
            year = current_date.year
            
            # Adjust for previous year
            while month <= 0:
                month += 12
                year -= 1
            
            # Calculate start and end date for the month
            start_date = f"{year}-{month:02d}-01"
            last_day = calendar.monthrange(year, month)[1]
            end_date = f"{year}-{month:02d}-{last_day}"
            
            # Month name
            month_name = calendar.month_abbr[month]
            months.append(month_name)
            
            # Get expenses for the month
            self.cursor.execute(
                "SELECT SUM(amount) FROM expenses WHERE date BETWEEN ? AND ?",
                (start_date, end_date)
            )
            monthly_expense = self.cursor.fetchone()[0] or 0
            expenses.append(monthly_expense)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(5, 4))
        
        # Create bar chart
        bars = ax.bar(months, expenses, color=self.colors["chart3"])
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'${height:,.0f}',
                    ha='center', va='bottom', fontsize=8)
        
        # Add labels and title
        ax.set_xlabel('Month')
        ax.set_ylabel('Amount ($)')
        ax.set_title('Monthly Expenses Trend')
        
        # Rotate x-axis labels
        plt.xticks(rotation=45)
        
        # Add to frame
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frames["monthly_trend"])
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Add toolbar
        toolbar = NavigationToolbar2Tk(canvas, self.chart_frames["monthly_trend"])
        toolbar.update()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def create_income_vs_expense_chart(self):
        # Get the last 6 months of data
        current_date = datetime.now()
        
        # Store month names and data
        months = []
        incomes = []
        expenses = []
        
        # Get data for each of the last 6 months
        for i in range(5, -1, -1):
            # Calculate month and year
            month = current_date.month - i
            year = current_date.year
            
            # Adjust for previous year
            while month <= 0:
                month += 12
                year -= 1
            
            # Calculate start and end date for the month
            start_date = f"{year}-{month:02d}-01"
            last_day = calendar.monthrange(year, month)[1]
            end_date = f"{year}-{month:02d}-{last_day}"
            
            # Month name
            month_name = calendar.month_abbr[month]
            months.append(month_name)
            
            # Get income for the month
            self.cursor.execute(
                "SELECT SUM(amount) FROM income WHERE date BETWEEN ? AND ?",
                (start_date, end_date)
            )
            monthly_income = self.cursor.fetchone()[0] or 0
            incomes.append(monthly_income)
            
            # Get expenses for the month
            self.cursor.execute(
                "SELECT SUM(amount) FROM expenses WHERE date BETWEEN ? AND ?",
                (start_date, end_date)
            )
            monthly_expense = self.cursor.fetchone()[0] or 0
            expenses.append(monthly_expense)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(5, 4))
        
        # Create bar positions
        x = np.arange(len(months))
        width = 0.35
        
        # Create bars
        income_bars = ax.bar(x - width/2, incomes, width, label='Income', color=self.colors["chart1"])
        expense_bars = ax.bar(x + width/2, expenses, width, label='Expenses', color=self.colors["chart3"])
        
        # Add value labels on top of bars
        for bars in [income_bars, expense_bars]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'${height:,.0f}',
                        ha='center', va='bottom', fontsize=8)
        
        # Add labels and legend
        ax.set_xlabel('Month')
        ax.set_ylabel('Amount ($)')
        ax.set_title('Income vs Expenses')
        ax.set_xticks(x)
        ax.set_xticklabels(months)
        ax.legend()
        
        # Rotate x-axis labels
        plt.xticks(rotation=45)
        
        # Add to frame
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frames["income_vs_expense"])
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Add toolbar
        toolbar = NavigationToolbar2Tk(canvas, self.chart_frames["income_vs_expense"])
        toolbar.update()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def create_savings_trend_chart(self):
        # Get the last 6 months of data
        current_date = datetime.now()
        
        # Store month names and savings data
        months = []
        savings = []
        
        # Get data for each of the last 6 months
        for i in range(5, -1, -1):
            # Calculate month and year
            month = current_date.month - i
            year = current_date.year
            
            # Adjust for previous year
            while month <= 0:
                month += 12
                year -= 1
            
            # Calculate start and end date for the month
            start_date = f"{year}-{month:02d}-01"
            last_day = calendar.monthrange(year, month)[1]
            end_date = f"{year}-{month:02d}-{last_day}"
            
            # Month name
            month_name = calendar.month_abbr[month]
            months.append(month_name)
            
            # Get income for the month
            self.cursor.execute(
                "SELECT SUM(amount) FROM income WHERE date BETWEEN ? AND ?",
                (start_date, end_date)
            )
            monthly_income = self.cursor.fetchone()[0] or 0
            
            # Get expenses for the month
            self.cursor.execute(
                "SELECT SUM(amount) FROM expenses WHERE date BETWEEN ? AND ?",
                (start_date, end_date)
            )
            monthly_expense = self.cursor.fetchone()[0] or 0
            
            # Calculate savings
            monthly_savings = monthly_income - monthly_expense
            savings.append(monthly_savings)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(5, 4))
        
        # Create line chart
        line, = ax.plot(months, savings, marker='o', color=self.colors["chart4"], linewidth=2)
        
        # Add value labels on data points
        for x, y in zip(months, savings):
            ax.text(x, y, f'${y:,.0f}', ha='center', va='bottom', fontsize=8)
        
        # Add labels and title
        ax.set_xlabel('Month')
        ax.set_ylabel('Amount ($)')
        ax.set_title('Monthly Savings Trend')
        
        # Fill under the line
        ax.fill_between(months, savings, color=self.colors["chart4"], alpha=0.2)
        
        # Rotate x-axis labels
        plt.xticks(rotation=45)
        
        # Add to frame
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frames["savings_trend"])
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Add toolbar
        toolbar = NavigationToolbar2Tk(canvas, self.chart_frames["savings_trend"])
        toolbar.update()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def get_budget(self):
        # Get budget from settings
        self.cursor.execute("SELECT value FROM settings WHERE key = 'monthly_budget'")
        result = self.cursor.fetchone()
        
        if result and result[0]:
            return float(result[0])
        return None
    
    def save_settings(self):
        try:
            # Get budget value
            budget = float(self.budget_entry.get()) if self.budget_entry.get() else None
            
            # Save to database
            if budget:
                self.cursor.execute(
                    "INSERT OR REPLACE INTO settings (key, value) VALUES ('monthly_budget', ?)",
                    (str(budget),)
                )
                self.conn.commit()
                self.budget = budget
                
                # Refresh dashboard to update budget status
                self.refresh_dashboard()
                
                self.update_status("Budget settings saved")
                messagebox.showinfo("Success", "Budget settings saved successfully!")
            else:
                messagebox.showwarning("Warning", "No budget was set")
        except ValueError:
            messagebox.showerror("Invalid Budget", "Please enter a valid number for budget")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def check_budget(self):
        # Get current month's expenses
        current_date = datetime.now()
        current_month = current_date.month
        current_year = current_date.year
        
        # Calculate start and end date for current month
        start_date = f"{current_year}-{current_month:02d}-01"
        last_day = calendar.monthrange(current_year, current_month)[1]
        end_date = f"{current_year}-{current_month:02d}-{last_day}"
        
        # Get monthly expenses
        self.cursor.execute(
            "SELECT SUM(amount) FROM expenses WHERE date BETWEEN ? AND ?",
            (start_date, end_date)
        )
        monthly_expenses = self.cursor.fetchone()[0] or 0
        
        # Check against budget
        budget = self.get_budget()
        if budget:
            if monthly_expenses > budget:
                messagebox.showwarning("Budget Alert", f"You have exceeded your monthly budget of ${budget:,.2f}!")
            elif monthly_expenses > (budget * 0.8):
                messagebox.showwarning("Budget Alert", f"You have used {(monthly_expenses/budget)*100:.1f}% of your monthly budget!")
    
    def generate_report(self):
        self.update_status("Generating report...")
        
        # Clear previous report
        for widget in self.report_content_frame.winfo_children():
            widget.destroy()
        
        report_type = self.report_type.get()
        
        if report_type == "Monthly":
            month_index = self.months.index(self.selected_month.get()) + 1
            year = int(self.selected_year.get())
            
            # Generate monthly report
            self.generate_monthly_report(month_index, year)
        elif report_type == "Annual":
            year = int(self.selected_year.get())
            
            # Generate annual report
            self.generate_annual_report(year)
        else:
            # Custom date range - not implemented in this version
            messagebox.showinfo("Info", "Custom date range reports will be available in future updates")
        
        self.update_status("Report generated")
    
    def generate_monthly_report(self, month, year):
        # Calculate start and end date
        start_date = f"{year}-{month:02d}-01"
        last_day = calendar.monthrange(year, month)[1]
        end_date = f"{year}-{month:02d}-{last_day}"
        
        # Get expenses
        self.cursor.execute(
            "SELECT category, SUM(amount) FROM expenses WHERE date BETWEEN ? AND ? GROUP BY category",
            (start_date, end_date)
        )
        expense_data = self.cursor.fetchall()
        
        # Get income
        self.cursor.execute(
            "SELECT source, SUM(amount) FROM income WHERE date BETWEEN ? AND ? GROUP BY source",
            (start_date, end_date)
        )
        income_data = self.cursor.fetchall()
        
        # Calculate totals
        total_expense = sum(item[1] for item in expense_data) if expense_data else 0
        total_income = sum(item[1] for item in income_data) if income_data else 0
        savings = total_income - total_expense
        
        # Create report title
        month_name = calendar.month_name[month]
        self.report_title_label.config(text=f"Monthly Report: {month_name} {year}")
        
        # Create summary frame
        summary_frame = ttk.Frame(self.report_content_frame)
        summary_frame.pack(fill="x", pady=10)
        
        # Add summary labels
        ttk.Label(summary_frame, 
                 text=f"Total Income: ${total_income:,.2f}", 
                 font=("Segoe UI", 11)).pack(anchor="w", pady=2)
        ttk.Label(summary_frame, 
                 text=f"Total Expenses: ${total_expense:,.2f}", 
                 font=("Segoe UI", 11)).pack(anchor="w", pady=2)
        ttk.Label(summary_frame, 
                 text=f"Net Savings: ${savings:,.2f}", 
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=2)
        
        # Create charts frame
        charts_frame = ttk.Frame(self.report_content_frame)
        charts_frame.pack(fill="both", expand=True, pady=10)
        
        # Create expense pie chart
        if expense_data:
            fig1, ax1 = plt.subplots(figsize=(5, 4))
            labels = [item[0] for item in expense_data]
            sizes = [item[1] for item in expense_data]
            
            # Create beautiful colors
            colors = plt.cm.Pastel1(np.linspace(0, 1, len(labels)))
            
            ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
            ax1.axis('equal')
            plt.title(f'Expenses by Category: {month_name} {year}')
            
            chart_frame1 = ttk.Frame(charts_frame)
            chart_frame1.pack(side="left", fill="both", expand=True)
            
            canvas1 = FigureCanvasTkAgg(fig1, master=chart_frame1)
            canvas1.draw()
            canvas1.get_tk_widget().pack(fill="both", expand=True)
        
        # Create income pie chart
        if income_data:
            fig2, ax2 = plt.subplots(figsize=(5, 4))
            labels = [item[0] for item in income_data]
            sizes = [item[1] for item in income_data]
            
            # Create beautiful colors
            colors = plt.cm.Pastel2(np.linspace(0, 1, len(labels)))
            
            ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
            ax2.axis('equal')
            plt.title(f'Income by Source: {month_name} {year}')
            
            chart_frame2 = ttk.Frame(charts_frame)
            chart_frame2.pack(side="right", fill="both", expand=True)
            
            canvas2 = FigureCanvasTkAgg(fig2, master=chart_frame2)
            canvas2.draw()
            canvas2.get_tk_widget().pack(fill="both", expand=True)
    
    def generate_annual_report(self, year):
        # Create report title
        self.report_title_label.config(text=f"Annual Report: {year}")
        
        # Store monthly data
        months = []
        expenses = []
        incomes = []
        savings = []
        
        # Get data for each month
        for month in range(1, 13):
            # Calculate start and end date for the month
            start_date = f"{year}-{month:02d}-01"
            last_day = calendar.monthrange(year, month)[1]
            end_date = f"{year}-{month:02d}-{last_day}"
            
            # Month name
            month_name = calendar.month_abbr[month]
            months.append(month_name)
            
            # Get expenses for the month
            self.cursor.execute(
                "SELECT SUM(amount) FROM expenses WHERE date BETWEEN ? AND ?",
                (start_date, end_date)
            )
            monthly_expense = self.cursor.fetchone()[0] or 0
            expenses.append(monthly_expense)
            
            # Get income for the month
            self.cursor.execute(
                "SELECT SUM(amount) FROM income WHERE date BETWEEN ? AND ?",
                (start_date, end_date)
            )
            monthly_income = self.cursor.fetchone()[0] or 0
            incomes.append(monthly_income)
            
            # Calculate savings
            monthly_savings = monthly_income - monthly_expense
            savings.append(monthly_savings)
        
        # Calculate annual totals
        annual_income = sum(incomes)
        annual_expenses = sum(expenses)
        annual_savings = sum(savings)
        
        # Create summary frame
        summary_frame = ttk.Frame(self.report_content_frame)
        summary_frame.pack(fill="x", pady=10)
        
        # Add summary labels
        ttk.Label(summary_frame, 
                 text=f"Annual Income: ${annual_income:,.2f}", 
                 font=("Segoe UI", 11)).pack(anchor="w", pady=2)
        ttk.Label(summary_frame, 
                 text=f"Annual Expenses: ${annual_expenses:,.2f}", 
                 font=("Segoe UI", 11)).pack(anchor="w", pady=2)
        ttk.Label(summary_frame, 
                 text=f"Annual Savings: ${annual_savings:,.2f}", 
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=2)
        
        # Create trend chart
        fig, ax = plt.subplots(figsize=(10, 5))
        
        # Create bar positions
        x = np.arange(len(months))
        width = 0.3
        
        # Create bars
        income_bars = ax.bar(x - width, incomes, width, label='Income', color=self.colors["chart1"])
        expense_bars = ax.bar(x, expenses, width, label='Expenses', color=self.colors["chart3"])
        savings_bars = ax.bar(x + width, savings, width, label='Savings', color=self.colors["chart4"])
        
        # Add value labels on top of bars
        for bars in [income_bars, expense_bars, savings_bars]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'${height:,.0f}',
                        ha='center', va='bottom', fontsize=8)
        
        # Add labels and legend
        ax.set_xlabel('Month')
        ax.set_ylabel('Amount ($)')
        ax.set_title(f'Monthly Financial Trend: {year}')
        ax.set_xticks(x)
        ax.set_xticklabels(months)
        ax.legend()
        
        # Rotate x-axis labels
        plt.xticks(rotation=45)
        
        # Add to frame
        chart_frame = ttk.Frame(self.report_content_frame)
        chart_frame.pack(fill="both", expand=True, pady=10)
        
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def export_report(self):
        try:
            report_type = self.report_type.get()
            
            if report_type == "Monthly":
                month_name = self.selected_month.get()
                year = self.selected_year.get()
                filename = f"Report_{month_name}_{year}.xlsx"
            else:
                year = self.selected_year.get()
                filename = f"Annual_Report_{year}.xlsx"
            
            # Ask user for save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=filename
            )
            
            if not file_path:
                return
            
            if report_type == "Monthly":
                month_index = self.months.index(self.selected_month.get()) + 1
                year = int(self.selected_year.get())
                
                # Export monthly report
                self.export_monthly_report(month_index, year, file_path)
            else:
                year = int(self.selected_year.get())
                
                # Export annual report
                self.export_annual_report(year, file_path)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def export_monthly_report(self, month, year, file_path):
        # Calculate start and end date
        start_date = f"{year}-{month:02d}-01"
        last_day = calendar.monthrange(year, month)[1]
        end_date = f"{year}-{month:02d}-{last_day}"
        
        # Get expenses
        self.cursor.execute(
            "SELECT date, category, amount, description FROM expenses WHERE date BETWEEN ? AND ? ORDER BY date",
            (start_date, end_date)
        )
        expenses = self.cursor.fetchall()
        
        # Get income
        self.cursor.execute(
            "SELECT date, source, amount, description FROM income WHERE date BETWEEN ? AND ? ORDER BY date",
            (start_date, end_date)
        )
        incomes = self.cursor.fetchall()
        
        # Create Excel writer
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # Create summary sheet
            summary_data = {
                'Metric': ['Total Income', 'Total Expenses', 'Net Savings'],
                'Amount': [
                    sum(income[2] for income in incomes) if incomes else 0,
                    sum(expense[2] for expense in expenses) if expenses else 0,
                    sum(income[2] for income in incomes) - sum(expense[2] for expense in expenses) if incomes or expenses else 0
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Create expenses sheet
            if expenses:
                expense_df = pd.DataFrame(expenses, columns=['Date', 'Category', 'Amount', 'Description'])
                expense_df.to_excel(writer, sheet_name='Expenses', index=False)
            
            # Create income sheet
            if incomes:
                income_df = pd.DataFrame(incomes, columns=['Date', 'Source', 'Amount', 'Description'])
                income_df.to_excel(writer, sheet_name='Income', index=False)
        
        messagebox.showinfo("Export Successful", f"Report exported to {file_path}")
    
    def export_annual_report(self, year, file_path):
        # Create Excel writer
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # Create monthly summary sheet
            monthly_data = []
            
            for month in range(1, 13):
                # Calculate start and end date for the month
                start_date = f"{year}-{month:02d}-01"
                last_day = calendar.monthrange(year, month)[1]
                end_date = f"{year}-{month:02d}-{last_day}"
                
                # Month name
                month_name = calendar.month_name[month]
                
                # Get expenses for the month
                self.cursor.execute(
                    "SELECT SUM(amount) FROM expenses WHERE date BETWEEN ? AND ?",
                    (start_date, end_date)
                )
                monthly_expense = self.cursor.fetchone()[0] or 0
                
                # Get income for the month
                self.cursor.execute(
                    "SELECT SUM(amount) FROM income WHERE date BETWEEN ? AND ?",
                    (start_date, end_date)
                )
                monthly_income = self.cursor.fetchone()[0] or 0
                
                # Calculate savings
                monthly_savings = monthly_income - monthly_expense
                
                monthly_data.append([month_name, monthly_income, monthly_expense, monthly_savings])
            
            # Create monthly summary dataframe
            monthly_df = pd.DataFrame(monthly_data, columns=['Month', 'Income', 'Expenses', 'Savings'])
            monthly_df.to_excel(writer, sheet_name='Monthly Summary', index=False)
            
            # Create expense categories sheet
            self.cursor.execute(
                "SELECT category, SUM(amount) FROM expenses WHERE date LIKE ? GROUP BY category",
                (f"{year}%",)
            )
            category_data = self.cursor.fetchall()
            
            if category_data:
                category_df = pd.DataFrame(category_data, columns=['Category', 'Total Amount'])
                category_df.to_excel(writer, sheet_name='Expense Categories', index=False)
            
            # Create income sources sheet
            self.cursor.execute(
                "SELECT source, SUM(amount) FROM income WHERE date LIKE ? GROUP BY source",
                (f"{year}%",)
            )
            source_data = self.cursor.fetchall()
            
            if source_data:
                source_df = pd.DataFrame(source_data, columns=['Source', 'Total Amount'])
                source_df.to_excel(writer, sheet_name='Income Sources', index=False)
        
        messagebox.showinfo("Export Successful", f"Annual report exported to {file_path}")
    
    def export_to_excel(self, data_type):
        try:
            # Default filename
            default_filename = f"{data_type}_{datetime.now().strftime('%Y%m%d')}.xlsx"
            # Ask user for save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=default_filename
            )
            
            if not file_path:
                return
            
            # Get data from database
            if data_type == "expenses":
                self.cursor.execute("SELECT date, amount, category, description FROM expenses ORDER BY date DESC")
                data = self.cursor.fetchall()
                columns = ['Date', 'Amount', 'Category', 'Description']
            else:  # income
                self.cursor.execute("SELECT date, amount, source, description FROM income ORDER BY date DESC")
                data = self.cursor.fetchall()
                columns = ['Date', 'Amount', 'Source', 'Description']
            
            # Create DataFrame
            df = pd.DataFrame(data, columns=columns)
            
            # Save to Excel
            df.to_excel(file_path, index=False)
            
            self.update_status(f"{data_type.capitalize()} data exported to Excel")
            messagebox.showinfo("Export Successful", f"{data_type.capitalize()} data exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def export_all_data(self):
        try:
            # Default filename
            default_filename = f"finance_data_{datetime.now().strftime('%Y%m%d')}.xlsx"
            
            # Ask user for save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=default_filename
            )
            
            if not file_path:
                return
            
            # Get data from database
            self.cursor.execute("SELECT date, amount, category, description FROM expenses ORDER BY date DESC")
            expenses = self.cursor.fetchall()
            
            self.cursor.execute("SELECT date, amount, source, description FROM income ORDER BY date DESC")
            incomes = self.cursor.fetchall()
            
            # Get budget setting
            budget = self.get_budget()
            
            # Create Excel writer
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Create expenses sheet
                if expenses:
                    expense_df = pd.DataFrame(expenses, columns=['Date', 'Amount', 'Category', 'Description'])
                    expense_df.to_excel(writer, sheet_name='Expenses', index=False)
                
                # Create income sheet
                if incomes:
                    income_df = pd.DataFrame(incomes, columns=['Date', 'Amount', 'Source', 'Description'])
                    income_df.to_excel(writer, sheet_name='Income', index=False)
                
                # Create settings sheet
                settings_data = [['Monthly Budget', budget if budget else 'Not set']]
                settings_df = pd.DataFrame(settings_data, columns=['Setting', 'Value'])
                settings_df.to_excel(writer, sheet_name='Settings', index=False)
            
            self.update_status("All data exported to Excel")
            messagebox.showinfo("Export Successful", f"All data exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def import_from_excel(self):
        try:
            # Ask user for file
            file_path = filedialog.askopenfilename(
                filetypes=[("Excel files", "*.xlsx;*.xls")]
            )
            
            if not file_path:
                return
            
            # Read Excel file
            xls = pd.ExcelFile(file_path)
            sheet_names = xls.sheet_names
            
            imported_data = False
            
            # Check for expenses sheet
            if 'Expenses' in sheet_names:
                expense_df = pd.read_excel(file_path, sheet_name='Expenses')
                
                # Validate columns
                required_columns = ['Date', 'Amount', 'Category', 'Description']
                if all(col in expense_df.columns for col in required_columns):
                    # Import data
                    for _, row in expense_df.iterrows():
                        self.cursor.execute(
                            "INSERT INTO expenses (date, amount, category, description) VALUES (?, ?, ?, ?)",
                            (str(row['Date']), float(row['Amount']), str(row['Category']), str(row['Description']))
                        )
                    
                    self.conn.commit()
                    imported_data = True
                    self.update_status(f"Imported {len(expense_df)} expense records")
                    messagebox.showinfo("Import Successful", f"Imported {len(expense_df)} expense records")
            
            # Check for income sheet
            if 'Income' in sheet_names:
                income_df = pd.read_excel(file_path, sheet_name='Income')
                
                # Validate columns
                required_columns = ['Date', 'Amount', 'Source', 'Description']
                if all(col in income_df.columns for col in required_columns):
                    # Import data
                    for _, row in income_df.iterrows():
                        self.cursor.execute(
                            "INSERT INTO income (date, amount, source, description) VALUES (?, ?, ?, ?)",
                            (str(row['Date']), float(row['Amount']), str(row['Source']), str(row['Description']))
                        )
                    
                    self.conn.commit()
                    imported_data = True
                    self.update_status(f"Imported {len(income_df)} income records")
                    messagebox.showinfo("Import Successful", f"Imported {len(income_df)} income records")
            
            if not imported_data:
                messagebox.showwarning("Import Failed", "No valid data found in Excel file")
            else:
                # Refresh data
                self.load_recent_expenses()
                self.load_recent_income()
                self.refresh_dashboard()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def on_closing(self):
        """Handle window closing event"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.conn.close()
            self.root.destroy()

def main():
    root = tk.Tk()

    
    # Add splash screen
    splash = tk.Toplevel(root)
    splash.title("Loading...")
    splash.geometry("300x200")
    splash.overrideredirect(True)  # Remove window decorations
    
    # Center the splash screen
    window_width = 300
    window_height = 200
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    splash.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # Add splash content
    ttk.Label(splash, 
             text="Personal Finance Tracker", 
             font=("Segoe UI", 16, "bold"),
             foreground="#0f4c81").pack(pady=20)
    
    ttk.Label(splash, 
             text="Loading...", 
             font=("Segoe UI", 10)).pack()
    
    progress = ttk.Progressbar(splash, orient="horizontal", length=200, mode="indeterminate")
    progress.pack(pady=20)
    progress.start()
    
    # Update the splash screen
    splash.update()
    
    # Create the main app
    app = FinanceTracker(root)
    
    # Close splash screen after a delay
    splash.after(2000, splash.destroy)
    
    # Set window icon
    try:
        root.iconbitmap("finance_icon.ico")  # Replace with your icon file
    except:
        pass  # Icon file not found
    
    # Set closing handler
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    
    root.mainloop()

if __name__ == "__main__":
    main()
            
        