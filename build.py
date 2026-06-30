#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
레이크펄스 빌딩 — 월별 수입지출 대시보드 빌더
data/YYYY-MM.json 파일들을 읽어 index.html을 생성한다.

사용법:
    python build.py

매달 할 일: data/ 폴더에 YYYY-MM.json 파일 하나만 추가하면
GitHub Actions가 자동으로 이 스크립트를 실행해 index.html을 갱신한다.
"""
import json
import glob
import os
import html as html_lib

DATA_DIR = "data"
OUTPUT_FILE = "index.html"

MONTH_NAMES = {i: f"{i}월" for i in range(1, 13)}


def fmt_num(v):
    """숫자 포맷팅. 빈 문자열/None은 — 로, 문자열은 그대로 표시."""
    if v is None or v == "":
        return "—"
    if isinstance(v, (int, float)):
        if v == 0:
            return "—"
        return f"{v:,.0f}"
    return html_lib.escape(str(v))


def signed_class(v):
    if isinstance(v, (int, float)):
        if v > 0:
            return "pos"
        if v < 0:
            return "neg"
    return ""


def signed_str(v):
    if isinstance(v, (int, float)) and v != 0:
        sign = "+" if v > 0 else ""
        return f"{sign}{v:,.0f}"
    return fmt_num(v)


def load_months():
    months = []
    for path in sorted(glob.glob(os.path.join(DATA_DIR, "*.json"))):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        months.append(data)
    months.sort(key=lambda m: (m["year"], m["month"]))
    return months


def render_kpis(kpis):
    cells = []
    for k in kpis:
        tone_class = {
            "positive": "positive", "negative": "negative", "accent": "accent"
        }.get(k.get("tone"), "")
        cells.append(f'''
      <div class="kpi {tone_class}">
        <div class="label">{html_lib.escape(k["label"])}</div>
        <div class="value">{fmt_num(k["value"])}<span class="unit">원</span></div>
      </div>''')
    return f'<div class="kpi-row">{"".join(cells)}</div>'


def render_bar_chart(bar_chart):
    if not bar_chart:
        return ""
    bars = bar_chart["bars"]
    max_val = max((b["value"] for b in bars), default=1) or 1
    rows = []
    for i, b in enumerate(bars):
        pct = round(b["value"] / max_val * 100, 1)
        cls = "bar-fill" if i % 2 == 0 else "bar-fill alt"
        rows.append(f'''
      <div class="bar-row">
        <span class="bar-label">{html_lib.escape(b["label"])}</span>
        <div class="bar-track"><div class="{cls}" style="width:{pct}%"></div></div>
        <span class="bar-val">{fmt_num(b["value"])}</span>
      </div>''')
    return f'''
    <p class="section-label">{html_lib.escape(bar_chart.get("title","항목별 지출 요약"))}</p>
    <div class="bar-chart" style="margin-bottom:24px;">{"".join(rows)}</div>'''


def render_table_section(section):
    title = html_lib.escape(section["title"])
    cols = section["columns"]
    rows = section["rows"]

    thead = "".join(f"<th>{html_lib.escape(c)}</th>" for c in cols)

    body_rows = []
    for row in rows:
        tds = []
        for idx, cell in enumerate(row):
            cls = ""
            if idx >= len(cols) - 1 and isinstance(cell, (int, float)) and len(cols) >= 3:
                # 마지막 숫자 컬럼이 '차인' 성격이면 +/- 강조 (간단 휴리스틱: 컬럼명에 "차인" 포함)
                pass
            if isinstance(cell, (int, float)):
                if cols[idx] == "차인":
                    cls = signed_class(cell)
                    tds.append(f'<td class="{cls}">{signed_str(cell)}</td>')
                else:
                    tds.append(f"<td>{fmt_num(cell)}</td>")
            else:
                tds.append(f"<td>{html_lib.escape(str(cell)) if cell not in (None, '') else '—'}</td>")
        body_rows.append(f"<tr>{''.join(tds)}</tr>")

    total_html = ""
    if section.get("total_row"):
        tds = []
        for idx, cell in enumerate(section["total_row"]):
            if isinstance(cell, (int, float)):
                if idx < len(cols) and cols[idx] == "차인":
                    cls = signed_class(cell)
                    tds.append(f'<td class="{cls}">{signed_str(cell)}</td>')
                else:
                    tds.append(f"<td>{fmt_num(cell)}</td>")
            else:
                tds.append(f"<td>{html_lib.escape(str(cell)) if cell not in (None, '') else ''}</td>")
        total_html = f'<tr class="total">{"".join(tds)}</tr>'

    footer_html = ""
    if section.get("footer_row"):
        tds = []
        for cell in section["footer_row"]:
            if isinstance(cell, (int, float)):
                tds.append(f"<td>{fmt_num(cell)}</td>")
            else:
                tds.append(f"<td>{html_lib.escape(str(cell))}</td>")
        footer_html = f'<tr class="total" style="opacity:0.85;">{"".join(tds)}</tr>'

    note_html = ""
    if section.get("note"):
        note_html = f'<div style="font-size:0.74rem;color:var(--text3);margin:4px 0 0;">{html_lib.escape(section["note"])}</div>'

    return f'''
    <p class="section-label">{title}</p>
    <div class="table-wrap">
      <table>
        <thead><tr>{thead}</tr></thead>
        <tbody>{"".join(body_rows)}{total_html}{footer_html}</tbody>
      </table>
    </div>{note_html}'''


def render_keyvalue_section(section):
    title = html_lib.escape(section["title"])
    rows = "".join(
        f"<tr><td>{html_lib.escape(str(k))}</td><td>{html_lib.escape(str(v))}</td></tr>"
        for k, v in section["rows"]
    )
    return f'''
    <p class="section-label">{title}</p>
    <div class="table-wrap">
      <table><tbody>{rows}</tbody></table>
    </div>'''


def render_section(section):
    if section["type"] == "table":
        return render_table_section(section)
    if section["type"] == "keyvalue":
        return render_keyvalue_section(section)
    return ""


def render_fire_inspection(fire):
    if not fire:
        return ""
    title = html_lib.escape(fire.get("title", "⚠ 소방점검 지적사항"))
    cards = []
    for item in fire["items"]:
        urgent_cls = " urgent" if item.get("urgent") else ""
        issues = "".join(f"<li>{html_lib.escape(i)}</li>" for i in item["issues"])
        cards.append(f'''
      <div class="fire-card{urgent_cls}">
        <div class="floor">{html_lib.escape(item["floor"])}</div>
        <div class="room">{html_lib.escape(item["room"])}</div>
        <ul class="items">{issues}</ul>
      </div>''')
    return f'''
    <p class="section-label">{title}</p>
    <div class="fire-grid">{"".join(cards)}</div>'''


def render_insights(insights):
    if not insights:
        return ""
    cards = []
    for ins in insights:
        urgent_cls = " urgent" if ins.get("urgent") else ""
        detail = "".join(f"<li>{html_lib.escape(d)}</li>" for d in ins.get("detail", []))
        cards.append(f'''
      <div class="fire-card{urgent_cls}">
        <div class="floor">{html_lib.escape(ins["title"])}</div>
        <div class="room">{html_lib.escape(ins["summary"])}</div>
        <ul class="items">{detail}</ul>
      </div>''')
    return f'''
    <p class="section-label">⚠ 시사점 및 확인 필요 사항</p>
    <div class="fire-grid">{"".join(cards)}</div>'''


def render_warning(warning):
    if not warning:
        return ""
    return f'''
    <div style="margin:14px 0 0;padding:12px 16px;border:1px solid var(--danger);border-radius:8px;background:rgba(255,107,107,0.06);font-size:0.78rem;color:var(--text2);line-height:1.6;">
      ⚠ {html_lib.escape(warning)}
    </div>'''


def render_month_panel(m, is_active):
    active_cls = " active" if is_active else ""
    kpis_html = render_kpis(m.get("kpis", []))
    warning_html = render_warning(m.get("warning"))
    bar_html = render_bar_chart(m.get("bar_chart"))
    sections_html = "".join(render_section(s) for s in m.get("sections", []))
    fire_html = render_fire_inspection(m.get("fire_inspection"))
    insights_html = render_insights(m.get("insights"))

    status = m.get("status", "")
    last_updated = m.get("last_updated", "")

    return f'''
  <div class="month-panel{active_cls}" id="panel-{m["month"]}">

    <p class="section-label">요약</p>
    {kpis_html}
    {warning_html}
    {bar_html}
    {sections_html}
    {fire_html}
    {insights_html}

    <div style="margin-top:40px;padding-top:20px;border-top:1px solid var(--border);font-size:0.72rem;color:var(--text3);">
      레이크펄스 빌딩 관리사무소 &nbsp;·&nbsp; {m["year"]}년 {m["month"]}월 &nbsp;·&nbsp; 상태: {html_lib.escape(status)} &nbsp;·&nbsp; 최종 업데이트: {html_lib.escape(last_updated)}
    </div>
  </div><!-- /panel-{m["month"]} -->'''


def render_empty_panel(month_num):
    return f'''
  <div class="month-panel" id="panel-{month_num}">
    <div class="empty-state">
      <div class="icon">📂</div>
      <p>{MONTH_NAMES[month_num]} 자료가 아직 등록되지 않았습니다.<br>data/YYYY-{month_num:02d}.json 파일을 추가하면 자동으로 채워집니다.</p>
      <code>data/2026-{month_num:02d}.json</code>
    </div>
  </div>'''


def render_month_nav(months_by_num, active_month):
    buttons = []
    for i in range(1, 13):
        has_data = i in months_by_num
        cls = "month-btn"
        if has_data:
            cls += " has-data"
        if i == active_month:
            cls += " active"
        buttons.append(f'  <button class="{cls}" data-month="{i}">{MONTH_NAMES[i]}</button>')
    return "\n".join(buttons)


def build():
    months = load_months()
    if not months:
        raise SystemExit("data/ 폴더에 JSON 파일이 없습니다.")

    months_by_num = {m["month"]: m for m in months}
    active_month = months[-1]["month"]  # 가장 최근 달을 기본 활성화
    year = months[-1]["year"]

    nav_html = render_month_nav(months_by_num, active_month)

    panels_html = []
    for i in range(1, 13):
        if i in months_by_num:
            panels_html.append(render_month_panel(months_by_num[i], i == active_month))
        else:
            panels_html.append(render_empty_panel(i))
    panels_joined = "\n".join(panels_html)

    template_path = "template.html"
    with open(template_path, encoding="utf-8") as f:
        template = f.read()

    output = (
        template
        .replace("{{YEAR}}", str(year))
        .replace("{{MONTH_NAV}}", nav_html)
        .replace("{{MONTH_PANELS}}", panels_joined)
    )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"✅ {OUTPUT_FILE} 생성 완료 — {len(months)}개월 데이터 반영 (기본 활성: {active_month}월)")


if __name__ == "__main__":
    build()
