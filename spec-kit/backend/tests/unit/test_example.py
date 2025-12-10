def test_example():
    """Example unit test to verify pytest is working"""
    assert 1 + 1 == 2


def test_settings_loaded():
    """Test that settings are properly loaded"""
    from src.config.settings import settings

    # Check that the app name is set correctly
    assert settings.app_name == "Textbook Generation API"

    # Check that environment defaults to local
    assert settings.is_local is True