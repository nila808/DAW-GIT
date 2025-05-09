import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_repo():
    with patch("daw_git_gui.Repo") as mock:
        yield mock