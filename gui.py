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
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon


class ModernMolecularGUI(QMainWindow):
    def __init__(self, future_df, computation_manager):
        super().__init__()
        self.future_df = future_df
        self.computation_manager = computation_manager
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Molecular Universe")
        self.setGeometry(100, 100, 1200, 800)
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

        # Add content area
        content = self.create_content_area()
        main_layout.addWidget(content, 1)  # 1 is the stretch factor

    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setStyleSheet(
            """
            QFrame {
                background-color: #1E1E1E;
                min-width: 250px;
                max-width: 250px;
                padding: 20px;
            }
            QLabel {
                color: white;
            }
            QPushButton {
                text-align: left;
                padding: 12px;
                margin: 4px;
                color: white;
                border-radius: 8px;
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
        layout.setSpacing(24)
        layout.setContentsMargins(0, 0, 0, 0)

        # Logo
        logo_label = QLabel("MolecularUniverse")
        logo_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: white; margin-bottom: 32px;"
        )
        layout.addWidget(logo_label)

        # Profile section
        profile_widget = QWidget()
        profile_layout = QVBoxLayout(profile_widget)
        profile_layout.setSpacing(8)

        profile_label = QLabel("Gabriel")
        profile_label.setStyleSheet("font-size: 16px; color: white;")

        edit_button = QPushButton("Edit")
        edit_button.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                border: 1px solid #444;
                padding: 6px;
                font-size: 12px;
            }
        """
        )

        profile_layout.addWidget(profile_label)
        profile_layout.addWidget(edit_button)
        layout.addWidget(profile_widget)

        # Navigation buttons
        calculate_btn = QPushButton("🔢  Calculate")
        calculate_btn.setObjectName("nav-active")
        rankings_btn = QPushButton("📊  Rankings")
        history_btn = QPushButton("📜  History")

        layout.addWidget(calculate_btn)
        layout.addWidget(rankings_btn)
        layout.addWidget(history_btn)

        # Add spacer
        layout.addStretch()

        # Logout and version
        logout_btn = QPushButton("⬅️  Logout")
        logout_btn.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                color: #888;
            }
        """
        )
        layout.addWidget(logout_btn)

        version_label = QLabel("Version 0.1.1.0 (RC)")
        version_label.setStyleSheet("color: #666; font-size: 12px; margin-top: 8px;")
        layout.addWidget(version_label)

        return sidebar

    def create_content_area(self):
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
        layout.setContentsMargins(20, 20, 20, 20)

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
        layout.setSpacing(16)

        # Title and subtitle
        title = QLabel("Calculation Workflow")
        title.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        subtitle = QLabel("The program will execute when your computer is idle")
        subtitle.setStyleSheet("color: #888;")

        # Control buttons
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setAlignment(Qt.AlignRight)

        stop_btn = QPushButton("Stop")
        stop_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #333;
                min-width: 80px;
                padding: 8px 16px;
            }
        """
        )

        start_btn = QPushButton("Start")
        start_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #7CD332;
                min-width: 80px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #6BC22B;
            }
        """
        )

        buttons_layout.addWidget(stop_btn)
        buttons_layout.addWidget(start_btn)

        # Status label
        status = QLabel("⏳ Waiting for idle state")
        status.setStyleSheet("color: #888;")

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(buttons_widget)
        layout.addWidget(status)

        return card

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
        title = QLabel("Current calculation")
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
                max-width: 120px;
            }
        """
        )
        cycle_layout = QVBoxLayout(cycle_frame)

        cycle_label = QLabel("Cycle")
        cycle_label.setStyleSheet("color: white;")
        cycle_num = QLabel("12")
        cycle_num.setStyleSheet("color: #7CD332; font-size: 24px; font-weight: bold;")

        cycle_layout.addWidget(cycle_label)
        cycle_layout.addWidget(cycle_num)
        info_grid.addWidget(cycle_frame)

        # Molecule info
        molecule_widget = QWidget()
        molecule_layout = QVBoxLayout(molecule_widget)

        molecule_title = QLabel("Molecule")
        molecule_title.setStyleSheet("color: #666;")
        molecule_name = QLabel("Ethane (C2H4)")
        molecule_name.setStyleSheet("font-size: 16px;")

        molecule_layout.addWidget(molecule_title)
        molecule_layout.addWidget(molecule_name)
        info_grid.addWidget(molecule_widget)

        # Characteristics
        chars_widget = QWidget()
        chars_layout = QVBoxLayout(chars_widget)

        chars_title = QLabel("Characteristics")
        chars_title.setStyleSheet("color: #666;")
        chars_value = QLabel("Alcohol")
        chars_value.setStyleSheet("font-size: 16px;")

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
        title = QLabel("Previous calculations")
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
            }
        """
        )

        # Set up table
        headers = ["Name", "Score", "Date", "CPU time", "Settings", ""]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

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
                }
            """
            )
            table.setCellWidget(row, len(headers) - 1, view_btn)

        layout.addWidget(table)
        return card


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
