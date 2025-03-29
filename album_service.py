import gc
from pathlib import Path
import os
import shutil

from jmcomic import download_album
from PyPDF2 import PdfReader
from PyPDF2.errors import DependencyError, FileNotDecryptedError 

from pdf_util import merge_webp_to_pdf

def get_album_pdf_path(jm_album_id, pdf_dir, opt, enable_pwd=True, Titletype=2):
    album, _ = download_album(jm_album_id, option=opt)
    title = album.title 

    default_download_dir = Path(f"./{title}") 
    target_download_dir = Path(f"./webp/{jm_album_id}")

    if default_download_dir.exists() and default_download_dir.is_dir():
        if target_download_dir.exists():
            try:
                shutil.rmtree(target_download_dir)
                print(f"已删除已存在的目标目录: {target_download_dir}")
            except OSError as e:
                print(f"删除旧目标目录时出错 ({e}): {target_download_dir}")

        target_download_dir.parent.mkdir(parents=True, exist_ok=True)

        try:
            shutil.move(str(default_download_dir), str(target_download_dir))
            print(f"已将图片文件夹移动到: {target_download_dir}")
        except Exception as e:
            print(f"移动文件夹 {default_download_dir} 到 {target_download_dir} 时出错: {e}")
    if Titletype == 0:
        pdf_filename = f"{jm_album_id}.pdf"
    elif Titletype == 1:
        pdf_filename = f"{title}.pdf"
    else: # Default to TitleType 2 or any other value
        pdf_filename = f"[{jm_album_id}] {title}.pdf"

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
        webp_folder = str(target_download_dir) 

        if not target_download_dir.exists():
             if default_download_dir.exists():
                 print(f"警告: 目标目录 {target_download_dir} 不存在，尝试从原始下载目录 {default_download_dir} 生成 PDF")
                 webp_folder = str(default_download_dir)
             else:
                 print(f"错误: 图片目录 {target_download_dir} 和 {default_download_dir} 都不存在，无法生成 PDF")
                 return None, None 


        merge_webp_to_pdf(
            webp_folder,
            pdf_path=pdf_path,
            is_pwd=enable_pwd,
            password=jm_album_id if enable_pwd else None
        )
        gc.collect() 

    return pdf_path, pdf_filename
