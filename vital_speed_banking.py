import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox

import os
import os.path

import zipfile

class FileAddingTreeview(ttk.Frame):
	
	def __init__(self, parent, types, *args, **kwargs):
		super().__init__(parent, *args, **kwargs)

		label_text = types[0][0]
		for i in types[1:]:
			label_text += " & " + i[0]
		self.label_text = label_text+": "
		self.label = ttk.Label(self, text=label_text)
		self.tree = ttk.Treeview(self,columns=("#1","#2"))
		self.add_button = ttk.Button(self, text="Add", command=self.add_files)
		self.remove_button = ttk.Button(self, text="Remove", command=self.remove_items)
		self.types = types

		self.tree["show"] = "headings"
		self.tree.column("#1",anchor=tk.W, width=100)
		self.tree.heading("#1",text="Name")
		self.tree.column("#2",anchor=tk.W, width=200)
		self.tree.heading("#2",text="Path")

		self.current_var = tk.StringVar()
		self.current_entry = ttk.Entry(self, textvariable=self.current_var)
		self.current_var.set("c://parent_folder")

		self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
		self.tree.configure(yscrollcommand = self.scrollbar.set)
		self.tree.bind("<<TreeviewSelect>>",self._handle_selection)
		self.tree.bind("<Control-a>",self._select_all)

	def grid(self, *a, **k):
		super().grid(*a,**k)

		tk.Grid.columnconfigure(self,index=0,weight=3)
		tk.Grid.columnconfigure(self,index=1,weight=1)
		tk.Grid.columnconfigure(self,index=2,weight=1)

		tk.Grid.rowconfigure(self,index=0,weight=0)
		tk.Grid.rowconfigure(self,index=1,weight=1)
		tk.Grid.rowconfigure(self,index=2,weight=0)
		tk.Grid.rowconfigure(self,index=3,weight=0)

		self.label.grid(row=0, column=0, columnspan=2, sticky=tk.W)
		self.tree.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW)
		self.add_button.grid(row=2, column=0, sticky=tk.NSEW)
		self.remove_button.grid(row=2, column=1, sticky=tk.NSEW)
		self.scrollbar.grid(row=0,column=2,rowspan=3,sticky=tk.NSEW)
		self.current_entry.grid(row=3,column=0,columnspan=2,sticky=tk.NSEW)

	def update_label(self, *a):
		self.label.config(text=self.label_text+"("+str(len(self.tree.get_children()))+")")

	def add_files(self):
		items = fd.askopenfilenames(filetypes=self.types)
		self.add_items(*self._format_file_names(items))
		self.update_label()

	def _format_file_names(self, items):
		names = []
		paths = []
		for item in items:
			path, name = os.path.split(item)
			names.append(name)
			paths.append(path)
		return [[names[i], paths[i]] for i in range(len(items))]

	def _handle_selection(self, *a):
		if len(self.tree.get_children()) > 0:
			item = self.tree.selection()[0]
			text = self.tree.item(item)["values"][1]
			self.current_var.set(text)

	def _select_all(self, *a):
		print("bruh")
		self.tree.selection_set(self.tree.get_children())

	def add_items(self, *items):
		# items = [[name,path]]
		for item in items:
			self.tree.insert("",tk.END,values=(item[0],item[1]))
			self.update_label()

	def remove_items(self):
		selection = self.tree.selection()
		self.tree.delete(*selection)
		self.update_label()

	def delete_all(self):
		self.tree.delete(*self.tree.get_children())
		self.update_label()

	def get_all_paths(self):
		# Get children items
		items = self.tree.get_children()
		# Extract the values
		values = [self.tree.item(item)["values"] for item in items]
		# Join the basepath and name and then normalize the paths
		paths = []
		for value in values:
			new_path = os.path.join(*value[::-1])
			paths.append(new_path)

		return paths

class SpeedBank(ttk.Frame):
	"""docstring for SpeedBank"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.tree_frame = ttk.Frame(self)

		self.preset_tree = FileAddingTreeview(self.tree_frame,[("Presets","*.vital")])
		self.wavetable_tree = FileAddingTreeview(self.tree_frame,[("Wavetables","*.vitaltable")])
		self.lfo_tree = FileAddingTreeview(self.tree_frame,[("Lfos","*.vitallfo")])
		self.sample_tree = FileAddingTreeview(self.tree_frame,[("Samples","*.wav .flac .mp3 .aiff .ogg")])

		self.actions_frame = ttk.Frame(self)

		self.auto_add_frame = ttk.Frame(self.actions_frame)
		self.auto_add_check_frame = ttk.Frame(self.auto_add_frame)
		self.auto_add_button = ttk.Button(self.auto_add_frame, text="Auto Add", command=self.auto_add)
		self.remove_all_button = ttk.Button(self.auto_add_frame, text="Remove All", command=self.remove_all)

		self.auto_add_presets = tk.BooleanVar()
		self.auto_add_wavetables = tk.BooleanVar()
		self.auto_add_lfos = tk.BooleanVar()
		self.auto_add_samples = tk.BooleanVar()
		self.bank_name = tk.StringVar()

		self.auto_add_presets_check = ttk.Checkbutton(self.auto_add_check_frame, variable=self.auto_add_presets)
		self.auto_add_wavetables_check = ttk.Checkbutton(self.auto_add_check_frame, variable=self.auto_add_wavetables)
		self.auto_add_lfos_check = ttk.Checkbutton(self.auto_add_check_frame, variable=self.auto_add_lfos)
		self.auto_add_samples_check = ttk.Checkbutton(self.auto_add_check_frame, variable=self.auto_add_samples)

		self.auto_add_presets.set(True)
		self.auto_add_wavetables.set(True)
		self.auto_add_lfos.set(True)
		self.auto_add_samples.set(True)

		self.export_frame = ttk.Frame(self)
		self.bank_name_entry = ttk.Entry(self.export_frame, textvariable=self.bank_name, width=15)
		self.export_button = ttk.Button(self.export_frame, text="EXPORT", command=self.export)

	def grid(self,*a,**k):
		# Configure weighting
		tk.Grid.columnconfigure(self,index=0,weight=1)
		tk.Grid.columnconfigure(self,index=1,weight=2)

		self.rowconfigure(index=0,weight=1)

		self.tree_frame.columnconfigure(index=0,weight=1)
		self.tree_frame.columnconfigure(index=1,weight=3)
		self.tree_frame.columnconfigure(index=2,weight=3)
		self.tree_frame.columnconfigure(index=3,weight=3)

		self.tree_frame.rowconfigure(index=0,weight=1)

		tk.Grid.columnconfigure(self.actions_frame, index=0, weight=1)
		tk.Grid.columnconfigure(self.auto_add_frame, index=0, weight=1)
		tk.Grid.columnconfigure(self.auto_add_check_frame, index=0, weight=1)
		tk.Grid.columnconfigure(self.export_frame, index=0, weight=1)

		super().grid(*a,**k)

		self.preset_tree.grid(row=0,column=0, sticky=tk.NSEW)
		self.wavetable_tree.grid(row=0,column=1, sticky=tk.NSEW)
		self.lfo_tree.grid(row=0,column=2, sticky=tk.NSEW)
		self.sample_tree.grid(row=0,column=3, sticky=tk.NSEW)

		self.actions_frame.grid(row=0,column=0,sticky=tk.NSEW,padx=10)
		ttk.Label(self.actions_frame, text="Actions: ").grid(row=0,column=0)
		ttk.Separator(self.actions_frame, orient=tk.HORIZONTAL).grid(row=1,column=0,sticky=tk.EW,pady=10)

		self.auto_add_frame.grid(row=2,column=0,sticky=tk.NSEW)
		self.auto_add_check_frame.grid(row=3,column=0,sticky=tk.N)
		self.auto_add_button.grid(row=1,column=0,sticky=tk.NSEW)
		self.remove_all_button.grid(row=0,column=0,sticky=tk.NSEW)

		self.auto_add_presets_check.grid(row=0,column=1,sticky=tk.NSEW)
		self.auto_add_wavetables_check.grid(row=1,column=1,sticky=tk.NSEW)
		self.auto_add_lfos_check.grid(row=2,column=1,sticky=tk.NSEW)
		self.auto_add_samples_check.grid(row=3,column=1,sticky=tk.NSEW)

		ttk.Label(self.auto_add_check_frame, text="Presets: ").grid(row=0,column=0,sticky=tk.W)
		ttk.Label(self.auto_add_check_frame, text="Wavetables: ").grid(row=1,column=0,sticky=tk.W)
		ttk.Label(self.auto_add_check_frame, text="Lfos: ").grid(row=2,column=0,sticky=tk.W)
		ttk.Label(self.auto_add_check_frame, text="Samples: ").grid(row=3,column=0,sticky=tk.W)

		ttk.Separator(self.export_frame, orient=tk.HORIZONTAL).grid(row=0,column=0,sticky=tk.EW,pady=10,padx=10)
		ttk.Label(self.export_frame, text="Name: ").grid(row=0,column=0)

		self.bank_name_entry.grid(row=1,column=0, sticky=tk.NSEW)
		self.export_button.grid(row=2,column=0, sticky=tk.NSEW)

		self.export_frame.grid(row=1,column=0,sticky=tk.NSEW, padx=10)

		self.tree_frame.grid(row=0,column=1, sticky=tk.NSEW, rowspan=2)

	def remove_all(self, *a):
		deleting = {
			"presets":self.auto_add_presets.get(),
			"wavetables":self.auto_add_wavetables.get(),
			"lfos":self.auto_add_lfos.get(),
			"samples":self.auto_add_samples.get()
			}
		question = "Do you want to delete all: "
		for key, value in deleting.items():
			if value:
				question += key + " "

		delete_all = messagebox.askquestion("Confirm Deletion",question)
		if delete_all != "yes":
			return

		if deleting["presets"]:
			self.preset_tree.delete_all()
		if deleting["wavetables"]:
			self.wavetable_tree.delete_all()
		if deleting["lfos"]:
			self.lfo_tree.delete_all()
		if deleting["samples"]:
			self.sample_tree.delete_all()

	def auto_add(self):
		directory = fd.askdirectory(title="Auto Add Files from Folder")
		if directory == "":
			return

		def get_matching(directory, acceptable=None):
			acceptable = [".txt"] if acceptable is None else acceptable
			found = {"presets":[],"wavetables":[],"lfos":[],"samples":[]}
			dir_list = os.listdir(directory)

			for i in dir_list:
				full_path = os.path.join(directory, i)

				if os.path.isfile(full_path):
					ext = os.path.splitext(i)[-1].lower()

					if ext in acceptable:
						if ext == ".vital": 
							found["presets"].append(full_path)
						elif ext == ".vitaltable": 
							found["wavetables"].append(full_path)
						elif ext == ".vitallfo": 
							found["lfos"].append(full_path)
						elif ext in [".wav",".flac",".mp3",".aiff",".ogg"]: 
							found["samples"].append(full_path)

				if os.path.isdir(full_path):
					new_found = get_matching(os.path.join(directory,i),acceptable)
					found["presets"] += new_found["presets"]
					found["wavetables"] += new_found["wavetables"]
					found["lfos"] += new_found["lfos"]
					found["samples"] += new_found["samples"]

			return found

		looking_for = []
		if self.auto_add_presets.get():
			looking_for.append(".vital")
		if self.auto_add_wavetables.get():
			looking_for.append(".vitaltable")
		if self.auto_add_lfos.get():
			looking_for.append(".vitallfo")
		if self.auto_add_samples.get():
			looking_for += [".wav",".flac",".mp3",".aiff",".ogg"]

		matching = get_matching(directory,looking_for)

		presets = self.preset_tree._format_file_names(matching["presets"])
		wavetables = self.preset_tree._format_file_names(matching["wavetables"])
		lfos = self.preset_tree._format_file_names(matching["lfos"])
		samples = self.preset_tree._format_file_names(matching["samples"])

		self.preset_tree.add_items(*presets)
		self.wavetable_tree.add_items(*wavetables)
		self.lfo_tree.add_items(*lfos)
		self.sample_tree.add_items(*samples)

	def export(self, *a):
		bank_name = self.bank_name.get().strip()
		name = bank_name+".vitalbank"

		location = fd.askdirectory(title="Select directory to place "+name+" in")
		if location == "":
			return
			
		bank_path = os.path.join(location, name)

		if os.path.exists(bank_path):
			override = messagebox.askquestion("Confirm Override","Do you want to override "+name+" ?")
			if override != "yes":
				return
			os.remove(bank_path)

		self.export_button.config(text="Exporting...")

		presets = self.preset_tree.get_all_paths()
		wavetables = self.wavetable_tree.get_all_paths()
		lfos = self.lfo_tree.get_all_paths()
		samples = self.sample_tree.get_all_paths()

		with zipfile.ZipFile(bank_path, mode="x") as archive:
			for preset in presets:
				preset_name = os.path.split(preset)[-1]
				archive.write(preset,os.path.join(os.path.join(bank_name,"Presets"),preset_name))
			for wavetable in wavetables:
				wavetable_name = os.path.split(wavetable)[-1]
				archive.write(wavetable,os.path.join(os.path.join(bank_name,"Wavetables"),wavetable_name))
			for lfo in lfos:
				lfo_name = os.path.split(lfo)[-1]
				archive.write(lfo,os.path.join(os.path.join(bank_name,"LFOs"),lfo_name))
			for sample in samples:
				sample_name = os.path.split(sample)[-1]
				archive.write(sample,os.path.join(os.path.join(bank_name,"Samples"),sample_name))

		messagebox.showinfo(title="Export Complete",message="Export of "+name+" completed")
		self.export_button.config(text="EXPORT")

if __name__ == "__main__":
	root = tk.Tk()
	root.title("Vital Speed Banking")

	tk.Grid.columnconfigure(root,index=0,weight=1)
	tk.Grid.rowconfigure(root,index=0,weight=1)
	
	app = SpeedBank()
	app.grid(sticky=tk.NSEW,padx=10,pady=10)

	root.mainloop()