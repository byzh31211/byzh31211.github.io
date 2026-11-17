#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把带 TOML(+++) front matter 的 Markdown 编译成纯静态博客。

用法:    python build.py
输入:    仓库根目录下所有带 +++ 头的 .md
输出:    posts/<文件名>.html  +  index.html  +  about.html

不依赖任何框架, 不加 GitHub Actions, 生成的产物直接 push 即可。
"""

import html
import re
import shutil
import sys
import tomllib
from datetime import datetime
from pathlib import Path

import markdown

# ─────────────────────── 站点配置 (改这里就行) ───────────────────────
SITE_TITLE    = "byzh 的笔记本"
SITE_SUBTITLE = "AI 工具、Python 环境、深度学习，边踩坑边记"
SITE_AUTHOR   = "byzh"
SITE_URL      = "https://byzh31211.github.io"

STRIP_BODY_H1 = False   # True = 删掉正文第一行与标题重复的 H1
SHOW_CATEGORIES = True
SHOW_TAGS       = True

# 关于页正文 (Markdown)
ABOUT_MD = """
写点自己用得上的东西。

- 分类：AI 工具从入门到入土
- 环境：Python / PyTorch / Docker
- 站点：纯静态 HTML，`build.py` 编译，GitHub Pages 托管
"""

# CDN 资源 (想换镜像改这里即可)
HIGHLIGHT_JS  = "https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/highlight.min.js"
HIGHLIGHT_CSS = "https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/styles/github-dark.min.css"
MATHJAX_JS    = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-svg.js"
# ─────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent
POST_DIR = ROOT / "posts"

EMOJI = {
    ":art:": "🎨", ":pushpin:": "📌", ":gear:": "⚙️", ":bike:": "🚲",
    ":car:": "🚗", ":rocket:": "🚀", ":bulb:": "💡", ":warning:": "⚠️",
    ":book:": "📖", ":star:": "⭐", ":fire:": "🔥", ":memo:": "📝",
    ":package:": "📦", ":snake:": "🐍", ":bug:": "🐛", ":zap:": "⚡",
    ":framed_picture:": "🖼", ":white_check_mark:": "✅", ":x:": "❌",
}

FRONT_RE = re.compile(r"^\+\+\+\r?\n(.*?)\r?\n\+\+\+\r?\n", re.S)
CODE_RE  = re.compile(r"(```.*?```)", re.S)

PAGE = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{TITLE}}</title>
<meta name="description" content="{{DESC}}">
<link rel="stylesheet" href="{{ROOT}}style.css">
<link rel="stylesheet" href="{{HL_CSS}}">
{{HEAD_EXTRA}}
</head>
<body>
<header class="site-head">
  <a class="brand" href="{{ROOT}}index.html">{{SITE_TITLE}}</a>
  <nav>
    <a href="{{ROOT}}index.html">文章</a>
    <a href="{{ROOT}}about.html">关于</a>
  </nav>
</header>
<main>
{{MAIN}}
</main>
<footer class="site-foot">
  <p>© {{YEAR}} {{AUTHOR}} · <a href="{{SITE_URL}}">{{SITE_URL}}</a></p>
  <p class="built">由 build.py 生成</p>
</footer>
<script src="{{HL_JS}}"></script>
<script>if (window.hljs) hljs.highlightAll();</script>
{{BODY_EXTRA}}
</body>
</html>
"""


def _outside_code(text: str, fn) -> str:
    """对代码块之外的片段应用 fn, 代码块原样保留。"""
    parts = CODE_RE.split(text)
    for i in range(0, len(parts), 2):          # 偶数下标 = 非代码段
        parts[i] = fn(parts[i])
    return "".join(parts)


def _replace_emoji(seg: str) -> str:
    for k, v in EMOJI.items():
        seg = seg.replace(k, v)
    return seg


def emoji_outside_code(text: str) -> str:
    """只替换代码块之外的 emoji 短代码, 避免破坏代码内容。"""
    return _outside_code(text, _replace_emoji)


def preprocess(text: str) -> str:
    """非代码段: 转 emoji, 并把 CSDN 风格的 @[TOC] 换成 Markdown 目录标记。"""
    def fn(seg: str) -> str:
        seg = _replace_emoji(seg)
        return re.sub(r"^[ \t]*@?\[toc\][ \t]*$", "[TOC]", seg, flags=re.I | re.M)
    return _outside_code(text, fn)


def esc_title(text: str) -> str:
    """标题转义, 但保留 `inline code` 的反引号语义。"""
    out = html.escape(str(text), quote=False)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", out)


def parse_date(value) -> datetime:
    if isinstance(value, str):
        m = re.match(r"(\d{4})-(\d{1,2})-(\d{1,2})", value.strip())
        if m:
            y, mo, d = (int(x) for x in m.groups())
            try:
                return datetime(y, mo, d)
            except ValueError:
                pass
    return datetime(1970, 1, 1)


def render_page(*, title, desc, main, depth, year, extra_head="", extra_body=""):
    out = PAGE
    for k, v in {
        "{{TITLE}}": title,
        "{{DESC}}": html.escape(desc, quote=True),
        "{{MAIN}}": main,
        "{{ROOT}}": "../" * depth,
        "{{YEAR}}": str(year),
        "{{AUTHOR}}": SITE_AUTHOR,
        "{{SITE_TITLE}}": SITE_TITLE,
        "{{SITE_URL}}": SITE_URL,
        "{{HL_JS}}": HIGHLIGHT_JS,
        "{{HL_CSS}}": HIGHLIGHT_CSS,
        "{{HEAD_EXTRA}}": extra_head,
        "{{BODY_EXTRA}}": extra_body,
    }.items():
        out = out.replace(k, v)
    return out


def load_source(path: Path):
    """返回 (front_matter, body) 或 None (不是博客文章)。"""
    text = path.read_text(encoding="utf-8-sig")
    m = FRONT_RE.match(text)
    if not m:
        return None
    try:
        fm = tomllib.loads(m.group(1))
    except tomllib.TOMLDecodeError as e:
        print(f"  [跳过] {path.name}: front matter 解析失败 -> {e}")
        return None
    return fm, text[m.end():]


def strip_leading_h1(body: str) -> str:
    lines = body.lstrip("\r\n").splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    return "\n".join(lines).lstrip("\r\n")


def build():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    year = datetime.now().year

    if POST_DIR.exists():
        shutil.rmtree(POST_DIR)
    POST_DIR.mkdir(parents=True)

    md = markdown.Markdown(
        extensions=["fenced_code", "tables", "toc", "sane_lists", "attr_list"],
        extension_configs={"toc": {"anchorlink": False, "title": "目录"}},
    )

    posts = []
    for path in sorted(ROOT.glob("*.md")):
        loaded = load_source(path)
        if loaded is None:
            continue
        fm, body = loaded
        if fm.get("draft", False):
            print(f"  [草稿] {path.name}")
            continue

        slug = path.stem
        title_raw = str(fm.get("title") or slug)
        title = emoji_outside_code(title_raw)
        title = re.sub(r"([^\s])([\U0001F000-\U0001FAFF\u2600-\u27BF])", r"\1 \2", title)
        date = parse_date(fm.get("date"))
        cats = [emoji_outside_code(str(c)) for c in fm.get("categories") or []]
        tags = [emoji_outside_code(str(t)) for t in fm.get("tags") or []]

        source = body
        if STRIP_BODY_H1:
            source = strip_leading_h1(source)
        md.reset()
        content = md.convert(preprocess(source))

        meta_bits = [f'<time datetime="{date:%Y-%m-%d}">{date:%Y-%m-%d}</time>']
        if SHOW_CATEGORIES and cats:
            meta_bits.append(" · ".join(f'<span class="cat">{esc_title(c)}</span>' for c in cats))
        if SHOW_TAGS and tags:
            meta_bits.append(" · ".join(f'<span class="tag">#{esc_title(t)}</span>' for t in tags))

        main = (
            '<article class="post">\n'
            f'<h1>{esc_title(title)}</h1>\n'
            f'<p class="meta">{" · ".join(meta_bits)}</p>\n'
            f"{content}\n"
            "</article>\n"
            '<p class="back"><a href="../index.html">← 返回首页</a></p>'
        )

        extra_body = ""
        if fm.get("math", False) and ("$$" in source or "\\[" in source):
            extra_body = f'<script async src="{MATHJAX_JS}"></script>'

        page = render_page(
            title=f"{title} · {SITE_TITLE}",
            desc=title,
            main=main,
            depth=1,
            year=year,
            extra_body=extra_body,
        )
        (POST_DIR / f"{slug}.html").write_text(page, encoding="utf-8")
        posts.append({
            "slug": slug, "title": title, "date": date,
            "cats": cats, "tags": tags,
            "words": len(re.sub(r"\s", "", source)),
        })
        print(f"  [生成] posts/{slug}.html  ({title_raw})")

    posts.sort(key=lambda p: (p["date"], p["title"]), reverse=True)

    items = []
    for p in posts:
        cat = f'<span class="cat">{esc_title(p["cats"][0])}</span>' if p["cats"] else ""
        items.append(
            '<li>\n'
            f'  <a href="posts/{p["slug"]}.html">\n'
            f'    <time datetime="{p["date"]:%Y-%m-%d}">{p["date"]:%Y-%m-%d}</time>\n'
            f'    <span class="ptitle">{esc_title(p["title"])}</span>\n'
            "  </a>\n"
            f'  <span class="li-meta">{cat} <span class="words">{p["words"]} 字</span></span>\n'
            "</li>"
        )

    items_html = "\n".join(items)
    home_main = (
        f'<h1 class="home-title">{esc_title(SITE_TITLE)}</h1>\n'
        f'<p class="home-sub">{html.escape(SITE_SUBTITLE)}</p>\n'
        f'<ul class="post-list">\n{items_html}\n</ul>'
    )
    (ROOT / "index.html").write_text(
        render_page(
            title=SITE_TITLE, desc=SITE_SUBTITLE, main=home_main,
            depth=0, year=year,
        ),
        encoding="utf-8",
    )

    md.reset()
    about_main = (
        '<article class="post">\n<h1>关于</h1>\n'
        + md.convert(emoji_outside_code(ABOUT_MD.strip()))
        + "\n</article>"
    )
    (ROOT / "about.html").write_text(
        render_page(title=f"关于 · {SITE_TITLE}", desc="关于", main=about_main,
                    depth=0, year=year),
        encoding="utf-8",
    )

    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
    print(f"\n完成: {len(posts)} 篇文章 -> posts/  +  index.html  +  about.html")


if __name__ == "__main__":
    build()
