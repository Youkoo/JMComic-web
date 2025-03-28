# 使用官方的 Python 3 Alpine 镜像作为基础镜像
FROM python:3-alpine

# 更新包列表并安装 Git（Alpine 使用 apk 包管理）
RUN apk update && apk add --no-cache git

# 设置工作目录
WORKDIR /app

# 克隆指定的 Git 仓库
RUN git clone https://github.com/FfmpegZZZ/JMComic-Api
# COPY . /app
# 进入克隆的目录
WORKDIR /app/JMComic-Api

# 安装依赖，并且不缓存依赖包
RUN pip install --no-cache-dir -r requirements.txt

# 删除 Git 包，减小镜像体积
RUN apk del git

# 设置容器启动时运行的命令（假设是 main.py）
CMD ["python", "main.py"]