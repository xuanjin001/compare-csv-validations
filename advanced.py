import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class ColumnSelector(tk.Toplevel):
    """A popup window to search and select columns."""
    def __init__(self, parent, columns, title="Select Column"):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x500")
        self.result = None
        self.columns = columns
        self.vars = {}

        # Search Bar
        tk.Label(self, text="Search Columns:").pack(pady=5)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_columns)
        tk.Entry(self, textvariable=self.search_var).pack(fill="x", padx=10)

        # Scrollable List Frame
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

        # Confirm Button
        tk.Button(self, text="Confirm Selection", command=self.confirm, bg="#4CAF50", fg="white").pack(pady=10)
        
        self.grab_set() # Make window modal
        self.wait_window()

    def refresh_list(self, filter_text=""):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        for col in self.columns:
            if filter_text.lower() in col.lower():
                var = self.vars.get(col, tk.BooleanVar())
                self.vars[col] = var
                tk.Checkbutton(self.scrollable_frame, text=col, variable=var).pack(anchor="w")

    def filter_columns(self, *args):
        self.refresh_list(self.search_var.get())

    def confirm(self):
        self.result = [col for col, var in self.vars.items() if var.get()]
        self.destroy()

def select_file(title):
    return filedialog.askopenfilename(title=title, filetypes=[("CSV files", "*.csv")])

def run_comparison():
    f1, f2 = select_file("Select Baseline CSV"), select_file("Select Comparison CSV")
    if not f1 or not f2: return

    try:
        df1, df2 = pd.read_csv(f1), pd.read_csv(f2)
        common_cols = sorted(list(set(df1.columns) & set(df2.columns)))

        # 1. Select Key Column (Single Choice)
        key_selector = ColumnSelector(root, common_cols, "Select ONE Key Column (ID)")
        if not key_selector.result or len(key_selector.result) != 1:
            messagebox.showwarning("Warning", "You must select exactly one key column.")
            return
        key_col = key_selector.result[0]

        # 2. Select Columns to Compare (Multiple Choice)
        remaining_cols = [c for c in common_cols if c != key_col]
        compare_selector = ColumnSelector(root, remaining_cols, "Select Columns to Compare")
        cols_to_compare = compare_selector.result
        if not cols_to_compare: return

        # --- Comparison Engine ---
# --- Comparison Engine ---
        df1_sub = df1.set_index(key_col)[cols_to_compare].fillna('N/A')
        df2_sub = df2.set_index(key_col)[cols_to_compare].fillna('N/A')

        common_keys = df1_sub.index.intersection(df2_sub.index)
        
        # Filter both to only include common rows for comparison
        df1_common = df1_sub.loc[common_keys]
        df2_common = df2_sub.loc[common_keys]

        # Identify rows where ANY value is different
        diff_mask = (df1_common != df2_common).any(axis=1)
        
        # Initialize the final report with the index
        report_data = []

        for idx in common_keys[diff_mask]:
            row_diff = {key_col: idx}
            for col in cols_to_compare:
                val1 = df1_common.at[idx, col]
                val2 = df2_common.at[idx, col]
                
                if val1 != val2:
                    # Highlight the change visually in the cell
                    row_diff[col] = f"DIFF: [{val1}] -> [{val2}]"
                else:
                    # Keep it as is (or leave empty to make diffs pop)
                    row_diff[col] = val1
            
            report_data.append(row_diff)

        final_report = pd.DataFrame(report_data)

        # Save Logic
        if not final_report.empty:
            save_path = filedialog.asksaveasfilename(defaultextension=".csv", title="Save Differences")
            if save_path:
                final_report.to_csv(save_path, index=False)
                messagebox.showinfo("Success", f"Found {len(final_report)} rows with differences.")
        else:
            messagebox.showinfo("Results", "No differences found in selected columns!")

        # Add "New" values for side-by-side view
        for col in cols_to_compare:
            changes[f"{col}_new"] = df2_sub.loc[changes.index, col]

        # Save Logic
        if not changes.empty:
            save_path = filedialog.asksaveasfilename(defaultextension=".csv", title="Save Differences")
            if save_path:
                changes.to_csv(save_path)
                messagebox.showinfo("Success", f"Differences saved to {save_path}")
        else:
            messagebox.showinfo("Results", "No differences found in selected columns!")

    except Exception as e:
        messagebox.showerror("Error", f"Fatal Error: {e}")

root = tk.Tk()
root.title("Advanced CSV Compare")
root.geometry("300x100")
tk.Button(root, text="🚀 Start Comparison", command=run_comparison, height=2, width=20).pack(pady=20)
root.mainloop()