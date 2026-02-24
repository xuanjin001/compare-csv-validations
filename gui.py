import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

def select_file(title):
    path = filedialog.askopenfilename(title=title, filetypes=[("CSV files", "*.csv")])
    return path

def run_comparison():
    # 1. Select Files
    file1 = select_file("Select First CSV (Baseline)")
    if not file1: return
    file2 = select_file("Select Second CSV (Comparison)")
    if not file2: return

    try:
        df1 = pd.read_csv(file1)
        df2 = pd.read_csv(file2)

        # 2. Identify common columns to show the user
        common_cols = list(set(df1.columns) & set(df2.columns))
        if not common_cols:
            messagebox.showerror("Error", "No matching columns found between the two files.")
            return

        # 3. Ask for Key Column
        key_col = simpledialog.askstring("Input", f"Enter the Key Column (Unique ID):\nOptions: {', '.join(common_cols)}")
        if key_col not in common_cols:
            messagebox.showerror("Error", "Invalid key column.")
            return

        # 4. Ask for Columns to Compare (comma-separated)
        compare_str = simpledialog.askstring("Input", "Enter columns to compare (comma-separated):\nLeave blank to compare all.")
        if compare_str:
            cols_to_compare = [c.strip() for c in compare_str.split(',') if c.strip() in common_cols]
        else:
            cols_to_compare = [c for c in common_cols if c != key_col]

        # --- Comparison Logic ---
        df1_sub = df1.set_index(key_col)[cols_to_compare]
        df2_sub = df2.set_index(key_col)[cols_to_compare]

        # Find changes in overlapping keys
        common_keys = df1_sub.index.intersection(df2_sub.index)
        diff_mask = (df1_sub.loc[common_keys] != df2_sub.loc[common_keys]).any(axis=1)
        changes = df1_sub.loc[common_keys][diff_mask]

        # 5. Output Results
        output_msg = (f"Analysis Complete:\n"
                      f"- Rows missing in File 2: {len(df1.index.difference(df2.index))}\n"
                      f"- New rows in File 2: {len(df2.index.difference(df1.index))}\n"
                      f"- Rows with data differences: {len(changes)}")
        
        messagebox.showinfo("Results", output_msg)
        
        if len(changes) > 0:
            save_path = filedialog.asksaveasfilename(defaultextension=".csv", title="Save Differences As...")
            if save_path:
                changes.to_csv(save_path)

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Setup the GUI Window
root = tk.Tk()
root.title("CSV Compare Tool")
root.geometry("300x150")

label = tk.Label(root, text="Compare two CSV files by Key", pady=20)
label.pack()

btn = tk.Button(root, text="Start Comparison", command=run_comparison, bg="#4CAF50", fg="white")
btn.pack(pady=10)

root.mainloop()