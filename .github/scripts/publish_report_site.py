#!/usr/bin/env python3
"""Render one release report as a mobile-friendly, retained GitHub Pages page."""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

from markdown_it import MarkdownIt


REPORT_MARKER_RE = re.compile(r"(?m)^[ \t]*<!-- watch-release:[^\r\n]*-->[ \t]*(?:\r?\n|$)")
RUN_ID_RE = re.compile(r"\d+-\d+")
STYLE = """
:root { color-scheme: light; font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #18212f; background: #f4f6f8; }
* { box-sizing: border-box; }
body { margin: 0; line-height: 1.65; }
header { background: #fff; border-bottom: 1px solid #d8dee4; }
.container { width: min(100% - 2rem, 960px); margin: 0 auto; }
header .container { padding: 1rem 0; }
main { padding: 1.25rem 0 3rem; }
.card { background: #fff; border: 1px solid #d8dee4; border-radius: 12px; padding: clamp(1rem, 3vw, 2rem); overflow-wrap: anywhere; }
h1, h2, h3, h4 { line-height: 1.3; scroll-margin-top: 1rem; }
h1 { font-size: clamp(1.55rem, 5vw, 2rem); }
h2 { margin-top: 2rem; border-bottom: 1px solid #d8dee4; padding-bottom: .35rem; }
a { color: #0969da; }
img { max-width: 100%; height: auto; }
table { display: block; width: 100%; overflow-x: auto; border-collapse: collapse; }
th, td { border: 1px solid #d8dee4; padding: .45rem .65rem; text-align: left; }
pre { max-width: 100%; overflow-x: auto; padding: 1rem; background: #f6f8fa; border-radius: 8px; }
code { overflow-wrap: anywhere; }
.meta { color: #59636e; font-size: .92rem; }
.report-list { padding: 0; list-style: none; }
.report-list li { padding: .8rem 0; border-bottom: 1px solid #d8dee4; }
.report-list span { display: block; color: #59636e; font-size: .92rem; }
@media (max-width: 600px) { .container { width: min(100% - 1rem, 960px); } main { padding-top: .5rem; } .card { border-radius: 8px; } }
"""


def page(title: str, body: str) -> str:
    return (
        "<!doctype html>\n"
        '<html lang="zh-CN"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{html.escape(title)}</title><style>{STYLE}</style></head>\n"
        f"<body>{body}</body></html>\n"
    )


def render_report(markdown: str, report_id: str) -> tuple[str, dict]:
    clean_markdown = REPORT_MARKER_RE.sub("", markdown).strip()
    batch_match = re.search(r"(?m)^## 检查批次\s+(.+)$", clean_markdown)
    batch = batch_match.group(1).strip() if batch_match else "未知批次"
    title = f"上游 Release 监控报告 · {batch}"
    body_html = MarkdownIt("default", {"html": False}).render(clean_markdown)
    body = (
        '<header><div class="container"><a href="../../index.html">← 报告列表</a></div></header>'
        f'<main class="container"><article class="card">{body_html}</article></main>'
    )
    metadata = {
        "id": report_id,
        "batch": batch,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "coin_count": len(re.findall(r"(?m)^###\s+\S", clean_markdown)),
        "release_count": len(re.findall(r"(?m)^####\s+\S", clean_markdown)),
    }
    return page(title, body), metadata


def read_metadata(report_dir: Path) -> dict | None:
    try:
        metadata_path = report_dir / "metadata.json"
        if metadata_path.is_symlink():
            return None
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if not isinstance(metadata, dict) or not isinstance(metadata.get("batch"), str):
            return None
        if any(type(metadata.get(field)) is not int or metadata[field] < 0 for field in ("coin_count", "release_count")):
            return None
        if not RUN_ID_RE.fullmatch(str(metadata.get("id", ""))):
            return None
        if datetime.fromisoformat(metadata["published_at"]).tzinfo is None:
            return None
        return metadata
    except (OSError, KeyError, TypeError, ValueError):
        return None


def prune_reports(reports_dir: Path, cutoff: datetime, current_id: str) -> None:
    for report_dir in reports_dir.iterdir():
        if report_dir.is_symlink() or not report_dir.is_dir() or not RUN_ID_RE.fullmatch(report_dir.name):
            continue
        if report_dir.name == current_id:
            continue
        metadata = read_metadata(report_dir)
        if metadata and metadata["id"] == report_dir.name and datetime.fromisoformat(metadata["published_at"]) < cutoff:
            shutil.rmtree(report_dir)


def write_index(site_dir: Path) -> None:
    reports_dir = site_dir / "release-reports" / "reports"
    entries = []
    for report_dir in reports_dir.iterdir():
        if not report_dir.is_dir() or report_dir.is_symlink():
            continue
        metadata = read_metadata(report_dir)
        if metadata and metadata["id"] == report_dir.name:
            entries.append(metadata)
    entries.sort(key=lambda item: item["published_at"], reverse=True)

    rows = []
    for item in entries:
        report_id = html.escape(item["id"], quote=True)
        label = html.escape(item["batch"])
        rows.append(
            f'<li><a href="reports/{report_id}/index.html">{label}</a>'
            f'<span>{item["coin_count"]} 个币种 · {item["release_count"]} 个版本</span></li>'
        )
    report_list = "\n".join(rows) or "<li>暂无报告</li>"
    body = (
        '<header><div class="container"><strong>上游 Release 监控</strong></div></header>'
        '<main class="container"><section class="card">'
        '<h1>完整审查报告</h1>'
        '<p class="meta">每轮报告按币种和 Release 版本分组。</p>'
        f'<ul class="report-list">{report_list}</ul>'
        '</section></main>'
    )
    report_index = site_dir / "release-reports" / "index.html"
    if report_index.is_symlink():
        raise ValueError("Pages report index must not be a symlink")
    report_index.write_text(
        page("上游 Release 监控报告", body), encoding="utf-8"
    )
    root_index = site_dir / "index.html"
    if root_index.is_symlink():
        raise ValueError("Pages root index must not be a symlink")
    if not root_index.exists():
        root_body = (
            '<main class="container"><section class="card">'
            '<h1>上游 Release 监控</h1>'
            '<p><a href="release-reports/">查看完整审查报告</a></p>'
            '</section></main>'
        )
        root_index.write_text(page("上游 Release 监控", root_body), encoding="utf-8")


def publish_report(report_dir: Path, site_dir: Path, run_id: str, attempt: str, retention_days: int) -> str:
    if not run_id.isdecimal() or not attempt.isdecimal():
        raise ValueError("GitHub run ID and attempt must be numeric")
    if retention_days < 1:
        raise ValueError("Report retention must be at least one day")
    reports = sorted(report_dir.rglob("*.md"))
    if len(reports) != 1 or reports[0].is_symlink():
        raise ValueError(f"Expected one Markdown report, found {len(reports)}")

    report_id = f"{run_id}-{attempt}"
    if not RUN_ID_RE.fullmatch(report_id):
        raise ValueError("Invalid report ID")
    site_dir = site_dir.resolve()
    release_reports = site_dir / "release-reports"
    if release_reports.is_symlink():
        raise ValueError("Pages release-reports path must not be a symlink")
    reports_root = release_reports / "reports"
    if reports_root.is_symlink():
        raise ValueError("Pages reports path must not be a symlink")
    pages_reports = reports_root
    pages_reports.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    prune_reports(pages_reports, now - timedelta(days=retention_days), report_id)

    report_page, metadata = render_report(reports[0].read_text(encoding="utf-8"), report_id)
    report_path = pages_reports / report_id
    if report_path.is_symlink():
        raise ValueError("Pages report path must not be a symlink")
    report_path.mkdir(parents=True, exist_ok=True)
    (report_path / "index.html").write_text(report_page, encoding="utf-8")
    (report_path / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    write_index(site_dir)
    return f"release-reports/reports/{report_id}/index.html"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-dir", type=Path, required=True)
    parser.add_argument("--site-dir", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--run-attempt", required=True)
    parser.add_argument("--retention-days", type=int, default=180)
    args = parser.parse_args()
    print(publish_report(args.report_dir, args.site_dir, args.run_id, args.run_attempt, args.retention_days))


if __name__ == "__main__":
    main()
