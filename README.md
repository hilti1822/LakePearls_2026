# 레이크펄스 빌딩 — 월별 수입지출 대시보드

🔗 https://hilti1822.github.io/LakePearls_2026/

## 구조

```
data/
  2026-05.json     ← 월별 원자료 (숫자/표 데이터만)
  2026-06.json
template.html       ← 디자인 틀 (보통 건드릴 일 없음)
build.py            ← data/*.json + template.html → index.html 자동 생성
index.html           ← 자동 생성된 결과물 (직접 수정 X)
.github/workflows/
  build-dashboard.yml     ← data/ 변경 시 자동 빌드 + 배포
  monthly-reminder.yml    ← 매월 1일 자료 업로드 안내 이슈 생성
```

## 매달 할 일

1. `data/` 폴더에서 가장 최근 달 JSON 파일을 복사
2. 파일명을 `YYYY-MM.json` 형식으로 바꾸고 (예: `2026-07.json`)
3. 안의 숫자/표 내용을 새 자료로 교체
4. main 브랜치에 commit & push

→ GitHub Actions가 자동으로 `index.html`을 재생성하고 GitHub Pages에 배포합니다.
사람이 `index.html`을 직접 편집하거나 업로드할 필요가 없습니다.

## JSON 데이터 형식

```jsonc
{
  "year": 2026,
  "month": 7,
  "status": "검토중",          // 작성완료 | 검토중 | 미작성
  "last_updated": "2026-07-31",

  "kpis": [                     // 상단 4개 핵심 지표 카드
    { "label": "...", "value": 12345678, "tone": "accent" }
    // tone: accent | positive | negative | (생략 시 기본)
  ],

  "warning": "...",             // (선택) 주의 문구 박스

  "bar_chart": {                // (선택) 막대 그래프
    "title": "...",
    "bars": [{ "label": "...", "value": 1000 }]
  },

  "sections": [                 // 본문 표 (여러 개)
    {
      "title": "...",
      "type": "table",          // table | keyvalue
      "columns": ["내역", "지출", "수입", "차인"],
      "rows": [["전기료", 100, 200, 100]],
      "total_row": ["소계", 100, 200, 100],   // (선택)
      "note": "..."                            // (선택) 표 아래 작은 메모
    }
  ],

  "fire_inspection": {          // (선택) 소방점검 카드형 섹션
    "title": "...",
    "items": [
      { "floor": "5층", "room": "501호", "urgent": false, "issues": ["..."] }
    ]
  },

  "insights": [                 // (선택) 시사점 카드
    { "title": "...", "summary": "...", "detail": ["...", "..."], "urgent": true }
  ]
}
```

`columns`에 `"차인"`이라는 이름의 열이 있으면 자동으로 양수는 초록(+), 음수는 빨강(-)으로 표시됩니다.

## 로컬에서 미리보기

```bash
python build.py
open index.html   # 또는 브라우저로 직접 열기
```

## 수동으로 다시 빌드하고 싶을 때

GitHub 저장소 → **Actions** 탭 → **Build & Deploy Dashboard** → **Run workflow** 클릭
