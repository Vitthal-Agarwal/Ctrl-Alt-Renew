import sys, random
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QSpacerItem,
    QSizePolicy,
    QStackedWidget,
    QRadioButton,
    QButtonGroup,
    QCheckBox,
    QCalendarWidget,
    QTimeEdit,
)
from PyQt5.QtCore import Qt, QSize, QRect, QDate, QTimer, QTime
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon, QPixmap, QPainter, QBrush, QPen
import pandas as pd


class SchedulerGUI(QWidget):
    def __init__(self, future_df):
        super().__init__()
        self.future_df = future_df
        self.current_week_start = self.future_df["Timestamp"].min().date()
        self.current_time = QTime.currentTime()
        self.initUI()

    def initUI(self):
        self.setStyleSheet(
            """
            QWidget {
                background-color: #F5F5F5;
            }
            QLabel {
                color: #333;
                font-size: 14px;
            }
            QPushButton {
                border: none;
                padding: 8px;
                border-radius: 4px;
                color: white;
                background-color: #1E1E1E;
            }
            QPushButton:hover {
                background-color: #333333;
            }
            QCalendarWidget {
                background-color: white;
                color: black;
            }
            QTableWidget {
                background-color: white;
                gridline-color: #E0E0E0;
            }
            QHeaderView::section {
                background-color: #F0F0F0;
                padding: 6px;
                border: none;
                font-weight: bold;
                color: #666;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 5px;
                font-size: 14px;
            }
            QTimeEdit {
                font-size: 14px;
            }
        """
        )

        main_layout = QVBoxLayout()

        # Top section - Automation Button
        top_layout = QHBoxLayout()
        self.automation_button = QPushButton("Starting Automation with Low Intensity")
        self.automation_button.setFixedHeight(40)
        self.automation_button.setMinimumWidth(400)
        self.automation_button.setFont(QFont("Arial", 10, QFont.Bold))
        self.automation_button.clicked.connect(self.toggle_automation)
        top_layout.addStretch()
        top_layout.addWidget(self.automation_button)
        top_layout.addStretch()
        main_layout.addLayout(top_layout)

        # Content section
        content_layout = QHBoxLayout()

        # Left panel - Calendar and Controls
        left_panel = QVBoxLayout()
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.selectionChanged.connect(self.show_schedule)
        self.calendar.setStyleSheet(
            """
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
        """
        )
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
        self.table.setStyleSheet(
            """
            QTableWidget {
                background-color: white;
                gridline-color: #E0E0E0;
            }
            QHeaderView::section {
                background-color: #F0F0F0;
                padding: 6px;
                border: none;
                font-weight: bold;
                color: #666;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 5px;
                font-size: 14px;
            }
        """
        )
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
                item.setTextAlignment(Qt.AlignCenter)
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
            row = self.future_df[self.future_df["Timestamp"] <= current_datetime].iloc[
                -1
            ]
            predicted_status = row["Predicted_Status"]

            if predicted_status == 0:
                text = "Starting Automation with High Intensity"
                color = "#32CD32"  # Lime Green
                text_color = "black"
            elif predicted_status == 1:
                text = "Starting Automation with Medium Intensity"
                color = "#FFD700"  # Gold
                text_color = "black"
            elif predicted_status == 2:
                text = "Starting Automation with Low Intensity"
                color = "#FFA500"  # Orange
                text_color = "black"
            else:
                text = "Stop Automation due to High Usage"
                color = "#B22222"  # Firebrick
                text_color = "white"

            self.automation_button.setText(text)
            self.automation_button.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {color};
                    color: {text_color};
                    border-radius: 5px;
                    padding: 8px;
                    border: none;
                }}
                QPushButton:hover {{
                    background-color: {self.adjust_color(color)};
                }}
            """
            )
        except IndexError:
            # Handle case where no rows are present
            self.automation_button.setText("No Automation Scheduled")
            self.automation_button.setStyleSheet(
                """
                QPushButton {
                    background-color: #808080;  /* Gray */
                    color: white;
                    border-radius: 5px;
                    padding: 8px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #696969;
                }
            """
            )

    def adjust_color(self, hex_color):
        # Darken the color for hover effect
        color = QColor(hex_color)
        h, s, v, a = color.getHsv()
        return QColor.fromHsv(h, s, int(v * 0.8), a).name()

    def toggle_automation(self):
        print(f"Automation {self.automation_button.text()} clicked")


class ModernMolecularGUI(QMainWindow):
    def __init__(self, future_df, computation_manager):
        super().__init__()
        self.future_df = future_df
        self.computation_manager = computation_manager
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Molecular Universe")
        self.showFullScreen()  # Make the application full screen
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5F5F5;
            }
            QLabel {
                color: #333;
            }
            QPushButton {
                border: none;
                padding: 8px;
                border-radius: 4px;
                color: white;
                background-color: #1E1E1E;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.main_layout = QHBoxLayout(main_widget)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Add sidebar
        sidebar = self.create_sidebar()
        self.main_layout.addWidget(sidebar)

        # Add content area with stacked widget for navigation
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget, 1)  # 1 is the stretch factor

        # Create individual pages
        self.home_page = self.create_home_page()
        self.rankings_page = self.create_rankings_page()
        self.future_schedule_page = self.create_future_schedule_page()

        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.home_page)  # Index 0
        self.stacked_widget.addWidget(self.rankings_page)  # Index 1
        self.stacked_widget.addWidget(self.future_schedule_page)  # Index 2

        # Set default page
        self.stacked_widget.setCurrentWidget(self.home_page)


    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setStyleSheet(
            """
            QFrame {
                background-color: #1E1E1E;
                min-width: 300px;  /* Sidebar width */
                max-width: 300px;
                padding: 30px;     /* Sidebar padding */
            }
            QLabel {
                color: white;
            }
            QPushButton {
                text-align: left;
                padding: 15px;          /* Button padding */
                margin: 6px 0;          /* Button margin */
                color: white;
                border-radius: 8px;
                font-size: 16px;        /* Button font size */
                font-weight: 500;       /* Button font weight */
                background-color: #1E1E1E;
            }
            QPushButton:hover {
                background-color: #333333;
            }
            QPushButton#nav-active {
                background-color: #333333;
            }
        """
        )

        layout = QVBoxLayout(sidebar)
        layout.setSpacing(30)  # Spacing between sidebar elements
        layout.setContentsMargins(0, 0, 0, 0)

        # App Name Logo
        logo_label = QLabel("MolecularUniverse")
        logo_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: white; margin-bottom: 40px;"  # Logo styling
        )
        layout.addWidget(logo_label, alignment=Qt.AlignCenter)

        # Profile section
        profile_widget = QWidget()
        profile_layout = QVBoxLayout(profile_widget)
        profile_layout.setSpacing(10)  # Reduced spacing for better alignment
        profile_layout.setAlignment(Qt.AlignCenter)

        # Profile Picture
        profile_pic_label = QLabel()
        profile_pic_label.setFixedSize(
            150, 200
        )  # Adjusted to 150x150 for square fitting
        profile_pic_label.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap(
            "dan.jpeg"
        )  # Ensure 'dan.jpeg' is in the same directory as 'gui.py'
        if pixmap.isNull():
            pixmap = QPixmap(150, 200)
            pixmap.fill(Qt.gray)
        else:
            pixmap = pixmap.scaled(
                150, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )

        # Set the pixmap without circular masking
        profile_pic_label.setPixmap(pixmap)
        profile_pic_label.setStyleSheet(
            "border-radius: 10px;"  # Optional: Add slight rounding without border
        )

        # User Name
        user_name_label = QLabel("Dan Walsh")
        user_name_label.setStyleSheet(
            "font-size: 18px; color: white; font-weight: bold;"
        )
        user_name_label.setAlignment(Qt.AlignCenter)

        # Edit Button
        edit_button = QPushButton("Edit")
        edit_button.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                border: 1px solid #444;
                padding: 8px 12px;  /* Button padding */
                font-size: 14px;     /* Button font size */
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """
        )

        # Assemble profile layout: Image above Name
        profile_layout.addWidget(profile_pic_label)
        profile_layout.addWidget(user_name_label)
        profile_layout.addWidget(edit_button, alignment=Qt.AlignCenter)
        layout.addWidget(profile_widget)

        # Navigation buttons
        # Updated button labels with emojis and exact names
        self.home_btn = QPushButton("🏠  Home")
        self.rankings_btn = QPushButton("📊  Rankings")
        self.future_schedule_btn = QPushButton("📅  Future Schedule")

        # Set object names for styling
        self.home_btn.setObjectName("nav-active")  # Set Home as active by default

        # Connect buttons to methods
        self.home_btn.clicked.connect(self.show_home)
        self.rankings_btn.clicked.connect(self.show_rankings)
        self.future_schedule_btn.clicked.connect(self.show_future_schedule)

        layout.addWidget(self.home_btn)
        layout.addWidget(self.rankings_btn)
        layout.addWidget(self.future_schedule_btn)

        # Add spacer to push logout and version to the bottom
        layout.addStretch()

        # Logout and version
        logout_btn = QPushButton("⬅️  Logout")
        logout_btn.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                color: #888;
                font-size: 14px;  /* Logout button font size */
            }
            QPushButton:hover {
                color: #AAA;
            }
        """
        )
        layout.addWidget(logout_btn)

        version_label = QLabel("Version 0.1.1.0 (RC)")
        version_label.setStyleSheet("color: #666; font-size: 12px; margin-top: 10px;")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)

        return sidebar

    def create_home_page(self):
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background-color: #F5F5F5;
            }
        """)

        layout = QVBoxLayout(content_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # **Notification Banner**
        self.notification_banner = QLabel()
        self.notification_banner.setFixedHeight(50)
        self.notification_banner.setStyleSheet("""
            QLabel {
                background-color: #7CD332;
                color: white;
                font-size: 18px;
                padding: 10px;
                border-radius: 8px;
            }
        """)
        self.notification_banner.hide()  # Hidden by default
        layout.addWidget(self.notification_banner)

        # **Add CPU Units Given Boxes**
        cpu_boxes_widget = QWidget()
        cpu_boxes_layout = QVBoxLayout(cpu_boxes_widget)
        cpu_boxes_layout.setAlignment(Qt.AlignCenter)
        cpu_boxes_layout.setSpacing(20)

        # Current CPU Power Units Given Box
        self.current_cpu_box = QFrame()
        self.current_cpu_box.setFixedSize(400, 150)
        self.current_cpu_box.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border-radius: 20px;
            }
        """)
        current_cpu_layout = QVBoxLayout(self.current_cpu_box)
        current_cpu_label = QLabel("Current CPU Power Units Given")
        current_cpu_label.setStyleSheet("color: white; font-size: 24px;")
        self.current_cpu_value = QLabel("0 Units")
        self.current_cpu_value.setStyleSheet("color: #7CD332; font-size: 48px; font-weight: bold;")
        current_cpu_layout.addStretch()
        current_cpu_layout.addWidget(current_cpu_label, alignment=Qt.AlignCenter)
        current_cpu_layout.addWidget(self.current_cpu_value, alignment=Qt.AlignCenter)
        current_cpu_layout.addStretch()

        # Total CPU Units Given So Far Box
        self.total_cpu_box = QFrame()
        self.total_cpu_box.setFixedSize(350, 120)
        self.total_cpu_box.setStyleSheet("""
            QFrame {
                background-color: #333333;
                border-radius: 20px;
            }
        """)
        total_cpu_layout = QVBoxLayout(self.total_cpu_box)
        total_cpu_label = QLabel("Total CPU Units Contributed")
        total_cpu_label.setStyleSheet("color: white; font-size: 20px;")
        self.total_cpu_value = QLabel("0 Units")
        self.total_cpu_value.setStyleSheet("color: #FFD700; font-size: 36px; font-weight: bold;")
        total_cpu_layout.addStretch()
        total_cpu_layout.addWidget(total_cpu_label, alignment=Qt.AlignCenter)
        total_cpu_layout.addWidget(self.total_cpu_value, alignment=Qt.AlignCenter)
        total_cpu_layout.addStretch()

        cpu_boxes_layout.addWidget(self.current_cpu_box)
        cpu_boxes_layout.addWidget(self.total_cpu_box)

        layout.addWidget(cpu_boxes_widget, alignment=Qt.AlignCenter)

        # **Add Auto and Manual Buttons**
        workflow_buttons_widget = QWidget()
        workflow_buttons_layout = QHBoxLayout(workflow_buttons_widget)
        workflow_buttons_layout.setAlignment(Qt.AlignCenter)
        workflow_buttons_layout.setSpacing(40)

        # Auto Button
        self.auto_button = QPushButton("Auto Mode")
        self.auto_button.setFixedSize(180, 60)
        self.auto_button.setStyleSheet("""
            QPushButton {
                background-color: #7CD332;
                border-radius: 30px;
                color: white;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6BC22B;
            }
        """)
        self.auto_button.clicked.connect(self.start_auto_mode)

        # Manual Button
        self.manual_button = QPushButton("Manual Mode")
        self.manual_button.setFixedSize(180, 60)
        self.manual_button.setStyleSheet("""
            QPushButton {
                background-color: #FFA500;
                border-radius: 30px;
                color: white;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E59400;
            }
        """)
        self.manual_button.clicked.connect(self.start_manual_mode)

        workflow_buttons_layout.addWidget(self.auto_button)
        workflow_buttons_layout.addWidget(self.manual_button)

        layout.addWidget(workflow_buttons_widget, alignment=Qt.AlignCenter)

        # Spacer to push content to the top
        layout.addStretch()

        # **Timers and State Variables**
        self.cpu_usage_timer = QTimer()
        self.cpu_usage_timer.timeout.connect(self.update_cpu_usage)
        self.cpu_usage_level = 0  # Simulated CPU usage level

        self.manual_mode_active = False  # Track manual mode state

        return content_widget

    def start_auto_mode(self):
        # Display a banner that Auto Mode has started
        self.notification_banner.setText("Auto Mode has started.")
        self.notification_banner.setStyleSheet("""
            QLabel {
                background-color: #7CD332;
                color: white;
                font-size: 18px;
                padding: 10px;
                border-radius: 8px;
            }
        """)
        self.notification_banner.show()

        # Hide the banner after 3 seconds
        QTimer.singleShot(3000, self.notification_banner.hide)

        # Start updating CPU usage
        self.cpu_usage_timer.start(1000)  # Update every second

    def start_manual_mode(self):
        if not self.manual_mode_active:
            # Change button to Stop
            self.manual_button.setText("Stop")
            self.manual_button.setStyleSheet("""
                QPushButton {
                    background-color: #D9534F;
                    border-radius: 30px;
                    color: white;
                    font-size: 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #C9302C;
                }
            """)
            self.manual_mode_active = True

            # Display a banner
            self.notification_banner.setText("Manual Mode has started.")
            self.notification_banner.setStyleSheet("""
                QLabel {
                    background-color: #FFA500;
                    color: white;
                    font-size: 18px;
                    padding: 10px;
                    border-radius: 8px;
                }
            """)
            self.notification_banner.show()
            QTimer.singleShot(3000, self.notification_banner.hide)

            # Start updating CPU usage
            self.cpu_usage_timer.start(1000)  # Update every second
        else:
            # Change button back to Manual Mode
            self.manual_button.setText("Manual Mode")
            self.manual_button.setStyleSheet("""
                QPushButton {
                    background-color: #FFA500;
                    border-radius: 30px;
                    color: white;
                    font-size: 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #E59400;
                }
            """)
            self.manual_mode_active = False

            # Display a banner
            self.notification_banner.setText("Manual Mode has stopped.")
            self.notification_banner.setStyleSheet("""
                QLabel {
                    background-color: #D9534F;
                    color: white;
                    font-size: 18px;
                    padding: 10px;
                    border-radius: 8px;
                }
            """)
            self.notification_banner.show()
            QTimer.singleShot(3000, self.notification_banner.hide)

            # Stop updating CPU usage
            self.cpu_usage_timer.stop()

    def update_cpu_usage(self):
        # Simulate CPU usage level change
        self.cpu_usage_level = random.randint(0, 100)
        self.current_cpu_value.setText(f"{self.cpu_usage_level} Units")

        # Change color based on CPU usage level
        if self.cpu_usage_level < 30:
            color = "#7CD332"  # Green
        elif self.cpu_usage_level < 60:
            color = "#FFD700"  # Gold
        elif self.cpu_usage_level < 90:
            color = "#FFA500"  # Orange
        else:
            color = "#D9534F"  # Red

        self.current_cpu_value.setStyleSheet(f"color: {color}; font-size: 48px; font-weight: bold;")

        # Update total CPU units contributed
        total_units = int(self.total_cpu_value.text().split()[0]) + self.cpu_usage_level
        self.total_cpu_value.setText(f"{total_units} Units")

    def create_rankings_page(self):
        rankings_widget = QWidget()
        rankings_widget.setStyleSheet(
            """
            QWidget {
                background-color: #F5F5F5;
            }
        """
        )
        layout = QVBoxLayout(rankings_widget)
        layout.setAlignment(Qt.AlignCenter)

        label = QLabel("Rankings Page - Coming Soon!")
        label.setStyleSheet("font-size: 24px; color: #666;")
        layout.addWidget(label)

        return rankings_widget

    def create_future_schedule_page(self):
        # Integrate SchedulerGUI into the Future Schedule page
        schedule_widget = SchedulerGUI(self.future_df)
        return schedule_widget

    def create_workflow_card(self):
        card = QFrame()
        card.setStyleSheet(
            """
            QFrame {
                background-color: #1E1E1E;
                border-radius: 12px;
                padding: 24px;
            }
        """
        )

        layout = QVBoxLayout(card)
        layout.setSpacing(20)

        # Title and subtitle
        title = QLabel("Calculation Workflow")
        title.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        subtitle = QLabel("Choose your workflow mode")
        subtitle.setStyleSheet("color: #888; font-size: 16px;")
        subtitle.setAlignment(Qt.AlignCenter)

        # Options: Auto and Manual
        options_widget = QWidget()
        options_layout = QHBoxLayout(options_widget)
        options_layout.setAlignment(Qt.AlignCenter)
        options_layout.setSpacing(50)  # Spacing between options

        # Auto Option
        auto_widget = QWidget()
        auto_layout = QVBoxLayout(auto_widget)
        auto_layout.setAlignment(Qt.AlignCenter)

        auto_radio = QRadioButton("Auto")
        auto_radio.setStyleSheet("color: white; font-size: 16px;")
        auto_radio.setChecked(True)  # Default selection

        auto_layout.addWidget(auto_radio)

        # Manual Option
        manual_widget = QWidget()
        manual_layout = QVBoxLayout(manual_widget)
        manual_layout.setAlignment(Qt.AlignCenter)

        manual_radio = QRadioButton("Manual")
        manual_radio.setStyleSheet("color: white; font-size: 16px;")

        manual_layout.addWidget(manual_radio)

        # Button Group to ensure only one is selected
        self.workflow_group = QButtonGroup()
        self.workflow_group.addButton(auto_radio)
        self.workflow_group.addButton(manual_radio)
        self.workflow_group.buttonClicked.connect(self.workflow_mode_changed)

        options_layout.addWidget(auto_widget)
        options_layout.addWidget(manual_widget)

        # Control Buttons for Manual Mode
        self.manual_controls_widget = QWidget()
        self.manual_controls_layout = QHBoxLayout(self.manual_controls_widget)
        self.manual_controls_layout.setAlignment(Qt.AlignCenter)
        self.manual_controls_layout.setSpacing(20)

        self.start_btn = QPushButton("Start")
        self.start_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #7CD332;
                min-width: 120px;
                padding: 10px 20px;
                font-size: 16px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #6BC22B;
            }
        """
        )
        self.start_btn.clicked.connect(self.start_manual_workflow)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #D9534F;
                min-width: 120px;
                padding: 10px 20px;
                font-size: 16px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #C9302C;
            }
        """
        )
        self.stop_btn.clicked.connect(self.stop_manual_workflow)
        self.stop_btn.setEnabled(False)  # Initially disabled

        self.manual_controls_layout.addWidget(self.start_btn)
        self.manual_controls_layout.addWidget(self.stop_btn)
        self.manual_controls_widget.hide()  # Hidden by default

        # Layout Assembly
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(options_widget)
        layout.addWidget(self.manual_controls_widget)
        layout.addStretch()

        return card

    def workflow_mode_changed(self, button):
        if button.text() == "Manual":
            self.manual_controls_widget.show()
        else:
            self.manual_controls_widget.hide()

    def start_manual_workflow(self):
        # Implement start logic here
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        # Example: self.computation_manager.start_workflow()
        print("Manual workflow started.")

    def stop_manual_workflow(self):
        # Implement stop logic here
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        # Example: self.computation_manager.stop_workflow()
        print("Manual workflow stopped.")

    def create_current_calculation_card(self):
        card = QFrame()
        card.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 24px;
            }
        """
        )

        layout = QVBoxLayout(card)

        # Title
        title = QLabel("Current Calculation")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 16px;")
        layout.addWidget(title)

        # Info grid
        info_grid = QHBoxLayout()

        # Cycle indicator
        cycle_frame = QFrame()
        cycle_frame.setStyleSheet(
            """
            QFrame {
                background-color: #1E1E1E;
                border-radius: 8px;
                padding: 16px;
                max-width: 150px;  /* Increased width */
            }
        """
        )
        cycle_layout = QVBoxLayout(cycle_frame)

        cycle_label = QLabel("Cycle")
        cycle_label.setStyleSheet("color: white; font-size: 16px;")
        cycle_num = QLabel("12")
        cycle_num.setStyleSheet("color: #7CD332; font-size: 24px; font-weight: bold;")

        cycle_layout.addWidget(cycle_label, alignment=Qt.AlignCenter)
        cycle_layout.addWidget(cycle_num, alignment=Qt.AlignCenter)
        info_grid.addWidget(cycle_frame)

        # Molecule info
        molecule_widget = QWidget()
        molecule_layout = QVBoxLayout(molecule_widget)

        molecule_title = QLabel("Molecule")
        molecule_title.setStyleSheet("color: #666; font-size: 16px;")
        molecule_name = QLabel("Ethane (C2H4)")
        molecule_name.setStyleSheet("font-size: 16px; font-weight: 500;")

        molecule_layout.addWidget(molecule_title)
        molecule_layout.addWidget(molecule_name)
        info_grid.addWidget(molecule_widget)

        # Characteristics
        chars_widget = QWidget()
        chars_layout = QVBoxLayout(chars_widget)

        chars_title = QLabel("Characteristics")
        chars_title.setStyleSheet("color: #666; font-size: 16px;")
        chars_value = QLabel("Alcohol")
        chars_value.setStyleSheet("font-size: 16px; font-weight: 500;")

        chars_layout.addWidget(chars_title)
        chars_layout.addWidget(chars_value)
        info_grid.addWidget(chars_widget)

        layout.addLayout(info_grid)
        return card

    def create_previous_calculations_card(self):
        card = QFrame()
        card.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 24px;
            }
        """
        )

        layout = QVBoxLayout(card)

        # Title
        title = QLabel("Previous Calculations")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 16px;")
        layout.addWidget(title)

        # Table
        table = QTableWidget()
        table.setStyleSheet(
            """
            QTableWidget {
                border: none;
                gridline-color: #EEE;
            }
            QHeaderView::section {
                background-color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
                color: #666;
                font-size: 14px;
            }
            QTableWidget::item {
                font-size: 14px;
            }
        """
        )

        # Set up table
        headers = ["Name", "Score", "Date", "CPU time", "Settings", "Actions"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)

        # Add sample data
        sample_data = [
            ["Acetaldehyde (C2H4O)", "1027", "1/15/2024 11:25 AM", "00:02:17", "1.0.0"],
            ["Acetaldehyde (C2H4O)", "842", "1/15/2024 11:22 AM", "00:02:12", "1.0.0"],
            ["Acetaldehyde (C2H4O)", "797", "1/15/2024 11:15 AM", "00:01:22", "1.0.0"],
        ]

        table.setRowCount(len(sample_data))
        for row, data in enumerate(sample_data):
            for col, value in enumerate(data):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                table.setItem(row, col, item)

            # Add View Details button
            view_btn = QPushButton("View Details")
            view_btn.setStyleSheet(
                """
                QPushButton {
                    background-color: transparent;
                    color: #666;
                    text-decoration: underline;
                    font-size: 14px;
                }
                QPushButton:hover {
                    color: #333;
                }
            """
            )
            table.setCellWidget(row, len(headers) - 1, view_btn)

        layout.addWidget(table)
        return card

    def show_home(self):
        self.stacked_widget.setCurrentWidget(self.home_page)
        self.update_nav_buttons(active_button=self.home_btn)

    def show_rankings(self):
        self.stacked_widget.setCurrentWidget(self.rankings_page)
        self.update_nav_buttons(active_button=self.rankings_btn)

    def show_future_schedule(self):
        self.stacked_widget.setCurrentWidget(self.future_schedule_page)
        self.update_nav_buttons(active_button=self.future_schedule_btn)

    def update_nav_buttons(self, active_button):
        # Reset all buttons
        for btn in [self.home_btn, self.rankings_btn, self.future_schedule_btn]:
            btn.setObjectName("")
            btn.setStyleSheet(
                """
                QPushButton {
                    text-align: left;
                    padding: 15px;
                    margin: 6px 0;
                    color: white;
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: 500;
                    background-color: #1E1E1E;
                }
                QPushButton:hover {
                    background-color: #333333;
                }
            """
            )

        # Highlight the active button
        active_button.setObjectName("nav-active")
        active_button.setStyleSheet(
            """
            QPushButton#nav-active {
                background-color: #333333;
                text-align: left;
                padding: 15px;
                margin: 6px 0;
                color: white;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 500;
            }
        """
        )

def start_app(future_df=None, computation_manager=None):
    app = QApplication(sys.argv)

    # Set application-wide style
    app.setStyle("Fusion")


    # Set palette to match the overall theme
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(245, 245, 245))
    palette.setColor(QPalette.WindowText, QColor(51, 51, 51))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(51, 51, 51))
    palette.setColor(QPalette.Text, QColor(51, 51, 51))
    palette.setColor(QPalette.Button, QColor(245, 245, 245))
    palette.setColor(QPalette.ButtonText, QColor(51, 51, 51))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)

    gui = ModernMolecularGUI(future_df, computation_manager)
    gui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    # Example DataFrame for testing purposes
    data = {
        "Timestamp": pd.date_range(start="2024-01-01 08:00", periods=100, freq="15T"),
        "Predicted_Status": [0, 1, 2, 3]
        * 25,  # 0: Low, 1: Medium, 2: High, 3: Critical
        "Predicted_Status_Label": ["Low", "Medium", "High", "Critical"] * 25,
    }
    future_df = pd.DataFrame(data)

    # Placeholder for computation_manager
    computation_manager = None  # Replace with actual computation manager if available

    start_app(future_df, computation_manager)  # For testing purposes only
