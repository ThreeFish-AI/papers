"""Root conftest.py for pytest configuration."""

pytest_plugins = []


# Custom markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "unit: Mark test as a unit test")
    config.addinivalue_line("markers", "integration: Mark test as an integration test")
    config.addinivalue_line("markers", "e2e: Mark test as an end-to-end test")
    config.addinivalue_line("markers", "performance: Mark test as a performance test")
    config.addinivalue_line("markers", "websocket: Mark test as requiring WebSocket")
    config.addinivalue_line("markers", "slow: Mark test as slow running")
