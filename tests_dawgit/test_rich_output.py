import ui_strings
from rich import print

from ui_strings import (
    RICH_RED_MSG, 
    RICH_GREEN_CHECK_MSG,
    RICH_YELLOW_MSG
)

def test_colored_output():
    print(RICH_RED_MSG)
    print(RICH_GREEN_CHECK_MSG)
    print(RICH_YELLOW_MSG)