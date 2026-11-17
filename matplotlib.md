+++

date = '2026-05-17'
draft = false
math=true
title = '[AI工具从入门到入土] matplotlib:art:'
categories = ["AI工具从入门到入土"]
tags = []

+++

# [AI工具从入门到入土] matplotlib:art:

# 个人导航

知乎：https://www.zhihu.com/people/byzh_rc

CSDN：https://blog.csdn.net/qq_54636039

注：本文仅对所述内容做了框架性引导，具体细节可查询其余相关资料or源码

参考文章：各方资料

@[TOC]

# :pushpin:规范

#### 1. `plt`方式

全局级 -> 直接作用于当前图标

#### 2. `ax`方式

对象级 -> 精准作用于指定对象

# :gear:导入

```py
import matplotlib.pyplot as plt
from matplotlib.axes import Axes # 为ax提供类型提示

# 正常显示中文和负号
plt.rcParams['font.sans-serif'] = ['SimHei', 'Kaiti', 'Microsoft YaHei']  
plt.rcParams['axes.unicode_minus'] = False
```

# :gear:全局设置

```py
plt.rcParams['font.size'] = 12       # 默认字体大小
plt.rcParams['axes.titlesize'] = 14  # 标题字体大小
plt.rcParams['axes.labelsize'] = 12  # 坐标轴标签字体大小
plt.rcParams['xtick.labelsize'] = 10 # x轴刻度字体大小
plt.rcParams['ytick.labelsize'] = 10 # y轴刻度字体大小
plt.rcParams['legend.fontsize'] = 10 # 图例字体大小
```

# :framed_picture:画布

常用:

```py
plt.figure(figsize=(12, 6))
```

单图:

```py
# 麻烦
fig = plt.figure(figsize=(12, 6))
ax = plt.gca() # get current axes
```

```py
# 不推荐
fig = plt.figure(figsize=(12, 6))
ax = fig.add_subplot(111) # 1行1列第1个子图
```

```py
# 推荐
fig, ax = plt.subplots(figsize=(12, 6))
```

多图:

```py
fig, axs = plt.subplots(nrows=2, ncols=1, figsize=(12, 6), constrained_layout=True)
```

> 对于多图, 还可使用 `axs = axs.flatten()`

# 基础细节

#### 1. 标题

```py
plt.title('xxx', fontsize=16, pad=20, fontweight='bold')
```

```py
ax.set_title('xxx', fontsize=16, pad=20, fontweight='bold')
```

#### 2. 图例

```py
plt.legend(fontsize=17, loc='upper right')
plt.legend(fontsize=17, loc='lower left')
```

```py
ax.legend(fontsize=17, loc='upper right')
ax.legend(fontsize=17, loc='lower left')
```

#### 3. 坐标轴标签

```py
plt.xlabel('xxx', fontsize=17, labelpad=10)
plt.ylabel('xxx', fontsize=17, labelpad=10)
```

```py
ax.set_xlabel('xxx', fontsize=17, labelpad=10) 
ax.set_ylabel('xxx', fontsize=17, labelpad=10)
```

#### 4. 坐标轴刻度

```py
plt.xticks([0, 1, 2, 3], ['cat', 'dog', 'bird', 'mouse'], fontsize=17)
plt.yticks([10, 20, 30], ['low', 'mid', 'high'], fontsize=17)
```

```py
# 只在哪些位置显示刻度
ax.set_xticks([0, 1, 2, 3])
ax.set_yticks([10, 20, 30])
# 刻度显示的文本
ax.set_xticklabels(['cat', 'dog', 'bird', 'mouse'], fontsize=17)
ax.set_yticklabels(['low', 'mid', 'high'], fontsize=17)
# 更多样式设置
ax.tick_params(axis='x', labelsize=17)
ax.tick_params(axis='y', labelsize=17)
```

#### 5. 边框

```py
ax = plt.gca()
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.spines['bottom'].set_visible(False)
```

#### 6. 网格线

```py
plt.grid(axis='x', linestyle='--', alpha=0.7, color='gray')
plt.grid(axis='y', linestyle='--', alpha=0.7, color='gray')
```

```py
ax.grid(axis='x', linestyle='--', alpha=0.7, color='gray')
ax.grid(axis='y', linestyle='--', alpha=0.7, color='gray')
```

# 文本

```py
plt.text(
    0.5, 0.5, 'xxx',
    ha='center', va='center',
    fontsize=14, fontweight='bold', color='#555555',
    transform=plt.gca().transAxes
)
```

```py
ax.text(
    0.5, 0.5, 'xxx',
    ha='center', va='center',
    fontsize=14, fontweight='bold', color='#555555',
    transform=plt.gca().transAxes
)
```

# 线条

```py
plt.axhline(0.5, color='red', linestyle='--', label='xxx')
plt.axvline(0.5, color='red', linestyle='--', label='xxx')
```

```py
ax.axhline(0.5, color='red', linestyle='--', label='xxx')
ax.axvline(0.5, color='red', linestyle='--', label='xxx')
```

# 保存

```py
plt.savefig("fig.png", dpi=300, bbox_inches='tight')
plt.close()
```

# 拓展 - ax

#### 1. 双y轴(右轴)

在同一个图上，创建一个共享 x 轴、但拥有独立 y 轴的第二个坐标系

```py
ax_right = ax.twinx()
```

#### 2. y轴反转

```py
ax.invert_yaxis()
```

#### 3. x轴移到上分

```py
ax.xaxis.tick_top()
ax.xaxis.set_label_position('top')
```

# 拓展 - 修改已有legend

```py
leg = ax.get_legend()

leg.set_frame_on(False)
for text in leg.get_texts():
    text.set_fontsize(17)
```

# 拓展 - 排版

| 名字                      | 作用阶段 | 作用对象     |
| ------------------------- | -------- | ------------ |
| `constrained_layout=True` | 🟢 创建时 | 整个布局系统 |
| `tight_layout()`          | 🟡 绘图后 | 子图之间间距 |
| `bbox_inches='tight'`     | 🔵 保存时 | 图片裁剪     |

`constrained_layout=True`: **新方案**(智能布局引擎)

- 避免标题重叠, 避免 label 重叠, 避免 legend 挤压

`tight_layout()`: **老方案**

- 调整子图间距, 避免基本重叠
- 对 legend / colorbar 支持差, 有时会“挤坏布局”

`bbox_inches='tight'`: 

- 去掉外围空白
- 裁剪成“刚好包住内容”

**-> 推荐使用 `constrained_layout=True` 加 `bbox_inches='tight'`**