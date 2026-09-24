def test_app_exists():
    from pathlib import Path
    assert Path("app.py").exists()
