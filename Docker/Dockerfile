# 使用官方的 Python 3 Alpine 镜像作为基础镜像
FROM python:3-slim

# 更新包列表、安装 Git 并清理缓存（Debian 使用 apt-get 包管理）
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 本地build时去掉注释
# COPY . /app

# 克隆指定的 Git 仓库
RUN git clone https://github.com/Youkoo/JMComic-web.git

# 进入克隆的目录
WORKDIR /app/JMComic-Api

# 安装依赖，并且不缓存依赖包
RUN pip install --no-cache-dir -r requirements.txt

# 删除 Git 包，减小镜像体积
# 删除 Git 包，减小镜像体积
RUN apt-get purge -y --auto-remove git

# 设置容器启动时运行的命令（假设是 main.py）
CMD ["python", "main.py"]
