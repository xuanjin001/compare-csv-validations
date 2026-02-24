import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class ColumnSelector(tk.Toplevel):
    def __init__(self, parent, columns, title="Select Column", multi=True):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x500")
        self.result = None
        self.columns = columns
        self.vars = {}
        self.multi = multi

        tk.Label(self, text="Search Columns:").pack(pady=5)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_columns)
        tk.Entry(self, textvariable=self.search_var).pack(fill="x", padx=10)

        self.frame = tk.Frame(self)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.canvas = tk.Canvas(self.frame)
        self.scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.refresh_list()
        tk.Button(self, text="Confirm Selection", command=self.confirm, bg="#4CAF50", fg="white").pack(pady=10)
        self.grab_set()
        self.wait_window()

    def refresh_list(self, filter_text=""):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        for col in self.columns:
            if filter_text.lower() in col.lower():
                var = self.vars.get(col, tk.BooleanVar())
                self.vars[col] = var
                if self.multi:
                    tk.Checkbutton(self.scrollable_frame, text=col, variable=var).pack(anchor="w")
                else:
                    tk.Radiobutton(self.scrollable_frame, text=col, variable=var, value=True, 
                                   command=lambda c=col: self.single_select(c)).pack(anchor="w")

    def single_select(self, selected_col):
        for col, var in self.vars.items():
            var.set(col == selected_col)

    def filter_columns(self, *args):
        self.refresh_list(self.search_var.get())

    def confirm(self):
        self.result = [col for col, var in self.vars.items() if var.get()]
        self.destroy()

def select_file(title):
    return filedialog.askopenfilename(title=title, filetypes=[("CSV files", "*.csv")])

def run_comparison():
    f1_path, f2_path = select_file("Select Baseline CSV (File 1)"), select_file("Select Comparison CSV (File 2)")
    if not f1_path or not f2_path: return

    try:
        df1 = pd.read_csv(f1_path)
        df2 = pd.read_csv(f2_path)

        # 1. Map Key Columns
        key1 = ColumnSelector(root, df1.columns.tolist(), "Select KEY Column for File 1", multi=False).result
        key2 = ColumnSelector(root, df2.columns.tolist(), "Select KEY Column for File 2", multi=False).result
        if not key1 or not key2: return
        k1, k2 = key1[0], key2[0]

        # 2. Map Comparison Columns
        cols1 = ColumnSelector(root, [c for c in df1.columns if c != k1], "Select Columns in FILE 1 to check").result
        if not cols1: return
        
        # For each column in File 1, pick the partner in File 2
        mapping = {}
        for c1 in cols1:
            c2_choice = ColumnSelector(root, df2.columns.tolist(), f"Select matching column in File 2 for: {c1}", multi=False).result
            if c2_choice:
                mapping[c1] = c2_choice[0]

        # --- Comparison Engine ---
        df1_sub = df1.set_index(k1)[list(mapping.keys())].fillna('N/A')
        df2_sub = df2.set_index(k2)[list(mapping.values())].fillna('N/A')

        # Find overlapping IDs
        common_keys = df1_sub.index.intersection(df2_sub.index)
        report_data = []

        for idx in common_keys:
            row_diff = { "File1_Key": idx }
            has_change = False
            
            for c1, c2 in mapping.items():
                val1 = df1_sub.at[idx, c1]
                val2 = df2_sub.at[idx, c2]
                
                if str(val1) != str(val2):
                    row_diff[f"{c1} vs {c2}"] = f"DIFF: [{val1}] -> [{val2}]"
                    has_change = True
                else:
                    row_diff[f"{c1} vs {c2}"] = val1
            
            if has_change:
                report_data.append(row_diff)

        # Results and Saving
        if report_data:
            final_report = pd.DataFrame(report_data)
            save_path = filedialog.asksaveasfilename(defaultextension=".csv", title="Save Comparison")
            if save_path:
                final_report.to_csv(save_path, index=False)
                messagebox.showinfo("Done", f"Found {len(report_data)} rows with differences.")
        else:
            messagebox.showinfo("Results", "No differences found.")

    except Exception as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title("Multi-Column Mapper")
root.geometry("300x100")
tk.Button(root, text="🚀 Compare Different Files", command=run_comparison).pack(pady=30)
root.mainloop()