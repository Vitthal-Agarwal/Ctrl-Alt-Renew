import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCalendarWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QTimeEdit
)
from PyQt5.QtCore import QDate, Qt, QTimer, QTime
from PyQt5.QtGui import QColor, QFont
import pandas as pd

class SchedulerGUI(QWidget):
    def __init__(self, future_df):
        super().__init__()
        self.future_df = future_df
        self.current_week_start = self.future_df["Timestamp"].min().date()
        self.current_time = QTime.currentTime()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("DFT Computation Scheduler")
        self.setGeometry(100, 100, 1200, 800)
        
        main_layout = QVBoxLayout()
        
        # Top section - Automation Button
        top_layout = QHBoxLayout()
        self.automation_button = QPushButton("Starting Automation with Low Intensity")
        self.automation_button.setFixedHeight(40)
        self.automation_button.setMinimumWidth(400)
        self.automation_button.setFont(QFont('Arial', 10, QFont.Bold))
        self.automation_button.clicked.connect(self.toggle_automation)
        top_layout.addStretch()
        top_layout.addWidget(self.automation_button)
        top_layout.addStretch()
        main_layout.addLayout(top_layout)
        
        # Content section
        content_layout = QHBoxLayout()
        
        # Left panel - Calendar
        left_panel = QVBoxLayout()
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.selectionChanged.connect(self.show_schedule)
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: white;
                color: black;
            }
            QCalendarWidget QToolButton {
                color: black;
                background-color: transparent;
                border: none;
            }
            QCalendarWidget QMenu {
                width: 150px;
                left: 20px;
                color: black;
            }
            QCalendarWidget QSpinBox {
                width: 60px;
                font-size: 12px;
                color: black;
            }
            QCalendarWidget QTableView {
                alternate-background-color: #F0F0F0;
                gridline-color: #E0E0E0;
            }
            QCalendarWidget QTableView:selected {
                background-color: #4CAF50;
                color: white;
            }
        """)
        left_panel.addWidget(self.calendar)
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous Day")
        self.next_button = QPushButton("Next Day")
        self.prev_button.clicked.connect(self.previous_day)
        self.next_button.clicked.connect(self.next_day)
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.next_button)
        left_panel.addLayout(nav_layout)
        
        # Time control
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Current Time:"))
        self.time_edit = QTimeEdit(self.current_time)
        self.time_edit.setDisplayFormat("HH:mm")
        self.time_edit.timeChanged.connect(self.update_current_time)
        time_layout.addWidget(self.time_edit)
        left_panel.addLayout(time_layout)
        
        content_layout.addLayout(left_panel)
        
        # Right panel - Schedule Table
        right_panel = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: #E0E0E0;
            }
            QHeaderView::section {
                background-color: #F0F0F0;
                padding: 6px;
                border: none;
                border-bottom: 1px solid #E0E0E0;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)
        right_panel.addWidget(self.table)
        content_layout.addLayout(right_panel)
        
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)
        
        self.setup_calendar()
        self.show_schedule()
        
        # Timer to update button state
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_button_state)
        self.timer.start(1000)

    def setup_calendar(self):
        min_date = self.future_df["Timestamp"].min().date()
        max_date = self.future_df["Timestamp"].max().date()
        self.calendar.setMinimumDate(QDate(min_date))
        self.calendar.setMaximumDate(QDate(max_date))
        self.calendar.setSelectedDate(QDate(self.current_week_start))

    def previous_day(self):
        current_date = self.calendar.selectedDate()
        new_date = current_date.addDays(-1)
        if new_date >= self.calendar.minimumDate():
            self.calendar.setSelectedDate(new_date)

    def next_day(self):
        current_date = self.calendar.selectedDate()
        new_date = current_date.addDays(1)
        if new_date <= self.calendar.maximumDate():
            self.calendar.setSelectedDate(new_date)

    def show_schedule(self):
        selected_date = self.calendar.selectedDate().toPyDate()
        day_df = self.future_df[self.future_df["Timestamp"].dt.date == selected_date]

        self.table.clear()
        self.table.setRowCount(len(day_df))
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["Start Time", "End Time", "CPU Usage Level", "Calc Intensity"]
        )

        for idx, row in day_df.reset_index().iterrows():
            start_time = row["Timestamp"].strftime("%H:%M")
            end_time = (row["Timestamp"] + pd.Timedelta(minutes=15)).strftime("%H:%M")
            usage_level = row["Predicted_Status_Label"]
            predicted_status = row["Predicted_Status"]

            if predicted_status == 0:
                intensity = "HIGH"
                color = QColor(50, 205, 50)  # Green
            elif predicted_status == 1:
                intensity = "MEDIUM"
                color = QColor(255, 215, 0)  # Gold
            elif predicted_status == 2:
                intensity = "LOW"
                color = QColor(255, 140, 0)  # Orange
            else:
                intensity = "NONE"
                color = QColor(178, 34, 34)  # Dark Red

            for col, value in enumerate([start_time, end_time, usage_level, intensity]):
                item = QTableWidgetItem(value)
                item.setBackground(color)
                self.table.setItem(idx, col, item)

        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def update_current_time(self, time):
        self.current_time = time
        self.update_button_state()

    def update_button_state(self):
        selected_date = self.calendar.selectedDate().toPyDate()
        current_datetime = pd.Timestamp.combine(
            selected_date, self.current_time.toPyTime()
        )
        
        try:
            row = self.future_df[self.future_df["Timestamp"] <= current_datetime].iloc[-1]
            predicted_status = row["Predicted_Status"]
            
            if predicted_status == 0:
                text = "Starting Automation with High Intensity"
                color = "#32CD32"  # Green
            elif predicted_status == 1:
                text = "Starting Automation with Medium Intensity"
                color = "#FFD700"  # Gold
            elif predicted_status == 2:
                text = "Starting Automation with Low Intensity"
                color = "#FFA500"  # Orange
            else:
                text = "Stop Automation due to High Usage"
                color = "#B22222"  # Dark Red
                
            self.automation_button.setText(text)
            self.automation_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: {'black' if color == '#FFD700' else 'white'};
                    border-radius: 5px;
                    padding: 8px;
                    border: none;
                }}
                QPushButton:hover {{
                    background-color: {self.adjust_color(color)};
                }}
            """)
        except IndexError:
            pass

    def adjust_color(self, hex_color):
        # Darken the color for hover effect
        color = QColor(hex_color)
        h, s, v, a = color.getHsv()
        return QColor.fromHsv(h, s, int(v * 0.8), a).name()

    def toggle_automation(self):
        print(f"Automation {self.automation_button.text()} clicked")

def start_gui(future_df):
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    gui = SchedulerGUI(future_df)
    gui.show()
    sys.exit(app.exec_())
