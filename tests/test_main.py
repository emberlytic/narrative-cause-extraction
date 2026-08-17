from pathlib import Path

from main import load_reports

SAMPLE_CSV = Path(__file__).parent.parent / "data" / "sample_reports.csv"


def test_load_reports_reads_all_rows():
    reports = load_reports(SAMPLE_CSV)
    assert len(reports) == 18


def test_load_reports_has_expected_columns():
    reports = load_reports(SAMPLE_CSV)
    assert set(reports[0].keys()) == {"report_id", "report_text"}


def test_load_reports_preserves_row_order():
    reports = load_reports(SAMPLE_CSV)
    assert reports[0]["report_id"] == "RPT-001"
