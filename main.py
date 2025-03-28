import base64
from pathlib import Path

from jmcomic import create_option_by_file

from config import config

cfg = config()
host = cfg.host
port = cfg.port
pdf_pwd = cfg.pdf_pwd
optionFile = cfg.option_file
pdf_dir = cfg.pdf_dir
# opt = JmOption.construct(cfg.jmOpt)

opt = create_option_by_file(optionFile)
# pdf_dir = opt.plugins.after_album[0].kwargs.get('pdf_dir', './')

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


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

from flask import Flask, jsonify, request, send_file # 导入 request 和 send_file
from waitress import serve

from album_service import get_album_pdf_path

app = Flask(__name__)

@app.route('/get_pdf/<jm_album_id>', methods=['GET'])
def get_pdf(jm_album_id):
    passwd_str = request.args.get('passwd', 'true').lower()
    enable_pwd = passwd_str not in ('false', '0')
    try:
        titletype = int(request.args.get('Titletype', 1))
    except ValueError:
        titletype = 1 
    output_pdf_directly = request.args.get('pdf', 'false').lower() == 'true'

    path, name = get_album_pdf_path(jm_album_id, pdf_dir, opt, enable_pwd=enable_pwd, Titletype=titletype)
    if path is None:
        return jsonify({
            "success": False,
            "message": "PDF 文件不存在"
        }),

    if output_pdf_directly:
        try:
            return send_file(path, as_attachment=True, download_name=name)
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"发送 PDF 文件时出错: {e}"
            }), 500
    else:
        try:
            with open(path, "rb") as f:
                encoded_pdf = base64.b64encode(f.read()).decode('utf-8')
            return jsonify({
                "success": True,
                "message": "PDF 获取成功",
                "name": name,
                "data": encoded_pdf
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"读取或编码 PDF 文件时出错: {e}"
            }), 500


import os


@app.route('/get_pdf_path/<jm_album_id>', methods=['GET'])
def get_pdf_path(jm_album_id):
    passwd_str = request.args.get('passwd', 'true').lower()
    enable_pwd = passwd_str not in ('false', '0')
    try:
        titletype = int(request.args.get('Titletype', 1))
    except ValueError:
        titletype = 1 # 

    path, name = get_album_pdf_path(jm_album_id, pdf_dir, opt, enable_pwd=enable_pwd, Titletype=titletype)
    abspath = (os.path.abspath(path))
    if path is None:
        return jsonify({
            "success": False,
            "message": "PDF 文件不存在"
        }), 500
    else:
        return jsonify({
            "success": True,
            "message": "PDF 获取成功",
            "data": abspath,
            "name": name
        })


if __name__ == '__main__':
    serve(app, host=host, port=port)
