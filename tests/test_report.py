from logscope.report import render_markdown, render_text


def test_timeline_text_reports_no_errors() -> None:
    assert render_text("timeline", {"buckets": []}) == "No errors found"


def test_summary_markdown_contains_level_table() -> None:
    rendered = render_markdown(
        "summary",
        {
            "file": "app.log",
            "total_lines": 1,
            "well_formed": 1,
            "malformed": 0,
            "levels": {"INFO": 1},
            "top_errors": [],
            "first_timestamp": "2026-10-01T09:00:00",
            "last_timestamp": "2026-10-01T09:00:00",
        },
    )

    assert "| INFO | 1 |" in rendered
