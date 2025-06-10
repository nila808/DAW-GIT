from PyQt6.QtWidgets import QStackedWidget, QWidget
from ui_strings import DEBUG_PAGE_SWITCH_FAILED

class PagesController(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pages = {}


    def add_page(self, key: str, widget: QWidget):
        self.pages[key] = widget
        self.addWidget(widget)


    def switch_to(self, key: str):
        widget = self.pages.get(key)
        if widget:
            self.setCurrentWidget(widget)
        else:
            print(f"[debug] {DEBUG_PAGE_SWITCH_FAILED.format(key=key)}")


    def switch_to(self, key: str):
        widget = self.pages.get(key)
        if widget:
            self.setCurrentWidget(widget)
        else:
            print(f"[debug] Tried to switch to unknown page key: '{key}'")