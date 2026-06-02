from pathlib import Path


def test_required_application_files_exist():
    root = Path(__file__).resolve().parents[1]
    assert (root / "app.py").exists()
    assert (root / "requirements.txt").exists()
    assert (root / "utils" / "retriever.py").exists()


def test_scheme_data_is_available():
    root = Path(__file__).resolve().parents[1]
    scheme_files = list((root / "data").glob("*.txt"))
    assert len(scheme_files) >= 50
