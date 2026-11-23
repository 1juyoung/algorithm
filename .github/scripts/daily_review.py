"""그날 BaekjoonHub로 올라온 풀이를 찾아 Gemini로 분석하고 site/data/날짜.json으로 저장한다.

사용 예:
    python .github/scripts/daily_review.py --date 2026-11-22 --site-dir site
    python .github/scripts/daily_review.py --date 2026-11-22 --site-dir site --dry-run

결과는 GITHUB_OUTPUT(있으면)에 data_path, count, title, body, url 로 기록한다.
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
# 무료 티어(결제 계정 없음)로 쓸 수 있는 텍스트 모델만, 앞에서부터 시도한다.
# 바꾸려면 레포 Variables에 GEMINI_MODEL을 등록하면 그 모델을 맨 앞에 둔다.
FREE_MODELS = ["gemini-3.6-flash", "gemini-3.8-flash", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite"]
DEFAULT_MODEL = FREE_MODELS[0]
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

# 블로그 첫 화면 "내가 자주 막히는 곳" 막대그래프에 쓰는 고정 태그
WEAK_TAGS = ["시간복잡도 계산", "자료구조 선택", "경계값 처리", "입력 처리", "문법 · 내장 함수", "구현 · 시뮬레이션",
             "수학 · 공식", "정렬", "해시", "스택 · 큐", "투 포인터 · 슬라이딩 윈도우", "이분 탐색", "재귀 · 백트래킹",
             "그리디", "DP", "그래프 탐색"]

RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "problem_summary": {"type": "STRING"},
        "intended_approach": {"type": "STRING"},
        "approach_match": {"type": "BOOLEAN"},
        "verdict": {"type": "STRING", "enum": VERDICTS},
        "my_time": {"type": "STRING"},
        "best_time": {"type": "STRING"},
        "my_space": {"type": "STRING"},
        "best_space": {"type": "STRING"},
        "complexity_note": {"type": "STRING"},
        "summary": {"type": "STRING"},
        "good_points": {"type": "ARRAY", "items": {"type": "STRING"}},
        "comments": {"type": "ARRAY", "items": {
            "type": "OBJECT",
            "properties": {"title": {"type": "STRING"}, "body": {"type": "STRING"}},
            "required": ["title", "body"]}},
        "weaknesses": {"type": "ARRAY", "items": {
            "type": "OBJECT",
            "properties": {"tag": {"type": "STRING", "enum": WEAK_TAGS}, "reason": {"type": "STRING"}},
            "required": ["tag", "reason"]}},
        "better_summary": {"type": "STRING"},
        "better_code": {"type": "STRING"},
    },
    "required": ["problem_summary", "intended_approach", "approach_match", "verdict", "my_time", "best_time", "my_space", "best_space", "complexity_note",
                 "summary", "good_points", "comments", "weaknesses", "better_summary", "better_code"],
}


def build_prompt(p: Problem) -> str:
    lang = LANG_FENCE.get(p.code_ext, "")
    return f"""너는 코딩테스트를 준비하는 주니어 개발자의 풀이를 리뷰하는 시니어 개발자야.
아래 문제와 제출 코드를 보고 정확하게 판단해. 추측으로 단정하지 말고 문제의 입력 제한을 근거로 판단해.
제출 코드는 이미 정답 처리된 코드야.

필드
- problem_summary: 문제를 한 문장으로 요약 (입력 범위가 중요하면 포함)
- verdict: "최선"(복잡도와 접근 모두 적절) / "개선 가능"(복잡도·불필요한 코드·입력 처리 등 고칠 점 있음)
  / "더 쉬운 풀이 있음"(내장 함수·공식·자료구조로 훨씬 단순하게 풀 수 있는데 어렵게 풀었음)
- my_time, best_time, my_space, best_space: 빅오 표기만 (예: "O(N log N)"). 설명은 넣지 마.
- complexity_note: 내 풀이 복잡도가 왜 그런지, 입력 최대 크기에서 대략 몇 번 연산인지 2~3문장
- intended_approach: 이 문제를 푸는 정석 방법을 "이 문제는 ~로 푸는 문제야." 형태로 1~2문장.
  어떤 알고리즘·자료구조를 쓰는지, 핵심 아이디어가 무엇인지 포함해.
- approach_match: 제출 코드가 intended_approach와 같은 방식(또는 그만큼 좋은 방식)으로 풀었으면 true, 아니면 false
- summary: approach_match가 true면 "맞아, ~로 풀었어."로 시작하고, false면 "하지만 너는 ~로 풀었어."로 시작해서
  실제로 어떻게 풀었는지와 정석과 무엇이 다른지 1~2문장
- good_points: 잘한 점 1~3개, 짧고 구체적으로
- comments: 고칠 점 0~4개. title은 짧은 제목, body는 1~2문장. 시간 복잡도, 불필요한 코드, 경계값,
  입력 처리(예: split(" ") 대신 split()), 제출하면 안 되는 디버그 코드(예: sys.stdin = open(...)) 등. 없으면 빈 배열.
- weaknesses: 이 풀이에서 드러난 약점 0~2개. tag는 정해진 목록에서만 고르고, reason은 1문장.
  실제로 문제가 된 것만 골라: 시간·공간 복잡도를 나쁘게 만들었거나, 풀이를 불필요하게 복잡하게 만든 원인일 때만.
  변수 이름, 들여쓰기, str(input()) 같은 사소한 것은 comments에만 쓰고 weaknesses에는 넣지 마.
  verdict가 "최선"이면 반드시 빈 배열.
- better_summary: verdict가 "최선"이 아니면 더 나은 풀이의 핵심 아이디어 1~2문장, "최선"이면 빈 문자열
- better_code: verdict가 "최선"이 아니면 더 나은 전체 코드(같은 언어), "최선"이면 빈 문자열

말투는 친한 선배처럼 반말로, 초보자도 이해할 수 있게 쉽게 써. (예: "매번 다시 더하고 있어.")

[문제] {p.title} ({p.site} {p.tier}) {p.link}
[분류] {p.categories}
[성능] {p.performance}

{p.statement}

[제출 코드 ({p.language})]
```{lang}
{p.code}
```
"""


API_BASE = "https://generativelanguage.googleapis.com/v1beta"


def candidate_models(preferred: str) -> list[str]:
    """선호 모델을 먼저, 그다음 무료 모델을 순서대로 돌려준다."""
    return [preferred] + [m for m in FREE_MODELS if m != preferred]


def call_gemini_any(prompt: str, api_key: str, models: list[str]) -> tuple[dict, str]:
    """앞 모델이 바쁘거나(503/429) 없으면(404) 다음 모델로 넘어간다."""
    errors = []
    for model in models:
        try:
            return call_gemini(prompt, api_key, model), model
        except RuntimeError as e:
            errors.append(f"{model}: {e}")
            print(f"  {model} 실패, 다음 모델 시도 → {str(e)[:120]}", file=sys.stderr)
    raise RuntimeError(" / ".join(errors)[:600])


def call_gemini(prompt: str, api_key: str, model: str, retries: int = 2) -> dict:
    url = f"{API_BASE}/models/{model}:generateContent"
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
        if attempt < retries - 1:
            time.sleep(10)
    raise RuntimeError(f"Gemini 호출 실패: {last_error}")


def fake_analysis(p: Problem) -> dict:
    return {"problem_summary": "드라이런용 문제 요약이야.",
            "intended_approach": "이 문제는 슬라이딩 윈도우로 푸는 문제야.", "approach_match": False,
            "verdict": "개선 가능", "my_time": "O(N·K)",
            "best_time": "O(N)", "my_space": "O(K)", "best_space": "O(1)",
            "complexity_note": "드라이런이라 실제 분석은 하지 않았어.", "summary": "하지만 너는 매번 구간 합을 다시 구했어.",
            "good_points": ["입력을 빠르게 받았어"],
            "comments": [{"title": "겹치는 구간을 다시 더함", "body": "빠지는 값 하나, 들어오는 값 하나만 반영하면 돼."}],
            "weaknesses": [{"tag": "시간복잡도 계산", "reason": "제출 전에 최악의 연산 횟수를 계산하지 않았어."}],
            "better_summary": "처음 K개 합을 구하고 한 칸씩 밀면서 갱신해.", "better_code": "print('better')"}


# ---------------------------------------------------------------------------
# 3. 날짜별 데이터 저장 (화면은 build_site.py가 만든다)
# ---------------------------------------------------------------------------

SITE_CODE = {"백준": "boj", "프로그래머스": "pgs"}


def to_record(day: dt.date, i: int, p: Problem) -> dict:
    slug = f"{day.isoformat()}-{SITE_CODE.get(p.site, 'p')}-{p.number or i + 1}"
    return {"slug": slug, "date": day.isoformat(), "title": p.title, "tier": p.tier, "number": p.number,
            "link": p.link, "site": p.site, "language": p.language, "categories": p.categories,
            "performance": p.performance, "code": p.code, "code_ext": p.code_ext, "folder": p.folder,
            "analysis": p.analysis}


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
    ap.add_argument("--skip-if-exists", action="store_true", help="그날 글이 이미 있으면 아무것도 하지 않음(재시도 실행용)")
    args = ap.parse_args()

    day = (dt.date.fromisoformat(args.date) if args.date.strip()
           else dt.datetime.now(KST).date() - dt.timedelta(days=1))
    repo = Path(args.repo_dir).resolve()
    data_file = Path(args.site_dir) / "data" / f"{day.isoformat()}.json"
    if args.skip_if_exists and data_file.exists():
        print(f"{day} 글이 이미 있어서 건너뛰어요.", file=sys.stderr)
        write_output(skip="1", data_path="", count="", title="", body="", url="")
        return 0
    problems = find_problems(repo, day)
    label = f"{day.month}/{day.day}"
    print(f"{day}: {len(problems)}문제", file=sys.stderr)

    if not problems:
        write_output(data_path="", count="0", title="오늘은 푼 문제가 없어요",
                     body=f"{label}에 올라온 풀이가 없어요. 내일은 한 문제라도 풀어봐요!", url=args.base_url)
        return 0

    api_key = os.environ.get("GEMINI_API_KEY", "")
    model = os.environ.get("GEMINI_MODEL") or DEFAULT_MODEL
    if not args.dry_run and not api_key:
        print("GEMINI_API_KEY가 없어요. --dry-run으로 실행하거나 시크릿을 등록하세요.", file=sys.stderr)
        return 1

    models = [] if args.dry_run else candidate_models(model)
    if models:
        print(f"사용할 모델 순서: {', '.join(models)}", file=sys.stderr)
    for i, p in enumerate(problems):
        if args.dry_run:
            p.analysis = fake_analysis(p)
            continue
        if i:
            time.sleep(6)  # 무료 티어 분당 요청 제한 여유
        try:
            p.analysis, used = call_gemini_any(build_prompt(p), api_key, models)
            if p.analysis.get("verdict") == "최선":
                p.analysis["weaknesses"] = []
            print(f"[{p.title}] {used}로 분석 완료", file=sys.stderr)
            if used != models[0]:  # 성공한 모델을 다음 문제부터 먼저 쓴다
                models.remove(used)
                models.insert(0, used)
        except RuntimeError as e:
            print(f"[{p.title}] {e}", file=sys.stderr)
            p.analysis = {"verdict": "분석 실패", "problem_summary": "", "intended_approach": "",
                          "approach_match": True, "my_time": "-", "best_time": "-",
                          "my_space": "-", "best_space": "-", "complexity_note": "",
                          "summary": "분석 중 오류가 나서 다시 확인이 필요해.", "good_points": [], "comments": [],
                          "weaknesses": [], "better_summary": "", "better_code": ""}

    failed = sum(1 for p in problems if p.analysis.get("verdict") == "분석 실패")
    if failed == len(problems):
        print("모든 문제의 분석이 실패해서 글을 올리지 않아요. 위 오류를 확인하세요.", file=sys.stderr)
        return 1

    data_file.parent.mkdir(parents=True, exist_ok=True)
    records = [to_record(day, i, p) for i, p in enumerate(problems)]
    data_file.write_text(json.dumps({"date": day.isoformat(), "problems": records}, ensure_ascii=False, indent=2),
                         encoding="utf-8")

    need_work = sum(1 for p in problems if p.analysis.get("verdict") in ("개선 가능", "더 쉬운 풀이 있음"))
    if need_work:
        body = f"{len(problems)}문제 중 {need_work}문제에 고칠 점이 있어요."
    elif failed:
        body = f"{len(problems)}문제 중 {failed}문제는 분석에 실패했어요."
    else:
        body = f"{len(problems)}문제 모두 최선의 풀이예요!"
    if failed and need_work:
        body += f" ({failed}문제는 분석 실패)"
    url = f"{args.base_url.rstrip('/')}/" if args.base_url else ""
    write_output(data_path=str(data_file), count=str(len(problems)),
                 title=f"{label} 코테 분석이 올라왔어요", body=body, url=url)
    return 0


if __name__ == "__main__":
    sys.exit(main())
