from jmcomic import create_option_by_file, download_album
from pathlib import Path
from config import config

# 读取配置文件
cfg = config()
host = cfg.host
port = cfg.port
pdfPW = cfg.pdfPW
optionFile = cfg.optionFile
pdf_dir = cfg.pdf_dir
# opt = JmOption.construct(cfg.jmOpt)

# 可复用，不要在下方函数内部创建
opt = create_option_by_file(optionFile)
#pdf_dir = opt.plugins.after_album[0].kwargs.get('pdf_dir', './')

# 监听optionFile文件的变化, 实现配置文件的热更新
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 当配置文件发生变化时，重新读取配置文件
class cfgFileChangeHandler(FileSystemEventHandler):
    def __init__(self, observer):
        self.observer = observer

    def on_modified(self, event):
        if not event.is_directory and Path(optionFile).exists():            
            global opt, pdf_dir
            opt = create_option_by_file(optionFile)
            pdf_dir = opt.plugins.after_album[0].kwargs.get('pdf_dir', './')
            print("配置文件已更新")

observer = Observer()
observer.schedule(cfgFileChangeHandler(observer), path=optionFile, recursive=False)
observer.start()

from PyPDF2 import PdfReader, PdfWriter
from PIL import Image

def merge_webp_to_pdf(folder_path, pdf_path, password=None):
    """
    将指定文件夹下的所有 .webp 文件按照文件名顺序合并为 PDF 长图，并可选加密。
    
    :param folder_path: 包含 .webp 文件的文件夹路径
    :param output_pdf_path: 输出 PDF 文件的路径
    :param password: PDF 文件的密码（可选）
    """
    # 确保输出文件夹存在
    output_dir = Path(pdf_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # 获取文件夹下的所有 .webp 文件，并按文件名排序
    webp_files = sorted(Path(folder_path).glob("*.webp"))
    
    if not webp_files:
        raise FileNotFoundError(f"文件夹 {folder_path} 中没有找到 .webp 文件")
    
    # 打开所有 .webp 文件并转换为 RGB 模式
    images = [Image.open(webp).convert("RGB") for webp in webp_files]
    
    # 将所有图片合并为 PDF
    images[0].save(pdf_path, save_all=True, append_images=images[1:])
    print(f"PDF 文件已生成：{pdf_path}")

    pdf_reader = PdfReader(pdf_path)
    pdf_writer = PdfWriter()

    for page in pdf_reader.pages: # 尝试无损压缩
        page.compress_content_streams()
        pdf_writer.add_page(page)

    # 如果需要加密，则直接覆盖原文件
    if pdfPW and password:
        pdf_writer.encrypt(password)
        print(f"PDF 文件已加密：{pdf_path}")

    with open(pdf_path, "wb") as f:
        pdf_writer.write(f)

def get_album_pdf_path(jm_album_id):
    # 下载本子（只下载单文件，不需要 unpack tuple）
    album, _ = download_album(jm_album_id, option=opt)
    pdf_path = f"{pdf_dir}/{album.title}.pdf"

    if not Path(pdf_path).exists():
        webp_folder = f"./{album.title}"
        merge_webp_to_pdf(webp_folder, pdf_path=pdf_path, password=jm_album_id)

    return pdf_path


from flask import Flask, send_file, jsonify
from waitress import serve

app = Flask(__name__)

# 根据 jm_album_id 获取 pdf 文件
@app.route('/get_pdf_path/<jm_album_id>', methods=['GET'])
def get_pdf(jm_album_id):
    path = get_album_pdf_path(jm_album_id)
    if path is None:
        return jsonify({
            "success": False,
            "message": "PDF 文件不存在"
        }), 404
    else:
        return send_file(
            path,
            as_attachment=True,
            download_name=Path(path).name,
            mimetype='application/pdf'
        )


if __name__ == '__main__':
    serve(app, host=host, port=port)
