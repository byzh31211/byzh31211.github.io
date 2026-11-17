# byzh 的笔记本

个人博客，纯静态 HTML，由 `build.py` 编译，托管在 GitHub Pages：
<https://byzh31211.github.io>

## 写一篇新文章

1. 在仓库根目录新建 `xxx.md`，头部照抄这个格式（TOML）：

   ```toml
   +++
   date = '2026-11-18'
   draft = false
   math = false
   title = '文章标题'
   categories = ["AI工具从入门到入土"]
   tags = []
   +++
   ```

2. 正文直接写 Markdown。支持：
   - `@[TOC]` 或 `[TOC]` → 自动生成目录
   - emoji 短代码 `:rocket:` `:gear:` 等
   - 代码块指定语言（```py / ```shell），自动高亮
   - `math = true` 时可用 `$$...$$` 公式

3. 发布：

   ```powershell
   .\publish.ps1
   ```

   它会依次执行「编译 → 提交 → 推送」，约 1 分钟后线上生效。

## 文件说明

| 文件 | 作用 |
|---|---|
| `*.md` | 文章源文件（带 `+++` 头的会被编译） |
| `build.py` | 编译器，站点标题/副标题/作者在文件顶部改 |
| `style.css` | 全部样式，深浅色跟随系统 |
| `posts/*.html` | 生成物，**不要手改** |
| `index.html` / `about.html` | 生成物，**不要手改** |
| `publish.ps1` | 一键发布 |

## 只编译不发布

```powershell
E:\py_uv_env\py-3-11-5-opencode\.venv\Scripts\python.exe build.py
```

预览：在根目录起个静态服务器，然后打开 <http://127.0.0.1:8765>

```powershell
E:\py_uv_env\py-3-11-5-opencode\.venv\Scripts\python.exe -m http.server 8765
```

## 小开关（在 `build.py` 顶部）

- `STRIP_BODY_H1 = True` → 删掉正文里和标题重复的第一行 `# 标题`
- `SITE_TITLE` / `SITE_SUBTITLE` / `SITE_AUTHOR` → 站点标题、副标题、作者
