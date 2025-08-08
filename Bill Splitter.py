import tkinter as tk
from tkinter import ttk, messagebox, simpledialog


class CenteredDialog(simpledialog.Dialog):
    """Custom dialog to appear at center of the screen."""

    def __init__(self, parent, title=None, prompt="", currency="₹"):
        self.prompt = prompt
        self.currency = currency
        super().__init__(parent, title)

    def body(self, master):
        tk.Label(master, text=self.prompt).pack(pady=5)
        self.entry = tk.Entry(master)
        self.entry.pack(pady=5)
        return self.entry

    def apply(self):
        self.result = self.entry.get()

    def center(self):
        """Force dialog to center of the screen."""
        self.update_idletasks()
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

    def wait_visibility(self, window=None):
        """Override wait_visibility to center after visible."""
        super().wait_visibility(window)
        self.center()


class BillSplitterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("💵 Bill Splitter")
        self.root.resizable(True, True)

        self.all_windows = [self.root]

        # Position main window at the top-left
        self.root.geometry("+0+0")
        self.root.pack_propagate(True)

        # Themes
        self.light_theme = {"bg": "#ffffff", "fg": "#000000",
                            "entry_bg": "#f0f0f0", "btn_bg": "#4CAF50", "btn_fg": "#ffffff"}
        self.dark_theme = {"bg": "#2c2c2c", "fg": "#ffffff",
                           "entry_bg": "#444444", "btn_bg": "#2196F3", "btn_fg": "#ffffff"}
        self.current_theme = self.light_theme

        self.people_entries = []
        self.amount_entries = []
        self.currency_var = tk.StringVar(value="₹")
        self.split_type = tk.StringVar(value="even")
        self.tip_var = tk.StringVar(value="0")

        self.create_widgets()
        self.apply_theme()

    def style_button(self, btn):
        """Apply modern style with hover grow/shrink effect."""
        btn.configure(
            bg=self.current_theme["btn_bg"],
            fg=self.current_theme["btn_fg"],
            activebackground="#45a049",
            activeforeground="#ffffff",
            relief="flat",
            font=("Helvetica", 10, "bold"),
            bd=0
        )
        btn.bind("<Enter>", lambda e: btn.configure(
            font=("Helvetica", 11, "bold")))
        btn.bind("<Leave>", lambda e: btn.configure(
            font=("Helvetica", 10, "bold")))

    def create_widgets(self):
        # Title
        self.title_label = ttk.Label(
            self.root, text="💵 Bill Splitter", font=("Helvetica", 18, "bold"))
        self.title_label.pack(pady=10)

        # Currency
        currency_frame = tk.Frame(self.root)
        currency_frame.pack(pady=5)
        tk.Label(currency_frame, text="Currency Symbol:").pack(side="left")
        tk.Entry(currency_frame, textvariable=self.currency_var,
                 width=5).pack(side="left", padx=5)

        # Number of people
        num_frame = tk.Frame(self.root)
        num_frame.pack(pady=5)
        tk.Label(num_frame, text="Number of People:").pack(side="left")
        self.num_people_var = tk.StringVar()
        tk.Entry(num_frame, textvariable=self.num_people_var,
                 width=5).pack(side="left", padx=5)
        btn_set = tk.Button(num_frame, text="Set",
                            command=self.create_people_entries)
        btn_set.pack(side="left")
        self.style_button(btn_set)

        # Split type
        split_frame = tk.Frame(self.root)
        split_frame.pack(pady=5)
        tk.Label(split_frame, text="Split Type:").pack(side="left")
        ttk.Radiobutton(split_frame, text="Even", variable=self.split_type,
                        value="even", command=self.toggle_amount_fields).pack(side="left")
        ttk.Radiobutton(split_frame, text="Custom", variable=self.split_type,
                        value="custom", command=self.toggle_amount_fields).pack(side="left")

        # Tip
        tip_frame = tk.Frame(self.root)
        tip_frame.pack(pady=5)
        tk.Label(tip_frame, text="Tip %:").pack(side="left")
        tk.Entry(tip_frame, textvariable=self.tip_var,
                 width=5).pack(side="left", padx=5)

        # Frame for dynamic entries
        self.entries_frame = tk.Frame(self.root)
        self.entries_frame.pack(pady=5)

        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        btn_calc = tk.Button(btn_frame, text="Calculate",
                             command=self.calculate_bill)
        btn_calc.pack(side="left", padx=5)
        self.style_button(btn_calc)

        btn_theme = tk.Button(
            btn_frame, text="🌙 Toggle Theme", command=self.toggle_theme)
        btn_theme.pack(side="left", padx=5)
        self.style_button(btn_theme)

    def create_people_entries(self):
        try:
            num_people = int(self.num_people_var.get())
            if num_people <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Error", "Please enter a valid number of people.")
            return

        for widget in self.entries_frame.winfo_children():
            widget.destroy()
        self.people_entries.clear()
        self.amount_entries.clear()

        for i in range(num_people):
            frame = tk.Frame(self.entries_frame)
            frame.pack(pady=2)
            name_entry = tk.Entry(frame, width=20)
            name_entry.pack(side="left", padx=5)
            self.people_entries.append(name_entry)

            amount_entry = tk.Entry(frame, width=10)
            amount_entry.pack(side="left", padx=5)
            self.amount_entries.append(amount_entry)

        self.toggle_amount_fields()
        self.root.update_idletasks()

    def toggle_amount_fields(self):
        state = "disabled" if self.split_type.get() == "even" else "normal"
        for entry in self.amount_entries:
            entry.configure(state=state)

    def calculate_bill(self):
        currency = self.currency_var.get()
        tip_percentage = self.validate_float(self.tip_var.get(), "Tip %")
        if tip_percentage is None:
            return

        names = []
        for entry in self.people_entries:
            name = entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Please fill in all names.")
                return
            names.append(name.title())

        amounts = []
        if self.split_type.get() == "even":
            total_bill = self.ask_total_bill(currency)
            if total_bill is None:
                return
            share = total_bill / len(names)
            amounts = [share] * len(names)
        else:
            total_bill = 0
            for entry in self.amount_entries:
                amount = self.validate_float(entry.get(), "Amount")
                if amount is None:
                    return
                amounts.append(amount)
                total_bill += amount

        tip_amount = (tip_percentage / 100) * total_bill
        total_with_tip = total_bill + tip_amount
        amounts = [round(a + (a / total_bill) * tip_amount, 2)
                   for a in amounts]

        self.show_result(names, amounts, currency, total_bill,
                         tip_amount, total_with_tip)

    def validate_float(self, value, field_name):
        try:
            val = float(value)
            if val < 0:
                raise ValueError
            return val
        except ValueError:
            messagebox.showerror("Error", f"Invalid value for {field_name}.")
            return None

    def ask_total_bill(self, currency):
        dialog = CenteredDialog(self.root, title="Total Bill",
                                prompt=f"Enter total bill amount ({currency}):",
                                currency=currency)
        return self.validate_float(dialog.result, "Total Bill") if dialog.result else None

    def show_result(self, names, amounts, currency, total_bill, tip_amount, total_with_tip):
        result_win = tk.Toplevel(self.root)
        self.all_windows.append(result_win)
        result_win.title("📜 Bill Summary")

        result_win.configure(bg=self.current_theme["bg"])

        # Position bill summary window at the top-right
        result_win.update_idletasks()
        screen_width = result_win.winfo_screenwidth()
        win_width = 400  # estimated width
        result_win.geometry(f"{win_width}x400+{screen_width - win_width}+0")

        tree = ttk.Treeview(result_win, columns=(
            "Name", "Amount"), show="headings")
        tree.heading("Name", text="Name")
        tree.heading("Amount", text="Amount Owed")
        tree.column("Name", width=150, anchor="center")
        tree.column("Amount", width=100, anchor="center")
        for n, a in zip(names, amounts):
            tree.insert("", "end", values=(n, f"{currency}{a:.2f}"))
        tree.pack(padx=10, pady=10, fill="x")

        summary = f"Total Bill: {currency}{total_bill:.2f}\nTip: {currency}{tip_amount:.2f}\nGrand Total: {currency}{total_with_tip:.2f}"
        tk.Label(result_win, text=summary, bg=self.current_theme["bg"], fg=self.current_theme["fg"],
                 font=("Helvetica", 12, "bold")).pack(pady=5)

        btn_frame = tk.Frame(result_win, bg=self.current_theme["bg"])
        btn_frame.pack(pady=5)

        btn_copy = tk.Button(btn_frame, text="📋 Copy",
                             command=lambda: self.copy_to_clipboard(summary))
        btn_copy.pack(side="left", padx=5)
        self.style_button(btn_copy)

        btn_close = tk.Button(btn_frame, text="❌ Close",
                              command=self.close_all_windows)
        btn_close.pack(side="left", padx=5)
        self.style_button(btn_close)

        self.apply_theme()

    def copy_to_clipboard(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        messagebox.showinfo("Copied", "Summary copied to clipboard!")

    def close_all_windows(self):
        for win in self.all_windows:
            try:
                win.destroy()
            except:
                pass

    def toggle_theme(self):
        self.current_theme = self.dark_theme if self.current_theme == self.light_theme else self.light_theme
        self.apply_theme()

    def _blend_color(self, hex1, hex2, ratio):
        r1, g1, b1 = int(hex1[1:3], 16), int(hex1[3:5], 16), int(hex1[5:], 16)
        r2, g2, b2 = int(hex2[1:3], 16), int(hex2[3:5], 16), int(hex2[5:], 16)
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        return f"#{r:02x}{g:02x}{b:02x}"

    def apply_theme(self):
        theme = self.current_theme
        for win in self.all_windows:
            try:
                win.configure(bg=theme["bg"])
                for child in win.winfo_children():
                    try:
                        child.configure(bg=theme["bg"], fg=theme["fg"])
                    except:
                        pass
                    if isinstance(child, tk.Button):
                        self.style_button(child)
            except:
                pass

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = BillSplitterApp(root)
    app.run()
