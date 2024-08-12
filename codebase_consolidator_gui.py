import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, Scrollbar, Listbox

class CodebaseConsolidatorApp:
    def __init__(self, root, initial_dir=None):
        self.root = root
        root.title("Codebase Consolidator")

        # Define gitignore options
        self.gitignore_options = ["None", "Python", "Java", "Node", "C++", "C#", "Django", "Flask"]

        # Create and place widgets
        self.create_widgets()

        # If an initial directory was provided, set it
        if initial_dir:
            self.root_dir_entry.insert(0, initial_dir)
            self.populate_file_list(initial_dir)
        else:
            self.root_dir_entry.insert(0, "")  # Ensure entry is blank if no directory

    def create_widgets(self):
        # Root Directory
        tk.Label(self.root, text="Root Directory:").grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.root_dir_entry = tk.Entry(self.root)
        self.root_dir_entry.grid(row=0, column=1, padx=10, pady=5, sticky='ew')
        tk.Button(self.root, text="Browse...", command=self.browse_root_dir).grid(row=0, column=2, padx=10, pady=5)

        # Gitignore dropdown
        tk.Label(self.root, text="Git Ignore:").grid(row=1, column=0, padx=10, pady=5, sticky='w')
        self.gitignore_var = tk.StringVar(self.root)
        self.gitignore_var.set(self.gitignore_options[0])  # default value
        self.gitignore_menu = tk.OptionMenu(self.root, self.gitignore_var, *self.gitignore_options)
        self.gitignore_menu.grid(row=1, column=1, padx=10, pady=5, sticky='ew')

        # File Listbox
        tk.Label(self.root, text="Files to Consolidate:").grid(row=2, column=0, padx=10, pady=5, sticky='w')
        self.file_listbox = Listbox(self.root, selectmode='multiple')
        self.file_listbox.grid(row=2, column=1, columnspan=2, padx=10, pady=5, sticky='nsew')

        # Add scrollbar
        self.scrollbar = Scrollbar(self.root, orient='vertical', command=self.file_listbox.yview)
        self.scrollbar.grid(row=2, column=3, sticky='ns')
        self.file_listbox.config(yscrollcommand=self.scrollbar.set)

        # Action Buttons
        button_frame = tk.Frame(self.root)
        button_frame.grid(row=3, column=1, columnspan=2, pady=10)

        tk.Button(button_frame, text="Consolidate", command=self.consolidate_codebase).pack(side="left", padx=10)
        tk.Button(button_frame, text="Save", command=self.save_to_file).pack(side="left", padx=10)
        tk.Button(button_frame, text="Copy", command=self.copy_to_clipboard).pack(side="left", padx=10)

        # Output Text Widget
        self.output_text = tk.Text(self.root, wrap='word')
        self.output_text.grid(row=0, column=4, rowspan=4, padx=10, pady=5, sticky='nsew')

        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_rowconfigure(3, weight=0)
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=0)
        self.root.grid_columnconfigure(3, weight=0)
        self.root.grid_columnconfigure(4, weight=2)

    def browse_root_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.root_dir_entry.delete(0, tk.END)
            self.root_dir_entry.insert(0, directory)
            self.populate_file_list(directory)

    def populate_file_list(self, directory):
        self.file_listbox.delete(0, tk.END)  # Clear existing items

        if not directory or not os.path.isdir(directory):  # Handle empty or invalid directory
            return

        gitignore_selection = self.gitignore_var.get()
        gitignore_patterns = self.get_gitignore_patterns(gitignore_selection)
        gitignore_patterns.append(".git")  # Always ignore Git files and directories

        for root, dirs, files in os.walk(directory):
            # Skip directories matching gitignore patterns
            dirs[:] = [d for d in dirs if not any(ig in d for ig in gitignore_patterns)]

            for file in files:
                file_path = os.path.join(root, file)
                if any(ig in file_path for ig in gitignore_patterns):
                    continue  # Skip ignored files

                if self.is_text_file(file_path):
                    # Make file path relative to the root directory
                    relative_path = os.path.relpath(file_path, start=directory)
                    self.file_listbox.insert(tk.END, relative_path)

    def consolidate_codebase(self):
        selected_files = [self.file_listbox.get(i) for i in self.file_listbox.curselection()]
        root_dir = self.root_dir_entry.get()
        gitignore_selection = self.gitignore_var.get()

        if not selected_files:
            messagebox.showerror("Error", "No files selected for consolidation.")
            return

        # Convert relative paths back to absolute paths
        selected_files = [os.path.join(root_dir, f) for f in selected_files]

        # Check if all selected files are text files
        non_text_files = [f for f in selected_files if not self.is_text_file(f)]
        if non_text_files:
            non_text_files_str = "\n".join(non_text_files)
            messagebox.showwarning("Warning", f"The following files are not text files and will be excluded:\n{non_text_files_str}")
            selected_files = [f for f in selected_files if self.is_text_file(f)]

        try:
            self.generate_codebase_text(selected_files, gitignore_selection)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def is_text_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                file.read(512)  # Read first 512 bytes to determine if it's a text file
            return True
        except UnicodeDecodeError:
            return False

    def generate_codebase_text(self, selected_files, gitignore_selection):
        # Define files and directories to ignore
        gitignore_patterns = self.get_gitignore_patterns(gitignore_selection)
        gitignore_patterns.append(".git")  # Always ignore Git files and directories

        output_lines = []
        for file_path in selected_files:
            if any(ig in file_path for ig in gitignore_patterns):
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as infile:
                    # Make file path relative to the root directory
                    relative_path = os.path.relpath(file_path, start=os.path.dirname(file_path))
                    output_lines.append(f"--- {relative_path} ---\n")
                    output_lines.append(infile.read())
                    output_lines.append("\n\n")
            except Exception as e:
                output_lines.append(f"Error reading {file_path}: {e}\n\n")

        # Update Text widget with generated content
        self.output_text.delete(1.0, tk.END)  # Clear existing content
        self.output_text.insert(tk.END, ''.join(output_lines))

    def get_gitignore_patterns(self, selection):
        patterns = {
            "None": [],
            "Python": ["__pycache__", ".pyc", ".pyo", ".pyd", ".venv", ".env", "env/", "venv/"],
            "Java": ["*.class", "*.jar", "*.war", "*.ear", "*.nar", "*.rar", "*.har", "*.java"],
            "Node": ["node_modules", "*.log", "npm-debug.log", "yarn-error.log"],
            "C++": ["*.o", "*.obj", "*.exe", "*.dll", "*.so", "*.out"],
            "C#": ["bin/", "obj/", "*.exe", "*.dll", "*.pdb"],
            "Django": ["*.pyc", "__pycache__", "*.log", "*.pot", "db.sqlite3"],
            "Flask": ["instance/", "*.pyc", "__pycache__"],
        }
        return patterns.get(selection, [])

    def save_to_file(self):
        # Get the root directory from the entry
        root_dir = self.root_dir_entry.get()
        
        if not os.path.isdir(root_dir):
            messagebox.showerror("Error", "The selected root directory does not exist.")
            return
        
        # Extract the root directory name to use as the default file name
        root_dir_name = os.path.basename(os.path.normpath(root_dir))
        default_file_name = f"{root_dir_name}_consolidated.txt"

        # Open the save dialog with the default file name
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
        self.root.update()  # Important for clipboard to work on some systems

if __name__ == "__main__":
    initial_directory = None
    if len(sys.argv) > 1:
        initial_directory = sys.argv[1]
    
    root = tk.Tk()
    app = CodebaseConsolidatorApp(root, initial_directory)
    root.mainloop()
