"""그날 BaekjoonHub로 올라온 풀이를 찾아 Gemini로 분석하고 블로그 글(Jekyll)을 만든다.

사용 예:
    python .github/scripts/daily_review.py --date 2026-11-22 --site-dir site
    python .github/scripts/daily_review.py --date 2026-11-22 --site-dir site --dry-run

결과는 GITHUB_OUTPUT(있으면)에 post_path, count, title, body, url 로 기록한다.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

KST = dt.timezone(dt.timedelta(hours=9))
DEFAULT_MODEL = "gemini-3.8-flash"  # 바꾸려면 레포 Variables에 GEMINI_MODEL 등록
MAX_PROBLEM_CHARS = 6000
MAX_CODE_CHARS = 6000
SOLUTION_EXTS = {".py", ".js", ".ts", ".java", ".cpp", ".cc", ".c", ".kt", ".swift", ".go", ".rs", ".rb", ".cs", ".sql"}
LANG_FENCE = {".py": "python", ".js": "javascript", ".ts": "typescript", ".java": "java", ".cpp": "cpp",
              ".cc": "cpp", ".c": "c", ".kt": "kotlin", ".swift": "swift", ".go": "go", ".rs": "rust",
              ".rb": "ruby", ".cs": "csharp", ".sql": "sql"}


# ---------------------------------------------------------------------------
# 1. 그날 푼 문제 찾기
# ---------------------------------------------------------------------------

@dataclass
class Problem:
    folder: str
    commit: str
    committed_at: str
    title: str = ""
    tier: str = ""
    number: str = ""
    link: str = ""
    site: str = ""
    language: str = ""
    categories: str = ""
    performance: str = ""
    statement: str = ""
    code: str = ""
    code_ext: str = ""
    analysis: dict = field(default_factory=dict)


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-c", "core.quotepath=false", *args], cwd=repo,
                          check=True, capture_output=True, text=True).stdout


def find_problems(repo: Path, day: dt.date) -> list[Problem]:
    since = f"{day.isoformat()} 00:00:00 +0900"
    until = f"{day.isoformat()} 23:59:59 +0900"
    log = git(repo, "log", f"--since={since}", f"--until={until}",
              "--format=%x1e%H%x1f%cI%x1f%s", "--name-only")
    by_folder: dict[str, Problem] = {}
    # git log는 최신 커밋부터 나오므로, 같은 문제를 여러 번 제출했으면 처음 본 것(최신)을 쓴다.
    for block in log.split("\x1e"):
        block = block.strip("\n")
        if not block:
            continue
        header, *files = block.split("\n")
        sha, committed_at, subject = header.split("\x1f")
        if "BaekjoonHub" not in subject:
            continue
        for f in files:
            f = f.strip()
            if not f or "/" not in f:
                continue
            folder = f.rsplit("/", 1)[0]
            if folder not in by_folder:
                by_folder[folder] = Problem(folder=folder, commit=sha, committed_at=committed_at)
    problems = list(by_folder.values())
    for p in problems:
        load_problem(repo, p)
    problems = [p for p in problems if p.code]
    problems.sort(key=lambda p: p.committed_at)
    return problems


def show(repo: Path, commit: str, path: str) -> str | None:
    try:
        return git(repo, "show", f"{commit}:{path}")
    except subprocess.CalledProcessError:
        return None


class _TextExtractor(HTMLParser):
    BLOCK = {"p", "br", "li", "tr", "h1", "h2", "h3", "h4", "pre", "div", "table"}

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in self.BLOCK:
            self.parts.append("\n")
        if tag in ("td", "th"):
            self.parts.append(" | ")

    def handle_endtag(self, tag):
        if tag in self.BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        if data.strip():  # 태그 사이의 들여쓰기·줄바꿈은 버린다
            self.parts.append(data)


def html_to_text(raw: str) -> str:
    parser = _TextExtractor()
    parser.feed(raw)
    text = html.unescape("".join(parser.parts))
    text = re.sub(r"[ \t\u00a0]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


def section(readme: str, name: str) -> str:
    m = re.search(rf"^###\s*{re.escape(name)}\s*$(.*?)(?=^###\s|\Z)", readme, re.M | re.S)
    return m.group(1).strip() if m else ""


def load_problem(repo: Path, p: Problem) -> None:
    parts = p.folder.split("/")
    p.language = parts[0] if parts else ""
    p.site = parts[1] if len(parts) > 1 else ""

    files = git(repo, "ls-tree", "--name-only", p.commit, f"{p.folder}/").splitlines()
    for path in files:
        ext = Path(path).suffix.lower()
        if ext in SOLUTION_EXTS:
            p.code = (show(repo, p.commit, path) or "")[:MAX_CODE_CHARS]
            p.code_ext = ext
            break

    readme = show(repo, p.commit, f"{p.folder}/README.md") or ""
    first = readme.splitlines()[0] if readme else ""
    m = re.match(r"#\s*\[(?P<tier>[^\]]+)\]\s*(?P<title>.+?)\s*-\s*(?P<num>\d+)\s*$", first)
    if m:
        p.tier, p.title, p.number = m.group("tier"), m.group("title"), m.group("num")
    else:
        p.title = parts[-1] if parts else p.folder
    link = re.search(r"\[문제 링크\]\((.+?)\)", readme)
    p.link = link.group(1) if link else ""
    p.categories = " ".join(section(readme, "분류").split())
    p.performance = " ".join(section(readme, "성능 요약").split())

    statement_parts = []
    for name in ("문제 설명", "입력", "출력", "제한사항"):
        body = section(readme, name)
        if body:
            statement_parts.append(f"[{name}]\n{html_to_text(body)}")
    p.statement = "\n\n".join(statement_parts)[:MAX_PROBLEM_CHARS]


# ---------------------------------------------------------------------------
# 2. Gemini 분석
# ---------------------------------------------------------------------------

VERDICTS = ["최선", "개선 가능", "더 쉬운 풀이 있음"]

RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "verdict": {"type": "STRING", "enum": VERDICTS},
        "my_complexity": {"type": "STRING"},
        "best_complexity": {"type": "STRING"},
        "summary": {"type": "STRING"},
        "good_points": {"type": "ARRAY", "items": {"type": "STRING"}},
        "improvements": {"type": "ARRAY", "items": {"type": "STRING"}},
        "better_code": {"type": "STRING"},
        "better_code_explanation": {"type": "STRING"},
    },
    "required": ["verdict", "my_complexity", "best_complexity", "summary", "good_points", "improvements",
                 "better_code", "better_code_explanation"],
}


def build_prompt(p: Problem) -> str:
    lang = LANG_FENCE.get(p.code_ext, "")
    return f"""당신은 코딩테스트를 준비하는 주니어 개발자의 풀이를 리뷰하는 시니어 개발자입니다.
아래 문제와 제출 코드를 보고 정확하게 판단하세요. 추측으로 단정하지 말고, 문제의 입력 제한을 근거로 판단하세요.

판단 기준
1. my_complexity: 제출 코드의 시간 복잡도 (빅오 표기 + 무엇 때문에 그런지 한 문장)
2. best_complexity: 이 문제에서 가능한 최선의 시간 복잡도 (빅오 표기 + 근거 한 문장)
3. verdict:
   - "최선": 복잡도와 접근이 모두 적절함
   - "개선 가능": 정답이지만 복잡도, 불필요한 코드, 입력 처리 등 고칠 점이 있음
   - "더 쉬운 풀이 있음": 훨씬 단순한 접근(내장 함수, 공식, 자료구조)이 있는데 어렵게 풀었음
4. summary: 판단 결과를 한국어 한 문장으로
5. good_points: 잘한 점 1~3개 (구체적으로)
6. improvements: 고칠 점 0~5개. 시간 복잡도, 불필요한 코드, 경계값, 입력 처리(예: split(" ") 대신 split()),
   제출 시 남아 있으면 안 되는 디버그 코드(예: sys.stdin = open(...)) 등. 없으면 빈 배열.
7. better_code: verdict가 "최선"이 아니면 더 나은 전체 코드(같은 언어), "최선"이면 빈 문자열
8. better_code_explanation: better_code가 왜 나은지 1~3문장, 없으면 빈 문자열

모든 설명은 한국어로, 초보자도 이해할 수 있게 쉽게 쓰세요.

[문제] {p.title} ({p.site} {p.tier}) {p.link}
[분류] {p.categories}
[성능] {p.performance}

{p.statement}

[제출 코드 ({p.language})]
```{lang}
{p.code}
```
"""


def call_gemini(prompt: str, api_key: str, model: str, retries: int = 4) -> dict:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
            "responseSchema": RESPONSE_SCHEMA,
        },
    }
    data = json.dumps(payload).encode()
    last_error = None
    for attempt in range(retries):
        req = urllib.request.Request(url, data=data, method="POST",
                                     headers={"Content-Type": "application/json", "x-goog-api-key": api_key})
        try:
            with urllib.request.urlopen(req, timeout=120) as res:
                body = json.loads(res.read())
            text = body["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text)
        except urllib.error.HTTPError as e:
            last_error = f"HTTP {e.code}: {e.read()[:300]!r}"
            if e.code not in (429, 500, 502, 503, 504):
                break
        except (KeyError, IndexError, json.JSONDecodeError, urllib.error.URLError, TimeoutError) as e:
            last_error = repr(e)
        time.sleep(15 * (attempt + 1))
    raise RuntimeError(f"Gemini 호출 실패: {last_error}")


def fake_analysis(p: Problem) -> dict:
    return {"verdict": "개선 가능", "my_complexity": "O(n) (드라이런)", "best_complexity": "O(n) (드라이런)",
            "summary": "드라이런이라 실제 분석은 하지 않았어요.", "good_points": ["드라이런 예시"],
            "improvements": ["실제 실행 시 Gemini 분석 결과가 들어가요."], "better_code": "",
            "better_code_explanation": ""}


# ---------------------------------------------------------------------------
# 3. 블로그 글 만들기
# ---------------------------------------------------------------------------

def cell(text: str) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ").strip()


def render_post(day: dt.date, problems: list[Problem]) -> str:
    counts = {v: sum(1 for p in problems if p.analysis.get("verdict") == v) for v in VERDICTS}
    lines = [
        "---",
        "layout: post",
        f'title: "{day.isoformat()} 코테 분석"',
        f"date: {day.isoformat()} 00:00:00 +0900",  # 미래 시각이면 Jekyll이 글을 숨겨서 자정으로 둔다
        "tags: [코테, 분석]",
        "---",
        "",
        f"{len(problems)}문제를 풀었어요. 최선 {counts['최선']} · 개선 가능 {counts['개선 가능']} · "
        f"더 쉬운 풀이 있음 {counts['더 쉬운 풀이 있음']}",
        "",
        "| 문제 | 사이트 · 난이도 | 내 풀이 | 최선 | 판정 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for p in problems:
        a = p.analysis
        anchor = f"p-{p.number or abs(hash(p.folder)) % 10**6}"
        lines.append(f"| [{cell(p.title)}](#{anchor}) | {cell(p.site)} {cell(p.tier)} | "
                     f"{cell(a.get('my_complexity', '').split(' ')[0])} | "
                     f"{cell(a.get('best_complexity', '').split(' ')[0])} | {cell(a.get('verdict', ''))} |")
    for p in problems:
        a = p.analysis
        anchor = f"p-{p.number or abs(hash(p.folder)) % 10**6}"
        fence = LANG_FENCE.get(p.code_ext, "")
        title = f"[{p.title}]({p.link})" if p.link else p.title
        lines += ["", f'<h2 id="{anchor}">{html.escape(p.title)}</h2>', "",
                  f"{title} · {p.site} {p.tier} · {p.language}", ""]
        if p.categories:
            lines += [f"**분류**: {p.categories}  ", ""]
        lines += [f"**판정: {a.get('verdict', '')}** — {a.get('summary', '')}", "",
                  f"- 내 풀이: {a.get('my_complexity', '')}",
                  f"- 최선: {a.get('best_complexity', '')}", ""]
        if a.get("good_points"):
            lines += ["**잘한 점**", ""] + [f"- {x}" for x in a["good_points"]] + [""]
        if a.get("improvements"):
            lines += ["**고칠 점**", ""] + [f"- {x}" for x in a["improvements"]] + [""]
        if a.get("better_code"):
            lines += ["**더 나은 풀이**", "", f"```{fence}", a["better_code"].rstrip(), "```", ""]
            if a.get("better_code_explanation"):
                lines += [a["better_code_explanation"], ""]
        lines += ['<details markdown="1">', "<summary>내 코드 보기</summary>", "", f"```{fence}",
                  p.code.rstrip(), "```", "", "</details>"]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def write_output(**values: str) -> None:
    path = os.environ.get("GITHUB_OUTPUT")
    for k, v in values.items():
        print(f"{k}={v}")
    if not path:
        return
    with open(path, "a", encoding="utf-8") as f:
        for k, v in values.items():
            f.write(f"{k}<<__EOF__\n{v}\n__EOF__\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default="", help="YYYY-MM-DD (KST). 비우면 어제")
    ap.add_argument("--repo-dir", default=".")
    ap.add_argument("--site-dir", required=True, help="gh-pages 작업 폴더")
    ap.add_argument("--base-url", default="", help="예: https://1juyoung.github.io/algorithm")
    ap.add_argument("--dry-run", action="store_true", help="Gemini를 호출하지 않고 글 형태만 확인")
    args = ap.parse_args()

    day = (dt.date.fromisoformat(args.date) if args.date.strip()
           else dt.datetime.now(KST).date() - dt.timedelta(days=1))
    repo = Path(args.repo_dir).resolve()
    problems = find_problems(repo, day)
    label = f"{day.month}/{day.day}"
    print(f"{day}: {len(problems)}문제", file=sys.stderr)

    if not problems:
        write_output(post_path="", count="0", title="오늘은 푼 문제가 없어요",
                     body=f"{label}에 올라온 풀이가 없어요. 내일은 한 문제라도 풀어봐요!", url=args.base_url)
        return 0

    api_key = os.environ.get("GEMINI_API_KEY", "")
    model = os.environ.get("GEMINI_MODEL") or DEFAULT_MODEL
    if not args.dry_run and not api_key:
        print("GEMINI_API_KEY가 없어요. --dry-run으로 실행하거나 시크릿을 등록하세요.", file=sys.stderr)
        return 1

    for i, p in enumerate(problems):
        if args.dry_run:
            p.analysis = fake_analysis(p)
            continue
        if i:
            time.sleep(6)  # 무료 티어 분당 요청 제한 여유
        try:
            p.analysis = call_gemini(build_prompt(p), api_key, model)
        except RuntimeError as e:
            print(f"[{p.title}] {e}", file=sys.stderr)
            p.analysis = {"verdict": "분석 실패", "my_complexity": "-", "best_complexity": "-",
                          "summary": "분석 중 오류가 나서 다음 실행에서 다시 확인이 필요해요.",
                          "good_points": [], "improvements": [], "better_code": "",
                          "better_code_explanation": ""}

    failed = sum(1 for p in problems if p.analysis.get("verdict") == "분석 실패")
    if failed == len(problems):
        print("모든 문제의 분석이 실패해서 글을 올리지 않아요. 위 오류를 확인하세요.", file=sys.stderr)
        return 1

    site = Path(args.site_dir)
    post = site / "_posts" / f"{day.isoformat()}-daily-review.md"
    post.parent.mkdir(parents=True, exist_ok=True)
    post.write_text(render_post(day, problems), encoding="utf-8")

    need_work = sum(1 for p in problems if p.analysis.get("verdict") in ("개선 가능", "더 쉬운 풀이 있음"))
    if need_work:
        body = f"{len(problems)}문제 중 {need_work}문제에 고칠 점이 있어요."
    elif failed:
        body = f"{len(problems)}문제 중 {failed}문제는 분석에 실패했어요."
    else:
        body = f"{len(problems)}문제 모두 최선의 풀이예요!"
    if failed and need_work:
        body += f" ({failed}문제는 분석 실패)"
    url = f"{args.base_url.rstrip('/')}/reviews/{day.isoformat()}/" if args.base_url else ""
    write_output(post_path=str(post), count=str(len(problems)),
                 title=f"{label} 코테 분석이 올라왔어요", body=body, url=url)
    return 0


if __name__ == "__main__":
    sys.exit(main())
