import os
import base64
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

# Imports for hot-reloading and web server
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from flask import Flask, send_file, jsonify, request
from waitress import serve
from jmcomic.jm_exception import MissingAlbumPhotoException
from album_service import get_album_pdf_path

# 可复用，不要在下方函数内部创建
opt = create_option_by_file(optionFile)


# 当配置文件发生变化时，重新读取配置文件
class cfgFileChangeHandler(FileSystemEventHandler):
    def __init__(self, observer):
        self.observer = observer

    def on_modified(self, event):
        if not event.is_directory and Path(optionFile).exists():
            global opt, pdf_dir
            try:
                new_opt = create_option_by_file(optionFile)
                opt = new_opt # Update global opt only after successful load
                # Try to update pdf_dir from the reloaded option, fallback to current pdf_dir
                try:
                    # Check if plugins and after_album exist and are not empty
                    if hasattr(opt, 'plugins') and hasattr(opt.plugins, 'after_album') and opt.plugins.after_album:
                         pdf_dir = opt.plugins.after_album[0].kwargs.get('pdf_dir', pdf_dir)
                    # else: pdf_dir remains unchanged
                except (IndexError, AttributeError, KeyError, TypeError) as e:
                    print(f"警告：从配置文件更新 pdf_dir 失败: {e}. pdf_dir 保持不变。")
                print("配置文件已更新")
            except Exception as e:
                print(f"错误：重新加载配置文件 {optionFile} 失败: {e}")



observer = Observer()
observer.schedule(cfgFileChangeHandler(observer), path=optionFile, recursive=False)
observer.start()

app = Flask(__name__)


# 根据 jm_album_id 返回 pdf 文件
@app.route('/get_pdf/<jm_album_id>', methods=['GET'])
def get_pdf(jm_album_id):
    # 获取 passwd 查询参数，默认为 'true'，并转为小写
    passwd_str = request.args.get('passwd', 'true').lower()
    # 将字符串 'false' 转换为布尔值 False，其他为 True
    passwd_bool = passwd_str != 'false'

    try:
        # 使用 passwd_bool 替换原来的 pdf_pwd
        path = get_album_pdf_path(jm_album_id, pdf_dir, passwd_bool, opt)
        if path is None:
            # PDF 路径获取失败
            return jsonify({
                "success": False,
                "message": "PDF 文件不存在" # 根据反馈修改
            }), 404 # 使用 404 更合适
        else:
            # 读取 PDF 文件内容
            with open(path, 'rb') as f:
                pdf_data = f.read()
            
            # 进行 Base64 编码
            pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
            
            # 获取文件名
            pdf_file_name = Path(path).name

            # 返回 JSON 响应
            return jsonify({
                "success": True,
                "message": "PDF 获取成功",
                "name": pdf_file_name,
                "data": pdf_base64
            })
    except MissingAlbumPhotoException as e:
        # 捕获 jmcomic 库抛出的特定异常 (漫画不存在)
        return jsonify({
            "success": False,
            "message": "PDF 文件不存在" # 根据反馈修改
        }), 404 # 使用 404 Not Found 状态码
    except Exception as e:
        # 捕获其他可能的异常
        return jsonify({
            "success": False,
            "message": f"处理请求时发生未知错误: {e}"
        }), 500


# 根据 jm_album_id 获取 pdf 文件下载到本地，返回绝对路径
@app.route('/get_pdf_path/<jm_album_id>', methods=['GET'])
def get_pdf_path(jm_album_id):
    # 获取 passwd 查询参数，默认为 'true'，并转为小写
    passwd_str = request.args.get('passwd', 'true').lower()
    # 将字符串 'false' 转换为布尔值 False，其他为 True
    passwd_bool = passwd_str != 'false'

    try:
        # 使用 passwd_bool 替换原来的 pdf_pwd
        path = get_album_pdf_path(jm_album_id, pdf_dir, passwd_bool, opt)
        if path is None:
            # PDF 路径获取失败
            return jsonify({
                "success": False,
                "message": "PDF 文件不存在" # 根据反馈修改
            }), 404 # 使用 404 更合适
        else:
            abspath = os.path.abspath(path)
            pdf_file_name = Path(path).name # 获取文件名
            return jsonify({
                "success": True,
                "message": "PDF 获取成功", # 根据反馈修改
                "data": abspath,
                "name": pdf_file_name # 根据反馈添加
            })
    except MissingAlbumPhotoException as e:
        # 捕获 jmcomic 库抛出的特定异常 (漫画不存在)
        return jsonify({
            "success": False,
            "message": "PDF 文件不存在" # 根据反馈修改
        }), 404 # 使用 404 Not Found 状态码
    except Exception as e:
        # 捕获其他可能的异常
        return jsonify({
            "success": False,
            "message": f"处理请求时发生未知错误: {e}"
        }), 500


if __name__ == '__main__':
    serve(app, host=host, port=port)
