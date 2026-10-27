from __future__ import annotations

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers", "real_samples: needs uncommitted real samples in tests/fixtures"
    )
