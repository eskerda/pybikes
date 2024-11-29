def pytest_configure(config):
    config.addinivalue_line(
        "markers", "update: mark a test that uses network and might fail"
    )
    config.addinivalue_line(
        "markers", "changes: mark a test as a gen test about changes"
    )
