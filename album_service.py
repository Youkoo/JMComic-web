import base64

from jmcomic import create_option_by_file, download_album
from pathlib import Path

# param: is_path: 为否 则返回base64数据
def get_album_pdf_path(jm_album_id,is_path):
    # 读取配置文件
    opt = create_option_by_file('./option.yml')

    # 下载本子（只下载单文件，不需要 unpack tuple）
    album, _ = download_album(jm_album_id, option=opt)

    path,title = get_absolute_path(album,opt)
    if is_path:
        return path,title
    else:
        return to_base64(path),title


def get_absolute_path(album,opt):
    pdf_dir = opt.plugins.after_album[0].kwargs.get('pdf_dir', './')

    # 将 pdf_dir 转换为 Path 对象
    pdf_dir_path = Path(pdf_dir).resolve()  # 使用 resolve() 获取绝对路径

    # 检查目录是否存在
    if not pdf_dir_path.exists():
        return None
    else:
        # 返回完整的文件路径
        return pdf_dir_path / f"{album.title}.pdf", f"{album.title}.pdf"

def to_base64(path):
    with open(path, 'rb') as file:
        pdf_data = file.read()
        base64_data = base64.b64encode(pdf_data)
        return base64_data.decode('utf-8')
