+++

date = '2026-05-17'
draft = false
math=true
title = '[AI工具从入门到入土] docker'
categories = ["AI工具从入门到入土"]
tags = []

+++

# 基本命令

```
# 设置开机启动docker
systemctl enable docker
# 重启docker
systemctl restart docker
# 镜像:
docker images
docker search xxx
docker pull xxx
docker rmi xxx
# 容器:
docker run -it --name XXX (-v ...:...) xxx:5.0 /bin/bash
docker run -id --name XXX (-v ...:...) xxx:5.0 /bin/bash
docker exec -it XXX /bin/bash
exit
docker start XXX
docker ps # 当前容器
docker ps -a # 所有容器
docker stop XXX
docker rm XXX
# 加载镜像
docker commit 容器id 镜像名称:版本号
docker save -o 压缩文件名.tar 镜像名称:版本号
docker load -i 压缩文件
# 根据Dockerfile来构建镜像
docker build -f ./Dockerfile -t xxx:1.0 . # .代表寻址的路
```

# 创建容器

```
docker run -id --gpus all --name SY311 -v /home/qsun/桌面/SY:/root/SY sy311:4.0 /bin/bash
```

$$
\text{
docker run -id --gpus all --name SY311 -v \color{red}/home/qsun/桌面/SY\color{black}:\color{green}/root/SY \color{purple}sy311:4.0 \color{black}/bin/bash
}
\\
\begin{cases}
\color{red}外部主设备的项目文件夹路径(需要提前准备好)
\\
\color{green}容器内部的对应文件夹目录(会自动创建)
\\
\color{purple}镜像名与其对应版本
\end{cases}
$$

> 当创建容器后, 红色文件夹(实际存在) 与 绿色文件夹(容器内存在) 会关联起来
> -> 修改主机内实际存在的文件夹, 则容器内的该文件夹也会变

# Dockerfile

[Image Layer Details - pytorch/pytorch:2.3.1-cuda12.1-cudnn8-devel](https://hub.docker.com/layers/pytorch/pytorch/2.3.1-cuda12.1-cudnn8-devel/images/sha256-a22a1fca37f8361c8a1e859cd6eb6bd9d1fb384f9c0dcb2cfc691a178eb03d17)

[Image Layer Details - pytorch/pytorch:2.3.1-cuda11.8-cudnn8-devel](https://hub.docker.com/layers/pytorch/pytorch/2.3.1-cuda11.8-cudnn8-devel/images/sha256-5c2e1d0bbe0f000b12aef0dfba9980790c1240d40498a9f67d01bd2bfc131461)

`Dockerfile`:

```
FROM pytorch/pytorch:2.3.1-cuda11.8-cudnn8-devel

WORKDIR /workspace

RUN pip install --no-cache-dir --retries 5 --timeout 120 \
    numpy==1.26.4 \
    pandas==2.1.4 \
    matplotlib==3.9.4 \
    scikit-learn==1.6.1 \
    spikingjelly==0.0.0.0.14 \
    thop \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

CMD ["/bin/bash"]
```

> `touch Dockerfile`

根据Dockerfile来构建镜像:

```
docker build -f ./Dockerfile -t xxx:1.0 .
```

