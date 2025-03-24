from jmcomic import create_option_by_file, download_album
from pathlib import Path


def get_album_pdf_path(jm_album_id):
    # 读取配置文件
    opt = create_option_by_file('./option.yml')

    # 下载本子（只下载单文件，不需要 unpack tuple）
    album, _ = download_album(jm_album_id, option=opt)

    pdf_dir = opt.plugins.after_album[0].kwargs.get('pdf_dir', './')

    # 将 pdf_dir 转换为 Path 对象
    pdf_dir_path = Path(pdf_dir).resolve()  # 使用 resolve() 获取绝对路径

    # 检查目录是否存在
    if not pdf_dir_path.exists():
        return None
    else:
        # 返回完整的文件路径
        return str(pdf_dir_path / f"{album.title}.pdf")


from flask import Flask
from waitress import serve

app = Flask(__name__)


@app.route('/get_pdf_path/<jm_album_id>', methods=['GET'])
def get_pdf_path(jm_album_id):
    path = get_album_pdf_path(jm_album_id)
    if path is None:
        return {
            "success": False,
            "data": ""
        }
    else:
        return {
            "success": True,
            "data": path
        }


if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=8699)
