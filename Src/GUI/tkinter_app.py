import tkinter as tk
from tkinter import filedialog, ttk, font, simpledialog
import os
import Src.Main
import sys

class TextRedirector:
	def __init__(self, widget):
		self.widget = widget

	def write(self, text):
		self.widget.configure(state='normal')
		self.widget.insert(tk.END, text)
		self.widget.configure(state='disabled')
		self.widget.see(tk.END)

	def flush(self):
		pass

class MyApp:
	def __init__(self, root):
		self.root = root
		self.root.title('My Program GUI')

		# Set custom style
		self.style = ttk.Style(self.root)
		self.style.theme_create('mytheme', parent='alt', settings={
			'TFrame': {'configure': {'background': '#ffffff'}},
			'TLabelFrame': {'configure': {'background': '#ffffff', 'foreground': 'FAD7C0', 'relief': 'flat'}},
			'TButton': {'configure': {'background': '#FAD7C0', 'foreground': '#000000', 'relief': 'raised'},
			            'map': {'background': [('active', '#FAD7C0'), ('pressed', '#ffffff')],
			                    'foreground': [('active', '#000000'), ('pressed', '#000000')]}},
			'TEntry': {'configure': {'fieldbackground': '#FAD7C0', 'foreground': '#ffffff', 'relief': 'flat'}},
			'TListbox': {'configure': {'background': '#FAD7C0', 'foreground': '#000000', 'relief': 'flat', 'selectbackground': '#ffffff'}}
		})
		self.style.theme_use('mytheme')

		# Set custom font
		self.custom_font = font.Font(family='Arial', size=12)

		# Frames
		self.setup_file_frames()
		self.setup_run_method_frame()
		self.setup_logs_frame()

		self.preload_files()

		# Redirect standard output and standard error to the text widget
		sys.stdout = TextRedirector(self.logs)
		sys.stderr = TextRedirector(self.logs)

	def setup_file_frames(self):
		self.file_frame = ttk.Frame(self.root)
		self.file_frame.pack(fill='both', expand=True, padx=10, pady=5)

		# Input files
		self.input_frame = ttk.LabelFrame(self.file_frame, text='Input Files')
		self.input_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
		self.input_files_listbox = tk.Listbox(self.input_frame, bg='#FAD7C0', fg='#000000', selectbackground='#ffffff', font=self.custom_font)
		self.input_files_listbox.pack(fill='both', expand=True, padx=5, pady=5)

		# Output files
		self.output_frame = ttk.LabelFrame(self.file_frame, text='Output Files')
		self.output_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)
		self.output_files_listbox = tk.Listbox(self.output_frame, bg='#FAD7C0', fg='#000000', selectbackground='#ffffff', font=self.custom_font)
		self.output_files_listbox.pack(fill='both', expand=True, padx=5, pady=5)


	def setup_run_method_frame(self):
		self.method_frame = ttk.Frame(self.root)
		self.method_frame.pack(fill='x', padx=10, pady=5)
		ttk.Button(self.method_frame, text='Run Method', command=self.run_method, style='TButton').pack(side='left')

	def setup_logs_frame(self):
		self.logs_frame = ttk.LabelFrame(self.root, text='Logs')  # Removed the style argument
		self.logs_frame.pack(fill='both', expand=True, padx=10, pady=5)
		self.logs = tk.Text(self.logs_frame, state='disabled', height=10, bg='#FAD7C0', fg='#000000', font=self.custom_font)
		self.logs.pack(fill='both', expand=True, padx=5, pady=5)

	def run_method(self):
		method_name = "main_update_shopify_order_report"  # Hardcoded method name
		try:
			method = getattr(Src.Main, method_name)
			method()
			print(f'Executing {method_name}... Success\n')
		except AttributeError:
			print(f'Method {method_name} not found\n')
		except Exception as e:
			print(f'Executing {method_name}... Failed: {e}\n')

	def list_files(self, folder_path, listbox):
		listbox.delete(0, tk.END)
		if os.path.exists(folder_path):
			for file in os.listdir(folder_path):
				listbox.insert(tk.END, file)

	def select_input_folder(self):
		folder_path = filedialog.askdirectory()
		self.list_files(folder_path, self.input_files_listbox)

	def select_output_folder(self):
		folder_path = filedialog.askdirectory()
		self.list_files(folder_path, self.output_files_listbox)

	def preload_files(self):
		input_folder = r'C:\Users\Zander\IdeaProjects\Automation-Gel\gitignore\custom'
		output_folder = r'C:\Users\Zander\IdeaProjects\Automation-Gel\gitignore\output'
		self.list_files(input_folder, self.input_files_listbox)
		self.list_files(output_folder, self.output_files_listbox)

class CustomDialog(simpledialog.Dialog):
	def body(self, master):
		self.label = tk.Label(master, text="Waiting for input:")
		self.label.pack()
		self.entry = tk.Entry(master)
		self.entry.pack()
		return self.entry

	def apply(self):
		self.result = self.entry.get()

if __name__ == '__main__':
	root = tk.Tk()
	app = MyApp(root)
	root.mainloop()

