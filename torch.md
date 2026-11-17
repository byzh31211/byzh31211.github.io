+++

date = '2026-05-17'
draft = false
math=true
title = '[AI工具从入门到入土] torch'
categories = ["AI工具从入门到入土"]
tags = []

+++

# torch.cat

**在已有维度上堆叠**

张量(2, 10) 和 张量(2, 10)

-> 张量(4, 10): 称为沿第一个维度(axis/dim = 0)堆叠

-> 张量(2, 20): 称为沿第二个维度(axis/dim = 1)堆叠

# torch.stack

在新维度上堆叠 (**stack = unsqueeze + cat**)

张量(10,) 和 张量(10,)

-> 张量(2, 10): 称为沿第一个维度(axis/dim = 0)堆叠

