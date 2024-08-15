import os
import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, Scrollbar, Frame, Canvas

class CodebaseConsolidatorApp:
    GITIGNORE_PATTERNS = {
        "None": [],
        "Python": ["__pycache__", ".pyc", ".pyo", ".pyd", ".venv", ".env", "env/", "venv/"],
        "Java": ["*.class", "*.jar", "*.war", "*.ear", "*.nar", "*.rar", "*.har", "*.java"],
        "Node": ["node_modules", "*.log", "npm-debug.log", "yarn-error.log"],
        "C++": ["*.o", "*.obj", "*.exe", "*.dll", "*.so", "*.out"],
        "C#": ["bin/", "obj/", "*.exe", "*.dll", "*.pdb"],
        "Django": ["*.pyc", "__pycache__", "*.log", "*.pot", "db.sqlite3"],
        "Flask": ["instance/", "*.pyc", "__pycache__"],
    }

    def __init__(self, root, initial_dir=None):
        self.root = root
        root.title("Codebase Consolidator")

        self.file_vars = {}
        self.create_widgets()

        if initial_dir:
            self.root_dir_entry.config(state=tk.NORMAL)
            self.root_dir_entry.insert(0, initial_dir)
            self.root_dir_entry.config(state=tk.DISABLED)
            self.populate_file_list(Path(initial_dir))

    def create_widgets(self):
        tk.Label(self.root, text="Root Directory:").grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.root_dir_entry = tk.Entry(self.root, state=tk.DISABLED)
        self.root_dir_entry.grid(row=0, column=1, padx=10, pady=5, sticky='ew')
        tk.Button(self.root, text="Browse...", command=self.browse_root_dir).grid(row=0, column=2, padx=10, pady=5)

        tk.Label(self.root, text="Git Ignore:").grid(row=1, column=0, padx=10, pady=5, sticky='w')
        self.gitignore_var = tk.StringVar(self.root, "None")
        self.gitignore_menu = tk.OptionMenu(self.root, self.gitignore_var, *self.GITIGNORE_PATTERNS.keys())
        self.gitignore_menu.grid(row=1, column=1, padx=10, pady=5, sticky='ew')

        tk.Label(self.root, text="Files to Consolidate:").grid(row=2, column=0, padx=10, pady=5, sticky='w')
        self.canvas = Canvas(self.root)
        self.canvas.grid(row=2, column=1, columnspan=2, padx=10, pady=5, sticky='nsew')

        self.scrollbar = Scrollbar(self.root, orient='vertical', command=self.canvas.yview)
        self.scrollbar.grid(row=2, column=3, sticky='ns')

        self.canvas.config(yscrollcommand=self.scrollbar.set)

        self.file_frame = Frame(self.canvas)
        self.file_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.file_frame, anchor="nw")

        button_frame = tk.Frame(self.root)
        button_frame.grid(row=3, column=1, columnspan=2, pady=10)

        tk.Button(button_frame, text="Save", command=self.save_to_file).pack(side="left", padx=10)
        tk.Button(button_frame, text="Copy", command=self.copy_to_clipboard).pack(side="left", padx=10)

        # Add Select All and Deselect All buttons
        tk.Button(button_frame, text="Select All", command=self.select_all).pack(side="left", padx=10)
        tk.Button(button_frame, text="Deselect All", command=self.deselect_all).pack(side="left", padx=10)

        tk.Label(self.root, text="File Extension:").grid(row=4, column=0, padx=10, pady=5, sticky='w')
        self.extension_var = tk.StringVar(self.root, "*.*")
        self.extension_menu = tk.OptionMenu(self.root, self.extension_var, "*.*")
        self.extension_menu.grid(row=4, column=1, padx=10, pady=5, sticky='ew')
        tk.Button(self.root, text="Select All with Extension", command=self.select_all_with_extension).grid(row=4, column=2, padx=10, pady=5)

        self.output_text = tk.Text(self.root, wrap='word', state=tk.DISABLED)
        self.output_text.grid(row=0, column=4, rowspan=4, padx=10, pady=5, sticky='nsew')

        self.output_scrollbar = Scrollbar(self.root, orient='vertical', command=self.output_text.yview)
        self.output_scrollbar.grid(row=0, column=5, rowspan=4, sticky='ns')
        self.output_text.config(yscrollcommand=self.output_scrollbar.set)

        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(4, weight=2)

    def browse_root_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            path = Path(directory)
            self.root_dir_entry.config(state=tk.NORMAL)
            self.root_dir_entry.delete(0, tk.END)
            self.root_dir_entry.insert(0, path)
            self.root_dir_entry.config(state=tk.DISABLED)
            self.populate_file_list(path)

    def populate_file_list(self, directory):
        print(f"Populating file list for directory: {directory}")
        if not directory.is_dir():
            return

        for widget in self.file_frame.winfo_children():
            widget.destroy()

        self.file_vars.clear()

        gitignore_patterns = self.GITIGNORE_PATTERNS[self.gitignore_var.get()] + [".git"]
        row = 0
        extensions = set()

        try:
            for root, dirs, files in os.walk(directory):
                print(f"Processing directory: {root}")
                dirs[:] = [d for d in dirs if not any(ig in d for ig in gitignore_patterns)]
                for file in files:
                    file_path = os.path.join(root, file)
                    if any(ig in file_path for ig in gitignore_patterns):
                        continue

                    if file.lower().endswith(('.exe', '.dll', '.so', '.pyd', '.jar', '.class', '.pyc', '.pyo', '.pyd')):
                        print(f"Skipping non-text file: {file_path}")
                        continue

                    if not self.is_text_file(file_path):
                        print(f"File not recognized as text: {file_path}")
                        continue

                    relative_path = os.path.relpath(file_path, start=directory)
                    var = tk.BooleanVar(value=False)
                    cb = tk.Checkbutton(self.file_frame, text=relative_path, variable=var, command=self.update_text_field)
                    try:
                        cb.grid(row=row, column=0, sticky='w')
                        self.file_vars[relative_path] = var
                        row += 1

                    except Exception as e:
                        print(f"Error placing Checkbutton at row {row}: {e}")
                        break

                    # Extract file extension
                    ext = Path(file_path).suffix.lower()
                    if ext:
                        extensions.add(ext)

            # Update extension dropdown
            extension_list = sorted(extensions) + ["*.*"]
            self.update_extension_menu(extension_list)

            print("File list population complete")
            self.file_frame.update_idletasks()
            self.canvas.config(scrollregion=self.canvas.bbox("all"))
        except Exception as e:
            print(f"An error occurred while populating file list: {e}")

    def update_extension_menu(self, extensions):
        # Update the OptionMenu with new extensions
        menu = self.extension_menu['menu']
        menu.delete(0, 'end')

        for ext in extensions:
            menu.add_command(label=ext, command=tk._setit(self.extension_var, ext))

        # Ensure '*.*' option is always included
        menu.add_command(label="*.*", command=tk._setit(self.extension_var, "*.*"))

    def update_text_field(self):
        selected_files = [os.path.join(self.root_dir_entry.get(), path) for path, var in self.file_vars.items() if var.get()]
        try:
            self.generate_codebase_text(selected_files, self.gitignore_var.get())
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def is_text_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                file.read(512)
            return True
        except (UnicodeDecodeError, OSError):
            return False

    def generate_codebase_text(self, selected_files, gitignore_selection):
        gitignore_patterns = self.GITIGNORE_PATTERNS[gitignore_selection] + [".git"]

        output_lines = []
        root_dir = self.root_dir_entry.get()  # Get the root directory

        for file_path in selected_files:
            if any(ig in file_path for ig in gitignore_patterns):
                continue

            try:
                # Get the relative path based on the root directory
                relative_file_path = os.path.relpath(file_path, start=root_dir)
                output_lines.append(f"--- {relative_file_path} ---\n")  # Use relative path
                with open(file_path, 'r', encoding='utf-8') as infile:
                    output_lines.append(infile.read())
                    output_lines.append("\n\n")
            except Exception as e:
                output_lines.append(f"Error reading {file_path}: {e}\n\n")

        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, ''.join(output_lines))
        self.output_text.config(state=tk.DISABLED)

    def save_to_file(self):
        root_dir = self.root_dir_entry.get()
        
        if not os.path.isdir(root_dir):
            messagebox.showerror("Error", "The selected root directory does not exist.")
            return

        default_file_name = f"{os.path.basename(os.path.normpath(root_dir))}_consolidated.txt"
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                initialfile=default_file_name,
                                                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(self.output_text.get(1.0, tk.END))
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while saving the file: {e}")

    def copy_to_clipboard(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.output_text.get(1.0, tk.END))
        self.root.update()

    def select_all(self):
        for var in self.file_vars.values():
            var.set(True)
        self.update_text_field()

    def deselect_all(self):
        for var in self.file_vars.values():
            var.set(False)
        self.update_text_field()

    def select_all_with_extension(self):
        extension = self.extension_var.get()
        if extension == "*.*":
            messagebox.showinfo("Info", "Select 'All Files' is not supported. Use 'Select All' instead.")
            return

        for file_path, var in self.file_vars.items():
            if file_path.lower().endswith(extension.lower()):
                var.set(True)
            else:
                var.set(False)

        # Update the output text field with selected files
        self.update_text_field()

if __name__ == "__main__":
    initial_directory = sys.argv[1] if len(sys.argv) > 1 else None
    root = tk.Tk()
    app = CodebaseConsolidatorApp(root, initial_directory)
    root.mainloop()
