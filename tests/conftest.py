def pytest_configure(config):
    config.addinivalue_line(
        "markers", "update: mark a test that uses network and might fail"
    )
