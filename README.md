# compare-csv-validations

compare-csv-validations

## make it mac and windows compatible

To make your CSV Reconciliation Tool a professional standalone application (an **.exe** for Windows or a **.app** for macOS), you will use **PyInstaller**.

Since your code now uses **Pandas**, which is a large library, and **Tkinter**, which is a GUI framework, there are specific steps to ensure the application remains portable and doesn't trigger antivirus "false positives."

---

### 1. Preparation

Open your terminal (Mac) or Command Prompt/PowerShell (Windows) and install the necessary "freezing" tool:

```bash
pip install pyinstaller

```

### 2. The Build Command

Navigate to the folder containing your script (let's assume it's named `csv_recon.py`) and run the command specific to your Operating System.

#### For Windows

This creates a single, portable executable file.

```bash
pyinstaller --noconsole --onefile --clean --name "CSV_Reconciliation_Tool" csv_recon.py

```

#### For macOS

This creates a double-clickable app bundle.

```bash
pyinstaller --noconsole --onefile --windowed --name "CSV_Recon" csv_recon.py

```

**What these flags do:**

- `--onefile`: Bundles everything (Python, Pandas, your code) into **one** file.
- `--noconsole` / `--windowed`: Ensures the black terminal window doesn't appear when the user opens the app.
- `--clean`: Clears out old temporary cache files before building.

---

### 3. Locating Your Application

After the process finishes, you will see a folder named **`dist`**.

- **On Windows:** You will find `CSV_Reconciliation_Tool.exe`.
- **On macOS:** You will find `CSV_Recon.app`.

---

### 4. Important Platform Considerations

| Feature            | Windows Note                                                                                        | macOS Note                                                                                               |
| ------------------ | --------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| **Cross-Building** | You **cannot** build a Mac app from Windows. You must build on a Mac to get a Mac app.              | You **cannot** build a Windows .exe from a Mac.                                                          |
| **Permissions**    | The `.exe` might trigger "Windows Protected your PC." Users must click _More Info_ -> _Run Anyway_. | Users must **Right-Click -> Open** the first time to bypass the "Unidentified Developer" security block. |
| **Performance**    | The first launch may be slow (5–10 seconds) because it unpacks the Pandas engine to a temp folder.  | Launching the `.app` is generally snappy, but file sizes will be around 60MB.                            |

---

### 5. (Optional) Adding a Professional Icon

If you want a custom icon instead of the default Python logo:

1. Get an `.ico` file (Windows) or an `.icns` file (Mac).
2. Add the flag to your command: `--icon=my_logo.ico`.

### Troubleshooting Tip

If your app crashes immediately, try building it **without** the `--noconsole` flag first. This allows you to see the error message in the terminal if the program fails to find a file or a library.
