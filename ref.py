import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import os

class ReferenceManager:
    def __init__(self, root):
        self.root = root
        self.root.title("reference manager")
        self.root.geometry("600x400")

        self.input_frame = ttk.LabelFrame(self.root, text="Добавить референс")
        self.input_frame.pack(pady=10, padx=10, fill="both", expand="yes")

        self.nickname_label = ttk.Label(self.input_frame, text="Никнейм покупателя:")
        self.nickname_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.nickname_entry = ttk.Entry(self.input_frame)
        self.nickname_entry.grid(row=0, column=1, padx=5, pady=5)

        self.deadline_label = ttk.Label(self.input_frame, text="До какой даты референс:")
        self.deadline_label.grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.deadline_entry = ttk.Entry(self.input_frame)
        self.deadline_entry.grid(row=1, column=1, padx=5, pady=5)

        self.amount_label = ttk.Label(self.input_frame, text="Стоимость референса: ")
        self.amount_label.grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.amount_entry = ttk.Entry(self.input_frame)
        self.amount_entry.grid(row=2, column=1, padx=5, pady=5)

        self.info_label = ttk.Label(self.input_frame, text="Доп. информация:")
        self.info_label.grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.info_entry = ttk.Entry(self.input_frame)
        self.info_entry.grid(row=3, column=1, padx=5, pady=5)

        self.contact_label = ttk.Label(self.input_frame, text="Контактная информация:")
        self.contact_label.grid(row=4, column=0, padx=5, pady=5, sticky='w')
        self.contact_entry = ttk.Entry(self.input_frame)
        self.contact_entry.grid(row=4, column=1, padx=5, pady=5)

        self.add_button = ttk.Button(self.root, text="Добавить", command=self.add_or_update_reference)
        self.add_button.pack(pady=10)

        self.save_button = ttk.Button(self.root, text="Сохранить CSV", command=self.save_references)
        self.save_button.place(x=480, y=10)

        self.load_button = ttk.Button(self.root, text="Загрузить CSV", command=self.load_references)
        self.load_button.place(x=480, y=40)

        self.references = []
        self.references_frame = ttk.LabelFrame(self.root, text="Список референсов")
        self.references_frame.pack(pady=10, padx=10, fill="both", expand="yes")

        self.reference_list = tk.Listbox(self.references_frame, width=80)
        self.reference_list.pack(side=tk.LEFT, padx=5, pady=5)

        self.scrollbar = ttk.Scrollbar(self.references_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.reference_list.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.reference_list.yview)

        self.reference_list.bind("<Button-3>", self.show_context_menu)
        self.root.bind("<Button-1>", self.clear_selection)

        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Просмотреть детали", command=self.view_details)
        self.context_menu.add_command(label="Удалить", command=self.delete_reference)
        self.context_menu.add_command(label="Отметить как завершён", command=self.mark_completed)
        self.context_menu.add_command(label="Изменить", command=self.edit_reference)

        self.editing_index = None  

    def add_or_update_reference(self):
        nickname = self.nickname_entry.get()
        deadline = self.deadline_entry.get()
        amount = self.amount_entry.get()
        info = self.info_entry.get()
        contact = self.contact_entry.get()

        if nickname and deadline and amount:
            reference = {
                "nickname": nickname,
                "deadline": deadline,
                "amount": amount,
                "info": info,
                "contact": contact,
                "completed": False  
            }

            if self.editing_index is not None:  
                self.references[self.editing_index] = reference
                self.reference_list.delete(self.editing_index)
                self.reference_list.insert(self.editing_index, nickname)
                self.editing_index = None  
                self.add_button.config(text="Добавить")  
            else: 
                self.references.append(reference)
                self.reference_list.insert(tk.END, nickname)  

            self.clear_entries()
        else:
            messagebox.showwarning("Ошибка", "Пожалуйста, заполните все обязательные поля.")

    def clear_entries(self):
        self.nickname_entry.delete(0, tk.END)
        self.deadline_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.info_entry.delete(0, tk.END)
        self.contact_entry.delete(0, tk.END)

    def save_references(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                   filetypes=[("CSV files", "*.csv"),
                                                              ("All files", "*.*")])
        if file_path:
            df = pd.DataFrame(self.references)
            df.to_csv(file_path, index=False)

    def load_references(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"),
                                                           ("All files", "*.*")])
        if file_path and os.path.exists(file_path):
            df = pd.read_csv(file_path)
            self.references.clear()  
            self.reference_list.delete(0, tk.END) 
            for _, row in df.iterrows():
                reference = {
                    "nickname": row["nickname"],
                    "deadline": row["deadline"],
                    "amount": row["amount"],
                    "info": row["info"],
                    "contact": row["contact"],
                    "completed": row.get("completed", False)  
                }
                self.references.append(reference)
                self.reference_list.insert(tk.END, reference["nickname"])  

            self.update_reference_display()  

    def show_context_menu(self, event):
        self.reference_list.selection_clear(0, tk.END)  
        self.reference_list.selection_set(self.reference_list.nearest(event.y))  
        self.context_menu.post(event.x_root, event.y_root)

    def clear_selection(self, event):
        self.reference_list.selection_clear(0, tk.END)  

    def delete_reference(self):
        selected_index = self.reference_list.curselection()
        if selected_index:
            del self.references[selected_index[0]]  
            self.reference_list.delete(selected_index)  

    def mark_completed(self):
        selected_index = self.reference_list.curselection()
        if selected_index:
            ref = self.references[selected_index[0]]
            ref["completed"] = not ref["completed"]  
            self.update_reference_display(selected_index[0], ref)  

    def update_reference_display(self, index=None, reference=None):
        if index is None and reference is None:
            for i, ref in enumerate(self.references):
                self.update_reference_display(i, ref)
        else:
            display_text = reference['nickname']
            if reference["completed"]:
                display_text += " (завершён)"
                self.reference_list.itemconfig(index, {'bg': 'lightgray', 'fg': 'gray'}) 
            else:
                self.reference_list.itemconfig(index, {'bg': 'white', 'fg': 'black'})  

            self.reference_list.delete(index)  
            self.reference_list.insert(index, display_text)  

    def view_details(self):
        selected_index = self.reference_list.curselection()
        if selected_index:
            ref = self.references[selected_index[0]]
            details = (f"Никнейм: {ref['nickname']}\n"
                       f"До даты: {ref['deadline']}\n"
                       f"Количество выплат: {ref['amount']}\n"
                       f"Доп. информация: {ref['info']}\n"
                       f"Контакт: {ref['contact']}")
            messagebox.showinfo("Детали референса", details)

    def edit_reference(self):
        selected_index = self.reference_list.curselection()
        if selected_index:
            ref = self.references[selected_index[0]]
            self.nickname_entry.delete(0, tk.END)
            self.nickname_entry.insert(0, ref["nickname"])
            self.deadline_entry.delete(0, tk.END)
            self.deadline_entry.insert(0, ref["deadline"])
            self.amount_entry.delete(0, tk.END)
            self.amount_entry.insert(0, ref["amount"])
            self.info_entry.delete(0, tk.END)
            self.info_entry.insert(0, ref["info"])
            self.contact_entry.delete(0, tk.END)
            self.contact_entry.insert(0, ref["contact"])

            self.editing_index = selected_index[0]  
            self.add_button.config(text="Изменить")  

if __name__ == "__main__":
    root = tk.Tk()
    app = ReferenceManager(root)
    root.mainloop()
