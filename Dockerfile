# 使用官方 Python 3 镜像作为基础镜像
FROM python:3

# 安装 Git
RUN apt-get update && apt-get install -y git

# 设置工作目录
WORKDIR /app

# 克隆指定的 Git 仓库
RUN git clone https://github.com/LingLambda/JMComic-Api

# 进入克隆的目录
WORKDIR /app/JMComic-Api

# 安装依赖
RUN pip install -r requirements.txt

# 设置容器启动时运行的命令（假设是 app.py）
CMD ["python", "main.py"]