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

以下是 JMComic API 提供的接口：

### 1. 获取 PDF 文件

*   **路径:** `/get_pdf/<jm_album_id>`
*   **方法:** `GET`
*   **功能:** 根据禁漫相册 ID 获取对应的 PDF 文件。
*   **参数:**
    *   `passwd` (可选, 默认 'true'): 控制 PDF 是否加密 ('false' 或 '0' 表示不加密)。
    *   `Titletype` (可选, 默认 1): 控制 PDF 文件名的标题格式。
    *   `pdf` (可选, 默认 'false'): 如果为 'true'，则直接下载 PDF 文件；否则，返回包含 Base64 编码的 PDF 内容的 JSON。
*   **返回:** JSON 响应（包含成功状态、消息、文件名、Base64 数据）或直接返回 PDF 文件。
*   **示例:** `GET /get_pdf/12345?pdf=true` (直接下载) 或 `GET /get_pdf/12345` (获取 Base64)

### 2. 获取 PDF 文件路径

*   **路径:** `/get_pdf_path/<jm_album_id>`
*   **方法:** `GET`
*   **功能:** 根据禁漫相册 ID 获取对应的 PDF 文件在服务器上的绝对路径。
*   **参数:**
    *   `passwd` (可选, 默认 'true'): 控制 PDF 是否加密。
    *   `Titletype` (可选, 默认 1): 控制 PDF 文件名的标题格式。
*   **返回:** JSON 响应（包含成功状态、消息、文件绝对路径、文件名）。
*   **示例:** `GET /get_pdf_path/12345`

### 3. 搜索漫画

*   **路径:** `/search`
*   **方法:** `GET`
*   **功能:** 根据关键词搜索漫画。
*   **参数:**
    *   `query` (必需): 搜索的关键词。
    *   `page` (可选, 默认 1): 搜索结果的页码。
*   **返回:** JSON 响应（包含成功状态、消息、搜索结果列表 `[{id, title}]`、当前页码、是否有下一页）。
*   **示例:** `GET /search?query=中文&page=2`

### 4. 获取相册详情

*   **路径:** `/album/<jm_album_id>`
*   **方法:** `GET`
*   **功能:** 根据禁漫相册 ID 获取相册的详细信息。
*   **返回:** JSON 响应（包含成功状态、消息、相册 ID、标题、标签列表）。
*   **示例:** `GET /album/12345`

### 5. 按分类浏览

*   **路径:** `/categories`
*   **方法:** `GET`
*   **功能:** 根据分类、时间范围和排序方式浏览漫画列表。
*   **参数:**
    *   `page` (可选, 默认 1): 结果页码。
    *   `time` (可选, 默认 'all'): 时间范围 ('today', 'week', 'month', 'all', 't', 'w', 'm', 'a')。
    *   `category` (可选, 默认 'all'): 漫画分类 ('doujin', 'single', 'short', 'another', 'hanman', 'meiman', 'doujin_cosplay', 'cosplay', '3d', 'english_site', 'all')。
    *   `order_by` (可选, 默认 'latest'): 排序方式 ('latest', 'view', 'picture', 'like', 'month_rank', 'week_rank', 'day_rank')。
*   **返回:** JSON 响应（包含成功状态、消息、结果列表 `[{id, title}]`、当前页码、是否有下一页、实际使用的查询参数）。
*   **示例:** `GET /categories?category=hanman&order_by=view&page=3`
