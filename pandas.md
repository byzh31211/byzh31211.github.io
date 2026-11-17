+++

date = '2026-05-17'
draft = false
math=true
title = '[AI工具从入门到入土] pandas'
categories = ["AI工具从入门到入土"]
tags = []

+++

# 注意

1. 简单数据预处理先用excel做
2. 复杂数据预处理用jupyter
3. 全都处理好, 然后导出为csv, 再用py

# 读取

#### 1.第一行有杂乱信息

```py
df = pd.read_csv(
    './Wimbledon_featured_matches.csv', encoding='gbk',
    skiprows=1 # 跳过第1行, 从2行开始读取
)
```

# 显示

#### 1.横线被压缩成...

```py
pd.set_option("display.max_columns", None)   # 显示所有列
pd.set_option("display.width", None)         # 不限制总宽度（按终端/环境尽量铺开）
pd.set_option("display.max_colwidth", None)  # 单个单元格内容不截断（长字符串也全显示）
```

> 建议保存成excel再看

# 类型转换

```py
# 一维
s = pd.to_numeric(df[col], errors="coerce")
# 多维
df_numeric = df[cols].apply(pd.to_numeric, errors="coerce")
```

`errors="coerce"` 的意思是：**强制转**，转不了就变成 `NaN`（缺失值）

> 做 `quantile()`、`mean()` 这类统计时，**NaN 会被自动忽略**（默认 `skipna=True`）

# 分组 group

#### 1.拆成字典

```py
grouped = {
    依据内容: sub_df.reset_index(drop=True) # sub_df 的行索引重新设置为从 0 开始
    for 依据内容, sub_df in df.groupby("依据")
}
```

#### 2.直接遍历

```py
for 依据内容, sub_df in df.groupby("依据"):
    ...
```

# 数据分析

#### 1.序列中最多的前5个元素

```py
top5 = (
    pd.to_numeric(df['p1_distance_run_new'], errors='coerce')  # 只在统计时转数值
      .value_counts()                        # 统计频数
      .head(5)                               # 取前 5
)
```

#### 2.第几分位数

```py
Q1 = s.quantile(0.25) # 第1四分位数
Q3 = s.quantile(0.75) # 第3四分位数
```

# Series小工具

```py
# 有哪些类别
s.unique()
# 各类分别有多少个样本
s.value_counts()
# 均值,方差,最大,最小,分位数
s.describe()
```

