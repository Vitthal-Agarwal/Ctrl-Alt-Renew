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
    QLineEdit,
    QComboBox,
    QGraphicsDropShadowEffect,
)
from PyQt5.QtCore import Qt, QSize, QRect, QDate, QTimer, QTime
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon, QPixmap, QPainter, QBrush, QPen
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
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
        
        # Initialize data for leaderboards
        self.weekly_data = [
            [1, "Alice Smith", "alice@example.com", "Alice", 1500, 100],
            [2, "Bob Johnson", "bob@example.com", "Bob", 1400, 90],
            [3, "Charlie Brown", "charlie@example.com", "Charlie", 1300, 80],
            [4, "David Wilson", "david@example.com", "David", 1200, 70],
            [5, "Eva Green", "eva@example.com", "Eva", 1100, 60],
        ]
        
        self.all_time_data = [
            [1, "Andre Neto Win", "andre.neto.c.w@conceptpatech.com", "Neto Win", 132383, 360],
            [2, "Dan Hannah", "dan.hannah@ses.ai", "dan.hannah", 126554, 199],
            [3, "Roberta QATest", "robertaqatest@gmail.com", "qatest", 109424, 170],
            [4, "Cristiano Moraes", "cristianomoraescar@gmail.com", "ccmoraes", 81421, 121],
            [5, "Daniel Walsh", "danwalshhh@gmail.com", "Dan", 50477, 91],
            [6, "Leandro Barbosa", "leandro@fanhero.com", "leeaandrob", 36100, 60],
            [7, "Raquel Comunale", "comunale.qa@gmail.com", "comunale.qa", 24005, 41],
            [8, "Raul Burd", "raul@conceptpatech.com", "RB", 22928, 52],
            [9, "Sarah Chen", "sarah.chen@example.com", "SarahC", 21500, 48],
        [10, "Michael Rodriguez", "mrodriguez@example.com", "MikeR", 20100, 45],
        [11, "Emma Thompson", "emma.t@example.com", "EmmaT", 19500, 43],
        [12, "James Wilson", "jwilson@example.com", "JWil", 18900, 40],
        [13, "Lisa Anderson", "lisa.a@example.com", "LisaA", 17800, 38],
        [14, "Kevin Park", "kpark@example.com", "KPark", 16700, 35],
        [15, "Maria Garcia", "mgarcia@example.com", "MariaG", 15600, 33],
        [16, "Thomas Brown", "tbrown@example.com", "TomB", 14500, 30],
        [17, "Anna Kim", "akim@example.com", "AnnaK", 13400, 28],
        [18, "Peter Zhang", "pzhang@example.com", "PeterZ", 12300, 25],
        [19, "Sophie Martin", "smartin@example.com", "SophieM", 11200, 23],
        [20, "David Lee", "dlee@example.com", "DaveL", 10100, 20],
        ]
        
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

    def update_period(self):
        selected_period = self.period_combo.currentText()
        
        # Implement logic to filter data based on the selected period
        if selected_period == "Last 30 days":
            # Filter or modify self.all_time_data as needed
            self.populate_table(self.rankings_table, self.all_time_data)  # Replace with actual filtering logic
        elif selected_period == "Last 60 days":
            # Implement logic for Last 60 days
            self.populate_table(self.rankings_table, self.all_time_data)  # Replace with actual filtering logic
        elif selected_period == "All time":
            # Show all-time data
            self.populate_table(self.rankings_table, self.all_time_data)  # Replace with actual filtering logic

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
        home_widget = QWidget()
        main_layout = QVBoxLayout(home_widget)
        main_layout.setContentsMargins(0, 50, 0, 50)
        
        # Center container
        center_container = QWidget()
        center_layout = QVBoxLayout(center_container)
        center_layout.setAlignment(Qt.AlignCenter)
        
        # Workflow container
        workflow_container = QFrame()
        workflow_container.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border-radius: 20px;
                min-width: 480px;
                max-width: 480px;
                padding: 35px;
            }
        """)
        workflow_layout = QVBoxLayout(workflow_container)
        workflow_layout.setSpacing(25)
        
        # Add Dashboard Heading
        dashboard_title = QLabel("Calculation Workflow")
        dashboard_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial;
                margin-bottom: 10px;
            }
        """)
        dashboard_title.setAlignment(Qt.AlignCenter)
        
        # Add subtitle
        subtitle = QLabel("The program will execute when your computer is idle")
        subtitle.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 14px;
                font-family: 'Segoe UI', Arial;
                margin-bottom: 20px;
            }
        """)
        subtitle.setAlignment(Qt.AlignCenter)
        
        workflow_layout.addWidget(dashboard_title)
        workflow_layout.addWidget(subtitle)
        
        # Stats boxes - KEY MEASUREMENTS
        stats_box_style = """
            QFrame {
                background-color: #262626;
                border-radius: 15px;
                padding: 0px -15px;  /* Vertical 20px, Horizontal 25px */
                margin: 5px 0px;     /* Small vertical margin */
            }
        """
        
        # Current CPU Units Box
        current_cpu_box = QFrame()
        current_cpu_box.setStyleSheet(stats_box_style)
        current_cpu_layout = QVBoxLayout(current_cpu_box)
        current_cpu_layout.setSpacing(8)
        
        current_label = QLabel("Current CPU Power Units Given")
        current_label.setStyleSheet("""
            font-size: 16px;
            color: #E0E0E0;
            font-family: 'Segoe UI', Arial;
        """)
        current_label.setAlignment(Qt.AlignCenter)
        
        self.current_units = QLabel("0 Units")
        self.current_units.setStyleSheet("""
            font-size: 42px;
            font-weight: bold;
            color: #7CD332;
            font-family: 'Segoe UI', Arial;
        """)
        self.current_units.setAlignment(Qt.AlignCenter)
        
        current_cpu_layout.addWidget(current_label)
        current_cpu_layout.addWidget(self.current_units)
        
        # Total CPU Units Box
        total_cpu_box = QFrame()
        total_cpu_box.setStyleSheet(stats_box_style)
        total_cpu_layout = QVBoxLayout(total_cpu_box)
        total_cpu_layout.setSpacing(8)
        
        total_label = QLabel("Total CPU Units Contributed")
        total_label.setStyleSheet("""
            font-size: 16px;
            color: #E0E0E0;
            font-family: 'Segoe UI', Arial;
        """)
        total_label.setAlignment(Qt.AlignCenter)
        
        self.total_units = QLabel("0 Units")
        self.total_units.setStyleSheet("""
            font-size: 42px;
            font-weight: bold;
            color: #FFD700;
            font-family: 'Segoe UI', Arial;
        """)
        self.total_units.setAlignment(Qt.AlignCenter)
        
        total_cpu_layout.addWidget(total_label)
        total_cpu_layout.addWidget(self.total_units)
        
        # Mode Buttons Container
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setSpacing(15)
        buttons_layout.setContentsMargins(0, 15, 0, 0)
        
        # Auto Mode Button
        auto_mode_btn = QPushButton("Auto Mode")
        auto_mode_btn.setCursor(Qt.PointingHandCursor)
        auto_mode_btn.setFixedSize(180, 40)
        auto_mode_btn.setStyleSheet("""
            QPushButton {
                background-color: #7CD332;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial;
            }
            QPushButton:hover {
                background-color: #6BB22E;
            }
        """)
        
        # Manual Mode Button
        manual_mode_btn = QPushButton("Manual Mode")
        manual_mode_btn.setCursor(Qt.PointingHandCursor)
        manual_mode_btn.setFixedSize(180, 40)
        manual_mode_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFA500;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial;
            }
            QPushButton:hover {
                background-color: #E69500;
            }
        """)
        
        buttons_layout.addWidget(auto_mode_btn, alignment=Qt.AlignCenter)
        buttons_layout.addWidget(manual_mode_btn, alignment=Qt.AlignCenter)
        
        # Add all elements to workflow container
        workflow_layout.addWidget(current_cpu_box)
        workflow_layout.addWidget(total_cpu_box)
        workflow_layout.addWidget(buttons_container)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 5)
        workflow_container.setGraphicsEffect(shadow)
        
        # Add workflow container to center layout
        center_layout.addWidget(workflow_container, alignment=Qt.AlignCenter)
        
        # Add center container to main layout
        main_layout.addWidget(center_container)
        
        return home_widget

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
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #333;
            }
            QLineEdit {
                padding: 12px;
                font-size: 14px;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                background: white;
                min-width: 300px;
            }
            QComboBox {
                padding: 8px 12px;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                background: white;
                min-width: 150px;
            }
            QTableWidget {
                background-color: white;
                border: none;
                border-radius: 8px;
                gridline-color: transparent;
            }
            QHeaderView::section {
                background-color: white;
                padding: 15px;
                border: none;
                border-bottom: 2px solid #E0E0E0;
                font-weight: bold;
                color: #666;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 15px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #F5F5F5;
                color: black;
            }
            """
        )

        # Main Layout with increased padding
        layout = QVBoxLayout(rankings_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(30)

        # Header Section
        header_layout = QHBoxLayout()
        
        # Search Section with improved styling
        search_label = QLabel("Search by full name, nickname or email:")
        search_label.setStyleSheet("font-size: 14px; font-weight: normal; color: #666;")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type here...")
        self.search_input.setFixedWidth(400)
        # Explicitly disconnect any existing connections to avoid duplicates
        try:
            self.search_input.textChanged.disconnect()
        except:
            pass
        # Connect the search signal
        self.search_input.textChanged.connect(self.filter_tables)
        
        # Period Selection with improved styling
        period_label = QLabel("Period:")
        period_label.setStyleSheet("font-size: 14px; font-weight: normal; color: #666;")
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Last 30 days", "Last 60 days", "All time"])
        
        header_layout.addWidget(search_label)
        header_layout.addWidget(self.search_input)
        header_layout.addStretch()
        header_layout.addWidget(period_label)
        header_layout.addWidget(self.period_combo)
        
        layout.addLayout(header_layout)

        # Weekly Leaderboard with more sample data
        weekly_label = QLabel("Weekly Leaderboard 🥇")
        layout.addWidget(weekly_label)
        
        self.weekly_table = self.create_leaderboard_table()
        self.weekly_data = [
            [1, "Alice Smith", "alice@example.com", "Alice", 1500, 100],
            [2, "Bob Johnson", "bob@example.com", "Bob", 1400, 90],
            [3, "Charlie Brown", "charlie@example.com", "Charlie", 1300, 80],
            [4, "David Wilson", "david@example.com", "David", 1200, 70],
            [5, "Eva Green", "eva@example.com", "Eva", 1100, 60],
            [6, "Frank Miller", "frank@example.com", "Frank", 1000, 55],
            [7, "Grace Lee", "grace@example.com", "Grace", 950, 50],
            [8, "Henry Ford", "henry@example.com", "Henry", 900, 45],
            [9, "Iris West", "iris@example.com", "Iris", 850, 40],
            [10, "Jack Ryan", "jack@example.com", "Jack", 800, 35],
        ]
        self.populate_table(self.weekly_table, self.weekly_data)
        layout.addWidget(self.weekly_table)

        # All-Time Leaderboard with existing data
        all_time_label = QLabel("All-Time Leaderboard 🏆")
        layout.addWidget(all_time_label)
        
        self.rankings_table = self.create_leaderboard_table()
        # Keep your existing all_time_data
        self.populate_table(self.rankings_table, self.all_time_data)
        layout.addWidget(self.rankings_table)

        return rankings_widget

    def filter_tables(self, search_text):
        """
        Enhanced filter function for both tables
        """
        search_text = search_text.lower().strip()
        
        # Helper function to check if row matches search criteria
        def matches_search(row_data):
            # Check full name (index 1)
            if search_text in str(row_data[1]).lower():
                return True
            # Check email (index 2)
            if search_text in str(row_data[2]).lower():
                return True
            # Check nickname (index 3)
            if search_text in str(row_data[3]).lower():
                return True
            return False

        # Filter weekly table
        if hasattr(self, 'weekly_table') and hasattr(self, 'weekly_data'):
            filtered_weekly = [row for row in self.weekly_data if matches_search(row)]
            self.update_table_data(self.weekly_table, filtered_weekly)

        # Filter all-time table
        if hasattr(self, 'rankings_table') and hasattr(self, 'all_time_data'):
            filtered_alltime = [row for row in self.all_time_data if matches_search(row)]
            self.update_table_data(self.rankings_table, filtered_alltime)

    def update_table_data(self, table, filtered_data):
        """
        Update table with filtered data while maintaining styling
        """
        table.setRowCount(len(filtered_data))
        
        for row_idx, row_data in enumerate(filtered_data):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                
                # Apply column-specific styling
                if col_idx == 0:  # Position
                    item.setForeground(QColor("#666666"))
                    item.setFont(QFont("Arial", 10, QFont.Bold))
                elif col_idx == 4:  # Score
                    item.setForeground(QColor("#007AFF"))
                    item.setFont(QFont("Arial", 10, QFont.Bold))
                    # Right-align score
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                elif col_idx == 5:  # Molecules
                    item.setForeground(QColor("#28A745"))
                    item.setFont(QFont("Arial", 10))
                    # Right-align molecules
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                elif col_idx == 1:  # Full Name
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                elif col_idx == 2:  # Email
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    item.setForeground(QColor("#666666"))
                
                # Make items non-editable
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row_idx, col_idx, item)
            
            # Set row height
            table.setRowHeight(row_idx, 40)

        # Adjust column widths after updating data
        self.adjust_table_columns(table)

    def adjust_table_columns(self, table):
        """
        Adjust column widths for optimal display
        """
        header = table.horizontalHeader()
        
        # Set specific column widths and behaviors
        column_configs = {
            0: ("Position", 80, QHeaderView.Fixed),
            1: ("Full Name", 200, QHeaderView.Stretch),
            2: ("Email", 250, QHeaderView.Stretch),
            3: ("Nickname", 120, QHeaderView.Fixed),
            4: ("Score", 100, QHeaderView.Fixed),
            5: ("Molecules", 100, QHeaderView.Fixed)
        }
        
        for col, (name, width, resize_mode) in column_configs.items():
            header.setSectionResizeMode(col, resize_mode)
            if resize_mode == QHeaderView.Fixed:
                table.setColumnWidth(col, width)

    def create_leaderboard_table(self):
        """
        Create a table with proper configuration
        """
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["Position", "Full Name", "Email", "Nickname", "Score", "Molecules"])
        
        # Table properties
        table.setShowGrid(False)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setHighlightSections(False)
        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #F8F8F8;
                border: none;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #EEE;
            }
            QTableWidget::item:selected {
                background-color: #F0F7FF;
                color: black;
            }
        """)
        
        # Initialize column adjustments
        self.adjust_table_columns(table)
        
        return table

    def populate_table(self, table, data):
        """
        Populate table with data and maintain consistent styling
        """
        table.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                
                # Style specific columns
                if col_idx == 0:  # Position column
                    item.setForeground(QColor("#666666"))
                    item.setFont(QFont("Arial", 10, QFont.Bold))
                elif col_idx == 4:  # Score column
                    item.setForeground(QColor("#007AFF"))
                    item.setFont(QFont("Arial", 10, QFont.Bold))
                elif col_idx == 5:  # Molecules column
                    item.setForeground(QColor("#28A745"))
                    item.setFont(QFont("Arial", 10))
                
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row_idx, col_idx, item)
            
            # Set row height
            table.setRowHeight(row_idx, 40)

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

    def filter_table(self):
        """
        Filter both tables based on search input
        """
        search_text = self.search_input.text().lower()
        
        # Filter Weekly Table
        filtered_weekly_data = []
        for row in self.weekly_data:
            if any(search_text in str(item).lower() for item in row[1:4]):  # Search in name, email, and nickname
                filtered_weekly_data.append(row)
        
        # Filter All-Time Table
        filtered_all_time_data = []
        for row in self.all_time_data:
            if any(search_text in str(item).lower() for item in row[1:4]):  # Search in name, email, and nickname
                filtered_all_time_data.append(row)
        
        # Update both tables
        self.populate_table(self.weekly_table, filtered_weekly_data)
        self.populate_table(self.rankings_table, filtered_all_time_data)

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
