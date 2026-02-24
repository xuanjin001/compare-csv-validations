import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class MappingWindow(tk.Toplevel):
    """A side-by-side mapping interface."""
    def __init__(self, parent, cols1, cols2):
        super().__init__(parent)
        self.title("Map Columns: File 1 ➔ File 2")
        self.geometry("600x500")
        self.mapping_results = {}
        self.key_mapping = None

        # Container for scrolling
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
        tk.Label(self.scrollable_frame, text="FILE 1 COLUMN", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=10, pady=10)
        tk.Label(self.scrollable_frame, text="FILE 2 COLUMN (MATCH)", font=('Arial', 10, 'bold')).grid(row=0, column=1, padx=10, pady=10)
        tk.Label(self.scrollable_frame, text="IS KEY?", font=('Arial', 10, 'bold')).grid(row=0, column=2, padx=10, pady=10)

        self.rows = []
        options2 = ["(Ignore)"] + cols2
        
        # Create a row for every column in File 1
        for i, col1 in enumerate(cols1):
            # Left side: File 1 label
            tk.Label(self.scrollable_frame, text=col1).grid(row=i+1, column=0, sticky="w", padx=20)
            
            # Right side: File 2 dropdown
            combo = ttk.Combobox(self.scrollable_frame, values=options2, width=30)
            # Smart Guess: if name matches exactly, pre-select it
            if col1 in cols2:
                combo.set(col1)
            else:
                combo.set("(Ignore)")
            combo.grid(row=i+1, column=1, padx=10, pady=2)
            
            # Key Column Radio Logic
            key_var = tk.BooleanVar(value=False)
            rb = tk.Checkbutton(self.scrollable_frame, variable=key_var, command=lambda v=key_var, idx=i: self.ensure_single_key(idx))
            rb.grid(row=i+1, column=2)
            
            self.rows.append({'col1': col1, 'combo': combo, 'key_var': key_var})

        tk.Button(self, text="Start Comparison", command=self.validate_and_confirm, bg="#4CAF50", fg="white", height=2).pack(fill="x", pady=10)
        
        self.grab_set()
        self.wait_window()

    def ensure_single_key(self, current_idx):
        """Logic to ensure only one checkbox is selected as the Key."""
        for i, row in enumerate(self.rows):
            if i != current_idx:
                row['key_var'].set(False)

    def validate_and_confirm(self):
        mapping = {}
        key_pair = None
        
        for row in self.rows:
            c1 = row['col1']
            c2 = row['combo'].get()
            is_key = row['key_var'].get()

            if c2 != "(Ignore)":
                if is_key:
                    key_pair = (c1, c2)
                else:
                    mapping[c1] = c2

        if not key_pair:
            messagebox.showerror("Error", "Please select one 'IS KEY?' checkbox to link the files.")
            return
        
        self.key_mapping = key_pair
        self.mapping_results = mapping
        self.destroy()

def run_comparison():
    f1_path = filedialog.askopenfilename(title="Select File 1")
    f2_path = filedialog.askopenfilename(title="Select File 2")
    if not f1_path or not f2_path: return

    try:
        df1 = pd.read_csv(f1_path)
        df2 = pd.read_csv(f2_path)

        # Launch the Graphic Mapper
        mapper = MappingWindow(root, df1.columns.tolist(), df2.columns.tolist())
        
        if not mapper.key_mapping: return # User closed window

        k1, k2 = mapper.key_mapping
        mapping = mapper.mapping_results

        # --- Comparison Logic ---
        df1_sub = df1.set_index(k1)[list(mapping.keys())].fillna('N/A')
        df2_sub = df2.set_index(k2)[list(mapping.values())].fillna('N/A')

        common_keys = df1_sub.index.intersection(df2_sub.index)
        report_data = []

        for idx in common_keys:
            row_diff = { "Key_ID": idx }
            changed = False
            for c1, c2 in mapping.items():
                v1, v2 = df1_sub.at[idx, c1], df2_sub.at[idx, c2]
                if str(v1) != str(v2):
                    row_diff[f"{c1} vs {c2}"] = f"{v1} -> {v2}"
                    changed = True
                else:
                    row_diff[f"{c1} vs {c2}"] = v1
            
            if changed:
                report_data.append(row_diff)

        # Save Result
        if report_data:
            pd.DataFrame(report_data).to_csv(filedialog.asksaveasfilename(defaultextension=".csv"), index=False)
            messagebox.showinfo("Success", "Differences saved.")
        else:
            messagebox.showinfo("Result", "No differences found.")

    except Exception as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title("CSV Data Mapper")
root.geometry("300x100")
tk.Button(root, text="🚀 Load & Map Files", command=run_comparison, pady=10).pack(expand=True)
root.mainloop()