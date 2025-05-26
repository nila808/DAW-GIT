# gui_layout.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QCheckBox, QTextEdit, QSpacerItem, QSizePolicy, 
    QTableWidgetItem
)
from PyQt6.QtCore import Qt, QTimer

def build_main_ui(app):
    main_widget = QWidget()
    main_layout = QVBoxLayout(main_widget)

    from pages_controller import PagesController
    from snapshot_browser_page import SnapshotBrowserPage
    from branch_manager_page import BranchManagerPage

    app.pages = PagesController()
    app.snapshot_page = SnapshotBrowserPage()
    app.pages.add_page("snapshots", app.snapshot_page)
    app.load_commit_history()

    app.history_table = app.snapshot_page.commit_table
    app.status_label = app.snapshot_page.status_label
    app.status_label.setText("Ready")
    app.status_label.setObjectName("status_label")
    main_layout.addWidget(app.status_label)

    app.branch_page = BranchManagerPage(app)
    app.pages.add_page("branches", app.branch_page)

    app.pages.switch_to("snapshots")
    main_layout.addWidget(app.pages)

    main_layout.addLayout(build_project_controls(app))
    main_layout.addLayout(build_commit_controls(app))
    main_layout.addLayout(build_checkout_controls(app))
    main_layout.addWidget(build_commit_info_display(app))
    main_layout.addLayout(build_bottom_controls(app))

    # Navigation buttons
    nav_layout = QHBoxLayout()
    app.goto_branch_btn = QPushButton("🔀 Branch Manager")
    app.goto_snapshots_btn = QPushButton("🎧 Snapshot Browser")
    app.goto_branch_btn.clicked.connect(lambda: app.pages.switch_to("branches"))
    app.goto_snapshots_btn.clicked.connect(lambda: app.pages.switch_to("snapshots"))
    nav_layout.addWidget(app.goto_branch_btn)
    nav_layout.addWidget(app.goto_snapshots_btn)
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

    app.unsaved_indicator = QLabel("● Uncommitted Changes")
    app.unsaved_indicator.setObjectName("unsaved_indicator")
    app.unsaved_indicator.setVisible(False)
    app.unsaved_flash = False
    app.unsaved_timer = app.startTimer(800)
    layout.addWidget(app.unsaved_indicator)

    app.project_label = QLabel()
    app.project_label.setObjectName("project_label")
    app.project_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.LinksAccessibleByMouse)
    app.project_label.setOpenExternalLinks(True)
    app.project_label.setToolTip("Click to open in Finder")
    app.project_label.setWordWrap(True)
    layout.addWidget(app.project_label)

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
    app.commit_btn = QPushButton("💾 Save Snapshot")
    app.commit_btn.setMinimumHeight(36)
    app.commit_btn.setToolTip("Save the current version of your DAW project")
    app.commit_btn.clicked.connect(lambda: app.commit_changes(
        app.snapshot_page.commit_message_input.toPlainText().strip() or None
    ))
    buttons.addWidget(app.commit_btn)

    app.auto_save_toggle = QCheckBox("🎹 Auto-Save Snapshots")
    app.auto_save_toggle.setToolTip("Enable to auto-commit when changes are detected")
    app.auto_save_toggle.stateChanged.connect(app.handle_auto_save_toggle)
    buttons.addWidget(app.auto_save_toggle)
    layout.addLayout(buttons)

    vc_layout = QHBoxLayout()
    app.new_branch_btn = QPushButton("🎼 Start New Version Line")
    app.new_branch_btn.setToolTip("Start a new creative branch from here")
    app.new_branch_btn.clicked.connect(app.start_new_version_line)
    vc_layout.addWidget(app.new_branch_btn)

    app.return_to_latest_btn = QPushButton("🎯 Return to Latest")
    app.return_to_latest_btn.setToolTip("Return to the most recent version")
    app.return_to_latest_btn.clicked.connect(app.return_to_latest_clicked)
    vc_layout.addWidget(app.return_to_latest_btn)
    layout.addLayout(vc_layout)

    role_layout = QHBoxLayout()
    app.btn_set_version_main = QPushButton("🌟 Mark as Final Mix")
    app.btn_set_version_main.setToolTip("Assign this snapshot as your Main Mix")
    app.btn_set_version_main.clicked.connect(app.tag_main_mix)
    role_layout.addWidget(app.btn_set_version_main)

    app.btn_set_version_creative = QPushButton("🎨 Mark as Creative Version")
    app.btn_set_version_creative.setToolTip("Assign this snapshot as a creative alternative")
    app.btn_set_version_creative.clicked.connect(app.tag_creative_take)
    role_layout.addWidget(app.btn_set_version_creative)

    app.btn_set_version_alt = QPushButton("🎚️ Mark as Alternate Mix")
    app.btn_set_version_alt.setToolTip("Assign this snapshot as an alternate mixdown or stem")
    app.btn_set_version_alt.clicked.connect(app.tag_alt_mix)
    role_layout.addWidget(app.btn_set_version_alt)

    app.btn_custom_tag = QPushButton("✏️ Add Custom Tag")
    app.btn_custom_tag.setToolTip("Add your own label to this snapshot")
    app.btn_custom_tag.clicked.connect(app.tag_custom_label)
    role_layout.addWidget(app.btn_custom_tag)
    layout.addLayout(role_layout)

    group = QGroupBox("Snapshot Controls")
    group.setLayout(layout)
    group.setProperty("debug", True)
    group_layout = QVBoxLayout()
    group_layout.addWidget(group)
    return group_layout


def build_checkout_controls(app):
    layout = QHBoxLayout()
    app.load_snapshot_btn = QPushButton("🎧 Load This Snapshot")
    app.load_snapshot_btn.setToolTip("Load this version of your project safely")
    app.load_snapshot_btn.clicked.connect(app.load_snapshot_clicked)

    app.where_am_i_btn = QPushButton("📍 Where Am I?")
    app.where_am_i_btn.setToolTip("Show current snapshot version")
    app.where_am_i_btn.clicked.connect(app.show_current_commit)

    app.switch_branch_btn = QPushButton("🔀 Switch Version Line")
    app.switch_branch_btn.setToolTip("Switch to another creative path or saved version")
    app.switch_branch_btn.clicked.connect(app.switch_branch)

    for btn in [app.load_snapshot_btn, app.where_am_i_btn, app.switch_branch_btn]:
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
    app.remote_checkbox = QCheckBox("Push to remote after snapshot")
    layout.addWidget(app.remote_checkbox)

    app.connect_remote_btn = QPushButton("🔗 Connect to Remote Repo")
    app.connect_remote_btn.setToolTip("Set up a remote Git URL (e.g. GitHub)")
    app.connect_remote_btn.clicked.connect(app.connect_to_remote_repo)
    layout.addWidget(app.connect_remote_btn)

    app.open_in_daw_btn = QPushButton("🎧 Open This Version in DAW")
    app.open_in_daw_btn.setVisible(False)
    app.open_in_daw_btn.clicked.connect(app.open_latest_daw_project)
    layout.addWidget(app.open_in_daw_btn)

    app.show_tooltips_checkbox = QCheckBox("Show Tooltips")
    app.show_tooltips_checkbox.setChecked(True)
    app.show_tooltips_checkbox.stateChanged.connect(app.toggle_tooltips)
    layout.addWidget(app.show_tooltips_checkbox)

    return layout
