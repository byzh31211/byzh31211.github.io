# byzh 的笔记本

个人博客，纯静态 HTML，由 `build.py` 编译，托管在 GitHub Pages：
<https://byzh31211.github.io>

## 目录结构

```
notes/            文章源文件（Markdown + TOML 头） ← 只改这里
build.py          编译器
style.css         全部样式
publish.ps1       一键发布
index.html        首页          ┐
archives.html     归档          │
categories/       分类页        │ 全部是生成物，不要手改
tags/             标签页        │
posts/            文章页        │
search.html       搜索页        │
index.json        搜索索引      ┘
```

## 写一篇新文章

在 `notes/` 里新建 `xxx.md`，头部照抄（TOML 格式）：

```toml
+++
date = '2026-11-18'
draft = false
math = false
title = '文章标题'
categories = ["AI工具从入门到入土"]
tags = ["docker", "容器"]
+++
```

正文写 Markdown 即可，额外支持：

| 写法 | 效果 |
|---|---|
| `tags = ["docker", "容器"]` | 自动生成 `/tags/docker.html` 聚合页，首页和文章页出现可点击的标签 |
| `categories = ["…"]` | 同上，生成 `/categories/…html` |
| `math = true` | 页面加载 MathJax，可用 `$$…$$` |
| `draft = true` | 跳过不编译 |
| `@[TOC]` | 无需保留（目录由侧栏自动生成） |
| `:rocket:` `:gear:` 等 | emoji 短代码 |
| ```` ```py ```` | 代码块按语言高亮 |

**分类和标签不用登记**，写了就会自动出现；删掉最后一个引用后页面也会自动消失。

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
