import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QListWidget,
    QMessageBox,
    QComboBox,
    QDateEdit,
    QLabel,
    QTimeEdit,
    QGroupBox,
    QHBoxLayout,
    QFormLayout,
    QFrame
)
from PyQt6.QtCore import Qt, QDate, QTime, QTimer
from PyQt6.QtGui import QIcon
from plyer import notification

class TodoListApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Todo List")
        self.setGeometry(100, 100, 400, 600)
        self.tasks = []

        # Set the window to always stay on top
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        self.layout = QVBoxLayout()
        
        # Search bar
        self.search_entry = QLineEdit(self)
        self.search_entry.setPlaceholderText("Search tasks...")
        self.search_entry.textChanged.connect(self.update_task_list)
        self.layout.addWidget(self.search_entry)

        # Task input group with dropdown refinement
        task_group = QGroupBox("Add Task")
        task_layout = QVBoxLayout()

        # Add Task Header Dropdown
        self.task_details_frame = QFrame(self)
        self.task_details_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.task_details_layout = QFormLayout(self.task_details_frame)
        self.task_details_frame.hide()

        # Task type dropdown
        self.task_type_combo = QComboBox(self)
        self.task_type_combo.addItems(["Work", "Personal", "Shopping", "Other"])
        self.task_details_layout.addRow(QLabel("Task Type:"), self.task_type_combo)

        self.task_entry = QLineEdit(self)
        self.task_entry.setPlaceholderText("Enter a task...")
        self.task_details_layout.addRow(QLabel("Task Description:"), self.task_entry)

        # Priority Dropdown
        self.priority_combo = QComboBox(self)
        self.priority_combo.addItems(["Low", "Medium", "High"])
        self.task_details_layout.addRow(QLabel("Priority:"), self.priority_combo)

        # Due Date
        self.due_date_picker = QDateEdit(self)
        self.due_date_picker.setDate(QDate.currentDate())
        self.task_details_layout.addRow(QLabel("Due Date:"), self.due_date_picker)

        # Notification Time
        self.notification_time_picker = QTimeEdit(self)
        self.notification_time_picker.setTime(QTime.currentTime())
        self.task_details_layout.addRow(QLabel("Notification Time:"), self.notification_time_picker)

        # Add Task Button
        self.add_button = QPushButton("Add Task", self)
        self.add_button.setIcon(QIcon("icons/add.png"))  # Use an appropriate icon file
        self.add_button.clicked.connect(self.add_task)
        self.task_details_layout.addRow(self.add_button)

        task_group_layout = QVBoxLayout()
        self.toggle_details_button = QPushButton("▼ Add Task Details", self)
        self.toggle_details_button.clicked.connect(self.toggle_task_details)
        task_group_layout.addWidget(self.toggle_details_button)
        task_group_layout.addWidget(self.task_details_frame)

        task_group.setLayout(task_group_layout)
        self.layout.addWidget(task_group)

        # Task list and filter
        self.filter_combo = QComboBox(self)
        self.filter_combo.addItems(["All", "Work", "Personal", "Shopping", "Other"])
        self.filter_combo.currentIndexChanged.connect(self.update_task_list)
        self.layout.addWidget(QLabel("Filter by Category:"))
        self.layout.addWidget(self.filter_combo)

        self.task_listbox = QListWidget(self)
        self.task_listbox.itemDoubleClicked.connect(self.toggle_completed)
        self.layout.addWidget(self.task_listbox)

        self.remove_button = QPushButton("Remove Task", self)
        self.remove_button.setIcon(QIcon("icons/remove.png"))  # Use an appropriate icon file
        self.remove_button.clicked.connect(self.remove_task)
        self.layout.addWidget(self.remove_button)

        self.setLayout(self.layout)

        # Set up a timer to check for upcoming due dates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_due_dates)
        self.timer.start(60000)  # Check every minute

    def toggle_task_details(self):
        if self.task_details_frame.isHidden():
            self.task_details_frame.show()
            self.toggle_details_button.setText("▲ Hide Task Details")
        else:
            self.task_details_frame.hide()
            self.toggle_details_button.setText("▼ Add Task Details")

    def add_task(self):
        task = self.task_entry.text().strip()
        task_type = self.task_type_combo.currentText()
        priority = self.priority_combo.currentText()
        due_date = self.due_date_picker.date().toString(Qt.DateFormat.ISODate)
        notification_time = self.notification_time_picker.time().toString("HH:mm:ss")

        if task:
            self.tasks.append({"task": task, "completed": False, "priority": priority, "category": task_type, "due_date": due_date, "notification_time": notification_time})
            self.update_task_list()
            self.task_entry.clear()
        else:
            QMessageBox.warning(self, "Empty Task", "Please enter a task.")

    def remove_task(self):
        selected_items = self.task_listbox.selectedItems()
        if selected_items:
            for item in selected_items:
                task_index = self.task_listbox.row(item)
                del self.tasks[task_index]
            self.update_task_list()
        else:
            QMessageBox.warning(self, "No Task Selected", "Please select a task to remove.")

    def toggle_completed(self, item):
        task_index = self.task_listbox.row(item)
        self.tasks[task_index]["completed"] = not self.tasks[task_index]["completed"]
        self.update_task_list()

    def update_task_list(self):
        priority_order = {"Low": 1, "Medium": 2, "High": 3}
        self.tasks.sort(key=lambda x: priority_order[x["priority"]])

        selected_category = self.filter_combo.currentText()
        filtered_tasks = self.tasks if selected_category == "All" else [task for task in self.tasks if task["category"] == selected_category]

        search_query = self.search_entry.text().lower()
        filtered_tasks = [task for task in filtered_tasks if search_query in task["task"].lower()]

        self.task_listbox.clear()
        for task in filtered_tasks:
            task_text = f"{task['priority']} | {task['category']}: {task['task']} (Due: {task['due_date']}, Notify at: {task['notification_time']})"
            if task["completed"]:
                task_text = "✓ " + task_text
            
            if QDate.fromString(task['due_date'], Qt.DateFormat.ISODate) < QDate.currentDate() and not task["completed"]:
                task_text = f"[OVERDUE] {task_text}"

            self.task_listbox.addItem(task_text)

    def check_due_dates(self):
        current_time = QTime.currentTime()
        upcoming_tasks = [task for task in self.tasks if QDate.fromString(task['due_date'], Qt.DateFormat.ISODate) == QDate.currentDate() and QTime.fromString(task['notification_time'], Qt.TimeFormat.ISOFormat) == current_time and not task["completed"]]
        if upcoming_tasks:
            task_list = "\n".join([task['task'] for task in upcoming_tasks])
            QMessageBox.information(self, "Task Notification", f"You have tasks due now:\n{task_list}")

    def check_due_dates(self):
        current_time = QTime.currentTime().toString("HH:mm:ss")
        for task in self.tasks:
            task_due_date = QDate.fromString(task['due_date'], Qt.DateFormat.ISODate)
            task_notify_time = task['notification_time']
            
            if task_due_date == QDate.currentDate() and task_notify_time == current_time and not task["completed"]:
                notification.notify(
                    title="Task Notification",
                    message=f"Task Due: {task['task']}\nPriority: {task['priority']}",
                    app_name="Todo List",
                    timeout=10
                )

def main():
    app = QApplication(sys.argv)
    todo_app = TodoListApp()
    todo_app.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
