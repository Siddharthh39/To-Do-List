import tkinter as tk
from tkinter import messagebox

class TodoListApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Todo List")
        self.master.geometry("300x400")
        self.tasks = []

        self.task_entry = tk.Entry(master, font=("Helvetica", 12))
        self.task_entry.pack(pady=10, padx=20, fill=tk.X)

        add_button = tk.Button(master, text="Add Task", command=self.add_task)
        add_button.pack(pady=5, padx=20, fill=tk.X)

        self.task_listbox = tk.Listbox(master, font=("Helvetica", 12), selectmode=tk.SINGLE)
        self.task_listbox.pack(pady=5, padx=20, fill=tk.BOTH, expand=True)
        self.task_listbox.bind("<Double-1>", self.toggle_completed)

        remove_button = tk.Button(master, text="Remove Task", command=self.remove_task)
        remove_button.pack(pady=5, padx=20, fill=tk.X)

        self.update_task_list()

    def add_task(self):
        task = self.task_entry.get().strip()
        if task:
            self.tasks.append({"task": task, "completed": False})
            self.update_task_list()
            self.task_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Empty Task", "Please enter a task.")

    def remove_task(self):
        selected_index = self.task_listbox.curselection()
        if selected_index:
            task_index = selected_index[0]
            del self.tasks[task_index]
            self.update_task_list()
        else:
            messagebox.showwarning("No Task Selected", "Please select a task to remove.")

    def toggle_completed(self, event):
        selected_index = self.task_listbox.curselection()
        if selected_index:
            task_index = selected_index[0]
            self.tasks[task_index]["completed"] = not self.tasks[task_index]["completed"]
            self.update_task_list()

    def update_task_list(self):
        self.task_listbox.delete(0, tk.END)
        for task in self.tasks:
            task_text = task["task"]
            if task["completed"]:
                task_text = "✓ " + task_text
            self.task_listbox.insert(tk.END, task_text)

def main():
    root = tk.Tk()
    root.geometry("800x720")
    root.maxsize(720,700)
    root.minsize(320,540)
    app = TodoListApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
