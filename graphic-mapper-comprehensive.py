import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class MappingWindow(tk.Toplevel):
    """A side-by-side mapping interface."""
    def __init__(self, parent, cols1, cols2):
        super().__init__(parent)
        self.title("Map Columns: File 1 ➔ File 2")
        self.geometry("700x600")
        self.mapping_results = {}
        self.key_mapping = None

        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Table Headers
        headers = [("FILE 1 COLUMN", 0), ("FILE 2 COLUMN (MATCH)", 1), ("IS KEY?", 2)]
        for text, col in headers:
            tk.Label(self.scrollable_frame, text=text, font=('Arial', 10, 'bold')).grid(row=0, column=col, padx=10, pady=10)

        self.rows = []
        options2 = ["(Ignore)"] + cols2
        
        for i, col1 in enumerate(cols1):
            tk.Label(self.scrollable_frame, text=col1).grid(row=i+1, column=0, sticky="w", padx=20)
            combo = ttk.Combobox(self.scrollable_frame, values=options2, width=30)
            if col1 in cols2: combo.set(col1)
            else: combo.set("(Ignore)")
            combo.grid(row=i+1, column=1, padx=10, pady=2)
            
            key_var = tk.BooleanVar(value=False)
            tk.Checkbutton(self.scrollable_frame, variable=key_var, command=lambda v=key_var, idx=i: self.ensure_single_key(idx)).grid(row=i+1, column=2)
            self.rows.append({'col1': col1, 'combo': combo, 'key_var': key_var})

        tk.Button(self, text="Run Full Analysis", command=self.validate_and_confirm, bg="#4CAF50", fg="white", height=2).pack(fill="x", pady=10)
        self.grab_set()
        self.wait_window()

    def ensure_single_key(self, current_idx):
        for i, row in enumerate(self.rows):
            if i != current_idx: row['key_var'].set(False)

    def validate_and_confirm(self):
        mapping = {}
        key_pair = None
        for row in self.rows:
            c2 = row['combo'].get()
            if c2 != "(Ignore)":
                if row['key_var'].get(): key_pair = (row['col1'], c2)
                else: mapping[row['col1']] = c2

        if not key_pair:
            messagebox.showerror("Error", "Please select one 'IS KEY?' checkbox.")
            return
        
        self.key_mapping, self.mapping_results = key_pair, mapping
        self.destroy()

def run_comparison():
    f1_path = filedialog.askopenfilename(title="Select File 1 (Baseline)")
    f2_path = filedialog.askopenfilename(title="Select File 2 (Current)")
    if not f1_path or not f2_path: return

    try:
        df1, df2 = pd.read_csv(f1_path), pd.read_csv(f2_path)
        mapper = MappingWindow(root, df1.columns.tolist(), df2.columns.tolist())
        if not mapper.key_mapping: return 

        k1, k2 = mapper.key_mapping
        mapping = mapper.mapping_results

        # Pre-process DataFrames
        df1.set_index(k1, inplace=True)
        df2.set_index(k2, inplace=True)

        # 1. Missing Rows (In F1, not in F2)
        missing_ids = df1.index.difference(df2.index)
        df_missing = df1.loc[missing_ids].reset_index()

        # 2. New Rows (In F2, not in F1)
        new_ids = df2.index.difference(df1.index)
        df_new = df2.loc[new_ids].reset_index()

        # 3. Changed Data (Rows in both)
        common_keys = df1.index.intersection(df2.index)
        report_data = []
        for idx in common_keys:
            row_diff = { "Key_ID": idx }
            changed = False
            for c1, c2 in mapping.items():
                v1, v2 = df1.at[idx, c1], df2.at[idx, c2]
                if str(v1) != str(v2):
                    row_diff[f"{c1} vs {c2}"] = f"{v1} -> {v2}"
                    changed = True
                else: row_diff[f"{c1} vs {c2}"] = v1
            if changed: report_data.append(row_diff)
        
        df_changes = pd.DataFrame(report_data)

        # 4. Save Results to Multiple Sheets (Excel) or Multiple CSVs
        save_folder = filedialog.askdirectory(title="Select Folder to Save Reports")
        if save_folder:
            if not df_changes.empty: df_changes.to_csv(f"{save_folder}/data_changes.csv", index=False)
            if not df_missing.empty: df_missing.to_csv(f"{save_folder}/missing_rows.csv", index=False)
            if not df_new.empty: df_new.to_csv(f"{save_folder}/new_rows.csv", index=False)
            
            messagebox.showinfo("Success", f"Reports generated:\n- Changes: {len(df_changes)}\n- Missing: {len(df_missing)}\n- New: {len(df_new)}")

    except Exception as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title("CSV Reconciliation Tool")
root.geometry("300x120")
tk.Label(root, text="Map & Compare CSV Files", font=('Arial', 10)).pack(pady=10)
tk.Button(root, text="🚀 Start Analysis", command=run_comparison, bg="#2196F3", fg="white").pack(pady=5)
root.mainloop()