+++

date = '2026-05-17'
draft = false
math = true
title = '[十万个为什么] U盘刷镜像后再也看不到了'
categories = ["十万个为什么"]
tags = []

+++

# [十万个为什么] U盘刷镜像后再也看不到了

## 个人导航

知乎：https://www.zhihu.com/people/byzh_rc

CSDN：https://blog.csdn.net/qq_54636039

注：本文仅对所述内容做了框架性引导，具体细节可查询其余相关资料or源码

参考文章：各方资料

@[TOC]

## 解释

U盘刷镜像后, 在`此电脑`里再也看不到了

首先这不是说明U盘坏了:

1. 刷系统镜像（如 Linux、Armbian、Jetson、OpenWRT、Android 镜像）时，工具会**重写整个磁盘开头的分区表**
2. ==Windows 只认识普通 U 盘分区，不认识这种**系统级磁盘结构**，所以直接不显示盘符==
3. 若没有分配盘符, 则`磁盘管理`里能看到 U 盘, `此电脑`里就看不见

```
diskpart
list disk

select disk 2
clean

create partition primary
select partition 1
format fs=exfat quick
```

## 解决方法

### 1. 启动专业工具

```
# 启动专业磁盘管理工具
diskpart
# 扫描并列出电脑所有物理磁盘
list disk
```

### 2. 彻底清除

```
# 根据list disk找到U盘的编号(例如2)
select disk 2
# 把 U 盘最开头的分区表、所有的分区记录、引导信息全部抹除
clean
```

### 3. 重新创建

```
# 在空白磁盘上创建一个主分区
create partition primary
# 选中刚创建好的这个分区(也就是第1个分区)
select partition 1
# 快速格式化分区为 exfat 格式
format fs=exfat quick
# 给 U盘 分配一个盘符
assign
```

> exfat: 最适合 U 盘的格式，支持 4GB 以上的大文件，且 Windows 和 Mac 都能读写

