

import gc
import re # 导入 re 模块
from pathlib import Path
import os  # 导入 os 模块
import base64 # 导入 base64 模块
import shutil # 导入 shutil 模块 for rmtree

from jmcomic import download_album
# 假设 JmOption 是配置类，虽然这里没直接用，但 opt 参数可能就是这个类型
# from jmcomic import JmOption

from pdf_util import merge_webp_to_pdf


def sanitize_filename(filename):
    """移除或替换 Windows/Linux 文件名中的非法字符。"""
    # 移除 Windows 中的非法字符: < > : " / \ | ? *
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # 移除开头和结尾的空白字符
    sanitized = sanitized.strip()
    # Windows 文件名不能以句点或空格结尾
    sanitized = sanitized.rstrip('. ')
    # 将多个连续的下划线替换为单个下划线
    sanitized = re.sub(r'_+', '_', sanitized)
    return sanitized


def get_album_pdf_path(jm_album_id, pdf_dir, is_pwd, opt):
    """
    下载 JMComic 漫画并转换为 PDF，实现缓存机制。

    Args:
        jm_album_id: 要下载的漫画 ID。
        pdf_dir: 保存最终 PDF 文件的目录。
        is_pwd: 布尔值，指示 PDF 是否应受密码保护。
        opt: 用于 download_album 的 JmOption 对象或类似配置。

    Returns:
        生成或已存在的 PDF 文件的 base64 编码字符串。

    缓存行为:
    1. 函数首先检查基于 jm_album_id 的 PDF 文件是否已存在。
    2. 如果存在，读取文件内容，进行 base64 编码，删除文件，然后返回编码字符串（缓存命中）。
    3. 如果不存在，调用 `download_album` 来获取漫画元数据（如标题）并下载图片。
       假设 `download_album` 可能内部实现了避免重复下载已存在图片文件夹的机制。
    4. 从下载的图片生成 PDF。
    5. 读取生成的 PDF 文件内容，进行 base64 编码，删除文件，然后返回编码字符串。
    """
    # 确保 pdf_dir 存在
    Path(pdf_dir).mkdir(parents=True, exist_ok=True)

    # 步骤 1: 构建基于 ID 的 PDF 文件路径
    pdf_filename = f"{jm_album_id}.pdf" # 使用 ID 命名
    pdf_path = os.path.join(pdf_dir, pdf_filename)

    # 步骤 2: 检查 PDF 是否已存在 (缓存命中)
    if os.path.exists(pdf_path):
        print(f"PDF 文件已存在 (缓存命中): {pdf_path}")
        try:
            with open(pdf_path, "rb") as pdf_file:
                pdf_content = pdf_file.read()
            base64_encoded_pdf = base64.b64encode(pdf_content).decode('utf-8')
            print(f"已读取并编码缓存的 PDF: {pdf_path}")
            # 删除缓存文件
            try:
                os.remove(pdf_path)
                print(f"已删除缓存的 PDF 文件: {pdf_path}")
            except OSError as e:
                print(f"警告：删除缓存的 PDF 文件 {pdf_path} 时出错: {e}")
            return base64_encoded_pdf
        except Exception as e:
            print(f"错误：处理缓存的 PDF 文件 {pdf_path} 时出错: {e}")
            # 如果处理缓存文件失败，尝试继续生成流程
            # 或者可以选择在这里抛出异常，取决于期望的行为
            pass # 继续尝试生成

    # PDF 不存在或处理缓存失败，继续下载和生成
    print(f"开始处理漫画 ID: {jm_album_id}，将生成 PDF 并编码: {pdf_path}")
    try:
        # 步骤 3: 下载漫画（获取元数据和图片）
        # download_album 内部应处理图片是否已存在的问题
        album, _ = download_album(jm_album_id, option=opt)
        print(f"漫画 '{album.title}' 元数据获取/下载初步完成。")
    except Exception as e:
        print(f"错误：下载或获取漫画 {jm_album_id} 元数据失败: {e}")
        raise # 如果下载失败，则向上抛出异常

    # 步骤 4: 重命名下载文件夹并生成 PDF
    original_webp_folder_name = sanitize_filename(album.title)
    temp_webp_folder_name = f"temp_webp_{jm_album_id}" # 使用 ID 创建临时文件夹名
    original_webp_folder_path = Path(original_webp_folder_name)
    temp_webp_folder_path = Path(temp_webp_folder_name)

    base64_encoded_pdf = None # 初始化返回值

    try:
        # 检查原始文件夹是否存在
        if not original_webp_folder_path.is_dir():
            print(f"错误：找不到下载的图片文件夹: {original_webp_folder_path.absolute()}")
            raise FileNotFoundError(f"图片文件夹 '{original_webp_folder_path}' 在尝试下载后未找到。")

        # 重命名文件夹
        try:
            # 如果目标临时文件夹已存在（上次运行失败残留？），先删除
            if temp_webp_folder_path.exists():
                print(f"警告：发现残留的临时文件夹，将删除: {temp_webp_folder_path}")
                shutil.rmtree(temp_webp_folder_path)
            os.rename(original_webp_folder_path, temp_webp_folder_path)
            print(f"已将文件夹 '{original_webp_folder_path}' 重命名为 '{temp_webp_folder_path}'")
        except OSError as e:
            print(f"错误：重命名文件夹 '{original_webp_folder_path}' 到 '{temp_webp_folder_path}' 失败: {e}")
            raise # 重命名失败，无法继续

        # 使用重命名后的短路径生成 PDF
        print(f"开始从 '{temp_webp_folder_path}' 合并生成 PDF: {pdf_path}")
        password_to_set = str(jm_album_id) if is_pwd else None
        merge_webp_to_pdf(str(temp_webp_folder_path), pdf_path=pdf_path, is_pwd=is_pwd, password=password_to_set)
        print(f"成功生成 PDF: {pdf_path}")
        gc.collect()

        # 步骤 5: 读取、编码并删除生成的 PDF
        with open(pdf_path, "rb") as pdf_file:
            pdf_content = pdf_file.read()
        base64_encoded_pdf = base64.b64encode(pdf_content).decode('utf-8')
        print(f"已读取并编码新生成的 PDF: {pdf_path}")

        # 删除生成的 PDF 文件
        try:
            os.remove(pdf_path)
            print(f"已删除新生成的 PDF 文件: {pdf_path}")
        except OSError as e:
            print(f"警告：删除新生成的 PDF 文件 {pdf_path} 时出错: {e}")

    except Exception as e:
        print(f"错误：在处理漫画 {jm_album_id} ('{album.title}') 时发生错误: {e}")
        # 清理可能不完整的 PDF 文件
        if Path(pdf_path).exists():
            try:
                os.remove(pdf_path)
                print(f"已删除可能不完整的 PDF: {pdf_path}")
            except OSError as rm_err:
                print(f"错误：删除不完整的 PDF {pdf_path} 时出错: {rm_err}")
        # 重新引发错误，以便上层调用知道失败了
        raise
    finally:
        # 步骤 6: 清理临时的 webp 文件夹 (无论成功或失败都尝试清理)
        if temp_webp_folder_path.exists():
            try:
                shutil.rmtree(temp_webp_folder_path)
                print(f"已清理临时图片文件夹: {temp_webp_folder_path}")
            except OSError as e:
                print(f"警告：清理临时图片文件夹 {temp_webp_folder_path} 时出错: {e}")
        # 也尝试清理原始名称的文件夹，以防重命名失败但文件夹已创建
        elif original_webp_folder_path.exists():
             try:
                shutil.rmtree(original_webp_folder_path)
                print(f"已清理原始名称的图片文件夹: {original_webp_folder_path}")
             except OSError as e:
                print(f"警告：清理原始名称的图片文件夹 {original_webp_folder_path} 时出错: {e}")

    if base64_encoded_pdf is None:
         # 如果执行到这里 base64_encoded_pdf 仍然是 None，说明在 try 块中生成/编码之前就出错了
         # 或者 finally 块在 raise 之后执行了，但我们需要确保有返回值或异常
         # 由于 try 块中的错误会 raise，正常情况下不会到这里，除非有未捕获的逻辑错误
         # 为了健壮性，如果到了这里，明确抛出错误
         raise RuntimeError(f"未能成功生成或编码漫画 {jm_album_id} 的 PDF。")

    return base64_encoded_pdf
