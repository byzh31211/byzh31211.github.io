+++

date = '2026-05-17'
draft = false
math=true
title = '[AI工具从入门到入土] venv、pip、conda、uv一次讲清'
categories = ["AI工具从入门到入土"]
tags = []

+++

# [Python-环境] venv、pip、conda、uv一次讲清

## 个人导航

知乎：https://www.zhihu.com/people/byzh_rc

CSDN：https://blog.csdn.net/qq_54636039

注：本文仅对所述内容做了框架性引导，具体细节可查询其余相关资料or源码

参考文章：各方资料

@[TOC]

## :bike:Python官方虚拟环境venv

#### 1. 创建环境

```shell
python -m venv .venv
```

生成结构：

```
.venv
├─ Scripts/
│  ├─ python.exe
│  └─ pip.exe
├─ Lib/
└─ pyvenv.cfg
```

#### 2. 激活环境

```shell
# Windows
.venv\Scripts\activate

# Linux/Mac
source myenv/bin/activate
```

#### 3. 退出环境

```shell
deactivate
```

#### 3. 安装包

```shell
# 不标准写法
pip install requests

# 更标准写法
python -m pip install requests
```

> **conda、uv、pipenv、poetry 最终都是在调用 pip**

#### 4. 其他常用命令

pip系列:

```shell
# 导入
pip install -r requirements.txt
# 导出
pip freeze > requirements.txt
# 查看当前python版本
python --version
# 查看当前python路径
python -c "import sys ; print(sys.executable)"
# 查看当前pip路径
pip show pip
```

py系列:

```
# 查看所有python
py -0p
# 用某个版本的python创建环境
py -3.11 -m venv .venv
```

> 可以使用`py -3.11`代替`python`

#### 5. 修改pip清华源

```shell
# 设置 pip 的默认包源！！！
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 设置额外的包索引地址(如果index-url找不到包，再去extra-index-url里找)
# 不建议设置！！！，会降低下载速度, 一般国内只开清华源最好！！！
# pip config set global.extra-index-url https://mirrors.aliyun.com/pypi/simple
```

然后就会在`%USERPROFILE%\AppData\Roaming\pip\pip.ini`生成配置文件

补充其他源:

```ini
Pypi: https://pypi.org/simple

豆瓣：	https://pypi.douban.com/simple
阿里：	https://mirrors.aliyun.com/pypi/simple
清华：	https://pypi.tuna.tsinghua.edu.cn/simple
中国科学技术大学	https://pypi.mirrors.ustc.edu.cn/simple
华中理工大学	http://pypi.hustunique.com/simple
山东理工大学	http://pypi.sdutlinux.org/simple
网易	https://mirrors.163.com/pypi/simple/
腾讯	https://mirrors.cloud.tencent.com/pypi/simple
```

#### 6. 本地化whl

下载所有的.whl文件到wheelhouse文件夹下

```
python -m pip download -r requirements.txt -d wheelhouse -i https://pypi.tuna.tsinghua.edu.cn/simple --prefer-binary
```

> 如果没有whl文件，而是tar.gz的话，则会编译成whl后保存

安装方式:

```
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt --find-links=wheelhouse -i https://pypi.tuna.tsinghua.edu.cn/simple --prefer-binary
```

## :car:Conda

使用`requirements.txt`管理python环境 -> 对版本管理不友好

分类:

- anaconda: 可视化界面, 支持命令行, 但冗杂庞大
- miniconda: 支持命令行, 轻量化 -> **个人推荐**

官网: https://www.anaconda.com/

下载: https://www.anaconda.com/download/success

> conda环境默认都在`C:\Users\用户\.conda\envs`下
> 安装的包放在`环境\Lib\site-packages`下

#### 1. 基础配置

虚拟环境(加入PATH):

```
D:\...\miniconda3
D:\...\miniconda3\Scripts
D:\...\miniconda3\Library\bin
```

cmd中执行:

```shell
# 让 Conda 能够在 cmd 中正常使用
conda init cmd.exe
# 在user下生成.condarc文件
conda config --set show_channel_urls yes 
```

替换.condarc文件: (清华源)

```
channels:
  - defaults
show_channel_urls: true
default_channels:
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/r
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/msys2
custom_channels:
  conda-forge: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  msys2: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  bioconda: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  menpo: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  pytorch: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  pytorch-lts: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  simpleitk: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  deepmodeling: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/
```

#### 2. 基础命令

```shell
# 所有环境
conda env list
# 创建
conda create --name 名字 python=3.11.5
conda create -n 名字 python=3.10.9
# 克隆环境
conda create --clone 名字 --name 新名字
# 删除环境
conda remove --name 名字 --all
# 激活环境
conda activate 名字
```

## :rocket:uv

使用`pyproject.toml`管理python环境 -> 利于环境迁移

官网: https://uv.doczh.com/getting-started/installation/

下载: https://github.com/astral-sh/uv

#### 1. 基础配置

```shell
# 设置复用缓存的目录(避免C盘被塞满)
setx UV_CACHE_DIR D:\uv_cache
# 查看复用缓存的目录
uv cache dir
```

#### 2. 虚拟环境

uv创建`python官方环境`: (较少使用)

```shell
# 方法1: 只创建环境
uv venv
uv venv --python 3.11.5
# 给该环境装入pip(因为uv的venv默认不装pip)
uv pip install pip
```

uv创建`uv项目环境`: (**常用**)

```shell
# 方法2: 创建环境和配置文件(pyproject.toml和.python-version)
uv python pin 3.11.5
uv init

# 修改项目环境中的python版本
# (相当于修改.python-version)
# (前提是要与pyproject.toml里的匹配)
uv python pin 3.11.5

# 添加包(同步pyproject.toml)
uv add requests==2.31.0
# 删除包
uv remove requests

# 基于pyproject.toml来安装
uv sync

# 运行python代码(方法1)
# (uv的简化命令)
uv run ./xxx.py
# 运行python代码(方法2)
# (uv run python ... 等价于 python ...)
uv run python ...

# 查看项目环境(方法1)
uv tree
# 查看项目环境(方法2)
uv pip list
```

> `uv run python`等价于`python`
>
> `uv pip`等价于`pip`

#### 3. 基础命令

```shell
# 查看可用和已安装的 Python 版本
uv python list
```

#### 4. 清华下载源设置

在`pyproject.toml`后面写入:

```toml
[[tool.uv.index]]
# url = "https://pypi.org/simple"
url = "https://pypi.tuna.tsinghua.edu.cn/simple"
default = true
```

#### 5. pytorch下载源设置

在`pyproject.toml`后面写入: (注意需改cuda版本)

```toml
[tool.uv.sources]
torch = [
  { index = "pytorch-cu121", marker = "sys_platform == 'linux' or sys_platform == 'win32'" },
]
torchvision = [
  { index = "pytorch-cu121", marker = "sys_platform == 'linux' or sys_platform == 'win32'" },
]
torchaudio = [
  { index = "pytorch-cu121", marker = "sys_platform == 'linux' or sys_platform == 'win32'" },
]

[[tool.uv.index]]
name = "pytorch-cu121"
url = "https://download.pytorch.org/whl/cu121"
explicit = true # 表示 只有在 [tool.uv.sources] 明确指定了这个索引源的包，才会使用这个源
```

## :car:poetry

也是使用`pyproject.toml`, 挺好的

但是uv是rust重写的, 所以uv更快

-> 略

## :bike:pipenv

过时 

-> 略