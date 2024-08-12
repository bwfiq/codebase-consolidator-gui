import os
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

class CodebaseConsolidatorApp:
    def __init__(self, root):
        self.root = root
        root.title("Codebase Consolidator")

        # Create and place widgets
        self.create_widgets()

    def create_widgets(self):
        # Root Directory
        tk.Label(self.root, text="Root Directory:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.root_dir_entry = tk.Entry(self.root, width=50)
        self.root_dir_entry.grid(row=0, column=1, padx=10, pady=5)
        tk.Button(self.root, text="Browse...", command=self.browse_root_dir).grid(row=0, column=2, padx=10, pady=5)

        # Process Button
        tk.Button(self.root, text="Consolidate Codebase", command=self.consolidate_codebase).grid(row=1, column=1, padx=10, pady=20)

    def browse_root_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.root_dir_entry.delete(0, tk.END)
            self.root_dir_entry.insert(0, directory)

    def consolidate_codebase(self):
        root_dir = self.root_dir_entry.get()

        if not os.path.isdir(root_dir):
            messagebox.showerror("Error", "The selected root directory does not exist.")
            return

        # Prompt user for output directory
        output_dir = filedialog.askdirectory(initialdir=os.path.expanduser("~/Downloads"), title="Select Output Directory")
        if not output_dir:
            messagebox.showerror("Error", "No output directory selected.")
            return

        # Create 'outputs' directory in the selected output directory
        outputs_dir = os.path.join(output_dir, 'outputs')
        os.makedirs(outputs_dir, exist_ok=True)

        # Generate output file name based on the directory name and timestamp
        dir_name = os.path.basename(root_dir.rstrip(os.sep))
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(outputs_dir, f"{dir_name}_{timestamp}.txt")

        try:
            self.write_codebase_to_file(root_dir, output_file)
            messagebox.showinfo("Success", f"Codebase has been written to {output_file}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def write_codebase_to_file(self, root_dir, output_file):
        # Define file extensions to include
        code_file_extensions = {'.py', '.js', '.java', '.cpp', '.c', '.h', '.html', '.css', '.json', '.xml', '.rb', '.php'}
        
        # Get the root directory name to remove from file paths
        root_dir_name = os.path.basename(root_dir)

        with open(output_file, 'w', encoding='utf-8') as outfile:
            for root, _, files in os.walk(root_dir):
                for file in files:
                    file_ext = os.path.splitext(file)[1].lower()
                    if file_ext in code_file_extensions:
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as infile:
                                # Make file path relative to root_dir
                                relative_path = os.path.relpath(file_path, start=root_dir)
                                outfile.write(f"--- {relative_path} ---\n")
                                outfile.write(infile.read())
                                outfile.write("\n\n")
                        except Exception as e:
                            outfile.write(f"Error reading {file_path}: {e}\n\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = CodebaseConsolidatorApp(root)
    root.mainloop()
