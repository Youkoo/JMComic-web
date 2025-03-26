# JMComic API 

本仓库基于 [LingLambda/JMComic-Api](https://github.com/LingLambda/JMComic-Api) 修改，提供一个 Web API 服务。

## 使用方法 (docker 和直接运行二选一即可)

### 直接运行

1.  **下载源码包并解压**，进入项目根目录。

2.  **创建虚拟环境**:
    ```bash
    python -m venv .venv
    ```

3.  **激活虚拟环境**:
    *   在 Windows 上:
        ```bash
        .\.venv\Scripts\activate
        ```
    *   在 macOS 或 Linux 上:
        ```bash
        source .venv/bin/activate
        ```

4.  **安装依赖**:
    ```bash
    pip install -r requirements.txt
    ```


6.  **运行**:
    ```bash
    python main.py
    ```
    服务将在 `http://<host>:<port>` (默认为 `http://0.0.0.0:8699`) 上启动。

### 使用 Docker(推荐)

提供了预构建的 Docker 镜像 `linglambda/jmcomic-api`。

```bash
docker run -d --name jmcomic-api -p 8699:8699 orwellz/jmcomic-api:latest
```
## API 使用方法

### 获取 PDF

`GET /get_pdf/{jm_album_id}`

**可选参数**

`Get /get_pdf/{jm_album_id}?passwd=false`(如果没有参数则默认有密码)
