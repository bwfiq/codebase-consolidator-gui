import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

class CodebaseConsolidatorApp:
    def __init__(self, root, initial_dir=None):
        self.root = root
        root.title("Codebase Consolidator")

        # Create and place widgets
        self.create_widgets()

        # If an initial directory was provided, set it
        if initial_dir:
            self.root_dir_entry.insert(0, initial_dir)

    def create_widgets(self):
        # Root Directory
        tk.Label(self.root, text="Root Directory:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.root_dir_entry = tk.Entry(self.root, width=50)
        self.root_dir_entry.grid(row=0, column=1, padx=10, pady=5, columnspan=2)
        tk.Button(self.root, text="Browse...", command=self.browse_root_dir).grid(row=0, column=3, padx=10, pady=5)

        # Action Buttons
        button_frame = tk.Frame(self.root)
        button_frame.grid(row=1, column=1, columnspan=2, pady=10)

        tk.Button(button_frame, text="Consolidate", command=self.consolidate_codebase).pack(side="left", padx=10)
        tk.Button(button_frame, text="Save", command=self.save_to_file).pack(side="left", padx=10)
        tk.Button(button_frame, text="Copy", command=self.copy_to_clipboard).pack(side="left", padx=10)

        # Output Text Widget
        self.output_text = tk.Text(self.root, wrap='word', height=20, width=80)
        self.output_text.grid(row=0, column=4, rowspan=3, padx=10, pady=5, sticky='nsew')
        
        # Configure grid weights
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_columnconfigure(4, weight=2)


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

        try:
            self.generate_codebase_text(root_dir)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        # Removed success message

    def generate_codebase_text(self, root_dir):
        # Define file extensions to include
        code_file_extensions = {'.py', '.js', '.java', '.cpp', '.c', '.h', '.html', '.css', '.json', '.xml', '.rb', '.php', '.go', '.bat', '.sh', '.reg'}
        
        # Get the root directory name to remove from file paths
        root_dir_name = os.path.basename(root_dir)

        output_lines = []
        for root, _, files in os.walk(root_dir):
            for file in files:
                file_ext = os.path.splitext(file)[1].lower()
                if file_ext in code_file_extensions:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            # Make file path relative to root_dir
                            relative_path = os.path.relpath(file_path, start=root_dir)
                            output_lines.append(f"--- {relative_path} ---\n")
                            output_lines.append(infile.read())
                            output_lines.append("\n\n")
                    except Exception as e:
                        output_lines.append(f"Error reading {file_path}: {e}\n\n")

        # Update Text widget with generated content
        self.output_text.delete(1.0, tk.END)  # Clear existing content
        self.output_text.insert(tk.END, ''.join(output_lines))

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
                # Success message can be added here if needed
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while saving the file: {e}")

    def copy_to_clipboard(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.output_text.get(1.0, tk.END))
        self.root.update()  # Important for clipboard to work on some systems
        # Removed success message

if __name__ == "__main__":
    initial_directory = None
    if len(sys.argv) > 1:
        initial_directory = sys.argv[1]
    else:
        print("No directory passed")
        sys.exit(1)
    
    # Check if the directory is valid
    if not os.path.isdir(initial_directory):
        print(f"Invalid directory: {initial_directory}")
        sys.exit(1)
    
    root = tk.Tk()
    app = CodebaseConsolidatorApp(root, initial_directory)
    root.mainloop()
