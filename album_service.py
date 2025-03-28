import gc
from pathlib import Path
import os # 导入 os 用于删除文件

from jmcomic import download_album
from PyPDF2 import PdfReader
from PyPDF2.errors import DependencyError, FileNotDecryptedError # 导入特定错误

from pdf_util import merge_webp_to_pdf

def get_album_pdf_path(jm_album_id, pdf_dir, opt, enable_pwd=True, Titletype=2):
    album, _ = download_album(jm_album_id, option=opt)
    title = album.title

    if Titletype == 0:
        pdf_filename = f"{jm_album_id}.pdf"
    elif Titletype == 1:
        pdf_filename = f"{title}.pdf"
    else: 
        pdf_filename = f"{jm_album_id}—{title}.pdf"

    pdf_path_obj = Path(pdf_dir) / pdf_filename
    pdf_path = str(pdf_path_obj) 

    use_cache = False
    if pdf_path_obj.exists():
        try:
            reader = PdfReader(pdf_path)
            if enable_pwd:
                if reader.is_encrypted:
                    try:
                        if reader.decrypt(jm_album_id): 
                            print(f"缓存 PDF 已使用 '{jm_album_id}' 成功解密，使用缓存: {pdf_path}")
                            use_cache = True
                        else:
                             print(f"缓存 PDF 使用 '{jm_album_id}' 解密失败 (decrypt returned false)，重新生成: {pdf_path}")
                    except (FileNotDecryptedError, DependencyError, NotImplementedError) as decrypt_error:
                        print(f"缓存 PDF 使用 '{jm_album_id}' 解密失败 ({decrypt_error})，重新生成: {pdf_path}")
                else:
                    print(f"缓存 PDF 未加密，但请求需要加密，重新生成: {pdf_path}")
            else:
                if not reader.is_encrypted:
                    print(f"缓存 PDF 未加密，符合请求，使用缓存: {pdf_path}")
                    use_cache = True
                else:
                    print(f"缓存 PDF 已加密，但请求不需要加密，重新生成: {pdf_path}")

        except Exception as e:
            print(f"检查缓存 PDF 时出错 ({e})，将重新生成: {pdf_path}")
            use_cache = False 

        if not use_cache:
            try:
                os.remove(pdf_path)
            except OSError as e:
                print(f"删除旧缓存 PDF 时出错 ({e}): {pdf_path}")

    if not use_cache:
        print(f"开始生成 PDF (加密={enable_pwd}): {pdf_path}")
        webp_folder = f"./{title}"
        merge_webp_to_pdf(
            webp_folder,
            pdf_path=pdf_path,
            is_pwd=enable_pwd,
            password=jm_album_id if enable_pwd else None
        )
        gc.collect() 

    return pdf_path, pdf_filename
