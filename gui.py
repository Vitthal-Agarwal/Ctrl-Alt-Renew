import sys
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
)
from PyQt5.QtCore import Qt, QSize, QRect
from PyQt5.QtGui import (
    QFont,
    QColor,
    QPalette,
    QIcon,
    QPixmap,
    QPainter,
    QBrush,
    QPen,
)


class ModernMolecularGUI(QMainWindow):
    def __init__(self, future_df, computation_manager):
        super().__init__()
        self.future_df = future_df
        self.computation_manager = computation_manager
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Molecular Universe")
        self.showFullScreen()  # Make the application full screen
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: white;
            }
            QLabel {
                color: #333;
            }
            QPushButton {
                border: none;
                padding: 8px;
                border-radius: 4px;
                color: white;
            }
            QPushButton:hover {
                background-color: #404040;
            }
            QRadioButton {
                font-size: 16px;
            }
            QCheckBox::indicator {
                width: 40px;
                height: 20px;
            }
            QCheckBox::indicator:checked {
                background-color: #7CD332;
                border-radius: 10px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #ccc;
                border-radius: 10px;
            }
        """
        )

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Add sidebar
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)

        # Add content area with stacked widget for navigation
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget, 1)  # 1 is the stretch factor

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
                padding: 20px;     /* Sidebar padding */
            }
            QLabel {
                color: white;
            }
            QPushButton {
                text-align: left;
                padding: 12px;          /* Button padding */
                margin: 4px 0;          /* Button margin */
                color: white;
                border-radius: 8px;
                font-size: 16px;        /* Button font size */
                font-weight: 500;       /* Button font weight */
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
        layout.setSpacing(24)  # Spacing between sidebar elements
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
        profile_layout.setSpacing(8)  # Spacing between profile elements
        profile_layout.setAlignment(Qt.AlignCenter)

        # Profile Picture
        profile_pic_label = QLabel()
        profile_pic_label.setFixedSize(
            150, 200
        )  # Adjusted to 150x200 for better fitting
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
        profile_layout.addWidget(profile_pic_label, alignment=Qt.AlignCenter)
        profile_layout.addWidget(user_name_label, alignment=Qt.AlignCenter)
        profile_layout.addWidget(edit_button, alignment=Qt.AlignCenter)
        layout.addWidget(profile_widget)

        # Navigation buttons
        # Updated button labels with emojis
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
        content_widget.setStyleSheet(
            """
            QWidget {
                background-color: #F5F5F5;
            }
        """
        )

        layout = QVBoxLayout(content_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(
            30, 30, 30, 30
        )  # Increased margins for better spacing

        # Calculation Workflow card
        workflow_card = self.create_workflow_card()
        layout.addWidget(workflow_card)

        # Current calculation card
        current_calc_card = self.create_current_calculation_card()
        layout.addWidget(current_calc_card)

        # Previous calculations card
        prev_calc_card = self.create_previous_calculations_card()
        layout.addWidget(prev_calc_card)

        return content_widget

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
        future_schedule_widget = QWidget()
        future_schedule_widget.setStyleSheet(
            """
            QWidget {
                background-color: #F5F5F5;
            }
        """
        )
        layout = QVBoxLayout(future_schedule_widget)
        layout.setAlignment(Qt.AlignCenter)

        label = QLabel("Future Schedule Page - Coming Soon!")
        label.setStyleSheet("font-size: 24px; color: #666;")
        layout.addWidget(label)

        return future_schedule_widget

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

        # Options: Auto and Manual
        options_widget = QWidget()
        options_layout = QHBoxLayout(options_widget)
        options_layout.setAlignment(Qt.AlignCenter)
        options_layout.setSpacing(15)  # Spacing between options

        # Auto Option
        auto_widget = QWidget()
        auto_layout = QVBoxLayout(auto_widget)
        auto_layout.setAlignment(Qt.AlignCenter)

        auto_radio = QRadioButton("Auto")
        auto_radio.setStyleSheet("color: white; font-size: 16px;")
        auto_radio.setChecked(True)  # Default selection

        # Description for Auto
        auto_desc = QLabel(
            "Automated response generated by the simulation and scheduling."
        )
        auto_desc.setStyleSheet("color: #ccc; font-size: 14px; text-align: center;")
        auto_desc.setWordWrap(True)

        auto_layout.addWidget(auto_radio)
        auto_layout.addWidget(auto_desc)

        # Manual Option
        manual_widget = QWidget()
        manual_layout = QVBoxLayout(manual_widget)
        manual_layout.setAlignment(Qt.AlignCenter)

        manual_radio = QRadioButton("Manual")
        manual_radio.setStyleSheet("color: white; font-size: 16px;")

        # Description for Manual
        manual_desc = QLabel(
            "Control the workflow manually with start and stop options."
        )
        manual_desc.setStyleSheet("color: #ccc; font-size: 14px; text-align: center;")
        manual_desc.setWordWrap(True)

        manual_layout.addWidget(manual_radio)
        manual_layout.addWidget(manual_desc)

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

    # Set dark theme palette
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
    start_app()  # For testing purposes only
