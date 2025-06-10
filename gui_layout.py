from ui_strings import SNAPSHOT_MODE_UNKNOWN
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
from ui_strings import (
    BTN_CHANGE_PROJECT_FOLDER,
    BTN_CLEAR_SAVED_PROJECT,
    BTN_EXPORT_SNAPSHOT,
    BTN_IMPORT_SNAPSHOT,
    BTN_LOAD_ALT_SESSION,
    BTN_OPEN_VERSION_IN_DAW,
    BTN_RESTORE_BACKUP,
    BTN_START_TRACKING,
    BTN_SWITCH_VERSION_LINE,
    CURRENT_BRANCH_UNKNOWN,
    CURRENT_COMMIT_UNKNOWN,
    STATUS_READY,
    TAB_BRANCH_MANAGER,
    TAB_COMMIT_PAGE,
    TAB_PROJECT_SETUP,
    TAB_SNAPSHOT_BROWSER,
    TOOLTIP_ENABLE_AUTOCOMMIT,
    TOOLTIP_OPEN_IN_FINDER,
    TOOLTIP_START_TRACKING_FOLDER,
    TOOLTIP_SWITCH_ALT_VERSION,
    TOOLTIP_SWITCH_BRANCH, 
    STATUS_READY,
    STATUS_UNKNOWN
)


def build_main_ui(app):
    main_widget = QWidget()
    main_layout = QVBoxLayout(main_widget)

    app.pages = PagesController()

    app.snapshot_page = SnapshotBrowserPage(app)
    app.pages.add_page("snapshots", app.snapshot_page)

    app.branch_page = BranchManagerPage(app)
    app.pages.add_page("branches", app.branch_page)

    app.commit_page = CommitPage(app, parent=app)
    app.pages.add_page("commit", app.commit_page)

    app.setup_page = ProjectSetupPage(app)
    app.pages.add_page("setup", app.setup_page)

    if app.project_path:
        app.pages.switch_to("snapshots")
    else:
        app.pages.switch_to("setup")

    app.load_commit_history()
    app.history_table = app.snapshot_page.commit_table

    app.status_label = app.snapshot_page.status_label
    app.status_label.setText(STATUS_READY)
    app.status_label.setObjectName("status_label")
    main_layout.addWidget(app.status_label)

    # 🎧 Snapshot Status Label (e.g. Detached / Editing Info)
    app.snapshot_status = QLabel(STATUS_UNKNOWN)
    app.snapshot_status.setObjectName("snapshot_status")
    main_layout.addWidget(app.snapshot_status)

    # app.snapshot_mode_label = QLabel(SNAPSHOT_MODE_UNKNOWN)
    # app.snapshot_mode_label.setObjectName("snapshot_mode_label")
    # main_layout.addWidget(app.snapshot_mode_label)

    app.status_mode_label = QLabel(STATUS_UNKNOWN)
    app.status_mode_label.setObjectName("status_mode_label")
    main_layout.addWidget(app.status_mode_label)

    main_layout.addWidget(app.pages)
    main_layout.addWidget(build_commit_info_display(app))
    main_layout.addLayout(build_bottom_controls(app))

    nav_layout = QHBoxLayout()
    app.goto_branch_btn = QPushButton(TAB_BRANCH_MANAGER)
    app.goto_snapshots_btn = QPushButton(TAB_SNAPSHOT_BROWSER)
    app.goto_commit_btn = QPushButton(TAB_COMMIT_PAGE)

    app.goto_branch_btn.clicked.connect(lambda: app.pages.switch_to("branches"))
    app.goto_snapshots_btn.clicked.connect(lambda: app.pages.switch_to("snapshots"))
    app.goto_commit_btn.clicked.connect(lambda: app.pages.switch_to("commit"))

    app.goto_setup_btn = QPushButton(TAB_PROJECT_SETUP)
    app.goto_setup_btn.clicked.connect(lambda: app.pages.switch_to("setup"))
    nav_layout.addWidget(app.goto_setup_btn)
    nav_layout.addWidget(app.goto_branch_btn)
    nav_layout.addWidget(app.goto_snapshots_btn)
    nav_layout.addWidget(app.goto_commit_btn)
    main_layout.addLayout(nav_layout)

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

    app.path_label = QLabel(str(app.project_path))
    app.path_label.setVisible(False)
    layout.addWidget(app.path_label)
    app.update_project_label()

    app.setup_label = QLabel(TOOLTIP_START_TRACKING_FOLDER)
    app.setup_label.setObjectName("setup_label")
    layout.addWidget(app.setup_label)

    app.setup_btn = QPushButton(BTN_START_TRACKING)
    app.setup_btn.setToolTip(TOOLTIP_START_TRACKING_FOLDER)
    app.setup_btn.clicked.connect(app.run_setup)
    layout.addWidget(app.setup_btn)

    app.load_branch_btn = QPushButton(BTN_LOAD_ALT_SESSION)
    app.load_branch_btn.setToolTip(TOOLTIP_SWITCH_ALT_VERSION)
    app.load_branch_btn.clicked.connect(app.show_branch_selector)
    layout.addWidget(app.load_branch_btn)

    controls_layout = QHBoxLayout()
    app.change_folder_btn = QPushButton(BTN_CHANGE_PROJECT_FOLDER)
    app.change_folder_btn.clicked.connect(app.change_project_folder)

    app.clear_project_btn = QPushButton(BTN_CLEAR_SAVED_PROJECT)
    app.clear_project_btn.clicked.connect(app.clear_saved_project)

    app.export_btn = QPushButton(BTN_EXPORT_SNAPSHOT)
    app.export_btn.clicked.connect(app.export_snapshot)

    app.import_btn = QPushButton(BTN_IMPORT_SNAPSHOT)
    app.import_btn.clicked.connect(app.import_snapshot)

    app.restore_backup_btn = QPushButton(BTN_RESTORE_BACKUP)
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
    app.auto_save_toggle.setToolTip(TOOLTIP_ENABLE_AUTOCOMMIT)
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
    app.switch_branch_btn = QPushButton(BTN_SWITCH_VERSION_LINE)
    app.switch_branch_btn.setToolTip(TOOLTIP_SWITCH_BRANCH)
    app.switch_branch_btn.clicked.connect(app.switch_branch)

    for btn in [app.switch_branch_btn]:
        layout.addWidget(btn)

    return layout

def build_commit_info_display(app):
    app.detached_warning_label = QLabel("")
    app.detached_warning_label.setWordWrap(True)
    app.detached_warning_label.hide()

    app.version_line_label = QLabel("🎵 Editing: Not set")
    app.branch_label = QLabel(CURRENT_BRANCH_UNKNOWN)   # From ui_strings.py
    app.commit_label = QLabel(CURRENT_COMMIT_UNKNOWN)   # From ui_strings.py

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

    app.open_in_daw_btn = QPushButton(BTN_OPEN_VERSION_IN_DAW)
    app.open_in_daw_btn.setVisible(False)
    app.open_in_daw_btn.clicked.connect(app.open_latest_daw_project)
    layout.addWidget(app.open_in_daw_btn)

    app.show_tooltips_checkbox = QCheckBox("Show Tooltips")
    app.show_tooltips_checkbox.setChecked(True)
    app.show_tooltips_checkbox.stateChanged.connect(app.toggle_tooltips)
    layout.addWidget(app.show_tooltips_checkbox)

    return layout
