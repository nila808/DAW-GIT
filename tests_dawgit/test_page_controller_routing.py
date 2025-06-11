import pytest
from pages_controller import PagesController
from PyQt6.QtWidgets import QLabel

def test_pages_controller_routing():
    pages = PagesController()

    widget1 = QLabel("Page 1")
    widget2 = QLabel("Page 2")

    pages.add_page("one", widget1)
    pages.add_page("two", widget2)

    pages.switch_to("one")
    assert pages.currentWidget().text() == "Page 1"

    pages.switch_to("two")
    assert pages.currentWidget().text() == "Page 2"

    # Test fallback (invalid key)
    pages.switch_to("unknown")  # Should not raise
