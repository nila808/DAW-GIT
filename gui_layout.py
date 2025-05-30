# gui_layout.py
from pages_controller import PagesController
from snapshot_browser_page import SnapshotBrowserPage
from branch_manager_page import BranchManagerPage
from commit_page import CommitPage
from project_setup_page import ProjectSetupPage

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QCheckBox, QTextEdit, QSpacerItem, QSizePolicy, 
    QTableWidgetItem
)
from PyQt6.QtCore import Qt, QTimer

def build_main_ui(app):
    main_widget = QWidget()
    main_layout = QVBoxLayout(main_widget)

    app.pages = PagesController()

    # app.snapshot_page = SnapshotBrowserPage()
    app.snapshot_page = SnapshotBrowserPage(app)
    app.pages.add_page("snapshots", app.snapshot_page)

    app.branch_page = BranchManagerPage(app)
    app.pages.add_page("branches", app.branch_page)

    # app.commit_page = CommitPage(app)
    app.commit_page = CommitPage(app, parent=app)
    app.pages.add_page("commit", app.commit_page)

    app.setup_page = ProjectSetupPage(app)
    app.pages.add_page("setup", app.setup_page)

    app.pages.switch_to("snapshots")  # ✅ safe now — snapshots page already added

    app.load_commit_history()

    app.history_table = app.snapshot_page.commit_table

    app.status_label = app.snapshot_page.status_label
    app.status_label.setText("Ready")
    app.status_label.setObjectName("status_label")
    main_layout.addWidget(app.status_label)

    # 🎧 Add snapshot/editing mode display
    app.snapshot_mode_label = QLabel("🎧 Snapshot mode: unknown")
    app.snapshot_mode_label.setObjectName("snapshot_mode_label")
    main_layout.addWidget(app.snapshot_mode_label)

    # 📢 Persistent session/editing state label
    app.status_mode_label = QLabel("🎚️ Status: unknown")
    app.status_mode_label.setObjectName("status_mode_label")
    main_layout.addWidget(app.status_mode_label)

    main_layout.addWidget(app.pages)   

    main_layout.addWidget(build_commit_info_display(app))
    main_layout.addLayout(build_bottom_controls(app))

    # Navigation buttons
    nav_layout = QHBoxLayout()
    app.goto_branch_btn = QPushButton("🔀 Branch Manager")
    app.goto_snapshots_btn = QPushButton("🎧 Snapshot Browser")
    app.goto_commit_btn = QPushButton("📥 Commit Page")

    app.goto_branch_btn.clicked.connect(lambda: app.pages.switch_to("branches"))
    app.goto_snapshots_btn.clicked.connect(lambda: app.pages.switch_to("snapshots"))
    app.goto_commit_btn.clicked.connect(lambda: app.pages.switch_to("commit"))

    app.goto_setup_btn = QPushButton("🛠 Project Setup")
    app.goto_setup_btn.clicked.connect(lambda: app.pages.switch_to("setup"))
    nav_layout.addWidget(app.goto_setup_btn)

    nav_layout.addWidget(app.goto_branch_btn)
    nav_layout.addWidget(app.goto_snapshots_btn)
    nav_layout.addWidget(app.goto_commit_btn)
    main_layout.addLayout(nav_layout)

    # Sync status label pointer
    app.status_label = app.snapshot_page.status_label

    QTimer.singleShot(500, lambda: app.branch_page.populate_branches())
    app.update_role_buttons()
    app.safe_single_shot(250, app.load_commit_history, parent=app)

    container = QWidget()
    container.setLayout(main_layout)
    app.setCentralWidget(container)
    return main_widget


def build_project_controls(app):
    layout = QVBoxLayout()

    # app.unsaved_indicator = QLabel("● Uncommitted Changes")
    # app.unsaved_indicator.setObjectName("unsaved_indicator")
    # app.unsaved_indicator.setVisible(False)
    # app.unsaved_flash = False
    # app.unsaved_timer = app.startTimer(800)
    # layout.addWidget(app.unsaved_indicator)

    # app.project_label = QLabel()
    # app.project_label.setObjectName("project_label")
    # app.project_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.LinksAccessibleByMouse)
    # app.project_label.setOpenExternalLinks(True)
    # app.project_label.setToolTip("Click to open in Finder")
    # app.project_label.setWordWrap(True)
    # layout.addWidget(app.project_label)

    app.path_label = QLabel(str(app.project_path))
    app.path_label.setVisible(False)
    layout.addWidget(app.path_label)
    app.update_project_label()

    app.setup_label = QLabel("🎚️ Step 1: Choose your Ableton or Logic project folder")
    app.setup_label.setObjectName("setup_label")
    layout.addWidget(app.setup_label)

    app.setup_btn = QPushButton("Start Tracking")
    app.setup_btn.setToolTip("Start tracking the folder where your current Ableton or Logic project is saved.")
    app.setup_btn.clicked.connect(app.run_setup)
    layout.addWidget(app.setup_btn)

    app.load_branch_btn = QPushButton("🎹 Load Alternate Session")
    app.load_branch_btn.setToolTip("Switch to a different creative version of this track")
    app.load_branch_btn.clicked.connect(app.show_branch_selector)
    layout.addWidget(app.load_branch_btn)

    controls_layout = QHBoxLayout()
    app.change_folder_btn = QPushButton("Change Project Folder")
    app.change_folder_btn.clicked.connect(app.change_project_folder)

    app.clear_project_btn = QPushButton("Clear Saved Project")
    app.clear_project_btn.clicked.connect(app.clear_saved_project)

    app.export_btn = QPushButton("Export Snapshot")
    app.export_btn.clicked.connect(app.export_snapshot)

    app.import_btn = QPushButton("Import Snapshot")
    app.import_btn.clicked.connect(app.import_snapshot)

    app.restore_backup_btn = QPushButton("Restore Last Backup")
    app.restore_backup_btn.clicked.connect(app.restore_last_backup)

    for btn in [app.change_folder_btn, app.clear_project_btn, app.export_btn, app.import_btn, app.restore_backup_btn]:
        controls_layout.addWidget(btn)

    layout.addLayout(controls_layout)
    return layout


def build_commit_controls(app):
    layout = QVBoxLayout()
    layout.addWidget(QLabel("Snapshot Notes:"))

    buttons = QHBoxLayout()

    app.auto_save_toggle = QCheckBox("🎹 Auto-Save Snapshots")
    app.auto_save_toggle.setToolTip("Enable to auto-commit when changes are detected")
    app.auto_save_toggle.stateChanged.connect(app.handle_auto_save_toggle)
    buttons.addWidget(app.auto_save_toggle)
    layout.addLayout(buttons)

    group = QGroupBox("Snapshot Controls")
    group.setLayout(layout)
    group.setProperty("debug", True)
    group_layout = QVBoxLayout()
    group_layout.addWidget(group)
    return group_layout


def build_checkout_controls(app):
    layout = QHBoxLayout()
 
    app.switch_branch_btn = QPushButton("🔀 Switch Version Line")
    app.switch_branch_btn.setToolTip("Switch to another creative path or saved version")
    app.switch_branch_btn.clicked.connect(app.switch_branch)

    for btn in [app.switch_branch_btn]:  # Only this remains global
        layout.addWidget(btn)

    return layout


def build_commit_info_display(app):
    app.detached_warning_label = QLabel("")
    app.detached_warning_label.setWordWrap(True)
    app.detached_warning_label.hide()

    app.version_line_label = QLabel("🎚️ No active version line")
    app.branch_label = QLabel("Session branch: unknown • Current take: unknown")
    app.commit_label = QLabel("🎶 Commit: unknown")

    wrapper = QWidget()
    layout = QVBoxLayout()
    layout.addWidget(app.detached_warning_label)
    layout.addWidget(app.version_line_label)
    layout.addWidget(app.branch_label)
    layout.addWidget(app.commit_label)
    wrapper.setLayout(layout)
    return wrapper


def build_bottom_controls(app):
    layout = QVBoxLayout()

    app.unsaved_indicator = QLabel("● Uncommitted Changes")
    app.unsaved_indicator.setObjectName("unsaved_indicator")
    app.unsaved_indicator.setVisible(False)
    app.unsaved_flash = False
    app.unsaved_timer = app.startTimer(800)
    layout.addWidget(app.unsaved_indicator)

    app.open_in_daw_btn = QPushButton("🎧 Open This Version in DAW")
    app.open_in_daw_btn.setVisible(False)
    app.open_in_daw_btn.clicked.connect(app.open_latest_daw_project)
    layout.addWidget(app.open_in_daw_btn)

    app.show_tooltips_checkbox = QCheckBox("Show Tooltips")
    app.show_tooltips_checkbox.setChecked(True)
    app.show_tooltips_checkbox.stateChanged.connect(app.toggle_tooltips)
    layout.addWidget(app.show_tooltips_checkbox)

    return layout
