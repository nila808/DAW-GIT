from PyQt6.QtWidgets import QStackedWidget, QWidget

class PagesController(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pages = {}

    def add_page(self, key: str, widget: QWidget):
        self.pages[key] = widget
        self.addWidget(widget)

    def switch_to(self, key: str):
        if key in self.pages:
            self.setCurrentWidget(self.pages[key])
