+++

date = '2026-05-17'
draft = false
math=true
title = '[AI工具从入门到入土] `cache缓存` 正摧毁你的C盘'
categories = ["AI工具从入门到入土"]
tags = []

+++

# [AI工具从入门到入土] `cache缓存` 正摧毁你的C盘

# 个人导航

知乎：https://www.zhihu.com/people/byzh_rc

CSDN：https://blog.csdn.net/qq_54636039

注：本文仅对所述内容做了框架性引导，具体细节可查询其余相关资料or源码

参考文章：各方资料

@[TOC]

# pip - cache

pip下载的各种包的whl文件等, 都会存着, 可以二次复用, 避免再次下载

查看cache位置:

```
pip cache dir
```

释放空间:

```
pip cache purge # 完全
pip cache prune # 温和
```

修改cache位置:

```
setx PIP_CACHE_DIR D:\.cache_byzh\pip
```

# UV - cache

uv下载的各种包的whl文件, 都会存着, 可以二次复用, 避免再次下载

查看cache位置:

```
uv cache dir
```

释放空间:

```
uv cache clean
```

修改cache位置:

```
setx UV_CACHE_DIR D:\.cache_byzh\uv
```

# HuggingFace - cache

修改cache位置:

```
# 一键全部设置
setx HF_HOME D:\.cache_byzh\huggingface
# 如果设置了别的, 那么HF_HOME的优先级最低
# - HF_DATASETS_CACHE: 数据集(Arrow文件和索引)
# - HF_HUB_CACHE: 模型、分词器、...
setx HF_DATASETS_CACHE D:\.cache_byzh\huggingface\datasets
setx HF_HUB_CACHE D:\.cache_byzh\huggingface\hub
```

`datasets`: HF_DATASETS_CACHE
`transformers`/`diffusers`: HF_HUB_CACHE

> 优先级: HF_DATASETS_CACHE > HF_HUB_CACHE > HF_HOME

# ModelScope - cache

修改cache位置:

```
setx MODELSCOPE_CACHE D:\.cache_byzh\modelscope
```

# 汇总

windows下的常见默认路径:

```
# pip
%LocalAppData%\pip\Cache
# uv
%LocalAppData%\uv\cache
# huggingface
%USERPROFILE%\.cache\huggingface
# modelscope
%USERPROFILE%\.cache\modelscope
```

cache环境变量:

```
# windows
setx PIP_CACHE_DIR D:\.cache_byzh\pip
setx UV_CACHE_DIR D:\.cache_byzh\uv
setx HF_HOME D:\.cache_byzh\huggingface
setx MODELSCOPE_CACHE D:\.cache_byzh\modelscope
# linux
export PIP_CACHE_DIR=~/.cache_byzh/pip
export UV_CACHE_DIR=~/.cache_byzh/uv
export HF_HOME=~/.cache_byzh/huggingface
export MODELSCOPE_CACHE=~/.cache_byzh/modelscope
```

