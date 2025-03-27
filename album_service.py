import gc
from pathlib import Path
import os # 导入 os 用于删除文件

from jmcomic import download_album
from PyPDF2 import PdfReader
from PyPDF2.errors import DependencyError, FileNotDecryptedError # 导入特定错误

from pdf_util import merge_webp_to_pdf


# 添加 enable_pwd 和 Titletype 参数
def get_album_pdf_path(jm_album_id, pdf_dir, opt, enable_pwd=True, Titletype=2):
    # 下载本子（只下载单文件，不需要 unpack tuple）
    album, _ = download_album(jm_album_id, option=opt)
    title = album.title

    # 根据 Titletype 确定文件名格式
    if Titletype == 0:
        pdf_filename = f"{jm_album_id}.pdf"
    elif Titletype == 1:
        pdf_filename = f"{title}.pdf"
    else: # Titletype == 2 或其他值（包括默认）
        pdf_filename = f"{jm_album_id}—{title}.pdf"

    pdf_path_obj = Path(pdf_dir) / pdf_filename
    pdf_path = str(pdf_path_obj) # 转换为字符串路径

    use_cache = False
    if pdf_path_obj.exists():
        try:
            reader = PdfReader(pdf_path)
            if enable_pwd:
                # 请求加密：尝试用 jm_album_id 解密
                if reader.is_encrypted:
                    try:
                        if reader.decrypt(jm_album_id): # 检查解密是否成功 (decrypt 返回解密状态)
                            print(f"缓存 PDF 已使用 '{jm_album_id}' 成功解密，使用缓存: {pdf_path}")
                            use_cache = True
                        else:
                             # decrypt 返回 False 或 0 通常也表示失败
                             print(f"缓存 PDF 使用 '{jm_album_id}' 解密失败 (decrypt returned false)，重新生成: {pdf_path}")
                    except (FileNotDecryptedError, DependencyError, NotImplementedError) as decrypt_error:
                        # FileNotDecryptedError: 密码错误
                        # DependencyError: 可能缺少解密库 (如 pypdfium2)
                        # NotImplementedError: 不支持的加密方式
                        print(f"缓存 PDF 使用 '{jm_album_id}' 解密失败 ({decrypt_error})，重新生成: {pdf_path}")
                else:
                    # 文件存在但未加密，而请求需要加密
                    print(f"缓存 PDF 未加密，但请求需要加密，重新生成: {pdf_path}")
            else:
                # 请求不加密：检查缓存是否加密
                if not reader.is_encrypted:
                    print(f"缓存 PDF 未加密，符合请求，使用缓存: {pdf_path}")
                    use_cache = True
                else:
                    # 文件存在且已加密，但请求不需要加密
                    print(f"缓存 PDF 已加密，但请求不需要加密，重新生成: {pdf_path}")

        except Exception as e:
            # 读取PDF时发生其他错误 (例如文件损坏)
            print(f"检查缓存 PDF 时出错 ({e})，将重新生成: {pdf_path}")
            use_cache = False # 确保不使用缓存

        if not use_cache:
            # 如果不使用缓存，尝试删除旧文件
            try:
                os.remove(pdf_path)
            except OSError as e:
                print(f"删除旧缓存 PDF 时出错 ({e}): {pdf_path}")

    if not use_cache:
        print(f"开始生成 PDF (加密={enable_pwd}): {pdf_path}")
        webp_folder = f"./{title}"
        # 根据 enable_pwd 决定是否加密以及密码
        merge_webp_to_pdf(
            webp_folder,
            pdf_path=pdf_path,
            is_pwd=enable_pwd,
            password=jm_album_id if enable_pwd else None
        )
        gc.collect()  # 强制垃圾回收

    return pdf_path, pdf_filename
