"""site/data/*.json(날짜별 분석 결과)을 읽어 정적 블로그(HTML)를 만든다.

사용 예:
    python .github/scripts/build_site.py --site-dir site

만드는 파일: index.html, posts/<slug>/index.html, assets/style.css, .nojekyll
"""

from __future__ import annotations

import argparse
import json
import shutil
from collections import Counter
from html import escape
from pathlib import Path

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import TextLexer, get_lexer_by_name

REPO_URL = "https://github.com/1juyoung/algorithm"
SITE_NAME = "1juyoung/algo-notes"
LEXER = {".py": "python", ".js": "javascript", ".ts": "typescript", ".java": "java", ".cpp": "cpp", ".cc": "cpp",
         ".c": "c", ".kt": "kotlin", ".swift": "swift", ".go": "go", ".rs": "rust", ".rb": "ruby", ".cs": "csharp",
         ".sql": "sql"}
RECENT = 20  # "내가 자주 막히는 곳"은 최근 N문제의 약점만 센다
VERDICT_CLASS = {"최선": "best", "개선 가능": "warn", "더 쉬운 풀이 있음": "warn", "분석 실패": "fail"}
LEGACY = ["_posts", "_config.yml", "index.md", "reviews"]  # 예전 Jekyll 방식의 파일


# ---------------------------------------------------------------------------
# 데이터
# ---------------------------------------------------------------------------

def load_problems(site: Path) -> list[dict]:
    items = []
    for f in sorted((site / "data").glob("*.json")):
        items.extend(json.loads(f.read_text(encoding="utf-8")).get("problems", []))
    items.sort(key=lambda p: (p["date"], p["slug"]), reverse=True)
    return items


def a(p: dict, key: str, default=""):
    return (p.get("analysis") or {}).get(key, default) or default


# ---------------------------------------------------------------------------
# 조각
# ---------------------------------------------------------------------------

def page(title: str, body: str, root: str) -> str:
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#f3f4ef">
<title>{escape(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}assets/style.css">
</head>
<body>
<header class="site-header">
  <div class="container header-inner">
    <a class="logo" href="{root}"><span class="prompt">&gt;</span> {SITE_NAME}</a>
    <a class="header-link" href="{REPO_URL}" target="_blank" rel="noopener">GitHub ↗</a>
  </div>
</header>
{body}
<footer class="site-footer"><div class="container">매일 자정, 그날 푼 풀이를 자동으로 분석해서 올려요.</div></footer>
</body>
</html>
"""


def code_block(code: str, ext: str, label: str) -> str:
    try:
        lexer = get_lexer_by_name(LEXER.get(ext, "text"))
    except Exception:
        lexer = TextLexer()
    html = highlight(code.rstrip("\n") + "\n", lexer,
                     HtmlFormatter(linenos="inline", nowrap=False, cssclass="hl", wrapcode=True))
    lang = LEXER.get(ext, "")
    return (f'<div class="code-card"><div class="code-head"><span>{escape(label)}</span>'
            f'<span>{escape(lang)}</span></div>{html}</div>')


def complexity_inline(p: dict) -> str:
    my, best = a(p, "my_time", "-"), a(p, "best_time", "-")
    if a(p, "verdict") != "최선" and my != best and best not in ("", "-"):
        return (f'<span class="cx"><s>{escape(my)}</s><span class="arrow">⟶</span>'
                f'<mark>{escape(best)}</mark></span>')
    return f'<span class="cx">{escape(my)}</span>'


def chips(p: dict) -> str:
    tags = [w.get("tag", "") for w in a(p, "weaknesses", [])] or \
        [t.strip() for t in (p.get("categories") or "").split(",") if t.strip()][:3]
    return "".join(f'<span class="chip">{escape(t)}</span>' for t in tags if t)


def meta_line(p: dict, with_date: bool) -> str:
    parts = [p["date"]] if with_date else []
    parts.append(f'{p.get("site", "")} {p.get("number", "")}'.strip())
    if p.get("tier"):
        parts.append(p["tier"])
    return " · ".join(escape(x) for x in parts if x)


# ---------------------------------------------------------------------------
# 첫 화면
# ---------------------------------------------------------------------------

def render_index(problems: list[dict]) -> str:
    def tag_counts(ps):
        return Counter(w.get("tag") for p in ps for w in a(p, "weaknesses", []) if w.get("tag"))

    recent = tag_counts(problems[:RECENT])  # problems는 최신순
    total = tag_counts(problems)
    top = recent.most_common(6)

    if top:
        peak = top[0][1]
        rows = "".join(
            f'<div class="bar-row"><span class="bar-label">{escape(tag)}</span>'
            f'<span class="bar-track"><span class="bar-fill{" top" if i == 0 else ""}" '
            f'style="width:{n / peak * 100:.0f}%"></span></span><span class="bar-num">{n}'
            f'<small>/ {total[tag]}</small></span></div>'
            for i, (tag, n) in enumerate(top))
        weak = (f'<section class="card weak"><h2>내가 자주 막히는 곳</h2>'
                f'<p class="sub">지금 가장 많이 걸린 건 <strong>{escape(top[0][0])}</strong> — '
                f'다음 문제는 이 유형으로 골라 보자.</p><p class="basis">최근 {RECENT}문제 기준 / 전체 누적</p>'
                f'<div class="bars">{rows}</div></section>')
    else:
        weak = ('<section class="card weak"><h2>내가 자주 막히는 곳</h2>'
                '<p class="sub">아직 쌓인 약점이 없어. 문제를 풀면 여기에 모여.</p></section>')

    items = "".join(
        f'<a class="rec" href="posts/{escape(p["slug"])}/">'
        f'<span class="rec-date">{escape(p["date"])}</span>'
        f'<span class="rec-main"><span class="rec-meta">{meta_line(p, False)}</span>'
        f'<span class="rec-title">{escape(p["title"])}</span><span class="chips">{chips(p)}</span></span>'
        f'<span class="rec-cx">{complexity_inline(p)}</span></a>'
        for p in problems) or '<p class="empty">아직 기록이 없어.</p>'

    body = f"""<main class="container home">
  <p class="eyebrow">// {len(problems)}문제 기록됨</p>
  <h1>오늘 푼 문제를, <span class="hl-mark">한 단계 더</span> 빠르게.</h1>
  <p class="lead">매일 푼 코딩 테스트 풀이의 시간 복잡도를 따지고, 더 나은 답안을 붙여 두고,
  내가 반복해서 막히는 지점을 모아 보는 1juyoung 전용 노트.</p>
  {weak}
  <section class="records"><h2>풀이 기록</h2><div class="rec-list">{items}</div></section>
</main>"""
    return page("1juyoung의 알고리즘 노트", body, "")


# ---------------------------------------------------------------------------
# 상세 화면
# ---------------------------------------------------------------------------

def render_post(p: dict) -> str:
    verdict = a(p, "verdict", "")
    my_t, best_t = a(p, "my_time", "-"), a(p, "best_time", "-")
    if verdict != "최선" and my_t != best_t and best_t not in ("", "-"):
        big = f'<s>{escape(my_t)}</s><span class="arrow">⟶</span><mark>{escape(best_t)}</mark>'
    else:
        big = f'<mark>{escape(my_t)}</mark>'
    space = (f'<div class="space"><div><span class="label">내 공간</span><code>{escape(a(p, "my_space", "-"))}</code></div>'
             f'<div><span class="label">최선 공간</span><code>{escape(a(p, "best_space", "-"))}</code></div></div>')

    goods = "".join(f"<li>{escape(g)}</li>" for g in a(p, "good_points", []))
    comments = "".join(f'<div class="comment"><strong>{escape(c.get("title", ""))}</strong>'
                       f'<p>{escape(c.get("body", ""))}</p></div>' for c in a(p, "comments", []))
    two_col = ""
    if goods or comments:
        two_col = (f'<div class="two-col"><section><h2>잘한 점</h2><ul class="plus">{goods or "<li>-</li>"}</ul></section>'
                   f'<section><h2>코멘트</h2>{comments or "<p class=muted>고칠 점이 없어.</p>"}</section></div>')

    weak_rows = "".join(f'<div class="weak-row"><span class="weak-tag">{escape(w.get("tag", ""))}</span>'
                        f'<span>{escape(w.get("reason", ""))}</span></div>' for w in a(p, "weaknesses", []))
    weak = f'<section><h2>이 문제에서 드러난 약점</h2><div class="card weak-table">{weak_rows}</div></section>' \
        if weak_rows else ""

    better = ""
    if a(p, "better_code"):
        better = (f'<section><h2>더 나은 풀이</h2><p>{escape(a(p, "better_summary"))}</p>'
                  f'{code_block(a(p, "better_code"), p.get("code_ext", ""), f"better · {best_t}")}</section>')

    approach = (f'<div class="approach"><span class="label">푸는 방법</span>'
                f'<p>{escape(a(p, "intended_approach"))}</p></div>' if a(p, "intended_approach") else "")
    match = (p.get("analysis") or {}).get("approach_match", True)
    judge = ""
    if a(p, "summary"):
        mark = ('<span class="judge-mark ok">✓ 방향 맞음</span>' if match
                else '<span class="judge-mark no">✕ 다른 방식</span>')
        judge = (f'<section class="judge {"ok" if match else "no"}"><div class="judge-head">'
                 f'<h2>내 풀이는?</h2>{mark}</div><p>{escape(a(p, "summary"))}</p></section>')
    link = (f'<a class="ext" href="{escape(p["link"])}" target="_blank" rel="noopener">문제 보러 가기 ↗</a>'
            if p.get("link") else "")
    body = f"""<main class="container post">
  <a class="back" href="../../">← 목록으로</a>
  <p class="post-meta">{meta_line(p, True)}</p>
  <h1>{escape(p["title"])}</h1>
  <p class="summary">{escape(a(p, "problem_summary"))}</p>
  {link}
  {approach}
  <section><h2>내 풀이</h2>{code_block(p.get("code", ""), p.get("code_ext", ""), "my solution")}</section>
  {judge}
  <section class="card cx-card">
    <div class="cx-head"><span class="label">시간 복잡도</span>
      <span class="badge {VERDICT_CLASS.get(verdict, "warn")}">{escape(verdict)}</span></div>
    <div class="cx-big">{big}</div>
    {space}
    <p>{escape(a(p, "complexity_note"))}</p>
  </section>
  {two_col}
  {weak}
  {better}
</main>"""
    return page(f"{p.get('site', '')} {p.get('number', '')} {p['title']} · 1juyoung의 알고리즘 노트", body, "../../")


# ---------------------------------------------------------------------------
# 스타일
# ---------------------------------------------------------------------------

CSS = """
:root{--bg:#f3f4ef;--fg:#172033;--card:#fbfbf8;--primary:#2b4fd8;--on-primary:#fbfbf8;--muted:#e7e9e2;
--muted-fg:#586173;--hl:#f3e24b;--border:#d6d9d0;--danger:#c23a2b;--r:6px;
--sans:"IBM Plex Sans KR",system-ui,-apple-system,sans-serif;--mono:"JetBrains Mono",ui-monospace,monospace}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;font:16px/1.6 var(--sans);color:var(--fg);background-color:var(--bg);
background-image:linear-gradient(to right,rgba(214,217,208,.45) 1px,transparent 1px),
linear-gradient(rgba(214,217,208,.45) 1px,transparent 1px);background-size:24px 24px}
a{color:inherit;text-decoration:none}
h1,h2{margin:0;letter-spacing:-.01em}
p{margin:0}
.container{max-width:1024px;margin:0 auto;padding:0 20px}
.site-header{position:sticky;top:0;z-index:10;background:rgba(251,251,248,.85);backdrop-filter:blur(6px);
border-bottom:1px solid var(--border)}
.header-inner{display:flex;align-items:center;justify-content:space-between;height:68px}
.logo{font:700 14px var(--mono)}
.logo .prompt{color:var(--primary)}
.header-link{font-size:14px;color:var(--muted-fg)}
.header-link:hover{color:var(--fg)}
.site-footer{padding:40px 0 56px;color:var(--muted-fg);font-size:13px}
.card{background:var(--card);border:1px solid var(--border);border-radius:var(--r)}
mark,.hl-mark{background:linear-gradient(transparent 55%,var(--hl) 55%);color:inherit;padding:0 .08em}
s{color:var(--muted-fg);text-decoration-thickness:1.5px}
.arrow{margin:0 .4em;color:var(--muted-fg)}

/* 첫 화면 */
.home{padding-top:64px;padding-bottom:24px}
.eyebrow{font:13px var(--mono);color:var(--muted-fg);letter-spacing:.06em}
.home h1{font-size:48px;line-height:1.25;margin:14px 0 18px}
.lead{color:var(--muted-fg);max-width:600px;line-height:1.7}
.weak{margin-top:56px;padding:28px}
.weak h2{font-size:20px}
.sub{color:var(--muted-fg);font-size:14px;margin-top:6px}
.sub strong{color:var(--fg)}
.bars{margin-top:20px;display:grid;gap:10px}
.bar-row{display:grid;grid-template-columns:220px 1fr 56px;align-items:center;gap:16px;font-size:14px}
.bar-track{height:12px;background:var(--muted);border-radius:2px;overflow:hidden}
.bar-fill{display:block;height:100%;background:var(--primary)}
.bar-fill.top{background:var(--hl)}
.bar-num{text-align:right;font-family:var(--mono)}
.bar-num small{color:var(--muted-fg);font-size:11px;margin-left:3px}
.basis{font:11px var(--mono);color:var(--muted-fg);margin-top:14px;text-align:right}
.records{margin-top:56px}
.records h2{font-size:20px;margin-bottom:18px}
.rec-list{border-top:1px solid var(--border)}
.rec{display:grid;grid-template-columns:120px 1fr auto;align-items:center;gap:16px;padding:18px 12px;
border-bottom:1px solid var(--border);transition:background .15s}
.rec:hover{background:var(--card)}
.rec-date{font:13px var(--mono);color:var(--muted-fg)}
.rec-main{display:flex;flex-direction:column;gap:4px;min-width:0}
.rec-meta{font:12px var(--mono);color:var(--muted-fg)}
.rec-title{font-size:18px;font-weight:700}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:2px}
.chip{font-size:12px;background:var(--muted);border-radius:3px;padding:2px 6px}
.rec-cx,.cx{font:14px var(--mono);white-space:nowrap}
.rec-cx mark{font-weight:700}
.empty{color:var(--muted-fg);padding:24px 0}

/* 상세 화면 */
.post{max-width:768px;padding-top:40px}
.back{font-size:14px;color:var(--muted-fg)}
.back:hover{color:var(--fg)}
.post-meta{margin-top:36px;font:13px var(--mono);color:var(--muted-fg)}
.post h1{font-size:34px;margin:6px 0 10px}
.summary{line-height:1.7}
.ext{display:inline-block;margin-top:10px;font-size:14px;color:var(--primary)}
.post section{margin-top:40px}
.post section h2{font-size:18px;margin-bottom:12px}
.post section>p{line-height:1.75}
.post section>p+.code-card{margin-top:14px}
.code-card{border:1px solid var(--border);border-radius:var(--r);overflow:hidden;background:var(--card)}
.code-head{display:flex;justify-content:space-between;padding:8px 16px;background:var(--muted);
font:12px var(--mono);color:var(--muted-fg)}
.hl pre{margin:0;padding:16px;overflow-x:auto;font:13.5px/1.75 var(--mono);background:var(--card)}
.hl .linenos{display:inline-block;width:2.2em;margin-right:12px;color:#9aa1ad;text-align:right;user-select:none}
.approach{margin-top:22px;padding:16px 18px;border-left:3px solid var(--primary);background:var(--card);
border-radius:0 var(--r) var(--r) 0}
.approach p{margin-top:4px;line-height:1.7;font-weight:500}
.post section.judge{padding:18px 20px;border:1px solid var(--border);border-radius:var(--r);background:var(--card);
margin-top:20px}
.judge-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.judge-head h2{margin:0!important}
.judge p{line-height:1.75}
.judge-mark{font:500 12px var(--mono);padding:2px 8px;border-radius:3px}
.judge-mark.ok{color:var(--primary);border:1px solid var(--primary)}
.judge-mark.no{color:var(--fg);background:var(--hl)}
.cx-card{padding:24px 26px}
.cx-head{display:flex;justify-content:space-between;align-items:center}
.label{font:12px var(--mono);color:var(--muted-fg);letter-spacing:.08em}
.badge{font-size:12px;font-weight:500;border:1px solid var(--fg);border-radius:3px;padding:2px 8px;background:var(--card)}
.badge.best{border-color:var(--primary);color:var(--primary)}
.badge.fail{border-color:var(--danger);color:var(--danger)}
.cx-big{font:700 34px var(--mono);margin:14px 0 18px;padding-bottom:18px;border-bottom:1px solid var(--border);
max-width:60%;white-space:nowrap}
.cx-big s{font-weight:500}
.space{display:grid;grid-template-columns:200px 200px;margin-bottom:16px}
.space div{display:flex;flex-direction:column;gap:2px}
.space code{font:14px var(--mono)}
.cx-card p{line-height:1.75}
.two-col{display:grid;grid-template-columns:1fr 1fr;gap:40px}
.plus{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.plus li{display:grid;grid-template-columns:14px 1fr;gap:8px;line-height:1.6}
.plus li::before{content:"+";color:var(--primary);font-family:var(--mono)}
.comment{margin-bottom:14px}
.comment p{color:var(--muted-fg);line-height:1.65;margin-top:2px}
.muted{color:var(--muted-fg)}
.weak-table{overflow:hidden}
.weak-row{display:grid;grid-template-columns:220px 1fr;gap:16px;padding:16px 18px;border-bottom:1px solid var(--border)}
.weak-row:last-child{border-bottom:0}
.weak-tag{font-weight:700;font-size:13px;align-self:start;justify-self:start;
background:linear-gradient(transparent 55%,var(--hl) 55%)}

/* 코드 색상 */
.hl .k,.hl .kn,.hl .kd,.hl .kc,.hl .kr,.hl .ow{color:#2b4fd8}
.hl .s,.hl .s1,.hl .s2,.hl .sa,.hl .se,.hl .si,.hl .sd{color:#1f7a4d}
.hl .c,.hl .c1,.hl .cm,.hl .ch{color:#8a919e;font-style:italic}
.hl .mi,.hl .mf,.hl .mh{color:#b35c1e}
.hl .nb,.hl .bp{color:#6b46c1}
.hl .nf,.hl .nc{color:#172033;font-weight:700}

@media (max-width:720px){
.home{padding-top:40px}.home h1{font-size:32px}
.bar-row{grid-template-columns:110px 1fr 48px;gap:10px}
.rec{grid-template-columns:1fr;gap:6px}.rec-cx{justify-self:start}
.two-col{grid-template-columns:1fr;gap:0}
.weak-row{grid-template-columns:1fr;gap:6px}
.cx-big{font-size:26px;max-width:100%;white-space:normal}
.space{grid-template-columns:1fr 1fr}
}
"""


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--site-dir", required=True)
    args = ap.parse_args()
    site = Path(args.site_dir)

    for name in LEGACY + ["posts", "assets"]:
        path = site / name
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()

    problems = load_problems(site)
    (site / "assets").mkdir(parents=True, exist_ok=True)
    (site / "assets" / "style.css").write_text(CSS.strip() + "\n", encoding="utf-8")
    (site / ".nojekyll").write_text("", encoding="utf-8")
    (site / "index.html").write_text(render_index(problems), encoding="utf-8")
    for p in problems:
        out = site / "posts" / p["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_post(p), encoding="utf-8")
    print(f"{len(problems)}개 문제 페이지를 만들었어요.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
