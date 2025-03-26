from pathlib import Path

from jmcomic import create_option_by_file

from config import config

# 读取配置文件
cfg = config()
host = cfg.host
port = cfg.port
pdf_pwd = cfg.pdf_pwd
optionFile = cfg.option_file
pdf_dir = cfg.pdf_dir
# opt = JmOption.construct(cfg.jmOpt)

# 可复用，不要在下方函数内部创建
opt = create_option_by_file(optionFile)
# pdf_dir = opt.plugins.after_album[0].kwargs.get('pdf_dir', './')

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

from flask import Flask, send_file, jsonify
from waitress import serve
from jmcomic.jm_exception import MissingAlbumPhotoException # 导入异常类

from album_service import get_album_pdf_path

app = Flask(__name__)


# 根据 jm_album_id 返回 pdf 文件
@app.route('/get_pdf/<jm_album_id>', methods=['GET'])
def get_pdf(jm_album_id):
    try:
        path = get_album_pdf_path(jm_album_id, pdf_dir, pdf_pwd, opt)
        if path is None:
            # 这种情况理论上在 MissingAlbumPhotoException 之前被捕获，但也保留
            return jsonify({
                "success": False,
                "message": "获取 PDF 路径失败，但未找到具体漫画"
            }), 500
        else:
            return send_file(
                path,
                as_attachment=True,
                download_name=Path(path).name,
                mimetype='application/pdf'
            )
    except MissingAlbumPhotoException as e:
        # 捕获 jmcomic 库抛出的特定异常
        return jsonify({
            "success": False,
            "message": f"无法找到 ID 为 {jm_album_id} 的漫画: {e}"
        }), 404 # 使用 404 Not Found 状态码
    except Exception as e:
        # 捕获其他可能的异常
        return jsonify({
            "success": False,
            "message": f"处理请求时发生未知错误: {e}"
        }), 500


import os


# 根据 jm_album_id 获取 pdf 文件下载到本地，返回绝对路径
@app.route('/get_pdf_path/<jm_album_id>', methods=['GET'])
def get_pdf_path(jm_album_id):
    try:
        path = get_album_pdf_path(jm_album_id, pdf_dir, pdf_pwd, opt)
        if path is None:
            # 这种情况理论上在 MissingAlbumPhotoException 之前被捕获，但也保留
            return jsonify({
                "success": False,
                "message": "获取 PDF 路径失败，但未找到具体漫画"
            }), 500
        else:
            abspath = (os.path.abspath(path))
            return jsonify({
                "success": True,
                "message": "ok",
                "data": abspath
            })
    except MissingAlbumPhotoException as e:
        # 捕获 jmcomic 库抛出的特定异常
        return jsonify({
            "success": False,
            "message": f"无法找到 ID 为 {jm_album_id} 的漫画: {e}"
        }), 404 # 使用 404 Not Found 状态码
    except Exception as e:
        # 捕获其他可能的异常
        return jsonify({
            "success": False,
            "message": f"处理请求时发生未知错误: {e}"
        }), 500


if __name__ == '__main__':
    serve(app, host=host, port=port)
