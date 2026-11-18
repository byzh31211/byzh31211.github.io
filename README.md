# byzh 的笔记本

个人博客，纯静态 HTML，由 `build.py` 编译，托管在 GitHub Pages：
<https://byzh31211.github.io>

## 目录结构

```
notes/            文章源文件 ← 只改这里
  xxx.md            单文件形式
  某目录/index.md   bundle 形式（配图放同目录）
assets/           图标等原始素材（favicon.ico 会自动生成到根目录）
build.py          编译器
style.css         全部样式
publish.ps1       一键发布
index.html        首页          ┐
archives.html     归档          │
categories/       分类页        │ 全部是生成物，不要手改
tags/             标签页        │
posts/            文章页+配图   │
search.html       搜索页        │
index.json        搜索索引      ┘
```

## 写一篇新文章

两种写法都支持，任选其一。

**① 单文件（没配图）**：`notes/xxx.md`

**② bundle（有配图）**：新建文件夹 `notes/某文章/index.md`，图片直接放同一层，正文里用相对路径引用：

```
notes/画质and分辨率/
├── index.md          ← 里面写 ![](image1.jpeg)
└── image1.jpeg
```

编译时会自动把图片复制到 `posts/画质and分辨率/image1.jpeg`，并改好正文里的路径。

头部照抄（TOML 格式）：

```toml
+++
date = '2026-11-18'
draft = false
math = false
title = '文章标题'
categories = ["AI工具从入门到入土"]
tags = ["docker", "容器"]
slug = 'my-post'      # 可选，自定义 URL
+++
```

正文写 Markdown 即可，额外支持：

| 写法 | 效果 |
|---|---|
| `tags = ["docker", "容器"]` | 自动生成 `/tags/docker.html` 聚合页，首页和文章页出现可点击的标签 |
| `categories = ["…"]` | 同上，生成 `/categories/…html` |
| `math = true` | 页面加载 MathJax，可用 `$$…$$` |
| `draft = true` | 跳过不编译 |
| `slug = 'my-post'` | 自定义文章 URL 为 `/posts/my-post.html`；不写就用文件名/目录名 |
| `@[TOC]` | 无需保留（目录由侧栏自动生成） |
| `:rocket:` `:gear:` 等 | emoji 短代码 |
| ```` ```py ```` | 代码块按语言高亮 |

**分类和标签不用登记**，写了就会自动出现；删掉最后一个引用后页面也会自动消失。

页面 URL 用的文件名规则（`build.py` 的 `TERM_SLUGS`）：

| 分类/标签名 | 生成的文件 |
|---|---|
| `docker`、`python` | `tags/docker.html`、`tags/python.html`（纯英文直接用） |
| `AI工具从入门到入土` | `categories/ai-tools.html`（在 `TERM_SLUGS` 里配了英文名） |
| `容器`（没配） | `tags/t-1a2b3c4d.html`（自动 md5，编译时会提示） |

**为什么不用中文文件名**：部分浏览器会把中文路径按 GBK 编码发出去，导致 404。用 ASCII 文件名可以彻底避免。给中文分类配一个英文名的写法：

```python
TERM_SLUGS = {
    "AI工具从入门到入土": "ai-tools",
    "容器": "container",
}
```

发布：

```powershell
.\publish.ps1
```

依次执行「编译 → 提交 → 推送」，约 1 分钟后线上生效。编译完会自动跑**链接自检**：扫描所有生成页面的 `href`，解析成真实文件路径，有一条坏链就中止、不会推送。

> 注意：GitHub Pages 的 CDN 缓存最长 10 分钟，推送后如果看到旧页面，等一下再刷新。

## 站点功能

- 首页：最新文章 + 分类/标签入口
- 分类页 / 标签页：自动聚合，按文章数排序
- 归档页：按年、月分组
- 搜索：`index.json` + 纯前端匹配，支持标题/分类/标签/正文
- 文章页：宽屏（≥1300px）右侧悬浮目录并跟随滚动高亮，窄屏折叠成「目录」
- 深色模式：跟随系统，右上角按钮可手动切换（记在 localStorage）
- 站点图标：`assets/*.ico` 自动复制成根目录 `favicon.ico`，换图标只要替换 assets 里的 ico

## 文章 URL 规则

| 源 | URL |
|---|---|
| `notes/cache.md` | `/posts/cache.html` |
| `notes/冷笑话/index.md` | `/posts/冷笑话.html`（中文目录名直接用） |
| 任意文章写 `slug = 'cold-jokes'` | `/posts/cold-jokes.html` |

> 中文 URL 在地址栏会显示成 `%E5%86%B7...`，个别老浏览器（360 兼容模式等）可能打不开。
> 想避开就用 `slug = '英文名'`。

## 只编译不发布

```powershell
E:\py_uv_env\py-3-11-5-opencode\.venv\Scripts\python.exe build.py --check
```

`--check` 会额外做链接自检，发现坏链时退出码为 1。

本地预览（起一个静态服务器，因为搜索要 fetch `index.json`）：

```powershell
E:\py_uv_env\py-3-11-5-opencode\.venv\Scripts\python.exe -m http.server 8765
```

然后打开 <http://127.0.0.1:8765>

## 可调开关（`build.py` 顶部）

| 变量 | 作用 |
|---|---|
| `SITE_TITLE` / `SITE_SUBTITLE` / `SITE_AUTHOR` | 站点标题、副标题、作者 |
| `STRIP_BODY_H1 = True` | 删掉正文里与标题重复的第一行 `# 标题` |
| `WORDS_PER_MIN` | 阅读速度，影响「约 N 分钟」 |
| `HIGHLIGHT_JS` / `MATHJAX_JS` | 换 CDN 镜像 |
