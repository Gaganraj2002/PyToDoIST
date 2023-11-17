import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime, timedelta
import pickle


class PyToDoIST:
    def __init__(self, root):
        self.root = root
        self.root.title("PyToDoIST")
        self.root.geometry("680x480")

        self.priority_var = tk.StringVar(root)
        self.priority_var.set("Low")

        self.priority_icons = {"Low": " 🟢 ", "Medium": " 🟠 ", "High": " 🔴 "}

        self.create_widgets()

    def create_widgets(self):
        self.task_label = tk.Label(self.root, text="Task:")
        self.task_label.place(relx=0.05, rely=0.02)
        self.entry = tk.Entry(self.root, width=40)
        self.entry.place(relx=0.05, rely=0.1, relwidth=0.9)
        self.entry.bind("<Return>", lambda event: self.add_task())

        self.due_date_label = tk.Label(self.root, text="Due Date (YYYY-MM-DD):")
        self.due_date_label.place(relx=0.05, rely=0.2)
        self.due_date_entry = tk.Entry(self.root, width=20)
        self.due_date_entry.place(relx=0.05, rely=0.28, relwidth=0.6)

        self.today_button = tk.Button(
            self.root, text="Set Today's Date", command=self.set_today_date
        )
        self.today_button.place(relx=0.7, rely=0.28, relwidth=0.25)

        self.priority_label = tk.Label(self.root, text="Priority:")
        self.priority_label.place(relx=0.05, rely=0.38)
        self.priority_dropdown = tk.OptionMenu(
            self.root, self.priority_var, "Low", "Medium", "High"
        )
        self.priority_dropdown.place(relx=0.05, rely=0.46, relwidth=0.6)

        self.add_button = tk.Button(self.root, text="Add Task", command=self.add_task)
        self.add_button.place(relx=0.7, rely=0.46, relwidth=0.25)

        self.edit_button = tk.Button(
            self.root, text="Edit Task", command=self.edit_task
        )
        self.edit_button.place(relx=0.05, rely=0.56, relwidth=0.3)

        self.delete_button = tk.Button(
            self.root, text="Delete Task", command=self.delete_task
        )
        self.delete_button.place(relx=0.4, rely=0.56, relwidth=0.3)

        self.toggle_done_button = tk.Button(
            self.root, text="Toggle Mark as Done", command=self.toggle_mark_as_done
        )
        self.toggle_done_button.place(relx=0.75, rely=0.56, relwidth=0.2)

        self.listbox = tk.Listbox(self.root, selectmode=tk.SINGLE, width=40, height=10)
        self.listbox.place(relx=0.05, rely=0.66, relwidth=0.9)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        self.load_tasks()

    def add_task(self):
        task = self.entry.get().strip()
        if task:
            due_date = self.due_date_entry.get().strip()
            priority = self.priority_var.get()

            if not due_date:
                due_date = datetime.now().strftime("%Y-%m-%d")

            try:
                due_date = datetime.strptime(due_date, "%Y-%m-%d")
                today = datetime.strptime(
                    datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d"
                )
                if today > due_date:
                    messagebox.showwarning(
                        "Warning", "Due date should be in the future."
                    )
                    return
            except ValueError:
                messagebox.showwarning(
                    "Warning", "Invalid date format. Use YYYY-MM-DD."
                )
                return

            priority_icon = self.priority_icons.get(priority, "")
            task_text = f"⬜ {task} (Due: {due_date.strftime('%Y-%m-%d')}, Priority: {priority}){priority_icon}"

            self.listbox.insert(tk.END, task_text)
            self.entry.delete(0, tk.END)
            self.due_date_entry.delete(0, tk.END)
            self.priority_var.set("Low")
            self.save_tasks()
            self.set_overdue_reminders()
        else:
            messagebox.showwarning("Warning", "Please enter a task.")

    def edit_task(self):
        try:
            selected_task = self.listbox.curselection()
            task = self.listbox.get(selected_task)
            edited_task = simpledialog.askstring(
                "Edit Task", "Edit Task:", initialvalue=task
            )

            if edited_task is not None:
                self.listbox.delete(selected_task)
                self.listbox.insert(tk.END, edited_task)
                self.save_tasks()
        except:
            messagebox.showwarning("Warning", "Please select a task to edit.")

    def delete_task(self):
        try:
            selected_task = self.listbox.curselection()
            self.listbox.delete(selected_task)
            self.save_tasks()
        except:
            messagebox.showwarning("Warning", "Please select a task to delete.")

    def toggle_mark_as_done(self):
        try:
            selected_task = self.listbox.curselection()
            task = self.listbox.get(selected_task)
            if "⬜" in task:
                self.listbox.delete(selected_task)
                self.listbox.insert(tk.END, task.replace("⬜", "✅"))
                self.save_tasks()
            elif "✅" in task:
                self.listbox.delete(selected_task)
                self.listbox.insert(tk.END, task.replace("✅", "⬜"))
                self.save_tasks()
        except:
            messagebox.showwarning("Warning", "Please select a task to mark as done.")

    def set_today_date(self):
        today_date = datetime.now().strftime("%Y-%m-%d")
        self.due_date_entry.delete(0, tk.END)
        self.due_date_entry.insert(0, today_date)

    def set_overdue_reminders(self):
        today = datetime.strptime(datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d")
        tasks = self.listbox.get(0, tk.END)
        for task in tasks:
            if "Due:" in task:
                due_date_str = task.split("Due:")[1].split(",")[0].strip()
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
                if today > due_date:
                    messagebox.showwarning(
                        "Overdue Task", f"The following task is overdue:\n\n{task}"
                    )

    def save_tasks(self):
        tasks = self.listbox.get(0, tk.END)
        with open("tasks.pkl", "wb") as file:
            pickle.dump(tasks, file)

    def load_tasks(self):
        try:
            with open("tasks.pkl", "rb") as file:
                tasks = pickle.load(file)
                for task in tasks:
                    self.listbox.insert(tk.END, task)
        except FileNotFoundError:
            pass

    def on_select(self, event):
        selected_task = self.listbox.curselection()
        if selected_task:
            task = self.listbox.get(selected_task)
            if "⬜" in task:
                self.toggle_done_button.config(text="Mark as Done")
            elif "✅" in task:
                self.toggle_done_button.config(text="Unmark")


def main():
    root = tk.Tk()
    app = PyToDoIST(root)
    root.mainloop()


if __name__ == "__main__":
    main()
