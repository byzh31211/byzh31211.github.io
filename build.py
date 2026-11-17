#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""静态博客编译器。

源文件:  notes/*.md       (TOML 风格 +++ front matter)
产物:    index.html  archives.html  search.html  index.json  about.html
         posts/*.html  categories/*.html  tags/*.html

零框架 / 零 npm / 零 GitHub Actions，产物直接 push 即可。
"""

import html
import json
import re
import shutil
import sys
import tomllib
from datetime import datetime
from pathlib import Path
from urllib.parse import quote, unquote

import markdown

# ───────────────────── 站点配置 (改这里) ─────────────────────
SITE_TITLE    = "byzh 的笔记本"
SITE_SUBTITLE = "AI 工具、Python 环境、深度学习，边踩坑记"
SITE_AUTHOR   = "byzh"
SITE_URL      = "https://byzh31211.github.io"

SRC_DIR       = "notes"    # Markdown 源文件目录
STRIP_BODY_H1 = False      # True = 删掉正文第一行与标题重复的 H1
WORDS_PER_MIN = 400        # 阅读速度, 用于估算阅读时间

# 关于页正文 (Markdown)
ABOUT_MD = """
写点自己用得上的东西。

- 分类：AI 工具从入门到入土
- 环境：Python / PyTorch / Docker
- 站点：纯静态 HTML，`build.py` 编译，GitHub Pages 托管
"""

# CDN 资源（想换镜像改这里）
HIGHLIGHT_JS  = "https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/highlight.min.js"
HIGHLIGHT_CSS = "https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/styles/github-dark.min.css"
MATHJAX_JS    = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-svg.js"
# ─────────────────────────────────────────────────────────────

ROOT     = Path(__file__).resolve().parent
SRC      = ROOT / SRC_DIR
POST_DIR = ROOT / "posts"
CAT_DIR  = ROOT / "categories"
TAG_DIR  = ROOT / "tags"

EMOJI = {
    ":art:": "🎨", ":pushpin:": "📌", ":gear:": "⚙️", ":bike:": "🚲",
    ":car:": "🚗", ":rocket:": "🚀", ":bulb:": "💡", ":warning:": "⚠️",
    ":book:": "📖", ":star:": "⭐", ":fire:": "🔥", ":memo:": "📝",
    ":package:": "📦", ":snake:": "🐍", ":bug:": "🐛", ":zap:": "⚡",
    ":framed_picture:": "🖼", ":white_check_mark:": "✅", ":x:": "❌",
}

FRONT_RE = re.compile(r"^\+\+\+\r?\n(.*?)\r?\n\+\+\+\r?\n", re.S)
CODE_RE  = re.compile(r"(```.*?```)", re.S)
TAG_RE   = re.compile(r"<[^>]+>")

SITE_JS = """<script>
(function () {
  var root = document.documentElement;
  var btn  = document.querySelector('.theme-btn');
  var mq   = window.matchMedia('(prefers-color-scheme: dark)');
  function current() { return root.getAttribute('data-theme') || (mq.matches ? 'dark' : 'light'); }
  function paint()   { btn.textContent = current() === 'dark' ? '☀️' : '🌙'; }
  paint();
  btn.addEventListener('click', function () {
    var next = current() === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    try { localStorage.setItem('theme', next); } catch (e) {}
    paint();
  });
  mq.addEventListener('change', paint);
})();

(function () {
  var side = document.querySelector('.toc-side');
  if (!side) return;
  var links = [].slice.call(side.querySelectorAll('a[href^="#"]'));
  if (links.length < 3) return;
  var map = {}, current = null;
  links.forEach(function (a) { map[decodeURIComponent(a.hash.slice(1))] = a; });
  var heads = [].slice.call(document.querySelectorAll('.post h1[id], .post h2[id], .post h3[id]'))
    .filter(function (h) { return map[h.id]; });
  if (!heads.length) return;
  function onScroll() {
    var found = heads[0];
    for (var i = 0; i < heads.length; i++) {
      if (heads[i].getBoundingClientRect().top <= 120) found = heads[i];
    }
    if (found === current) return;
    if (current) current.classList.remove('active');
    current = found;
    var a = map[found.id];
    if (a) a.classList.add('active');
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
})();
</script>"""

PAGE = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{TITLE}}</title>
<meta name="description" content="{{DESC}}">
<script>(function(){try{var t=localStorage.getItem('theme');if(t)document.documentElement.setAttribute('data-theme',t);}catch(e){}})();</script>
<link rel="stylesheet" href="{{ROOT}}style.css">
<link rel="stylesheet" href="{{HL_CSS}}">
{{HEAD_EXTRA}}
</head>
<body>
<header class="site-head">
  <a class="brand" href="{{ROOT}}index.html">{{SITE_TITLE}}</a>
  <nav>
    <a href="{{ROOT}}index.html">文章</a>
    <a href="{{ROOT}}categories/index.html">分类</a>
    <a href="{{ROOT}}tags/index.html">标签</a>
    <a href="{{ROOT}}archives.html">归档</a>
    <a href="{{ROOT}}search.html">搜索</a>
    <a href="{{ROOT}}about.html">关于</a>
  </nav>
  <button class="theme-btn" type="button" title="切换深色模式" aria-label="切换深色模式">🌙</button>
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


# ───────────────────────── 工具函数 ─────────────────────────

def _outside_code(text: str, fn) -> str:
    """对代码块之外的片段应用 fn，代码块原样保留。"""
    parts = CODE_RE.split(text)
    for i in range(0, len(parts), 2):
        parts[i] = fn(parts[i])
    return "".join(parts)


def _replace_emoji(seg: str) -> str:
    for k, v in EMOJI.items():
        seg = seg.replace(k, v)
    return seg


def emoji_outside_code(text: str) -> str:
    return _outside_code(text, _replace_emoji)


def preprocess(text: str) -> str:
    """非代码段：转 emoji，去掉 CSDN 的 @[TOC] 标记（目录改由侧栏渲染）。"""
    def fn(seg: str) -> str:
        seg = _replace_emoji(seg)
        return re.sub(r"^[ \t]*@?\[toc\][ \t]*$\r?\n?", "", seg, flags=re.I | re.M)
    return _outside_code(text, fn)


def esc(text: str) -> str:
    return html.escape(str(text), quote=False)


def esc_title(text: str) -> str:
    """标题转义，但保留 `inline code` 的反引号语义。"""
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", esc(text))


def parse_date(value) -> datetime:
    if isinstance(value, str):
        m = re.match(r"(\d{4})-(\d{1,2})-(\d{1,2})", value.strip())
        if m:
            try:
                return datetime(*(int(x) for x in m.groups()))
            except ValueError:
                pass
    return datetime(1970, 1, 1)


def u(name: str) -> str:
    """中文文件名 -> URL 编码。"""
    return quote(str(name))


def read_minutes(words: int) -> int:
    return max(1, round(words / WORDS_PER_MIN))


def render_page(*, title, desc, main, depth, year,
                head_extra="", body_extra=""):
    out = PAGE
    for k, v in {
        "{{TITLE}}": title,
        "{{DESC}}": html.escape(str(desc), quote=True),
        "{{MAIN}}": main,
        "{{ROOT}}": "../" * depth,
        "{{YEAR}}": str(year),
        "{{AUTHOR}}": SITE_AUTHOR,
        "{{SITE_TITLE}}": SITE_TITLE,
        "{{SITE_URL}}": SITE_URL,
        "{{HL_JS}}": HIGHLIGHT_JS,
        "{{HL_CSS}}": HIGHLIGHT_CSS,
        "{{HEAD_EXTRA}}": head_extra,
        "{{BODY_EXTRA}}": SITE_JS + ("\n" + body_extra if body_extra else ""),
    }.items():
        out = out.replace(k, v)
    return out


def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# ───────────────────────── 片段渲染 ─────────────────────────

def cat_links(post, depth=0) -> str:
    prefix = "../" * depth
    return " ".join(
        f'<a class="cat" href="{prefix}categories/{u(c)}.html">{esc(c)}</a>'
        for c in post["cats"]
    )


def tag_links(post, depth=0) -> str:
    prefix = "../" * depth
    return " ".join(
        f'<a class="tag" href="{prefix}tags/{u(t)}.html">#{esc(t)}</a>'
        for t in post["tags"]
    )


def post_list(posts, depth=0, show_meta=True, limit=None,
              show_cats=True, show_tags=True) -> str:
    prefix = "../" * depth
    items = []
    for p in (posts[:limit] if limit else posts):
        bits = [f"{p['words']} 字 · 约 {read_minutes(p['words'])} 分钟"]
        extra = " ".join(x for x in (
            cat_links(p, depth) if show_cats else "",
            tag_links(p, depth) if show_tags else "",
        ) if x)
        meta = " · ".join(bits + ([extra] if extra else []))
        items.append(
            "<li>\n"
            f'  <a class="row" href="{prefix}posts/{p["slug"]}.html">\n'
            f'    <time datetime="{p["date"]:%Y-%m-%d}">{p["date"]:%Y-%m-%d}</time>\n'
            f'    <span class="ptitle">{p["title_html"]}</span>\n'
            "  </a>\n"
            + (f'  <span class="li-meta">{meta}</span>\n' if show_meta else "")
            + "</li>"
        )
    return '<ul class="post-list">\n' + "\n".join(items) + "\n</ul>"


def chips(mapping, kind, depth=0, empty_hint="") -> str:
    prefix = "../" * depth
    if not mapping:
        return f'<p class="muted">{esc(empty_hint)}</p>'
    parts = []
    for name, items in mapping:
        parts.append(
            f'<li><a href="{prefix}{kind}/{u(name)}.html">{esc(name)}'
            f'<span class="n">{len(items)}</span></a></li>'
        )
    return '<ul class="chips">\n' + "\n".join(parts) + "\n</ul>"


# ───────────────────────── 主流程 ─────────────────────────

def load_posts(md: markdown.Markdown):
    posts = []
    if not SRC.exists():
        print(f"源目录不存在: {SRC}")
        return posts

    for path in sorted(SRC.glob("*.md")):
        text = path.read_text(encoding="utf-8-sig")
        m = FRONT_RE.match(text)
        if not m:
            continue
        try:
            fm = tomllib.loads(m.group(1))
        except tomllib.TOMLDecodeError as e:
            print(f"  [跳过] {path.name}: front matter 解析失败 -> {e}")
            continue
        if fm.get("draft", False):
            print(f"  [草稿] {path.name}")
            continue

        slug = path.stem
        body = text[m.end():]
        if STRIP_BODY_H1:
            body = "\n".join(body.lstrip("\r\n").splitlines()[1:]) \
                if body.lstrip("\r\n").startswith("# ") else body

        title_raw = str(fm.get("title") or slug)
        title_plain = re.sub(r"([^\s])([\U0001F000-\U0001FAFF\u2600-\u27BF])",
                             r"\1 \2", emoji_outside_code(title_raw))
        cats = [emoji_outside_code(str(c)) for c in fm.get("categories") or []]
        tags = [emoji_outside_code(str(t)) for t in fm.get("tags") or []]
        date = parse_date(fm.get("date"))

        md.reset()
        content = md.convert(preprocess(body))
        toc = re.sub(r'<span class="toctitle">.*?</span>', "", md.toc, flags=re.S)

        plain = html.unescape(TAG_RE.sub(" ", content))
        plain = re.sub(r"\s+", " ", plain).strip()

        posts.append({
            "slug": slug,
            "title": title_raw,
            "title_plain": title_plain,
            "title_html": esc_title(title_plain),
            "date": date,
            "cats": cats,
            "tags": tags,
            "content": content,
            "toc": toc,
            "toc_count": toc.count("<li>"),
            "words": len(re.sub(r"\s", "", preprocess(body))),
            "plain": plain[:4000],
            "math": bool(fm.get("math")) and ("$$" in body or "\\[" in body),
        })

    posts.sort(key=lambda p: (p["date"], p["title"]), reverse=True)
    return posts


def build_post(p, year):
    toc_html = ""
    if p["toc_count"] >= 3:
        toc_html = (
            '<details class="toc-mobile">\n<summary>目录</summary>\n'
            f'{p["toc"]}\n</details>\n'
        )

    meta = [f'<time datetime="{p["date"]:%Y-%m-%d}">{p["date"]:%Y-%m-%d}</time>',
            f'{p["words"]} 字 · 约 {read_minutes(p["words"])} 分钟']
    if p["cats"]:
        meta.append(cat_links(p, 1))
    if p["tags"]:
        meta.append(tag_links(p, 1))

    article = (
        '<article class="post">\n'
        f'<h1>{p["title_html"]}</h1>\n'
        f'<p class="meta">{" · ".join(meta)}</p>\n'
        f"{toc_html}"
        f'{p["content"]}\n'
        "</article>\n"
        '<p class="back"><a href="../index.html">← 返回首页</a></p>'
    )

    aside = ""
    has_toc = bool(toc_html)
    if has_toc:
        aside = (
            '<aside class="toc-side">\n<p class="toc-title">目录</p>\n'
            f'{p["toc"]}\n</aside>\n'
        )

    main = (
        f'<div class="post-wrap{" has-toc" if has_toc else ""}">\n'
        f'<div class="post-main">\n{article}</div>\n{aside}</div>'
    )

    body_extra = ""
    if p["math"]:
        body_extra = f'<script async src="{MATHJAX_JS}"></script>'

    write(POST_DIR / f'{p["slug"]}.html', render_page(
        title=f'{html.escape(p["title_plain"])} · {SITE_TITLE}',
        desc=p["title_plain"],
        main=main,
        depth=1,
        year=year,
        body_extra=body_extra,
    ))
    print(f'  [文章] posts/{p["slug"]}.html')


def build_home(posts, cats, tags, year):
    sections = [
        f'<h1 class="home-title">{esc_title(SITE_TITLE)}</h1>',
        f'<p class="home-sub">{esc(SITE_SUBTITLE)}</p>',
        '<h2 class="sec-title">最新文章</h2>',
        post_list(posts),
        '<h2 class="sec-title">分类</h2>',
        chips(cats, "categories", 0, "还没有分类"),
        '<h2 class="sec-title">标签</h2>',
        chips(tags, "tags", 0, "还没有标签 —— 在 notes/*.md 的 tags 里加上词即可自动生成"),
    ]
    write(ROOT / "index.html", render_page(
        title=SITE_TITLE, desc=SITE_SUBTITLE,
        main='<div class="container">\n' + "\n".join(sections) + "\n</div>",
        depth=0, year=year,
    ))


def build_categories(cats, year):
    secs = ['<h1 class="page-title">分类</h1>']
    if cats:
        secs.append(chips(cats, "categories", 1, ""))
        for name, items in cats:
            secs.append(
                f'<section class="term">\n'
                f'<h2>{esc(name)} <span class="n">{len(items)} 篇</span></h2>\n'
                f'{post_list(items, 1, show_cats=False)}\n</section>'
            )
    else:
        secs.append('<p class="muted">还没有任何分类。</p>')
    write(CAT_DIR / "index.html", render_page(
        title=f"分类 · {SITE_TITLE}",
        desc="全部分类",
        main='<div class="container">\n' + "\n".join(secs) + "\n</div>",
        depth=1, year=year,
    ))

    for name, items in cats:
        write(CAT_DIR / f"{name}.html", render_page(
            title=f"分类：{name} · {SITE_TITLE}",
            desc=f"{name} 分类下的全部文章",
            main=(
                '<div class="container">\n'
                f'<h1 class="page-title">分类：{esc(name)}</h1>\n'
                f'<p class="muted">{len(items)} 篇文章</p>\n'
                f'{post_list(items, 1, show_cats=False)}\n'
                '<p class="back"><a href="index.html">← 全部分类</a></p>\n</div>'
            ),
            depth=1, year=year,
        ))
        print(f"  [分类] categories/{name}.html")


def build_tags(tags, year):
    secs = ['<h1 class="page-title">标签</h1>']
    if tags:
        secs.append(chips(tags, "tags", 1, ""))
        for name, items in tags:
            secs.append(
                f'<section class="term">\n'
                f'<h2>#{esc(name)} <span class="n">{len(items)} 篇</span></h2>\n'
                f'{post_list(items, 1, show_tags=False)}\n</section>'
            )
    else:
        secs.append('<p class="muted">还没有任何标签。在 notes/*.md 里写 '
                    '<code>tags = ["docker", "容器"]</code> 后重新编译即可。</p>')
    write(TAG_DIR / "index.html", render_page(
        title=f"标签 · {SITE_TITLE}",
        desc="全部标签",
        main='<div class="container">\n' + "\n".join(secs) + "\n</div>",
        depth=1, year=year,
    ))

    for name, items in tags:
        write(TAG_DIR / f"{name}.html", render_page(
            title=f"标签：{name} · {SITE_TITLE}",
            desc=f"标签 {name} 下的全部文章",
            main=(
                '<div class="container">\n'
                f'<h1 class="page-title">标签：#{esc(name)}</h1>\n'
                f'<p class="muted">{len(items)} 篇文章</p>\n'
                f'{post_list(items, 1, show_tags=False)}\n'
                '<p class="back"><a href="index.html">← 全部标签</a></p>\n</div>'
            ),
            depth=1, year=year,
        ))
        print(f"  [标签] tags/{name}.html")


def build_archives(posts, year):
    secs = ['<h1 class="page-title">归档</h1>']
    if not posts:
        secs.append('<p class="muted">还没有文章。</p>')
    years = {}
    for p in posts:
        years.setdefault(p["date"].year, {}).setdefault(p["date"].month, []).append(p)

    for y in sorted(years, reverse=True):
        months = years[y]
        total = sum(len(v) for v in months.values())
        secs.append(f'<section class="year">\n<h2>{y} <span class="n">{total} 篇</span></h2>')
        for mo in sorted(months, reverse=True):
            secs.append(f'<h3>{mo:02d} 月</h3>\n{post_list(months[mo], 0)}')
        secs.append("</section>")

    write(ROOT / "archives.html", render_page(
        title=f"归档 · {SITE_TITLE}",
        desc="全部文章归档",
        main='<div class="container">\n' + "\n".join(secs) + "\n</div>",
        depth=0, year=year,
    ))


SEARCH_JS = """<script>
(function () {
  var input = document.getElementById('q');
  var list  = document.getElementById('search-results');
  var hint  = document.getElementById('search-hint');
  var data = null;

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  function snippet(text, q) {
    var i = text.toLowerCase().indexOf(q);
    if (i < 0) return text.slice(0, 90);
    var s = Math.max(0, i - 40);
    return (s > 0 ? '…' : '') + text.slice(s, i + q.length + 60) + '…';
  }
  function run() {
    if (!data) return;
    var q = input.value.trim().toLowerCase();
    list.innerHTML = '';
    if (!q) {
      hint.textContent = '共 ' + data.length + ' 篇文章，输入关键词开始搜索';
      return;
    }
    var hits = data.filter(function (p) {
      return (p.title + ' ' + p.tags.join(' ') + ' ' + p.cats.join(' ') + ' ' + p.text)
        .toLowerCase().indexOf(q) >= 0;
    });
    hint.textContent = hits.length ? ('找到 ' + hits.length + ' 篇') : '没有匹配的文章';
    hits.slice(0, 40).forEach(function (p) {
      var li = document.createElement('li');
      li.innerHTML =
        '<a class="row" href="' + p.url + '">' +
          '<time>' + p.date + '</time>' +
          '<span class="ptitle">' + esc(p.title) + '</span>' +
        '</a>' +
        '<span class="li-meta">' + esc(snippet(p.text, q)) + '</span>';
      list.appendChild(li);
    });
  }
  fetch('index.json')
    .then(function (r) { return r.json(); })
    .then(function (d) { data = d; run(); })
    .catch(function () {
      hint.textContent = '索引加载失败。请用 http:// 访问（本地预览：python -m http.server 8765）';
    });
  input.addEventListener('input', run);
})();
</script>"""


def build_search(posts, year):
    secs = [
        '<h1 class="page-title">搜索</h1>',
        '<div class="search-box">'
        '<input id="q" type="search" class="search-input" '
        'placeholder="搜索标题、分类、标签或正文…" autocomplete="off"></div>',
        '<p id="search-hint" class="search-hint"></p>',
        '<ul id="search-results" class="post-list"></ul>',
    ]
    write(ROOT / "search.html", render_page(
        title=f"搜索 · {SITE_TITLE}",
        desc="站内搜索",
        main='<div class="container">\n' + "\n".join(secs) + "\n</div>",
        depth=0, year=year,
        body_extra=SEARCH_JS,
    ))

    index = [{
        "title": p["title_plain"],
        "url": f'posts/{p["slug"]}.html',
        "date": f'{p["date"]:%Y-%m-%d}',
        "cats": p["cats"],
        "tags": p["tags"],
        "text": p["plain"],
    } for p in posts]
    write(ROOT / "index.json", json.dumps(index, ensure_ascii=False, indent=0))


def build_about(year):
    md = markdown.Markdown(extensions=["fenced_code", "tables", "sane_lists"])
    body = md.convert(preprocess(ABOUT_MD.strip()))
    write(ROOT / "about.html", render_page(
        title=f"关于 · {SITE_TITLE}",
        desc="关于",
        main='<div class="container">\n<article class="post">\n'
             f'<h1>关于</h1>\n{body}\n</article>\n</div>',
        depth=0, year=year,
    ))


def check_links() -> list[str]:
    """扫描所有生成的 html，检查站内相对链接是否有坏链。"""
    errors = []
    pages = sorted(ROOT.rglob("*.html"))
    for page in pages:
        rel = page.relative_to(ROOT)
        text = page.read_text(encoding="utf-8")
        for href in re.findall(r'href="([^"]+)"', text):
            if href.startswith(("http://", "https://", "mailto:", "//", "#")):
                continue
            if "+" in href:            # JS 里拼接的模板串，跳过
                continue
            target = href.split("#")[0].split("?")[0]
            if not target:
                continue
            resolved = (page.parent / unquote(target)).resolve()
            if resolved.is_dir():
                resolved = resolved / "index.html"
            if not resolved.exists():
                errors.append(f"{rel}  ->  {href}")

    if not (ROOT / "index.json").exists():
        errors.append("(根目录缺少 index.json，搜索会失效)")

    return sorted(set(errors))


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    year = datetime.now().year

    for d in (POST_DIR, CAT_DIR, TAG_DIR):
        if d.exists():
            shutil.rmtree(d)

    md = markdown.Markdown(
        extensions=["fenced_code", "tables", "toc", "sane_lists", "attr_list"],
        extension_configs={"toc": {"anchorlink": False, "title": "",
                                   "toc_depth": "1-3", "permalink": False}},
    )

    print(f"==> 读取 {SRC_DIR}/*.md")
    posts = load_posts(md)
    if not posts:
        print("没有找到任何文章（检查 front matter 是否以 +++ 开头）")

    cat_map, tag_map = {}, {}
    for p in posts:
        for c in p["cats"]:
            cat_map.setdefault(c, []).append(p)
        for t in p["tags"]:
            tag_map.setdefault(t, []).append(p)

    cats = sorted(cat_map.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    tags = sorted(tag_map.items(), key=lambda kv: (-len(kv[1]), kv[0]))

    print("==> 生成页面")
    for p in posts:
        build_post(p, year)
    build_home(posts, cats, tags, year)
    build_categories(cats, year)
    build_tags(tags, year)
    build_archives(posts, year)
    build_search(posts, year)
    build_about(year)

    write(ROOT / ".nojekyll", "")
    print(f"\n完成: {len(posts)} 篇文章 · {len(cats)} 个分类 · {len(tags)} 个标签")

    if "--check" in sys.argv:
        print("\n==> 链接自检")
        errs = check_links()
        if errs:
            print(f"发现 {len(errs)} 条坏链:")
            for e in errs:
                print("   ", e)
            sys.exit(1)
        print(f"    通过: {len(list(ROOT.rglob('*.html')))} 个页面, 0 坏链")


if __name__ == "__main__":
    main()
