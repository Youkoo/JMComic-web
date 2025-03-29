# JMComic API

本仓库基于 [LingLambda/JMComic-Api](https://github.com/LingLambda/JMComic-Api) 修改，提供一个用于与禁漫天堂（JMComic）交互的 Web API 服务。

## 使用方法

你可以选择直接运行源代码或使用 Docker 镜像。

### 直接运行

1.  **下载源码包并解压**，然后进入项目根目录。
2.  **创建并激活 Python 虚拟环境**:
    *   创建: `python -m venv .venv`
    *   激活 (Windows): `.\.venv\Scripts\activate`
    *   激活 (macOS/Linux): `source .venv/bin/activate`
3.  **安装依赖**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **(可选) 配置**: 编辑 `option.yml` 文件以配置 JMComic 客户端选项和 API 服务设置（如主机和端口）。默认服务运行在 `0.0.0.0:8699`。
5.  **运行**:
    ```bash
    python main.py
    ```
    服务将在 `option.yml` 中配置的地址和端口启动。

### 使用 Docker (推荐)

我们提供了预构建的 Docker 镜像 `orwellz/jmcomic-api`

1.  **拉取镜像**:
    ```bash
    docker pull orwellz/jmcomic-api:latest
    ```
2.  **运行容器**:
    ```bash
    # 运行在后台，将容器的 8699 端口映射到宿主机的 8699 端口
    docker run -d --name jmcomic-api -p 8699:8699 orwellz/jmcomic-api:latest

## API 接口文档

以下是 JMComic API 提供的接口详情：

### 1. 获取 PDF 文件

*   **路径:** `/get_pdf/<jm_album_id>`
*   **方法:** `GET`
*   **功能:** 根据 ID 下载对应的漫画，生成并返回 PDF 文件。
*   **路径参数:**
    *   `jm_album_id`: 车牌号。
*   **查询参数:**
    *   `passwd` (可选，默认加密): 控制 PDF 是否加密。设置为 `'false'` 或 `'0'` 表示不加密。
    *   `Titletype` (可选, 默认 2): 控制生成的 PDF 文件名的格式:
        *   `0`: `<jm_album_id>.pdf`
        *   `1`: `<相册标题>.pdf`
        *   `2` (或其他值): `[<jm_album_id>] <相册标题>.pdf`
    *   `pdf` (可选, 字符串, 默认 'false'): 控制返回类型。如果设置为 `'true'`，则直接以 `application/pdf` 类型返回文件供下载。
*   **成功返回 (pdf='false'):**
    ```json
    {
        "success": true,
        "message": "PDF 获取成功",
        "name": "生成的PDF文件名.pdf",
        "data": "<Base64编码的PDF内容>"
    }
    ```
*   **成功返回 （pdf=true）:**
    *   HTTP 状态码 `200`
    *   `Content-Type: application/pdf`
    *   文件内容作为响应体。
*   **失败返回:**
    ```json
    {
        "success": false,
        "message": "错误信息"
    }
    ```
*   **示例:**
    *   获取 Base64 编码的 PDF: `GET /get_pdf/12345`
    *   直接下载 PDF 文件: `GET /get_pdf/12345?pdf=true`
    *   获取不加密的 PDF: `GET /get_pdf/12345?passwd=false`
    *   使用标题作为文件名: `GET /get_pdf/12345?Titletype=1`

### 2. 获取 PDF 文件路径

*   **路径:** `/get_pdf_path/<jm_album_id>`
*   **方法:** `GET`
*   **功能:** 与 `/get_pdf` 类似，会触发下载和生成 PDF（如果需要），但最终返回 PDF 文件在服务器上的绝对路径。
*   **路径参数:**
    *   `jm_album_id`: 禁漫天堂的相册 ID。
*   **查询参数:**
    *   `passwd` (可选, 字符串, 默认 'true'): 同 `/get_pdf`。
    *   `Titletype` (可选, 整数, 默认 2): 同 `/get_pdf`。
*   **成功返回:**
    ```json
    {
        "success": true,
        "message": "PDF 获取成功",
        "data": "/path/to/server/pdf/folder/[12345] 标题.pdf",
        "name": "[12345] 标题.pdf"
    }
    ```
*   **失败返回:**
    ```json
    {
        "success": false,
        "message": "错误信息"
    }
    ```
*   **示例:** `GET /get_pdf_path/12345`

### 3. 搜索漫画

*   **路径:** `/search`
*   **方法:** `GET`
*   **功能:** 根据提供的关键词在禁漫天堂网站上搜索漫画。
*   **查询参数:**
    *   `query` (必需, 字符串): 要搜索的关键词。
    *   `page` (可选, 整数, 默认 1): 搜索结果的页码。
*   **成功返回:**
    ```json
    {
        "success": true,
        "message": "Search successful",
        "data": {
            "results": [
                {"id": "album_id_1", "title": "title_1"},
                {"id": "album_id_2", "title": "title_2"}
                // ...
            ],
            "current_page": 1,
            "has_next_page": true // 或 false
        }
    }
    ```
*   **失败返回:**
    ```json
    {
        "success": false,
        "message": "错误信息 (例如 'Missing 'query' parameter')"
    }
    ```
*   **示例:** `GET /search?query=dingyi&page=2`

### 4. 获取详情

*   **路径:** `/album/<jm_album_id>`
*   **方法:** `GET`
*   **功能:** 根据jm_album_id获取tag。
*   **路径参数:**
    *   `jm_album_id`: 车牌号。
*   **成功返回:**
    ```json
    {
        "success": true,
        "message": "Album details retrieved",
        "data": {
            "id": "12345",
            "title": "相册标题",
            "tags": ["tag1", "tag2", ...]
        }
    }
    ```
*   **失败返回 (例如 404 Not Found):**
    ```json
    {
        "success": false,
        "message": "Album with ID '12345' not found..."
    }
    ```
*   **示例:** `GET /album/12345`

### 5. 按分类浏览

*   **路径:** `/categories`
*   **方法:** `GET`
*   **功能:** 根据分类、时间范围和排序方式浏览禁漫天堂的漫画列表。
*   **查询参数:**
    *   `page` (可选, 整数, 默认 1): 结果页码。
    *   `time` (可选, 字符串, 默认 'all'): 时间范围。可用值: `'today'`, `'week'`, `'month'`, `'all'`, `'t'`, `'w'`, `'m'`, `'a'`。
    *   `category` (可选, 字符串, 默认 'all'): 漫画分类。可用值: `'doujin'`, `'single'`, `'short'`, `'another'`, `'hanman'`, `'meiman'`, `'doujin_cosplay'`, `'cosplay'`, `'3d'`, `'english_site'`, `'all'`。
    *   `order_by` (可选, 字符串, 默认 'latest'): 排序方式。可用值: `'latest'`, `'view'`, `'picture'`, `'like'`, `'month_rank'`, `'week_rank'`, `'day_rank'`。
*   **成功返回:**
    ```json
    {
        "success": true,
        "message": "Categories retrieved successfully",
        "data": {
            "results": [
                {"id": "album_id_3", "title": "漫画标题3"},
                {"id": "album_id_4", "title": "漫画标题4"}
                // ...
            ],
            "current_page": 3,
            "has_next_page": true, // 或 false
            "params_used": { // 显示实际使用的参数值
                "time": "all",
                "category": "hanman",
                "order_by": "view"
            }
        }
    }
    ```
*   **失败返回:**
    ```json
    {
        "success": false,
        "message": "错误信息"
    }
    ```
*   **示例:** `GET /categories?category=hanman&order_by=view&page=3`
